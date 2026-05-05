import os
import json
from groq import Groq
from dotenv import load_dotenv
from typing import List, Dict, Any
from tools_registry import TOOLS, handle_tool_call

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

client = Groq(api_key=os.environ.get("GROQ_API_KEY").strip())
MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """
You are the 'Weekly Product Review Pulse' AI Agent. Your goal is to generate a high-quality weekly summary of user feedback for specific fintech products and deliver it via Google Workspace.

Your workflow is:
1. **Fetch Data**: Use 'fetch_all_reviews' to get reviews.
2. **Handle Empty Data**: If no reviews are returned, inform the user and STOP. Do NOT hallucinate data or proceed to clustering.
3. **Cluster & Analyze**: Use 'cluster_and_summarize' to group the raw reviews into semantic themes.
4. **Reason & Write**: Based on the clusters and sample reviews, write a professional Markdown report.
   - Use headings for top themes.
   - Include a few high-impact verbatim quotes (must be exactly from the provided samples).
   - Provide 2-3 actionable product ideas.
   - Add a 'Who this helps' section.
5. **Deliver**: Use 'deliver_report'. 

Constraint: Be concise, professional, and data-driven. Do NOT hallucinate quotes.
"""

class PulseAgent:
    def __init__(self, product_name: str, iso_week: str, doc_id: str, email_to: str):
        self.product_name = product_name
        self.iso_week = iso_week
        self.doc_id = doc_id
        self.email_to = email_to
        self.messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Generate the weekly pulse for {product_name} for ISO week {iso_week}. Deliver it to Doc ID {doc_id} and email {email_to}."}
        ]

    def run(self):
        print(f"Starting Pulse Agent for {self.product_name}...")
        
        while True:
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
    # Test run
    agent = PulseAgent(
        product_name="INDMoney",
        iso_week="latest",
        doc_id="test",
        email_to="test"
    )
    agent.run()
