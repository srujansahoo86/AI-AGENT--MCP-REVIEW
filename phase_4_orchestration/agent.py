import os
import json
import httpx
from groq import Groq
from dotenv import load_dotenv
from typing import List, Dict, Any
from tools_registry import TOOLS, handle_tool_call

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY").strip(),
    timeout=60.0
)
MODEL = "llama-3.1-8b-instant"

SYSTEM_PROMPT = """
You are the 'Weekly Product Review Pulse' AI Agent.
PRODUCT DATA:
- Groww: Apple ID '1404115983', Google ID 'com.nextbillion.groww'
- INDMoney: Apple ID '1459334316', Google ID 'com.indwealth'

WORKFLOW:
1. Fetch reviews using 'fetch_all_reviews' with the IDs above. Use weeks_ago=8.
2. Cluster and summarize using 'cluster_and_summarize'.
3. Deliver the Markdown report using 'deliver_report'.

RULES:
- NO MATH in arguments. Use only simple integers.
- NO HALLUCINATING IDs. Use the data provided above.
- NO HTML. Use ONLY plain Markdown.
"""

class PulseAgent:
    def __init__(self, product_name: str, iso_week: str, doc_id: str, email_to: str):
        self.product_name = product_name
        self.iso_week = iso_week
        self.doc_id = doc_id
        self.email_to = email_to
        self.messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Generate the weekly pulse for {product_name} ({iso_week}). Doc: {doc_id}, Email: {email_to}"}
        ]

    def run(self):
        print(f"Starting Pulse Agent for {self.product_name}...")
        
        for _ in range(5): # Max 5 turns
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
                continue
            
            print("\nFinal Agent Message:")
            print(response_message.content)
            return response_message.content

if __name__ == "__main__":
    agent = PulseAgent(product_name="Groww", iso_week="latest", doc_id="test", email_to="test")
    agent.run()
