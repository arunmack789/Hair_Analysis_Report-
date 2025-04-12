from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from PIL import Image
import os
from dotenv import load_dotenv
from io import BytesIO
import base64
from typing import List, Dict
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import re

# Load environment variables
load_dotenv()

# Initialize model with memory
model = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=os.getenv("GEMINI_API_KEY"))
memory = ConversationBufferMemory(memory_key="history", return_messages=True)
conversation = ConversationChain(llm=model, memory=memory, verbose=True)

class HairAnalysisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Professional Hair Analysis System")
        self.root.geometry("800x600")
        
        # Configure style
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10), padding=5)
        self.style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        
        # Create main container
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        self.title_label = ttk.Label(
            self.main_frame, 
            text="Professional Hair Analysis System", 
            style='Title.TLabel'
        )
        self.title_label.pack(pady=(0, 20))
        
        # Image upload section
        self.upload_frame = ttk.LabelFrame(
            self.main_frame, 
            text="Upload Hair Images (Max 4)", 
            padding=10
        )
        self.upload_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.image_paths = []
        self.image_labels = []
        
        for i in range(4):
            row_frame = ttk.Frame(self.upload_frame)
            row_frame.pack(fill=tk.X, pady=2)
            
            label = ttk.Label(row_frame, text=f"Image {i+1}:", width=8)
            label.pack(side=tk.LEFT)
            
            path_label = ttk.Label(row_frame, text="No image selected", width=40)
            path_label.pack(side=tk.LEFT, padx=5)
            
            btn = ttk.Button(
                row_frame, 
                text="Browse", 
                command=lambda idx=i: self.browse_image(idx)
            )
            btn.pack(side=tk.LEFT)
            
            self.image_labels.append(path_label)
        
        # Analysis button
        self.analyze_btn = ttk.Button(
            self.main_frame,
            text="Analyze Hair",
            command=self.analyze_images,
            state=tk.DISABLED
        )
        self.analyze_btn.pack(pady=10)
        
        # Results section
        self.results_frame = ttk.LabelFrame(
            self.main_frame, 
            text="Analysis Results", 
            padding=10
        )
        self.results_frame.pack(fill=tk.BOTH, expand=True)
        
        self.results_text = tk.Text(
            self.results_frame,
            wrap=tk.WORD,
            font=('Arial', 10),
            height=15,
            padx=10,
            pady=10
        )
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.results_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.results_text.yview)
        
        # Save report button (initially hidden)
        self.save_btn = ttk.Button(
            self.main_frame,
            text="Save Full Report",
            command=self.save_report,
            state=tk.DISABLED
        )
        self.save_btn.pack(pady=10)
        
        # Store analysis results
        self.analysis_results = ""
        self.advice_results = ""
    
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
            self.image_paths.insert(index, filename)
            self.image_labels[index].config(text=filename)
            
            # Enable analyze button if at least one image is selected
            if any(self.image_paths):
                self.analyze_btn.config(state=tk.NORMAL)
    
    def analyze_images(self):
        # Filter out empty paths
        valid_paths = [path for path in self.image_paths if path]
        
        if not valid_paths:
            messagebox.showerror("Error", "Please select at least one image")
            return
        
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "Analyzing images... Please wait...\n")
        self.root.update()
        
        try:
            if len(valid_paths) == 1:
                analysis = analyze_single_hair_image(valid_paths[0])
                self.analysis_results = analysis
                self.results_text.delete(1.0, tk.END)
                self.results_text.insert(tk.END, "=== ANALYSIS RESULTS ===\n\n")
                self.results_text.insert(tk.END, analysis)
                
                if "unclear" not in analysis.lower():
                    self.results_text.insert(tk.END, "\n\n=== BASIC RECOMMENDATIONS ===\n\n")
                    advice = get_hair_advice("Provide basic care recommendations based on this analysis")
                    self.advice_results = advice
                    self.results_text.insert(tk.END, advice)
                    self.save_btn.config(state=tk.NORMAL)
            else:
                analysis = analyze_multiple_hair_images(valid_paths)
                self.analysis_results = analysis
                self.results_text.delete(1.0, tk.END)
                self.results_text.insert(tk.END, "=== ANALYSIS RESULTS ===\n\n")
                self.results_text.insert(tk.END, analysis)
                
                if "unclear" not in analysis.lower():
                    self.results_text.insert(tk.END, "\n\n=== COMPREHENSIVE RECOMMENDATIONS ===\n\n")
                    advice = get_comprehensive_advice(analysis)
                    self.advice_results = advice
                    self.results_text.insert(tk.END, advice)
                    self.save_btn.config(state=tk.NORMAL)
                    
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during analysis: {str(e)}")
            self.results_text.insert(tk.END, f"\n\nError: {str(e)}")
    
    def save_report(self):
        if not self.analysis_results or not self.advice_results:
            messagebox.showerror("Error", "No analysis results to save")
            return
        
        filetypes = (
            ('HTML files', '*.html'),
            ('All files', '*.*')
        )
        
        filename = filedialog.asksaveasfilename(
            title='Save Hair Analysis Report',
            defaultextension='.html',
            filetypes=filetypes,
            initialfile='hair_analysis_report.html'
        )
        
        if filename:
            try:
                save_analysis_report(self.analysis_results, self.advice_results, filename)
                messagebox.showinfo("Success", f"Report saved successfully to:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save report: {str(e)}")

