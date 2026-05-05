import argparse
import sys
import os
import logging
from datetime import datetime
from typing import Optional

# Setup logging
log_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, "pulse.log")),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("PulseCLI")

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

from phase_1_foundation.database import get_run_status, update_run_status, init_db
from phase_4_orchestration.agent import PulseAgent

def main():
    parser = argparse.ArgumentParser(description="Weekly Product Review Pulse CLI")
    parser.add_argument("--product", required=True, help="Product name (e.g., INDMoney, Groww, Kuvera)")
    parser.add_argument("--week", required=True, help="ISO Week (e.g., 2024-W19)")
    parser.add_argument("--doc-id", required=True, help="Target Google Doc ID")
    parser.add_argument("--email", required=True, help="Recipient email address")
    parser.add_argument("--force", action="store_true", help="Force run even if already completed")
    
    args = parser.parse_args()
    
    # Initialize DB if not exists
    init_db()
    
    # Idempotency check
    status = get_run_status(args.product, args.week)
    if status == "completed" and not args.force:
        logger.info(f"Skipping: Review for {args.product} in week {args.week} is already completed.")
        return

    logger.info(f"Processing Pulse for {args.product} | Week: {args.week}")
    update_run_status(args.product, args.week, "pending")
    
    try:
        agent = PulseAgent(
            product_name=args.product,
            iso_week=args.week,
            doc_id=args.doc_id,
            email_to=args.email
        )
        agent.run()
        
        # In a real scenario, we'd extract doc_id and message_id from the agent's delivery response
        # For now, we'll mark as completed
        update_run_status(args.product, args.week, "completed", doc_id=args.doc_id)
        logger.info(f"SUCCESS: Pulse generated and delivered for {args.product} ({args.week}).")
        
    except Exception as e:
        logger.error(f"FAILURE: Error during agent execution: {e}", exc_info=True)
        update_run_status(args.product, args.week, "failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
