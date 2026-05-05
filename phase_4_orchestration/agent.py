import os
import json
import httpx
import sys
from groq import Groq
from dotenv import load_dotenv
from typing import List, Dict, Any
from tools_registry import TOOLS, handle_tool_call

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    print("CRITICAL ERROR: GROQ_API_KEY is missing from environment!")
    sys.exit(1)

# Debug: Print the first 4 chars of the key to verify it's loaded (SAFE)
print(f"GROQ_API_KEY loaded: {api_key[:4]}...{api_key[-4:]}")

# Initialize Groq
client = Groq(api_key=api_key.strip()) # STRIP SPACES
MODEL = "llama-3.3-70b-versatile"

def test_connection():
    """Verifies if we can reach Groq at all."""
    print("Testing connection to api.groq.com...")
    try:
        response = httpx.get("https://api.groq.com/openai/v1/models", headers={"Authorization": f"Bearer {api_key.strip()}"})
        print(f"Connection test status: {response.status_code}")
        if response.status_code != 200:
            print(f"Connection test failed! Details: {response.text}")
    except Exception as e:
        print(f"Network is UNREACHABLE: {e}")

SYSTEM_PROMPT = """
You are the 'Weekly Product Review Pulse' AI Agent. Your goal is to generate a high-quality weekly summary of user feedback for specific fintech products and deliver it via Google Workspace.
"""

class PulseAgent:
    def __init__(self, product_name: str, iso_week: str, doc_id: str, email_to: str):
        self.product_name = product_name
        self.iso_week = iso_week
        self.doc_id = doc_id
        self.email_to = email_to
        self.messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Pulse for {product_name} ({iso_week}). Doc: {doc_id}, Email: {email_to}"}
        ]

    def run(self):
        print(f"Starting Pulse Agent for {self.product_name}...")
        test_connection() # RUN TEST
        
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=self.messages,
                tools=TOOLS,
                tool_choice="auto"
            )
            
            response_message = response.choices[0].message
            self.messages.append(response_message)
            
            if response_message.tool_calls:
                for tool_call in response_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    print(f"Agent calling tool: {function_name}...")
                    try:
                        function_response = handle_tool_call(function_name, function_args)
                        self.messages.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": json.dumps(function_response)
                        })
                    except Exception as e:
                        print(f"Error executing tool {function_name}: {e}")
                        self.messages.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": json.dumps({"error": str(e)})
                        })
                
                # After tool calls, we usually need another completion to get the final message
                response = client.chat.completions.create(
                    model=MODEL,
                    messages=self.messages
                )
                print("\nFinal Agent Message:")
                print(response.choices[0].message.content)
                return response.choices[0].message.content
            
            print("\nFinal Agent Message:")
            print(response_message.content)
            return response_message.content
        except Exception as e:
            print(f"AGENT EXECUTION ERROR: {e}")
            raise e

if __name__ == "__main__":
    agent = PulseAgent(
        product_name="Groww",
        iso_week="2026-W19",
        doc_id="test",
        email_to="test"
    )
    agent.run()