def prepare_image(image_path: str) -> Dict:
    """Optimize image for analysis with clear instructions"""
    try:
        img = Image.open(image_path)
        
        # Enhance image quality for hair analysis
        img = img.convert('RGB')
        
        # Resize maintaining aspect ratio (optimal for hair analysis)
        width, height = img.size
        if width > 1024 or height > 1024:
            ratio = min(1024/width, 1024/height)
            new_size = (int(width*ratio), int(height*ratio))
            img = img.resize(new_size, Image.LANCZOS)
        
        # Convert to base64
        buffered = BytesIO()
        img.save(buffered, format="JPEG", quality=90)
        return {
            "mime_type": "image/jpeg",
            "data": base64.b64encode(buffered.getvalue()).decode('utf-8'),
            "filename": os.path.basename(image_path)
        }
    except Exception as e:
        raise ValueError(f"Error processing image {image_path}: {str(e)}")

def analyze_single_hair_image(image_path: str) -> str:
    """Specialized hair analysis with guided prompts for single image"""
    try:
        if not os.path.exists(image_path):
            return "Please provide a valid image path."
        
        image_data = prepare_image(image_path)
        
        prompt = """Please analyze this hair image carefully. Focus on:
        1. Visible hair texture (straight, wavy, curly, coily)
        2. Hair thickness (fine, medium, coarse)
        3. Visible scalp condition
        4. Hair ends condition
        5. Any visible damage patterns
        
        Provide confidence level for each assessment.
        If unclear, specify what additional images would help."""
        
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

def analyze_multiple_hair_images(image_paths: List[str]) -> str:
    """Comprehensive analysis of multiple hair images from same person"""
    try:
        # Validation
        if not image_paths:
            return "Please provide at least one image path."
        
        if len(image_paths) > 5:
            return "Please provide no more than 5 images for optimal analysis."
        
        # Prepare all images
        image_data_list = []
        for path in image_paths:
            if not os.path.exists(path):
                return f"Image not found: {path}"
            image_data_list.append(prepare_image(path))
        
        # Specialized prompt for multi-image analysis
        prompt = f"""I'm providing {len(image_data_list)} images of the same person's hair from different angles/lighting.
        
        Perform COMPREHENSIVE ANALYSIS by:
        1. Comparing all images to identify consistent characteristics
        2. Analyzing each image individually first, then comparing
        3. Creating unified assessment of:
           - Hair type/texture (consider all angles)
           - Overall hair health
           - Scalp condition visibility
           - Damage patterns
        4. Note any discrepancies between images with possible reasons
        5. Provide confidence levels for each finding
        6. Suggest ideal image angles if more are needed
        
        IMAGE DETAILS:
        {[img['filename'] for img in image_data_list]}"""
        
        # Format messages with all images
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

def get_hair_advice(follow_up: str) -> str:
    """Get personalized hair care advice"""
    response = conversation.invoke({"input": follow_up})
    return response["response"]

def get_comprehensive_advice(analysis: str) -> str:
    """Get complete hair care regimen considering all factors"""
    prompt = f"""Based on this comprehensive hair analysis:
    {analysis}
    
    Provide DETAILED RECOMMENDATIONS covering:
    1. Daily care routine (shampoo, conditioner, brushing)
    2. Weekly treatments
    3. Professional treatments needed
    4. Lifestyle adjustments
    5. Product recommendations by hair concern
    6. Timeline for expected improvements
    
    Organize by priority (most to least important)."""
    
    return get_hair_advice(prompt)

def convert_to_html(text: str) -> str:
    """Convert markdown-like text to HTML with bullets and bold"""
    lines = text.splitlines()
    html_lines = []
    in_list = False

    for line in lines:
        stripped = line.strip()

        # Start of a list
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
            # Convert bold
            line = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", line)
            # Paragraph
            if line.strip():
                html_lines.append(f"<p>{line}</p>")

    if in_list:
        html_lines.append("</ul>")

    return "\n".join(html_lines)

def save_analysis_report(analysis: str, advice: str, output_path: str = "hair_report.html"):
    """Save analysis and recommendations to a styled HTML file with bullets and formatting"""
    analysis_html = convert_to_html(analysis)
    advice_html = convert_to_html(advice)

    html_content = f"""
    <html>
    <head>
        <title>Hair Analysis Report</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 40px;
                background-color: #f9f9f9;
                color: #333;
            }}
            h1 {{
                color: #5A189A;
                border-bottom: 2px solid #5A189A;
            }}
            h2 {{
                color: #0077b6;
                margin-top: 30px;
            }}
            .section {{
                background-color: #ffffff;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.1);
                margin-bottom: 30px;
            }}
            ul {{
                padding-left: 20px;
            }}
            li {{
                margin-bottom: 10px;
            }}
            p {{
                margin: 10px 0;
                line-height: 1.6;
            }}
        </style>
    </head>
    <body>
        <h1>Hair Analysis Report</h1>

        <div class="section">
            <h2>Analysis Results</h2>
            {analysis_html}
        </div>

        <div class="section">
            <h2>Recommendations</h2>
            {advice_html}
        </div>

        <footer style="text-align: center; margin-top: 50px; font-size: 0.9em; color: #777;">
            Generated by the Professional Hair Analysis System
        </footer>
    </body>
    </html>
    """

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"Styled HTML report saved to {output_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = HairAnalysisApp(root)
    root.mainloop()