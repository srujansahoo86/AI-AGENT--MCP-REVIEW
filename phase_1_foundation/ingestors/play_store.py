from google_play_scraper import Sort, reviews
from datetime import datetime, timedelta, timezone
from typing import List
from models import Review

class PlayStoreIngestor:
    def __init__(self, lang: str = 'en', country: str = 'in'):
        self.lang = lang
        self.country = country

    def fetch_reviews(self, app_id: str, weeks_ago: int = 8) -> List[Review]:
        """
        Fetches reviews from the Google Play Store.
        """
        cutoff_date = datetime.now(timezone.utc) - timedelta(weeks=weeks_ago)
        all_reviews = []
        continuation_token = None
        
        try:
            while True:
                # Fetch a batch of reviews
                result, continuation_token = reviews(
                    app_id,
                    lang=self.lang,
                    country=self.country,
                    sort=Sort.NEWEST,
                    count=100,
                    continuation_token=continuation_token
                )
                
                if not result:
                    break
                    
                batch_done = False
                
                for r in result:
                    # google-play-scraper returns naive datetime objects (usually local time or UTC based on locale, 
                    # but typically treated as naive UTC). We'll assume UTC and make them aware.
                    review_date = r['at']
                    if review_date.tzinfo is None:
                        review_date = review_date.replace(tzinfo=timezone.utc)
                    else:
                        review_date = review_date.astimezone(timezone.utc)
                        
                    if review_date < cutoff_date:
                        batch_done = True
                        break
                        
                    review = Review(
                        id=r['reviewId'],
                        date=review_date,
                        rating=r['score'],
                        title=None, # Play store reviews don't typically have titles like App store
                        review_text=r['content'],
                        version=r.get('reviewCreatedVersion'),
                        source="Play Store"
                    )
                    all_reviews.append(review)
                    
                # If we've hit reviews older than the cutoff, stop paginating
                if batch_done or not continuation_token:
                    break
                    
        except Exception as e:
            print(f"Error fetching Play Store reviews for app_id {app_id}: {e}")
            
        return all_reviews
