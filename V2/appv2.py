from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from PIL import Image
import os
from dotenv import load_dotenv
from io import BytesIO
import base64
from typing import List, Dict
import re
import datetime
import random
import webbrowser
import gradio as gr
import tempfile
import time

# Load environment variables
load_dotenv()

# Initialize model with memory
model = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=os.getenv("GEMINI_API_KEY"))
memory = ConversationBufferMemory(memory_key="history", return_messages=True)
conversation = ConversationChain(llm=model, memory=memory, verbose=True)

class ProfessionalHairAnalysisSystem:
    def __init__(self):
        self.analysis_results = ""
        self.advice_results = ""
        self.image_paths = []

    def get_product_recommendations(self, hair_type: str, concerns: List[str], budget: str = "medium") -> str:
    # This would normally query a database
        product_db = {
            "shampoo": {
                "dry": {
                    "low": "SheaMoisture Coconut & Hibiscus Curl & Shine Shampoo",
                    "medium": "Briogeo Don't Despair, Repair! Super Moisture Shampoo",
                    "high": "Oribe Gold Lust Repair & Restore Shampoo"
                },
                "damaged": {
                    "low": "Pantene Pro-V Repair and Protect Shampoo",
                    "medium": "Olaplex No. 4 Bond Maintenance Shampoo",
                    "high": "Kerastase Resistance Bain Extentioniste Shampoo"
                }
            },
            "conditioner": {
                # Similar structure
            }
        }
        
        recommendations = []
        for product_type in ['shampoo', 'conditioner', 'treatment']:
            for concern in concerns:
                if concern in product_db[product_type]:
                    rec = product_db[product_type][concern][budget]
                    recommendations.append(f"- {product_type.capitalize()}: {rec} (for {concern})")
        
        if not recommendations:
            return "No specific product recommendations available based on current analysis."
        
        return "Recommended Products:\n" + "\n".join(recommendations)

    def prepare_image(self, image_path: str) -> Dict:
        try:
            img = Image.open(image_path)
            img = img.convert('RGB')
            
            width, height = img.size
            if width > 1024 or height > 1024:
                ratio = min(1024/width, 1024/height)
                new_size = (int(width*ratio), (int(height*ratio)))
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
    # Add to your ProfessionalHairAnalysisSystem class
    # def get_detailed_product_recommendations(self, hair_analysis: str) -> str:
    #     """
    #     Extract key characteristics from analysis and generate detailed product recommendations
    #     """
    #     prompt = f"""From this hair analysis:
    #     {hair_analysis}
        
    #     Identify the following characteristics:
    #     1. Hair type (straight, wavy, curly, coily)
    #     2. Primary concerns (e.g., dryness, breakage, scalp issues)
    #     3. Current condition (damaged, color-treated, etc.)
        
    #     Then provide specific product recommendations including:
    #     - 3 shampoo options at different price points
    #     - 3 conditioner options
    #     - 2 treatment products
    #     - 1 styling product
    #     For each product include:
    #     - Brand and product name
    #     - Key beneficial ingredients
    #     - Where to purchase (e.g., Ulta, Sephora, drugstore)
    #     - Price range
        
    #     Format as a clear table with columns: Product Type, Brand/Name, Key Ingredients, Where to Buy, Price.
    #     """
        
    #     return self.get_hair_advice(prompt)
    def get_detailed_product_recommendations(self, hair_analysis: str, budget: str = "medium", concerns: List[str] = None) -> str:
        """
        Extract key characteristics from analysis and generate detailed product recommendations
        with budget and specific concerns taken into account.
        """
        if concerns is None:
            concerns = []
            
        prompt = f"""From this hair analysis:
        {hair_analysis}
        
        Identify the following characteristics:
        1. Hair type (straight, wavy, curly, coily)
        2. Primary concerns: {', '.join(concerns) if concerns else 'Not specified'}
        3. Current condition (damaged, color-treated, etc.)
        
        Then provide specific product recommendations for a {budget} budget including:
        - 3 shampoo options at different price points
        - 3 conditioner options
        - 2 treatment products
        - 1 styling product
        For each product include:
        - Brand and product name
        - Key beneficial ingredients
        - Where to purchase (e.g., Ulta, Sephora, drugstore)
        - Price range
        
        Format as a clear table with columns: Product Type, Brand/Name, Key Ingredients, Where to Buy, Price.
        """
        
        return self.get_hair_advice(prompt)


    def get_comprehensive_advice(self, analysis: str) -> str:
        prompt = f"""Based on this comprehensive hair analysis:
        {analysis}
        
        Provide DETAILED TREATMENT PLAN including:
        
        1. Immediate Care Recommendations:
            - Daily routine with specific product types
            - Key ingredients to look for
            - Application techniques
        
        2. Professional Treatments:
            - Recommended salon treatments
            - Frequency
            - Expected outcomes
        
        3. Product Recommendations:
            - For each recommended product type, suggest:
                - 1 budget option
                - 1 premium option
                - Key benefits of each
                - Where to purchase
        
        4. Lifestyle Adjustments:
            - Dietary suggestions
            - Protective styling advice
            - Environmental protection
        
        Format the recommendations clearly with headings for each category.
        """
        
        return self.get_hair_advice(prompt)
    
    # def get_comprehensive_advice(self, analysis: str) -> str:
    #     prompt = f"""Based on this comprehensive hair analysis:
    #     {analysis}
        
    #     Provide DETAILED TREATMENT PLAN covering:
        
    #     1. Immediate Care Recommendations:
    #        - Daily routine (cleansing, conditioning)
    #        - Recommended products
    #        - Handling instructions
        
    #     2. Professional Treatments:
    #        - Recommended salon treatments
    #        - Frequency
    #        - Expected outcomes
        
    #     3. Long-term Maintenance:
    #        - Ongoing care regimen
    #        - Lifestyle adjustments
    #        - Nutritional recommendations
        
    #     4. Follow-up Plan:
    #        - Recommended timeline for reassessment
    #        - Signs to watch for
    #        - When to seek professional help
        
    #     5. Product Recommendations:
    #        - Specific product types
    #        - Key ingredients to look for
    #        - Ingredients to avoid
        
    #     Organize by priority and provide rationale for each recommendation.
    #     """
        
    #     return self.get_hair_advice(prompt)
    
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
    
    def generate_html_report(self, patient_name: str = "", patient_id: str = "", dob: str = "",
                           gender: str = "", hospital_name: str = "", doctor_name: str = "",
                           analysis_date: str = "", report_id: str = None) -> str:
        if not self.analysis_results:
            return ""
        
        analysis_html = self.convert_to_html(self.analysis_results)
        advice_html = self.convert_to_html(self.advice_results)
        
        report_generated_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        age = ""
        if dob:
            try:
                birth_date = datetime.datetime.strptime(dob, "%Y-%m-%d")
                today = datetime.datetime.today()
                age = str(today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day)))
            except:
                age = "N/A"
        
        if not report_id:
            report_id = f"HA{random.randint(1000,9999)}-{datetime.datetime.now().strftime('%Y%m%d')}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Hair Analysis Report - {patient_name or 'Patient'}</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    margin: 0;
                    padding: 0;
                    background-color: #f9f9f9;
                }}
                .page {{
                    width: 21cm;
                    min-height: 29.7cm;
                    margin: 1cm auto;
                    padding: 2cm;
                    background: white;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                }}
                header {{
                    border-bottom: 2px solid #0066cc;
                    padding-bottom: 20px;
                    margin-bottom: 30px;
                }}
                .header-content {{
                    display: flex;
                    justify-content: space-between;
                    align-items: flex-end;
                }}
                .logo {{
                    max-width: 200px;
                }}
                .patient-info {{
                    margin: 20px 0;
                    background: #f0f8ff;
                    padding: 15px;
                    border-radius: 5px;
                }}
                .info-grid {{
                    display: grid;
                    grid-template-columns: repeat(2, 1fr);
                    gap: 10px;
                }}
                .info-item strong {{
                    display: inline-block;
                    width: 120px;
                }}
                h1, h2, h3 {{
                    color: #0066cc;
                }}
                h1 {{
                    margin-top: 0;
                }}
                h2 {{
                    border-bottom: 1px solid #ddd;
                    padding-bottom: 5px;
                    margin-top: 30px;
                }}
                ul {{
                    padding-left: 20px;
                }}
                .footer {{
                    margin-top: 50px;
                    text-align: center;
                    font-size: 0.8em;
                    color: #666;
                }}
                .signature {{
                    margin-top: 50px;
                    display: flex;
                    justify-content: space-between;
                }}
                .signature-line {{
                    width: 200px;
                    border-top: 1px solid #333;
                    text-align: center;
                    padding-top: 5px;
                }}
            </style>
        </head>
        <body>
            <div class="page">
                <header>
                    <div class="header-content">
                        <div>
                            <h1>Hair Analysis Report</h1>
                            <p><strong>Hospital/Clinic:</strong> {hospital_name}</p>
                        </div>
                        <div>
                            <p><strong>Report ID:</strong> {report_id}</p>
                            <p><strong>Date:</strong> {analysis_date}</p>
                        </div>
                    </div>
                </header>
                
                <div class="patient-info">
                    <h3>Patient Information</h3>
                    <div class="info-grid">
                        <div class="info-item"><strong>Name:</strong> {patient_name}</div>
                        <div class="info-item"><strong>Patient ID:</strong> {patient_id}</div>
                        <div class="info-item"><strong>Date of Birth:</strong> {dob} (Age: {age})</div>
                        <div class="info-item"><strong>Gender:</strong> {gender}</div>
                        <div class="info-item"><strong>Doctor:</strong> {doctor_name}</div>
                        <div class="info-item"><strong>Analysis Date:</strong> {analysis_date}</div>
                    </div>
                </div>
                
                <section>
                    <h2>Hair Analysis Findings</h2>
                    {analysis_html}
                </section>
                
                <section>
                    <h2>Treatment Recommendations</h2>
                    {advice_html}
                </section>
                
                <div class="signature">
                    <div class="signature-line">
                        <p>Doctor/Specialist Signature</p>
                    </div>
                    <div class="signature-line">
                        <p>Date: {datetime.datetime.now().strftime('%Y-%m-%d')}</p>
                    </div>
                </div>
                
                <div class="footer">
                    <p>Report generated on {report_generated_time} by Professional Hair Analysis System</p>
                    <p>This report is confidential and intended for the patient and their healthcare provider only.</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html_content
    
    def preview_report(self, patient_name: str, patient_id: str, dob: str, gender: str,
                      hospital_name: str, doctor_name: str, analysis_date: str) -> (str, str):
        if not self.analysis_results:
            return "", "No analysis results to preview"
        
        try:
            html_content = self.generate_html_report(
                patient_name=patient_name,
                patient_id=patient_id,
                dob=dob,
                gender=gender,
                hospital_name=hospital_name,
                doctor_name=doctor_name,
                analysis_date=analysis_date
            )
            return html_content, "Preview generated successfully"
        except Exception as e:
            return "", f"Error generating preview: {str(e)}"
    
    # def generate_report(self, patient_name: str, patient_id: str, dob: str, gender: str,
    #                    hospital_name: str, doctor_name: str, analysis_date: str) -> (str, str):
    #     if not self.analysis_results:
    #         return None, "No analysis results to generate report"
        
    #     try:
    #         timestamp = int(time.time())
    #         temp_html_path = os.path.join(tempfile.gettempdir(), f"hair_report_{timestamp}.html")
            
    #         html_content = self.generate_html_report(
    #             patient_name=patient_name,
    #             patient_id=patient_id,
    #             dob=dob,
    #             gender=gender,
    #             hospital_name=hospital_name,
    #             doctor_name=doctor_name,
    #             analysis_date=analysis_date
    #         )
    #         print()
    #         with open(temp_html_path, 'w', encoding='utf-8') as f:
    #             f.write(html_content)
            
    #         return temp_html_path, "Report generated successfully"
    #     except Exception as e:
    #         return None, f"Error generating report: {str(e)}"
    def generate_report(self, patient_name: str, patient_id: str, dob: str, gender: str,
                   hospital_name: str, doctor_name: str, analysis_date: str) -> (str, str):
        if not self.analysis_results:
            return None, "No analysis results to generate report"
        
        try:
            # Create a reports directory if it doesn't exist
            reports_dir = os.path.join(os.getcwd(), "hair_reports")
            os.makedirs(reports_dir, exist_ok=True)
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            report_filename = f"hair_report_{timestamp}.html"
            report_path = os.path.join(reports_dir, report_filename)
            
            html_content = self.generate_html_report(
                patient_name=patient_name,
                patient_id=patient_id,
                dob=dob,
                gender=gender,
                hospital_name=hospital_name,
                doctor_name=doctor_name,
                analysis_date=analysis_date
            )
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Open the report in default browser
            webbrowser.open(f"file://{report_path}")
            
            return report_path, f"Report generated successfully and saved to: {report_path}"
        except Exception as e:
            return None, f"Error generating report: {str(e)}"

