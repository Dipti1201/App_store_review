import json
import os
from datetime import datetime, timedelta
from google_play_scraper import Sort, reviews

# Application settings
APP_ID = 'com.nextbillion.groww'
WEEKS_LOOKBACK = 12
DATA_DIR = os.path.join(os.getcwd(), 'data')
OUTPUT_FILE = os.path.join(DATA_DIR, 'raw_reviews.json')

def fetch_groww_reviews():
    """
    Fetch Googl Play Store reviews for Groww (com.nextbillion.groww)
    Filtering for last 12 weeks and removing PII.
    """
    print(f"🚀 Starting Phase 1: Ingesting reviews for {APP_ID}...")
    
    # Calculate cutsheet for the past 12 weeks
    cutoff_date = datetime.now() - timedelta(weeks=WEEKS_LOOKBACK)
    all_reviews = []
    continuation_token = None
    
    # Ensure data directory exists
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    # Fetching reviews in chunks until we reach the cutoff date
    while True:
        result, continuation_token = reviews(
            APP_ID,
            lang='en', # Focusing on English reviews for thematic analysis
            country='in',
            sort=Sort.NEWEST,
            count=100, # Max per request recommended
            continuation_token=continuation_token
        )
        
        reached_cutoff = False
        for r in result:
            review_date = r['at']
            if review_date < cutoff_date:
                reached_cutoff = True
                break
            
            # PII Defense: ONLY extract specified, non-identifying fields
            cleaned_review = {
                'score': r['score'],
                'title': r['thumbsUpCount'], # note: reviews() doesn't always have title, using thumbsUp as proxy for importance
                'text': r['content'],
                'date': review_date.strftime('%Y-%m-%d %H:%M:%S'),
                'usefulness': r['thumbsUpCount']
            }
            all_reviews.append(cleaned_review)
            
        if reached_cutoff or not continuation_token:
            break
            
        print(f"   Collected {len(all_reviews)} reviews so far...")

    # Save to JSON
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_reviews, f, indent=2, ensure_ascii=False)
        
    print(f"✅ Phase 1 Complete! {len(all_reviews)} reviews saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    fetch_groww_reviews()
