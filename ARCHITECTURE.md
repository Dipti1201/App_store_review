# 🚀 Groww App Weekly Pulse: Architecture & Development Plan

## 📌 Project Overview
The **Groww App Weekly Pulse** is an automated tool designed to transform recent Google Play Store reviews into a high-impact, one-page summary for internal stakeholders (Product, Support, and Leadership). It leverages the **Groq LLM** to categorize feedback and generate actionable product ideas.

---

## 🛠️ Tech Stack
- **AI/LLM:** Groq (using Llama-3-70b or similar for high-speed analysis)
- **Scraper:** `google_play_scraper` (Python)
- **Backend:** FastAPI (Python)
- **Frontend:** Vite + React + Vanilla CSS (Premium, sleek, and responsive UI)
- **Email:** SMTP (Gmail) with fixed sender `dhuratdipti@gmail.com`
- **Data:** JSON/CSV for local persistence (No heavy database required for MVP)

---

## 🏗️ Phase-wise Development Architecture

### **Phase 1: Review Ingestion & PII Filtering**
*Focus: Data acquisition and security.*
- **Review Harvester:** Fetch reviews from the last 8–12 weeks for the Groww app.
- **Fields Collected:** `score` (rating), `title`, `content` (text), `at` (date), `thumbsUpCount` (usefulness).
- **PII Guard:** Explicit filtering to exclude `userName`, `userImage`, or personal identifiers.
- **Output:** Cleaned JSON file ready for LLM processing.

### **Phase 2: LLM Thematic Analysis (Core Engine)**
*Focus: Intelligence and Summarization using Groq.*
- **Thematic Grouping:** Categorize reviews into **max 5 themes** (e.g., Onboarding, KYC, Payments, Statements, Withdrawals).
- **Pulse Generator:** Use Groq to extract:
  - Top 3 themes based on volume/sentiment.
  - 3 representative user quotes.
  - 3 action-oriented ideas for the product team.
- **Constraints:** Keep summary scannable and under 250 words.

### **Phase 3: Backend & Email Automation**
*Focus: Report generation and dynamic delivery.*
- **API service:** FastAPI endpoint to trigger analytical pulses.
- **Email Drafter:** Sends the pulse as a formal HTML email from `dhuratdipti@gmail.com`.
- **Dynamic Routing:** Receiver email is captured via frontend input.
- **Requirement:** User must provide a Gmail App Password in `.env` for SMTP.

### **Phase 4: Frontend Dashboard**
*Focus: Premium Visual Experience.*
- **Pulse Wall:** A clean, modern dashboard to view the latest "Weekly Pulse".
- **Visual Analytics:** Tiny sparks/charts showing rating distribution for the period.
- **Action Center:** Buttons to "Trigger Re-analysis" or "Open Email Draft".
- **Design:** Dark mode support, glassmorphism, and smooth transitions.

---

## 📂 Project Directory Structure

```text
/
├── .cursor/                # Cursor configuration
├── phase_1_ingestion/      # Scripts for google_play_scraper and PII cleaning
│   ├── scraper.py
│   └── cleaner.py
├── phase_2_analysis/       # Groq integration and prompt engineering
│   ├── groq_client.py
│   └── analyzer.py
├── phase_3_backend/        # FastAPI server and Email drafting logic
│   ├── main.py
│   ├── email_service.py
│   └── templates/
├── phase_4_frontend/       # Vite/React dashboard
│   ├── src/
│   ├── public/
│   └── index.html
├── shared/                 # Configs, .env, and utility constants
├── data/                   # Local storage for cleaned reviews (gitignored)
└── ARCHITECTURE.md         # This file
```

---

## 📋 Key Constraints & Data Policy
- **Privacy:** Absolutely NO usernames, emails, or PII in any processed data.
- **Themes:** Strictly capped at 5 themes to maintain focus.
- **Brevity:** Summaries must be ≤ 250 words.
- **Scraping:** Use `google_play_scraper` library only (public exports). No login-required scraping.
