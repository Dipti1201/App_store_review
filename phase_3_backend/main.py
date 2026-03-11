import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Groww Weekly Pulse API")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, '../data'))
PULSE_FILE = os.path.join(DATA_DIR, 'weekly_pulse.json')
FRONTEND_FILE = os.path.abspath(os.path.join(BASE_DIR, "../phase_4_frontend/index.html"))

print(f"DEBUG: PULSE_FILE path is {PULSE_FILE}")
print(f"DEBUG: FRONTEND_FILE path is {FRONTEND_FILE}")

# Email Config
SENDER_EMAIL = "dhuratdipti@gmail.com"
EMAIL_PASSWORD = os.getenv("EMAIL_APP_PASSWORD") # Requires Gmail App Password

import subprocess

class EmailRequest(BaseModel):
    receiver_email: EmailStr

@app.get("/")
def read_root():
    """Serve the frontend dashboard."""
    if not os.path.exists(FRONTEND_FILE):
        raise HTTPException(status_code=404, detail=f"Frontend file not found at {FRONTEND_FILE}")
    return FileResponse(FRONTEND_FILE)

@app.post("/refresh")
def refresh_data():
    """Trigger the entire pipeline: Scrape -> Clean -> Analyze."""
    try:
        print("🔄 Triggering Pipeline...")
        scraper_path = os.path.abspath(os.path.join(BASE_DIR, "../phase_1_ingestion/scraper.py"))
        cleaner_path = os.path.abspath(os.path.join(BASE_DIR, "../phase_1_ingestion/cleaner.py"))
        analyzer_path = os.path.abspath(os.path.join(BASE_DIR, "../phase_2_analysis/analyzer.py"))

        # 1. Scrape
        subprocess.run(["python", scraper_path], check=True)
        # 2. Clean
        subprocess.run(["python", cleaner_path], check=True)
        # 3. Analyze
        subprocess.run(["python", analyzer_path], check=True)
        
        return {"status": "success", "message": "Pulse data refreshed successfully."}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/pulse")
def get_latest_pulse():
    """Retrieve the latest weekly pulse note."""
    if not os.path.exists(PULSE_FILE):
        raise HTTPException(status_code=404, detail="Weekly pulse not yet generated.")
    
    with open(PULSE_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

@app.post("/send-email")
def send_pulse_email(request: EmailRequest):
    """Send the pulse report to a dynamic receiver email."""
    if not os.path.exists(PULSE_FILE):
        raise HTTPException(status_code=404, detail="No pulse report available to send.")

    if not EMAIL_PASSWORD:
        raise HTTPException(status_code=500, detail="SMTP Error: EMAIL_APP_PASSWORD is not set in .env")

    with open(PULSE_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    note = data['weekly_note']
    metadata = data.get('metadata', {"generated_at": "N/A", "report_period": "N/A"})
    
    # Construct Professional HTML Email
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; border: 1px solid #eee; padding: 20px; border-radius: 10px;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 2px solid #00d09c; padding-bottom: 10px; margin-bottom: 20px;">
                <h2 style="color: #00d09c; margin: 0;">🚀 Groww Weekly Critical Pulse</h2>
                <span style="background: #f1f5f9; padding: 4px 10px; border-radius: 4px; font-size: 12px; color: #64748b;">Week: {metadata['generated_at']}</span>
            </div>
            
            <p>Hi Team,</p>
            <p>Here is the critical health pulse for the Groww app for the week of <b>{metadata['generated_at']}</b>.</p>
            
            <h3 style="color: #e74c3c;">🚨 Top 3 Critical Themes</h3>
            <ul>
                {"".join([f"<li><b>{t}</b></li>" for t in note['top_3_themes']])}
            </ul>
            
            <h3 style="color: #2980b9;">💬 Raw User Friction</h3>
            <blockquote style="background: #f9f9f9; border-left: 5px solid #ccc; padding: 10px; font-style: italic;">
                {"<br>".join([f"\"{q}\"" for q in note['user_quotes']])}
            </blockquote>
            
            <h3 style="color: #27ae60;">🛠️ Priority Action Ideas</h3>
            <ul>
                {"".join([f"<li>{i}</li>" for i in note['action_ideas']])}
            </ul>
            
            <div style="background: #f4f4f4; padding: 15px; border-radius: 5px; margin-top: 20px;">
                <b>Executive Summary:</b><br>
                {note['summary']}
            </div>
            
            <p style="font-size: 12px; color: #777; margin-top: 30px; text-align: center;">
                Automated Pulse Report | Generated on {metadata['generated_at']}<br>
                Data Source: Play Store Reviews
            </p>
        </div>
    </body>
    </html>
    """

    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = request.receiver_email
        msg['Subject'] = f"Critical Pulse: Groww App Performance ({metadata['generated_at']})"
        
        msg.attach(MIMEText(html_content, 'html'))

        # SMTP Setup (Gmail)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()

        return {"status": "success", "message": f"Pulse report sent to {request.receiver_email}"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
