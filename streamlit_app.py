import streamlit as st
import json
import os
import subprocess
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Page Config
st.set_page_config(page_title="Groww Weekly Pulse", layout="wide", page_icon="🚀")

# Load environment variables (Local) or use secrets (Streamlit Cloud)
if os.path.exists(".env"):
    load_dotenv()

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
EMAIL_APP_PASSWORD = st.secrets.get("EMAIL_APP_PASSWORD") or os.getenv("EMAIL_APP_PASSWORD")
SENDER_EMAIL = "dhuratdipti@gmail.com"

# Paths
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
PULSE_FILE = os.path.join(DATA_DIR, "weekly_pulse.json")
HTML_TEMPLATE = os.path.join(BASE_DIR, "phase_4_frontend", "index.html")

def get_pulse_data(file_path):
    # No cache here for now to ensure we see fresh disk changes
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

@st.cache_data
def load_html_template(template_path):
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()

def send_pulse_email(receiver_email, data):
    if not EMAIL_APP_PASSWORD:
        return False, "Email App Password not configured."
    
    note = data['weekly_note']
    metadata = data.get('metadata', {"generated_at": "N/A", "report_period": "N/A"})
    
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
            <ul>{"".join([f"<li><b>{t}</b></li>" for t in note['top_3_themes']])}</ul>
            <h3 style="color: #2980b9;">💬 Raw User Friction</h3>
            <blockquote style="background: #f9f9f9; border-left: 5px solid #ccc; padding: 10px; font-style: italic;">
                {"<br>".join([f"\"{q}\"" for q in note['user_quotes']])}
            </blockquote>
            <h3 style="color: #27ae60;">🛠️ Priority Action Ideas</h3>
            <ul>{"".join([f"<li>{i}</li>" for i in note['action_ideas']])}</ul>
            <div style="background: #f4f4f4; padding: 15px; border-radius: 5px; margin-top: 20px;">
                <b>Executive Summary:</b><br>{note['summary']}
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
        msg['To'] = receiver_email
        msg['Subject'] = f"Critical Pulse: Groww App Performance ({metadata['generated_at']})"
        msg.attach(MIMEText(html_content, 'html'))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, EMAIL_APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True, "Email sent successfully!"
    except Exception as e:
        return False, str(e)

def run_refresh():
    st.cache_data.clear() # Clear all caches when starting refresh
    try:
        # (scraper paths etc remain same)
        scraper_path = os.path.join(BASE_DIR, "phase_1_ingestion", "scraper.py")
        cleaner_path = os.path.join(BASE_DIR, "phase_1_ingestion", "cleaner.py")
        analyzer_path = os.path.join(BASE_DIR, "phase_2_analysis", "analyzer.py")
        
        env = os.environ.copy()
        if GROQ_API_KEY: env["GROQ_API_KEY"] = GROQ_API_KEY
        if EMAIL_APP_PASSWORD: env["EMAIL_APP_PASSWORD"] = EMAIL_APP_PASSWORD

        # Run pipeline
        for script in [scraper_path, cleaner_path, analyzer_path]:
            res = subprocess.run([sys.executable, script], env=env, capture_output=True, text=True)
            if res.returncode != 0:
                return False, f"Error in {os.path.basename(script)}: {res.stderr}"

        return True, "Pipeline refreshed successfully!"
    except Exception as e:
        return False, str(e)

# --- UI LOGIC ---
st.sidebar.title("🛠️ Actions")
st.sidebar.markdown("Use these controls to manage the Weekly Pulse report.")

# Email Input
receiver = st.sidebar.text_input("Distribute to Email", placeholder="stakeholder@company.com")
if st.sidebar.button("🚀 Send Pulse Note"):
    pulse_data = get_pulse_data(PULSE_FILE)
    if not pulse_data:
        st.sidebar.error("No pulse data available.")
    else:
        with st.sidebar.spinner("Sending..."):
            success, msg = send_pulse_email(receiver, pulse_data)
            if success: st.sidebar.success(msg)
            else: st.sidebar.error(msg)

st.sidebar.markdown("---")

# Refresh Button
if st.sidebar.button("🔄 Re-run Analysis"):
    with st.sidebar.spinner("Analyzing 12 weeks of data..."):
        success, msg = run_refresh()
        if success:
            st.sidebar.success(msg)
            st.rerun()
        else:
            st.sidebar.error(msg)

# Main Display
pulse_data = get_pulse_data(PULSE_FILE)

if pulse_data:
    html_code = load_html_template(HTML_TEMPLATE)
    
    # Simple data injection
    data_injection = f"<script>window.PULSE_DATA = {json.dumps(pulse_data)};</script>"
    
    # Hide the Sidebar/Actions in the HTML component since they are in Streamlit sidebar
    css_hide = "<style>.action-center { display: none !important; } .dashboard { grid-template-columns: 1fr !important; }</style>"
    
    final_html = html_code.replace("<body>", f"<body>{data_injection}{css_hide}")
    st.components.v1.html(final_html, height=1200, scrolling=True)
else:
    st.info("👋 Welcome! No pulse data found yet.")
    st.warning("Please click **'Re-run Analysis'** in the sidebar to generate the first report.")
