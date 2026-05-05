import os
import sys
from dotenv import load_dotenv

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

from phase_4_orchestration.agent import PulseAgent
from phase_4_orchestration.tools_registry import TOOLS

def verify():
    print("--- Phase 4: AI Agent Orchestration Verification ---")
    
    load_dotenv()
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("[ERROR] GROQ_API_KEY not found in environment.")
        return
    else:
        print(f"[OK] GROQ_API_KEY found (starts with {api_key[:10]}...)")
    
    print(f"[OK] {len(TOOLS)} tools registered in registry.")
    
    # Test initialization
    try:
        agent = PulseAgent(
            product_name="INDMoney",
            iso_week="2024-W19",
            doc_id="MOCK_DOC_ID",
            email_to="mock@example.com"
        )
        print("[OK] PulseAgent initialized successfully.")
    except Exception as e:
        print(f"[ERROR] Failed to initialize PulseAgent: {e}")
        return

    print("\nPhase 4 structure is valid. The system is ready for an end-to-end run.")
    print("To run the orchestrator, use: python cli.py --product INDMoney --week 2024-W19 --doc-id YOUR_DOC_ID --email YOUR_EMAIL")

if __name__ == "__main__":
    verify()
