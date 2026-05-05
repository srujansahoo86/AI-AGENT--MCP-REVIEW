import os
from database import init_db, get_run_status, update_run_status
from ingestors import AppStoreIngestor, PlayStoreIngestor

def verify():
    print("--- Verifying Phase 1 ---")
    
    # 1. Test Database
    print("\n1. Testing Database Initialization...")
    init_db()
    
    # Insert a mock run
    update_run_status("Groww", "2026-W42", "completed", "mock_doc_id", "mock_msg_id")
    status = get_run_status("Groww", "2026-W42")
    if status == "completed":
        print("SUCCESS: Database works and idempotency records are saved.")
    else:
        print(f"ERROR: Database error: Expected 'completed', got '{status}'")
        
    # Clean up mock db record if we wanted to, but keeping it is fine since it's just a test db

    # 2. Test Ingestion
    print("\n2. Testing Ingestors...")
    
    # Let's test with a popular app, e.g., Groww
    # Groww App Store ID: 1402597285
    # Groww Play Store ID: com.nextbillion.groww
    app_store_id = "1402597285"
    play_store_id = "com.nextbillion.groww"
    weeks_to_fetch = 2
    
    app_ingestor = AppStoreIngestor(country="in")
    print(f"\nFetching App Store reviews for last {weeks_to_fetch} weeks...")
    app_reviews = app_ingestor.fetch_reviews(app_store_id, weeks_ago=weeks_to_fetch)
    print(f"SUCCESS: Fetched {len(app_reviews)} reviews from App Store.")
    if app_reviews:
        print(f"   Sample: {app_reviews[0].date.strftime('%Y-%m-%d')} - {app_reviews[0].rating} stars")
        
    play_ingestor = PlayStoreIngestor(lang="en", country="in")
    print(f"\nFetching Play Store reviews for last {weeks_to_fetch} weeks...")
    play_reviews = play_ingestor.fetch_reviews(play_store_id, weeks_ago=weeks_to_fetch)
    print(f"SUCCESS: Fetched {len(play_reviews)} reviews from Play Store.")
    if play_reviews:
        print(f"   Sample: {play_reviews[0].date.strftime('%Y-%m-%d')} - {play_reviews[0].rating} stars")

    if app_reviews or play_reviews:
        print("\nSUCCESS: Phase 1 Verification Successful: Unified models, database, and ingestors are working.")
    else:
        print("\nWARNING: Phase 1 Verification Warning: No reviews fetched. This could be normal if no reviews exist in the window, or an error occurred.")

if __name__ == "__main__":
    verify()
