from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from PIL import Image
import os
from dotenv import load_dotenv
from io import BytesIO
import base64
from typing import List, Dict
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import re
import datetime
import random
import webbrowser

# Load environment variables
load_dotenv()

# Initialize model with memory
model = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=os.getenv("GEMINI_API_KEY"))
memory = ConversationBufferMemory(memory_key="history", return_messages=True)
conversation = ConversationChain(llm=model, memory=memory, verbose=True)

class ProfessionalHairAnalysisSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Professional Hair Analysis System")
        self.root.geometry("1000x800")
        self.root.minsize(900, 700)
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TFrame', background='#f5f5f5')
        self.style.configure('TLabel', background='#f5f5f5', font=('Helvetica', 10))
        self.style.configure('TButton', font=('Helvetica', 10), padding=5)
        self.style.configure('Title.TLabel', font=('Helvetica', 18, 'bold'), foreground='#2c3e50')
        self.style.configure('TEntry', padding=5)
        self.style.configure('TLabelFrame', font=('Helvetica', 11, 'bold'), background='#f5f5f5')
        
        # Create main container
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)
        
        # Title
        self.title_label = ttk.Label(
            self.main_frame, 
            text="Professional Hair Analysis System", 
            style='Title.TLabel'
        )
        self.title_label.pack(pady=(0, 20))
        
        # Patient Information Frame
        self.info_frame = ttk.LabelFrame(
            self.main_frame, 
            text="Patient & Clinic Information", 
            padding=(15, 10)
        )
        self.info_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Patient Details
        ttk.Label(self.info_frame, text="Patient Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.patient_name = ttk.Entry(self.info_frame, width=30)
        self.patient_name.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(self.info_frame, text="Patient ID:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.patient_id = ttk.Entry(self.info_frame, width=15)
        self.patient_id.grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(self.info_frame, text="Date of Birth:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.dob = ttk.Entry(self.info_frame, width=15)
        self.dob.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(self.info_frame, text="Gender:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.gender = ttk.Combobox(self.info_frame, values=["Male", "Female", "Other"], width=10)
        self.gender.grid(row=1, column=3, sticky=tk.W, padx=5, pady=5)
        
        # Clinic Details
        ttk.Label(self.info_frame, text="Clinic/Hospital:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.hospital_name = ttk.Entry(self.info_frame, width=30)
        self.hospital_name.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(self.info_frame, text="Doctor/Specialist:").grid(row=2, column=2, sticky=tk.W, padx=5, pady=5)
        self.doctor_name = ttk.Entry(self.info_frame, width=20)
        self.doctor_name.grid(row=2, column=3, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(self.info_frame, text="Date of Analysis:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.analysis_date = ttk.Entry(self.info_frame, width=15)
        self.analysis_date.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        self.analysis_date.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
        
        # Image upload section
        self.upload_frame = ttk.LabelFrame(
            self.main_frame, 
            text="Hair Image Upload (Max 4 Images)", 
            padding=(15, 10)
        )
        self.upload_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.image_paths = []
        self.image_labels = []
        
        for i in range(4):
            row_frame = ttk.Frame(self.upload_frame)
            row_frame.pack(fill=tk.X, pady=5)
            
            label = ttk.Label(row_frame, text=f"Image {i+1}:", width=8)
            label.pack(side=tk.LEFT)
            
            path_label = ttk.Label(row_frame, text="No image selected", width=50, relief=tk.SUNKEN, padding=5)
            path_label.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
            
            btn = ttk.Button(
                row_frame, 
                text="Browse", 
                command=lambda idx=i: self.browse_image(idx),
                width=10
            )
            btn.pack(side=tk.LEFT, padx=5)
            
            clear_btn = ttk.Button(
                row_frame,
                text="Clear",
                command=lambda idx=i: self.clear_image(idx),
                width=8
            )
            clear_btn.pack(side=tk.LEFT)
            
            self.image_labels.append(path_label)
        
        # Analysis button
        self.analyze_btn = ttk.Button(
            self.main_frame,
            text="Analyze Hair",
            command=self.analyze_images,
            state=tk.DISABLED,
            style='TButton'
        )
        self.analyze_btn.pack(pady=10)
        
        # Results section
        self.results_frame = ttk.LabelFrame(
            self.main_frame, 
            text="Analysis Results", 
            padding=(15, 10)
        )
        self.results_frame.pack(fill=tk.BOTH, expand=True)
        
        self.results_text = tk.Text(
            self.results_frame,
            wrap=tk.WORD,
            font=('Helvetica', 10),
            padx=10,
            pady=10,
            bg='white',
            relief=tk.SUNKEN
        )
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(self.results_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.results_text.yview)
        
        # Action buttons frame
        self.action_frame = ttk.Frame(self.main_frame)
        self.action_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.save_btn = ttk.Button(
            self.action_frame,
            text="Save Full Report",
            command=self.save_report,
            state=tk.DISABLED,
            width=15
        )
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        self.preview_btn = ttk.Button(
            self.action_frame,
            text="Preview Report",
            command=self.preview_report,
            state=tk.DISABLED,
            width=15
        )
        self.preview_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = ttk.Button(
            self.action_frame,
            text="Clear All",
            command=self.clear_all,
            width=15
        )
        self.clear_btn.pack(side=tk.RIGHT, padx=5)
        
        # Store analysis results
        self.analysis_results = ""
        self.advice_results = ""
        self.temp_html_path = "temp_report.html"
    
    def browse_image(self, index):
        filetypes = (
            ('Image files', '*.jpg *.jpeg *.png *.webp'),
            ('All files', '*.*')
        )
        
        filename = filedialog.askopenfilename(
            title=f'Select hair image {index+1}',
            filetypes=filetypes
        )
        
        if filename:
            if index < len(self.image_paths):
                self.image_paths[index] = filename
            else:
                self.image_paths.insert(index, filename)
            
            self.image_labels[index].config(text=filename)
            
            if any(self.image_paths):
                self.analyze_btn.config(state=tk.NORMAL)
    
    def clear_image(self, index):
        if index < len(self.image_paths):
            self.image_paths[index] = ""
            self.image_labels[index].config(text="No image selected")
            
            if not any(self.image_paths):
                self.analyze_btn.config(state=tk.DISABLED)
    
    def analyze_images(self):
        valid_paths = [path for path in self.image_paths if path]
        
        if not valid_paths:
            messagebox.showerror("Error", "Please select at least one image")
            return
        
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "Analyzing images... Please wait...\n")
        self.root.update()
        
        try:
            if len(valid_paths) == 1:
                analysis = self.analyze_single_hair_image(valid_paths[0])
                self.analysis_results = analysis
                self.results_text.delete(1.0, tk.END)
                self.results_text.insert(tk.END, "=== HAIR ANALYSIS RESULTS ===\n\n")
                self.results_text.insert(tk.END, analysis)
                
                if "unclear" not in analysis.lower():
                    self.results_text.insert(tk.END, "\n\n=== BASIC RECOMMENDATIONS ===\n\n")
                    advice = self.get_hair_advice("Provide basic care recommendations based on this analysis")
                    self.advice_results = advice
                    self.results_text.insert(tk.END, advice)
                    self.enable_report_buttons()
            else:
                analysis = self.analyze_multiple_hair_images(valid_paths)
                self.analysis_results = analysis
                self.results_text.delete(1.0, tk.END)
                self.results_text.insert(tk.END, "=== COMPREHENSIVE HAIR ANALYSIS ===\n\n")
                self.results_text.insert(tk.END, analysis)
                
                if "unclear" not in analysis.lower():
                    self.results_text.insert(tk.END, "\n\n=== DETAILED RECOMMENDATIONS ===\n\n")
                    advice = self.get_comprehensive_advice(analysis)
                    self.advice_results = advice
                    self.results_text.insert(tk.END, advice)
                    self.enable_report_buttons()
                    
        except Exception as e:
            messagebox.showerror("Analysis Error", f"An error occurred during analysis:\n{str(e)}")
            self.results_text.insert(tk.END, f"\n\nError: {str(e)}")
    
    def enable_report_buttons(self):
        self.save_btn.config(state=tk.NORMAL)
        self.preview_btn.config(state=tk.NORMAL)
    
    def save_report(self):
        if not self.analysis_results or not self.advice_results:
            messagebox.showerror("Error", "No analysis results to save")
            return
        
        filetypes = (
            ('HTML files', '*.html'),
            ('PDF files', '*.pdf'),
            ('All files', '*.*')
        )
        
        default_filename = f"Hair_Analysis_{self.patient_name.get() or 'Patient'}_{datetime.date.today().strftime('%Y%m%d')}"
        filename = filedialog.asksaveasfilename(
            title='Save Hair Analysis Report',
            defaultextension='.html',
            filetypes=filetypes,
            initialfile=default_filename
        )
        
        if filename:
            try:
                report_id = f"HA{random.randint(1000, 9999)}-{datetime.datetime.now().strftime('%Y%m%d')}"
                
                self.save_analysis_report(
                    self.analysis_results, 
                    self.advice_results, 
                    filename,
                    patient_name=self.patient_name.get(),
                    patient_id=self.patient_id.get(),
                    dob=self.dob.get(),
                    gender=self.gender.get(),
                    hospital_name=self.hospital_name.get(),
                    doctor_name=self.doctor_name.get(),
                    analysis_date=self.analysis_date.get(),
                    report_id=report_id
                )
                messagebox.showinfo("Success", f"Report saved successfully to:\n{filename}")
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save report:\n{str(e)}")
    
    def preview_report(self):
        if not self.analysis_results or not self.advice_results:
            messagebox.showerror("Error", "No analysis results to preview")
            return
        
        try:
            report_id = f"HA{random.randint(1000, 9999)}-{datetime.datetime.now().strftime('%Y%m%d')}"
            
            self.save_analysis_report(
                self.analysis_results, 
                self.advice_results, 
                self.temp_html_path,
                patient_name=self.patient_name.get(),
                patient_id=self.patient_id.get(),
                dob=self.dob.get(),
                gender=self.gender.get(),
                hospital_name=self.hospital_name.get(),
                doctor_name=self.doctor_name.get(),
                analysis_date=self.analysis_date.get(),
                report_id=report_id
            )
            webbrowser.open(f"file://{os.path.abspath(self.temp_html_path)}")
        except Exception as e:
            messagebox.showerror("Preview Error", f"Failed to generate preview:\n{str(e)}")
    
    def clear_all(self):
        self.image_paths = []
        for label in self.image_labels:
            label.config(text="No image selected")
        self.analyze_btn.config(state=tk.DISABLED)
        self.results_text.delete(1.0, tk.END)
        self.analysis_results = ""
        self.advice_results = ""
        self.save_btn.config(state=tk.DISABLED)
        self.preview_btn.config(state=tk.DISABLED)
        self.patient_name.delete(0, tk.END)
        self.patient_id.delete(0, tk.END)
        self.dob.delete(0, tk.END)
        self.gender.set('')
        self.hospital_name.delete(0, tk.END)
        self.doctor_name.delete(0, tk.END)
        self.analysis_date.delete(0, tk.END)
        self.analysis_date.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
    
    def prepare_image(self, image_path: str) -> Dict:
        try:
            img = Image.open(image_path)
            img = img.convert('RGB')
            
            width, height = img.size
            if width > 1024 or height > 1024:
                ratio = min(1024/width, 1024/height)
                new_size = (int(width*ratio), int(height*ratio))
                img = img.resize(new_size, Image.LANCZOS)
            
            buffered = BytesIO()
            img.save(buffered, format="JPEG", quality=90)
            return {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(buffered.getvalue()).decode('utf-8'),
                "filename": os.path.basename(image_path)
            }
        except Exception as e:
            raise ValueError(f"Error processing image {image_path}: {str(e)}")
    
    def analyze_single_hair_image(self, image_path: str) -> str:
        try:
            if not os.path.exists(image_path):
                return "Error: Image file not found."
            
            image_data = self.prepare_image(image_path)
            
            prompt = """As a professional hair specialist, analyze this hair image in detail:
            
            1. Hair Characteristics:
               - Texture (straight, wavy, curly, coily)
               - Density (thin, medium, thick)
               - Diameter (fine, medium, coarse)
               - Porosity level
            
            2. Scalp Condition:
               - Visible scalp health
               - Signs of irritation or abnormalities
            
            3. Hair Health:
               - Ends condition (split ends, damage)
               - Breakage patterns
               - Signs of chemical damage
               - Moisture/protein balance indicators
            
            4. Additional Observations:
               - Any visible scalp conditions
               - Hairline characteristics
               - Growth patterns
            
            Provide:
            - Detailed findings with confidence levels
            - Clear explanations of technical terms
            - Specific areas needing closer examination
            """
            
            message = [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {
                    "url": f"data:{image_data['mime_type']};base64,{image_data['data']}",
                    "detail": "high"
                }}
            ]
            
            response = conversation.invoke({"input": message})
            return response["response"]
        
        except Exception as e:
            return f"Error processing image: {str(e)}"
    
    def analyze_multiple_hair_images(self, image_paths: List[str]) -> str:
        try:
            if not image_paths:
                return "Error: No images provided."
            
            if len(image_paths) > 4:
                return "Error: Maximum 4 images allowed for analysis."
            
            image_data_list = []
            for path in image_paths:
                if not os.path.exists(path):
                    return f"Error: Image not found - {path}"
                image_data_list.append(self.prepare_image(path))
            
            prompt = f"""As a senior hair specialist, analyze these {len(image_data_list)} images of the same patient's hair:
            
            Perform COMPREHENSIVE ANALYSIS by:
            
            1. Individual Image Analysis:
               - Analyze each image separately first
               - Note unique observations from each angle
            
            2. Comparative Analysis:
               - Identify consistent characteristics across images
               - Resolve any discrepancies between images
               - Determine most accurate overall assessment
            
            3. Detailed Assessment of:
               - Hair type and texture from all angles
               - Scalp health from visible areas
               - Hair density and distribution
               - Damage patterns and severity
               - Growth patterns and hairline
            
            4. Final Evaluation:
               - Most likely hair characteristics
               - Confidence levels for each finding
               - Recommended additional views if needed
            
            Image Details: {[img['filename'] for img in image_data_list]}
            """
            
            messages = [{"type": "text", "text": prompt}]
            for img_data in image_data_list:
                messages.append({
                    "type": "image_url", 
                    "image_url": {
                        "url": f"data:{img_data['mime_type']};base64,{img_data['data']}",
                        "detail": "high"
                    }
                })
            
            response = conversation.invoke({"input": messages})
            return response["response"]
        
        except Exception as e:
            return f"Error processing images: {str(e)}"
    
    def get_hair_advice(self, follow_up: str) -> str:
        response = conversation.invoke({"input": follow_up})
        return response["response"]
    
    def get_comprehensive_advice(self, analysis: str) -> str:
        prompt = f"""Based on this comprehensive hair analysis:
        {analysis}
        
        Provide DETAILED TREATMENT PLAN covering:
        
        1. Immediate Care Recommendations:
           - Daily routine (cleansing, conditioning)
           - Recommended products
           - Handling instructions
        
        2. Professional Treatments:
           - Recommended salon treatments
           - Frequency
           - Expected outcomes
        
        3. Long-term Maintenance:
           - Ongoing care regimen
           - Lifestyle adjustments
           - Nutritional recommendations
        
        4. Follow-up Plan:
           - Recommended timeline for reassessment
           - Signs to watch for
           - When to seek professional help
        
        5. Product Recommendations:
           - Specific product types
           - Key ingredients to look for
           - Ingredients to avoid
        
        Organize by priority and provide rationale for each recommendation.
        """
        
        return self.get_hair_advice(prompt)
    
    def convert_to_html(self, text: str) -> str:
        lines = text.splitlines()
        html_lines = []
        in_list = False
        in_table = False

        for line in lines:
            stripped = line.strip()

            # Handle lists
            if stripped.startswith(("* ", "- ")):
                if not in_list:
                    html_lines.append("<ul>")
                    in_list = True
                item = stripped[2:]
                item = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", item)
                html_lines.append(f"<li>{item}</li>")
            else:
                if in_list:
                    html_lines.append("</ul>")
                    in_list = False
                
                # Convert bold text
                line = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", line)
                
                # Handle paragraphs
                if line.strip():
                    html_lines.append(f"<p>{line}</p>")

        if in_list:
            html_lines.append("</ul>")

        return "\n".join(html_lines)
    
    def save_analysis_report(self, analysis: str, advice: str, output_path: str, 
                           patient_name: str = "", patient_id: str = "", dob: str = "",
                           gender: str = "", hospital_name: str = "", doctor_name: str = "",
                           analysis_date: str = "", report_id: str = ""):
        analysis_html = self.convert_to_html(analysis)
        advice_html = self.convert_to_html(advice)
        
        report_generated_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        age = ""
        if dob:
            try:
                birth_date = datetime.datetime.strptime(dob, "%Y-%m-%d")
                today = datetime.datetime.today()
                age = str(today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day)))
            except:
                age = "N/A"
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Hair Analysis Report - {patient_name or 'Patient'}</title>
            <style>
                body {{
                    font-family: 'Arial', sans-serif;
                    margin: 0;
                    padding: 0;
                    color: #333;
                    line-height: 1.6;
                }}
                .page {{
                    width: 21cm;
                    min-height: 29.7cm;
                    margin: 1cm auto;
                    padding: 1.5cm;
                    box-sizing: border-box;
                    background: white;
                    box-shadow: 0 0 10px rgba(0,0,0,0.1);
                }}
                .letterhead {{
                    border-bottom: 3px double #5A189A;
                    padding-bottom: 15px;
                    margin-bottom: 25px;
                    text-align: center;
                }}
                .hospital-name {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #5A189A;
                    margin-bottom: 5px;
                }}
                .contact-info {{
                    font-size: 12px;
                    color: #666;
                }}
                .report-header {{
                    display: flex;
                    justify-content: space-between;
                    margin: 25px 0;
                }}
                .patient-info, .report-info {{
                    width: 48%;
                }}
                .info-box {{
                    border: 1px solid #ddd;
                    padding: 15px;
                    margin-bottom: 20px;
                    border-radius: 5px;
                }}
                .info-box h3 {{
                    margin-top: 0;
                    color: #5A189A;
                    border-bottom: 1px solid #eee;
                    padding-bottom: 5px;
                }}
                .info-grid {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 10px;
                }}
                .info-item {{
                    margin-bottom: 8px;
                }}
                .info-label {{
                    font-weight: bold;
                    color: #555;
                }}
                .section {{
                    margin: 30px 0;
                }}
                .section-title {{
                    background-color: #5A189A;
                    color: white;
                    padding: 8px 15px;
                    border-radius: 5px;
                    font-size: 18px;
                    margin-bottom: 15px;
                }}
                ul {{
                    padding-left: 25px;
                }}
                li {{
                    margin-bottom: 8px;
                }}
                .signature-area {{
                    margin-top: 50px;
                    text-align: right;
                }}
                .signature-line {{
                    display: inline-block;
                    border-top: 1px solid #333;
                    width: 250px;
                    margin-top: 40px;
                    padding-top: 5px;
                    text-align: center;
                }}
                .footer {{
                    margin-top: 50px;
                    font-size: 11px;
                    color: #777;
                    text-align: center;
                    border-top: 1px solid #eee;
                    padding-top: 10px;
                }}
                .report-id {{
                    background-color: #f0f0f0;
                    padding: 3px 8px;
                    border-radius: 3px;
                    font-family: monospace;
                    font-size: 14px;
                }}
                @media print {{
                    body {{
                        background: none;
                    }}
                    .page {{
                        width: auto;
                        margin: 0;
                        padding: 2cm;
                        box-shadow: none;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="page">
                <div class="letterhead">
                    <div class="hospital-name">{hospital_name or 'Hair Analysis Center'}</div>
                    <div class="contact-info">
                        123 Dermatology Street, Medical City | Tel: (123) 456-7890 | Email: contact@hairclinic.com
                    </div>
                </div>
                
                <div class="report-header">
                    <div class="info-box patient-info">
                        <h3>Patient Information</h3>
                        <div class="info-grid">
                            <div class="info-item">
                                <span class="info-label">Name:</span> {patient_name or 'Not specified'}
                            </div>
                            <div class="info-item">
                                <span class="info-label">Patient ID:</span> {patient_id or 'N/A'}
                            </div>
                            <div class="info-item">
                                <span class="info-label">Date of Birth:</span> {dob or 'N/A'}
                            </div>
                            <div class="info-item">
                                <span class="info-label">Age:</span> {age}
                            </div>
                            <div class="info-item">
                                <span class="info-label">Gender:</span> {gender or 'N/A'}
                            </div>
                            <div class="info-item">
                                <span class="info-label">Doctor:</span> {doctor_name or 'Not specified'}
                            </div>
                        </div>
                    </div>
                    
                    <div class="info-box report-info">
                        <h3>Report Information</h3>
                        <div class="info-grid">
                            <div class="info-item">
                                <span class="info-label">Report ID:</span> <span class="report-id">{report_id or 'N/A'}</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">Analysis Date:</span> {analysis_date or 'N/A'}
                            </div>
                            <div class="info-item">
                                <span class="info-label">Report Generated:</span> {report_generated_time}
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="section">
                    <div class="section-title">HAIR ANALYSIS FINDINGS</div>
                    {analysis_html}
                </div>
                
                <div class="section">
                    <div class="section-title">TREATMENT PLAN & RECOMMENDATIONS</div>
                    {advice_html}
                </div>
                
                <div class="signature-area">
                    <div class="signature-line">
                        {doctor_name or 'Hair Specialist'}
                    </div>
                </div>
                
                <div class="footer">
                    <p>This report was generated by the Professional Hair Analysis System. Confidential - For medical use only.</p>
                    <p>© {datetime.datetime.now().year} {hospital_name or 'Hair Analysis Center'}. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

if __name__ == "__main__":
    root = tk.Tk()
    app = ProfessionalHairAnalysisSystem(root)
    root.mainloop()