# Create an instance of the system
hair_analysis_system = ProfessionalHairAnalysisSystem()

def analyze_images(patient_name, patient_id, dob, gender, hospital_name, doctor_name, analysis_date, *image_files):
    # Filter out None values from image files
    image_paths = [file.name for file in image_files if file is not None]
    
    if not image_paths:
        return "Please upload at least one image.", "", gr.Button(visible=False)
    
    try:
        if len(image_paths) == 1:
            analysis = hair_analysis_system.analyze_single_hair_image(image_paths[0])
        else:
            analysis = hair_analysis_system.analyze_multiple_hair_images(image_paths)
        
        hair_analysis_system.analysis_results = analysis
        advice = hair_analysis_system.get_comprehensive_advice(analysis)
        hair_analysis_system.advice_results = advice
        
        return analysis, advice, gr.Button(visible=True)
    except Exception as e:
        return f"Error during analysis: {str(e)}", "", gr.Button(visible=False)

# Define Gradio interface components
with gr.Blocks(title="Professional Hair Analysis System", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# Professional Hair Analysis System")
    
    with gr.Row():
        with gr.Column(scale=1):
            with gr.Group():
                gr.Markdown("### Patient Information")
                patient_name = gr.Textbox(label="Patient Name")
                patient_id = gr.Textbox(label="Patient ID")
                dob = gr.Textbox(label="Date of Birth (YYYY-MM-DD)", value=datetime.date.today().strftime("%Y-%m-%d"))
                gender = gr.Dropdown(label="Gender", choices=["Male", "Female", "Other"])
                
            with gr.Group():
                gr.Markdown("### Clinic Information")
                hospital_name = gr.Textbox(label="Clinic/Hospital Name")
                doctor_name = gr.Textbox(label="Doctor/Specialist Name")
                analysis_date = gr.Textbox(label="Date of Analysis", value=datetime.date.today().strftime("%Y-%m-%d"))
        
        with gr.Column(scale=1):
            gr.Markdown("### Hair Image Upload (Max 4 Images)")
            image1 = gr.File(label="Image 1", type="filepath")
            image2 = gr.File(label="Image 2", type="filepath")
            image3 = gr.File(label="Image 3", type="filepath")
            image4 = gr.File(label="Image 4", type="filepath")
            
            analyze_btn = gr.Button("Analyze Hair", variant="primary")
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("### Analysis Results")
            analysis_output = gr.Textbox(label="Findings", lines=10, interactive=False)
            
            gr.Markdown("### Recommendations")
            advice_output = gr.Textbox(label="Treatment Plan", lines=10, interactive=False)
            
            with gr.Row():
                preview_btn = gr.Button("Preview Report", variant="secondary")
                generate_report_btn = gr.Button("Generate Report", variant="secondary", visible=False)
                report_output = gr.File(label="Download Report", visible=False)
            report_status = gr.Textbox(label="Report Status", interactive=False)
    
    gr.Markdown("### Report Preview")
    report_preview = gr.HTML()

    # Event handlers
    analyze_btn.click(
        analyze_images,
        inputs=[patient_name, patient_id, dob, gender, hospital_name, doctor_name, analysis_date, image1, image2, image3, image4],
        outputs=[analysis_output, advice_output, generate_report_btn]
    )
    
    preview_btn.click(
        hair_analysis_system.preview_report,
        inputs=[patient_name, patient_id, dob, gender, hospital_name, doctor_name, analysis_date],
        outputs=[report_preview, report_status]
    )
    
    generate_report_btn.click(
        hair_analysis_system.generate_report,
        inputs=[patient_name, patient_id, dob, gender, hospital_name, doctor_name, analysis_date],
        outputs=[report_output, report_status]
    )
    with gr.Accordion("Detailed Product Recommendations", open=False):
        budget = gr.Dropdown(label="Budget Preference", choices=["Economy", "Mid-range", "Premium"])
        concerns = gr.CheckboxGroup(
            label="Primary Concerns",
            choices=["Dryness", "Breakage", "Frizz", "Scalp Issues", "Thinning", "Damage Repair"]
        )
        get_products_btn = gr.Button("Get Product Recommendations")
        product_recommendations = gr.Markdown()

# Add event handler
    get_products_btn.click(
        hair_analysis_system.get_detailed_product_recommendations,
        inputs=[analysis_output, budget, concerns],
        outputs=product_recommendations
    )


if __name__ == "__main__":
    demo.launch()
