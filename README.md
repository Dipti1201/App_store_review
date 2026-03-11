# 🚀 Groww App: Weekly Critical Pulse

An automated intelligence engine that transforms thousands of Play Store reviews into a one-page "Critical Health Pulse" for product stakeholders.

## 📌 Project Overview

This tool identifies core friction points in the Groww app by specifically analyzing negative and neutral feedback (Rating ≤ 3). It filters out noise, protects PII, and uses LLMs (Groq / Llama 3) to generate actionable insights.

### Key Features:
- **Phase 1: Intelligent Ingestion**: Scrapes 12 weeks of reviews, filters PII, and removes non-English/junk content.
- **Phase 2: Thematic Analysis**: Vertical alignment of themes, raw user evidence, and fix-oriented action ideas.
- **Phase 3: Automated Distribution**: A FastAPI backend that generates professional HTML reports and sends them via SMTP.
- **Phase 4: Insights Dashboard**: A premium, glassmorphic UI for real-time monitoring and manual triggers.

---

## 🛠️ Tech Stack

- **LLM**: Groq (Llama-3.3-70b-versatile)
- **Backend**: FastAPI (Python)
- **Frontend**: Vanilla JS / CSS (Modern Glassmorphism)
- **Data Source**: `google-play-scraper`
- **Email**: SMTP (Gmail)

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.9+
- A [Groq API Key](https://console.groq.com/)
- A Gmail App Password

### 2. Setup
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd App_store_review
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure your `.env` file:
   ```env
   GROQ_API_KEY=your_key_here
   EMAIL_APP_PASSWORD=your_app_password_here
   ```

### 3. Running the System
#### Option A: Local (FastAPI)
1. **Start the Backend**:
   ```bash
   cd phase_3_backend
   python main.py
   ```
2. **Access the Dashboard**:
   Open `http://localhost:8000` in your browser.

#### Option B: Streamlit Cloud (Hosting)
1. Connect this repo to [Streamlit Cloud](https://share.streamlit.io/).
2. Set the Main File Path to `streamlit_app.py`.
3. Add your secrets in the Streamlit Dashboard (Advanced Settings > Secrets):
   ```toml
   GROQ_API_KEY = "your_key"
   EMAIL_APP_PASSWORD = "your_app_password"
   ```

---

## 📅 Maintenance
The system is designed to run on a **Monday-start cycle**. Reports generated mid-week will automatically align to the most recent Monday, making it perfect for weekly stakeholder syncs.

---

## 🔒 Security
- **PII Defense**: All identifiable data (usernames, images) is stripped during the ingestion phase.
- **Secrets**: API keys and passwords are managed via `.env` and are never committed to version control.

---
*Built for Product Growth & Excellence.*
