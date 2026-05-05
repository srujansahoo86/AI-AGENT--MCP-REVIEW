import requests
from datetime import datetime, timedelta, timezone
from typing import List
from models import Review

class AppStoreIngestor:
    def __init__(self, country: str = "in"):
        self.country = country

    def fetch_reviews(self, app_id: str, weeks_ago: int = 8) -> List[Review]:
        """
        Fetches reviews from the Apple App Store RSS feed.
        """
        url = f"https://itunes.apple.com/{self.country}/rss/customerreviews/id={app_id}/sortBy=mostRecent/json"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            print(f"Error fetching App Store reviews for app_id {app_id}: {e}")
            return []

        entries = data.get("feed", {}).get("entry", [])
        
        # The first entry in the RSS feed is usually information about the app itself, not a review.
        if entries and not isinstance(entries, list):
            entries = [entries]
            
        reviews = []
        cutoff_date = datetime.now(timezone.utc) - timedelta(weeks=weeks_ago)

        for entry in entries:
            # Skip the app info entry which doesn't have an author name often, or lacks author uri
            if "author" not in entry or "name" not in entry["author"]:
                continue
                
            try:
                # App store dates are like: 2024-03-12T10:20:30-07:00
                date_str = entry.get("updated", {}).get("label")
                if not date_str:
                    continue
                    
                review_date = datetime.fromisoformat(date_str).astimezone(timezone.utc)
                
                # Check if review is within the configurable time window
                if review_date < cutoff_date:
                    continue

                review = Review(
                    id=entry.get("id", {}).get("label", ""),
                    date=review_date,
                    rating=int(entry.get("im:rating", {}).get("label", 0)),
                    title=entry.get("title", {}).get("label", ""),
                    review_text=entry.get("content", {}).get("label", ""),
                    version=entry.get("im:version", {}).get("label", ""),
                    source="App Store"
                )
                reviews.append(review)
            except Exception as e:
                print(f"Error parsing App Store entry: {e}")
                continue

        return reviews
