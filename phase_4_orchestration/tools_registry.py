import sys
import os
import json
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# Add the project root and relevant phase directories to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
phase_1_path = os.path.join(project_root, "phase_1_foundation")
phase_2_path = os.path.join(project_root, "phase_2_reasoning")

if project_root not in sys.path:
    sys.path.append(project_root)
if phase_1_path not in sys.path:
    sys.path.append(phase_1_path)
if phase_2_path not in sys.path:
    sys.path.append(phase_2_path)

from phase_1_foundation.ingestors.app_store import AppStoreIngestor
from phase_1_foundation.ingestors.play_store import PlayStoreIngestor
from phase_2_reasoning.clustering import ReviewClusterer
from phase_3_mcp_client.client import GoogleMCPClient

# Initialize components
app_store = AppStoreIngestor()
play_store = PlayStoreIngestor()
clusterer = ReviewClusterer()
mcp_client = GoogleMCPClient()

def fetch_all_reviews(apple_app_id: str, google_play_id: str, weeks_ago: int = 8) -> List[Dict[str, Any]]:
    """Fetches reviews from both stores."""
    print(f"Fetching reviews for Apple: {apple_app_id}, Google: {google_play_id} (weeks_ago={weeks_ago})...")
    apple_reviews = app_store.fetch_reviews(apple_app_id, weeks_ago=weeks_ago)
    google_reviews = play_store.fetch_reviews(google_play_id, weeks_ago=weeks_ago)
    
    combined = []
    for r in apple_reviews + google_reviews:
        data = r.dict() if hasattr(r, 'dict') else r
        if isinstance(data.get('date'), datetime):
            data['date'] = data['date'].isoformat()
        combined.append(data)
    
    if len(combined) > 30:
        print(f"Limiting agent context to 30 reviews (out of {len(combined)}).")
        combined = combined[:30]
        
    return combined

def cluster_and_summarize(reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Scrubs PII and clusters reviews."""
    print("Scrubbing PII from reviews...")
    from phase_2_reasoning.scrubber import PIIScrubber
    scrubber = PIIScrubber()
    
    scrubbed_reviews = []
    for r in reviews:
        content = r.get('content', '') or r.get('text', '')
        r['content'] = scrubber.scrub(content)
        scrubbed_reviews.append(r)
        
    print(f"Clustering {len(scrubbed_reviews)} reviews...")
    return clusterer.cluster_reviews(scrubbed_reviews)

def deliver_report(doc_id: str, report_content: str, email_to: str, subject: str) -> Dict[str, Any]:
    """Delivers report via MCP Client."""
    print("Delivering report to Google Docs...")
    doc_res = mcp_client.append_section(doc_id, report_content)
    
    print(f"Sending email to {email_to}...")
    email_res = mcp_client.send_email(email_to, subject, report_content)
    
    return {
        "doc_status": doc_res,
        "email_status": email_res
    }

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "fetch_all_reviews",
            "description": "Fetch reviews from Apple and Google Play stores",
            "parameters": {
                "type": "object",
                "properties": {
                    "apple_app_id": {"type": "string"},
                    "google_play_id": {"type": "string"},
                    "weeks_ago": {"type": "integer"}
                },
                "required": ["apple_app_id", "google_play_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cluster_and_summarize",
            "description": "Cluster reviews into themes",
            "parameters": {
                "type": "object",
                "properties": {
                    "reviews": {"type": "array", "items": {"type": "object"}}
                },
                "required": ["reviews"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "deliver_report",
            "description": "Deliver report to Google Docs and Email",
            "parameters": {
                "type": "object",
                "properties": {
                    "doc_id": {"type": "string"},
                    "report_content": {"type": "string"},
                    "email_to": {"type": "string"},
                    "subject": {"type": "string"}
                },
                "required": ["doc_id", "report_content", "email_to", "subject"]
            }
        }
    }
]

def handle_tool_call(name: str, args: Dict[str, Any]):
    if name == "fetch_all_reviews":
        if "weeks_ago" in args and isinstance(args["weeks_ago"], str):
            args["weeks_ago"] = int(args["weeks_ago"])
        return fetch_all_reviews(**args)
    elif name == "cluster_and_summarize":
        return cluster_and_summarize(**args)
    elif name == "deliver_report":
        return deliver_report(**args)
    raise ValueError(f"Unknown tool: {name}")

from datetime import datetime # Late import to avoid issues
