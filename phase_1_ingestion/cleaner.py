import json
import os
import re
import emoji
from langdetect import detect, DetectorFactory

# Set seed for reproducible language detection
DetectorFactory.seed = 0

# Paths
DATA_DIR = os.path.join(os.getcwd(), 'data')
INPUT_FILE = os.path.join(DATA_DIR, 'raw_reviews.json')
OUTPUT_FILE = os.path.join(DATA_DIR, 'cleaned_reviews.json')

# Thresholds
MIN_WORDS = 5
MAX_REVIEWS = 2000

def contains_emoji(text):
    """Check if the string contains any emojis."""
    return emoji.emoji_count(text) > 0

def is_english(text):
    """Detect if the text is English using langdetect."""
    try:
        # We also want to reject Hinglish (often detected as other languages)
        # and non-Latin characters.
        if not text.isascii(): # Quick ASCII check for English-only focus
             return False
        return detect(text) == 'en'
    except:
        return False

def clean_reviews():
    """
    Refine raw reviews with strict criteria:
    - Min 5 words.
    - No Emojis.
    - English only.
    - No duplicates.
    - Max 2000 (sorted by usefulness).
    """
    print("🧹 Starting Strict Data Cleaning Step...")
    
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Error: {INPUT_FILE} not found. Run scraper first.")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    seen_text = set()
    filtered_data = []
    
    stats = {
        'short': 0,
        'emoji': 0,
        'non_english': 0,
        'duplicate': 0
    }

    for r in raw_data:
        text = r.get('text', '').strip()
        
        # 1. Word Count Check (>= 5)
        words = text.split()
        if len(words) < MIN_WORDS:
            stats['short'] += 1
            continue
        
        # 2. Emoji Check (No emojis allowed)
        if contains_emoji(text):
            stats['emoji'] += 1
            continue
            
        # 3. Duplicate Check
        # Normalize text for deduplication
        norm_text = re.sub(r'\s+', ' ', text.lower())
        if norm_text in seen_text:
            stats['duplicate'] += 1
            continue
            
        # 4. English Detection
        if not is_english(text):
            stats['non_english'] += 1
            continue
            
        seen_text.add(norm_text)
        filtered_data.append(r)

    # 5. Ranking & Capping (Max 2000)
    # Sort by usefulness (Thumbs up count) then by rating (lower ratings are often more insightful)
    filtered_data.sort(key=lambda x: (x.get('usefulness', 0), -x.get('score', 5)), reverse=True)
    
    final_data = filtered_data[:MAX_REVIEWS]

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Strict Cleaning Complete!")
    print(f"   Original: {len(raw_data)} reviews")
    print(f"   Skipped (Short < 5 words): {stats['short']}")
    print(f"   Skipped (Contains Emoji): {stats['emoji']}")
    print(f"   Skipped (Non-English): {stats['non_english']}")
    print(f"   Skipped (Duplicates): {stats['duplicate']}")
    print(f"   Total filtered: {len(filtered_data)}")
    print(f"   Final Capped Output: {len(final_data)} reviews")
    print(f"   Saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    clean_reviews()
