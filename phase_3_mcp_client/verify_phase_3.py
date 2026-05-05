import logging
import os
from client import GoogleMCPClient
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify():
    logger.info("Starting Phase 3 Verification")
    
    # Use environment variable for the render URL, or fallback to local
    base_url = os.getenv("MCP_SERVER_URL", "http://127.0.0.1:8000")
    client = GoogleMCPClient(base_url=base_url)
    
    logger.info(f"Targeting external MCP Server at: {client.base_url}")
    
    # Test 1: Check if the server is accessible (FastAPI root endpoint)
    try:
        response = requests.get(f"{client.base_url}/")
        response.raise_for_status()
        logger.info(f"✅ Server Connection Successful: {response.json()}")
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Failed to connect to server: {e}")
        logger.error("Please ensure the external server is running and MCP_SERVER_URL is correct.")
        return

    # We won't actually call append_to_doc or create_email_draft here unless the user wants us to 
    # mutate real data. But we know the connection is established.
    logger.info("Verification complete. The MCP Client is ready to be integrated into Phase 4.")

if __name__ == "__main__":
    verify()
