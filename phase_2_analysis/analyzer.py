import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

# Paths
# Paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, 'data')
INPUT_FILE = os.path.join(DATA_DIR, 'cleaned_reviews.json')
OUTPUT_FILE = os.path.join(DATA_DIR, 'weekly_pulse.json')

# Groq Config
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL = "llama-3.3-70b-versatile" 

client = Groq(api_key=GROQ_API_KEY)

def analyze_reviews_with_groq():
    """
    1. Filter for Negative Reviews (Rating <= 3).
    2. Group reviews into 5 themes based on pain points.
    3. Identify top 3 critical themes.
    4. Select 3 representative user quotes of friction/bugs.
    5. Generate 3 action-oriented fix ideas.
    """
    print("🧠 Starting Phase 2: Negative Review Thematic Analysis...")
    
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Error: {INPUT_FILE} not found. Run cleaner first.")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        reviews_data = json.load(f)

    # FILTER: Focus strictly on Negative/Neutral reviews (Rating <= 3)
    negative_reviews = [r for r in reviews_data if r.get('score', 5) <= 3]
    
    if not negative_reviews:
        print("⚠️ No negative reviews found in the dataset! Using all reviews as fallback.")
        negative_reviews = reviews_data

    # PRIORITIZE: Take the top 100 most "useful" negative reviews 
    # These represent pain points that many other users also experienced.
    top_negative_reviews = sorted(negative_reviews, key=lambda x: x.get('usefulness', 0), reverse=True)[:100]
    
    # Prepare metadata: Align with Monday-start cycle
    today = datetime.now()
    monday_of_week = today - timedelta(days=today.weekday()) # today.weekday() is 0 for Monday
    
    generation_date = monday_of_week.strftime("%d %B %Y")
    report_period = generation_date

    # Prepare reviews for the prompt
    formatted_reviews = ""
    for idx, r in enumerate(top_negative_reviews):
        formatted_reviews += f"Review {idx+1} (Rating: {r['score']}, Useful: {r['usefulness']}): {r['text']}\n"

    system_prompt = f"""
    You are a Senior Product Growth Analyst for Groww. 
    Your mission is to find the most critical friction points, bugs, and user frustrations from recent reviews.
    
    TASK: Generate a "Critical Weekly Pulse" report based EXCLUSIVELY on negative/neutral feedback.
    
    CONSTRAINTS:
    - MAX 5 themes for categorization.
    - The final note MUST be ≤ 250 words.
    - Tone: Professional, scannable, and action-oriented.
    - REPORT DATE: {generation_date}
    - VERTICAL ALIGNMENT (CRITICAL): The `top_3_themes`, `user_quotes`, and `action_ideas` MUST follow a perfect 1:1:1 mapping:
      - theme[0] (Problem) <-> quote[0] (Proof) <-> action[0] (Solution)
      - theme[1] (Problem) <-> quote[1] (Proof) <-> action[1] (Solution)
      - theme[2] (Problem) <-> quote[2] (Proof) <-> action[2] (Solution)
    - USER QUOTES: Select exactly 3 quotes. They MUST be COMPLETE sentences that clearly articulate the friction for the corresponding theme at the same index.
    
    OUTPUT STRUCTURE (JSON Format):
    {{
      "metadata": {{
        "generated_at": "{generation_date}",
        "report_period": "{report_period}"
      }},
      "all_themes": ["theme1", "theme2", "theme3", "theme4", "theme5"],
      "weekly_note": {{
        "top_3_themes": ["themeA", "themeB", "themeC"],
        "user_quotes": ["quote1", "quote2", "quote3"],
        "action_ideas": ["idea1", "idea2", "idea3"],
        "summary": "100-word executive summary pulse focused on current user frustrations and resolution path."
      }}
    }}
    """

    user_prompt = f"""
    Please analyze the following 100 recent NEGATIVE/NEUTRAL reviews for Groww:
    
    {formatted_reviews}
    
    Extract the most significant pain points and generate the JSON output as specified.
    """

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model=MODEL,
            response_format={"type": "json_object"}
        )

        response_content = chat_completion.choices[0].message.content
        pulse_data = json.loads(response_content)

        # Save to file
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(pulse_data, f, indent=2)

        print(f"✅ Phase 2 (Negatives) Complete! Weekly pulse saved to {OUTPUT_FILE}")
        
        # Print a preview
        print("\n--- CRITICAL WEEKLY PULSE PREVIEW (NEGATIVES) ---")
        note = pulse_data['weekly_note']
        print(f"🚨 Top 3 Critical Themes: {', '.join(note['top_3_themes'])}")
        print("\nUser Friction Quotes:")
        for q in note['user_quotes']: print(f"- \"{q}\"")
        print("\nFix-Oriented Action Ideas:")
        for i in note['action_ideas']: print(f"- {i}")
        print(f"\nExecutive Summary: {note['summary']}")
        print("----------------------------\n")

    except Exception as e:
        print(f"❌ Groq API Error: {str(e)}")

if __name__ == "__main__":
    analyze_reviews_with_groq()
