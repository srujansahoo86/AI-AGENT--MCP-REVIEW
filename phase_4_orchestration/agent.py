import os
import json
from groq import Groq
from dotenv import load_dotenv
from typing import List, Dict, Any
from tools_registry import TOOLS, handle_tool_call

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODEL = "llama-3.1-8b-instant"

SYSTEM_PROMPT = """
You are a product review agent. 
1. Call 'fetch_all_reviews' to get data.
2. Call 'cluster_and_summarize' to group them.
3. Call 'deliver_report' with a plain Markdown summary. 
RULES: No HTML. No loops.
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
        for _ in range(5): # Max 5 turns
            response = client.chat.completions.create(
                model=MODEL,
                messages=self.messages,
                tools=TOOLS,
                tool_choice="auto"
            )
            res_msg = response.choices[0].message
            self.messages.append(res_msg)
            if res_msg.tool_calls:
                for tc in res_msg.tool_calls:
                    print(f"Calling: {tc.function.name}")
                    try:
                        res = handle_tool_call(tc.function.name, json.loads(tc.function.arguments))
                        self.messages.append({"tool_call_id": tc.id, "role": "tool", "name": tc.function.name, "content": json.dumps(res)})
                    except Exception as e:
                        self.messages.append({"tool_call_id": tc.id, "role": "tool", "name": tc.function.name, "content": json.dumps({"error": str(e)})})
                continue
            print(f"Final: {res_msg.content}")
            return res_msg.content
