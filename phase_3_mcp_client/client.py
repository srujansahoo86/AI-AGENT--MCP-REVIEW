import os
import requests
import logging

logger = logging.getLogger(__name__)

class GoogleMCPClient:
    """
    Client to interact with the external FastAPI "MCP" server (saksham-mcp-server).
    The external server acts as a bridge to Google Docs and Gmail APIs.
    """
    
    def __init__(self, base_url: str = None):
        """
        Initialize the client.
        :param base_url: The URL of the deployed external MCP server.
                         If not provided, it falls back to the MCP_SERVER_URL env var.
        """
        # Remove any trailing slash to prevent // double-slash errors
        self.base_url = (base_url or os.getenv("MCP_SERVER_URL", "http://127.0.0.1:8000")).rstrip("/")
        
    def append_section(self, doc_id: str, content: str) -> dict:
        """
        Appends content to a Google Doc using the external MCP server.
        """
        url = f"{self.base_url}/append_to_doc"
        payload = {
            "doc_id": doc_id,
            "content": content
        }
        
        logger.info(f"Calling append_to_doc on {url} for doc {doc_id}")
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
        
    def send_email(self, to: str, subject: str, body: str) -> dict:
        """
        Sends an email directly using the external MCP server.
        """
        url = f"{self.base_url}/send_email"
        payload = {
            "to": to,
            "subject": subject,
            "body": body
        }
        
        logger.info(f"Calling send_email on {url} for recipient {to}")
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
