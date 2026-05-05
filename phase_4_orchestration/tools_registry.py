import sys
import os
import json
from typing import List, Dict, Any
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# Add the project root and relevant phase directories to sys.path to allow imports
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

def fetch_all_reviews(apple_app_id: str, google_play_id: str, weeks_ago: int = 52) -> List[Dict[str, Any]]:
    """
    Fetches reviews from both Apple App Store and Google Play Store for a given time window.
    Returns a combined list of review dictionaries.
    """
    # Hardcode for final verification run
    weeks_ago = 52
    print(f"Fetching reviews for Apple: {apple_app_id}, Google: {google_play_id} (FORCED weeks_ago={weeks_ago})...")
    apple_reviews = app_store.fetch_reviews(apple_app_id, weeks_ago=weeks_ago)
    google_reviews = play_store.fetch_reviews(google_play_id, weeks_ago=weeks_ago)
    
    combined = []
    for r in apple_reviews + google_reviews:
        # Convert Pydantic model to dict and handle datetime serialization
        data = r.model_dump()
        data['date'] = data['date'].isoformat()
        combined.append(data)
    
    if len(combined) > 5:
        print(f"Limiting agent context to 5 reviews (out of {len(combined)}) for final token economy.")
        combined = combined[:5]
        
    print(f"Returning {len(combined)} reviews to agent.")
    return combined

def cluster_and_summarize(reviews: List[Dict[str, Any]]) -> str:
    """
    Groups reviews into semantic clusters and returns a textual representation of the clusters
    to be consumed by the LLM.
    """
    if not reviews:
        return "No reviews found for the specified period."
        
    texts = [r.get('review_text', '') for r in reviews if r.get('review_text')]
    if not texts:
        return "No review text content found to cluster."
        
    clusters = clusterer.cluster_reviews(texts)
    
    summary = []
    for cid, docs in clusters.items():
        summary.append(f"Cluster {cid} ({len(docs)} reviews):")
        # Include first 5 reviews as samples to avoid context blowup
        for doc in docs[:5]:
            summary.append(f"  - {doc[:200]}...")
        summary.append("")
        
    return "\n".join(summary)

def deliver_report(doc_id: str, report_content: str, email_to: str, subject: str) -> Dict[str, Any]:
    """
    Appends the report to Google Docs and sends an email draft via the MCP Client.
    """
    print("Delivering report to Google Docs...")
    doc_res = mcp_client.append_section(doc_id, report_content)
    
    print(f"Creating email draft for {email_to}...")
    email_res = mcp_client.send_email(email_to, subject, report_content[:500] + "...") # Send preview in email
    
    return {
        "doc_response": doc_res,
        "email_response": email_res
    }

# Tool definitions for Groq
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "fetch_all_reviews",
            "description": "Fetch reviews from Apple App Store and Google Play Store.",
            "parameters": {
                "type": "object",
                "properties": {
                    "apple_app_id": {"type": "string", "description": "The Apple App Store ID (e.g., '1464306334')"},
                    "google_play_id": {"type": "string", "description": "The Google Play Store Package Name (e.g., 'com.investindmoney')"},
                    "weeks_ago": {"type": "string", "description": "How many weeks of history to fetch (integer as a string, e.g. '8')"}
                },
                "required": ["apple_app_id", "google_play_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cluster_and_summarize",
            "description": "Group a list of reviews into semantic themes/clusters.",
            "parameters": {
                "type": "object",
                "properties": {
                    "reviews": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "List of review objects as returned by fetch_all_reviews."
                    }
                },
                "required": ["reviews"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "deliver_report",
            "description": "Final step: Delivery of the pulse report via Google Docs and Gmail.",
            "parameters": {
                "type": "object",
                "properties": {
                    "doc_id": {"type": "string", "description": "The target Google Doc ID."},
                    "report_content": {"type": "string", "description": "The full Markdown report generated by the LLM."},
                    "email_to": {"type": "string", "description": "Recipient email address."},
                    "subject": {"type": "string", "description": "Email subject line."}
                },
                "required": ["doc_id", "report_content", "email_to", "subject"]
            }
        }
    }
]

def handle_tool_call(name: str, args: Dict[str, Any]):
    """Dispatches a tool call to the correct implementation."""
    if name == "fetch_all_reviews":
        # Cast weeks_ago to int as schema now expects string for LLM robustness
        if "weeks_ago" in args:
            args["weeks_ago"] = int(str(args["weeks_ago"]))
        return fetch_all_reviews(**args)
    elif name == "cluster_and_summarize":
        return cluster_and_summarize(**args)
    elif name == "deliver_report":
        return deliver_report(**args)
    else:
        raise ValueError(f"Unknown tool: {name}")
