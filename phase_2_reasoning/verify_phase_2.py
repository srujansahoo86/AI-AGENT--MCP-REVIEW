from clustering import ReviewClusterer
from scrubber import PIIScrubber

def verify():
    print("--- Verifying Phase 2 ---")
    
    # 1. Test Scrubber
    print("\n1. Testing PII Scrubber...")
    scrubber = PIIScrubber()
    test_pii = "My email is john.doe@example.com and phone is 555-123-4567. Terrible app!"
    scrubbed = scrubber.scrub(test_pii)
    print(f"Original: {test_pii}")
    print(f"Scrubbed: {scrubbed}")
    if "[EMAIL]" in scrubbed and "[PHONE]" in scrubbed:
        print("SUCCESS: Scrubber correctly masked PII.")
    else:
        print("ERROR: Scrubber failed to mask PII.")

    # 2. Test Clustering
    print("\n2. Testing Clustering Engine (with mock data)...")
    
    # Mock data with clear distinct themes
    mock_reviews = [
        # Theme 1: Login/Crash issues
        "App crashes immediately on startup",
        "Can't login, says incorrect password but it is correct",
        "Keeps crashing every time I try to open it",
        "The login screen is completely broken",
        "Crash on launch. Fix this please.",
        "Black screen when I open the app",
        "Unable to log into my account since the new update",
        
        # Theme 2: Great UI / Positive
        "Love the new design, looks very modern",
        "The UI is clean and easy to use",
        "Beautiful interface and smooth animations",
        "Great user experience overall, very intuitive",
        "Amazing app, love how it looks now",
        "Clean design. Good job developers.",
        "Very user friendly interface",
        
        # Theme 3: Customer Support
        "Customer service is terrible, no response for days",
        "Support team never replied to my email",
        "Bad support. Waiting 2 weeks for a refund.",
        "Nobody answers the phone when I call support",
        "Customer care is practically non-existent",
        "Horrible experience with the support staff",
        "Please improve your customer service response times"
    ]
    
    try:
        clusterer = ReviewClusterer()
        clusters = clusterer.cluster_reviews(mock_reviews)
        
        print("\nSUCCESS: Clustering completed.")
        print(f"Found {len(clusters)} clusters (including -1 for noise/outliers):")
        
        for cluster_id, reviews in clusters.items():
            print(f"\nCluster {cluster_id} ({len(reviews)} reviews):")
            # Print up to 3 samples from each cluster
            for r in reviews[:3]:
                print(f"  - {r}")
                
    except Exception as e:
        print(f"ERROR: Clustering failed: {e}")

if __name__ == "__main__":
    verify()
