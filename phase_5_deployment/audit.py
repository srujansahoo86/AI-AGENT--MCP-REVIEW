import sqlite3
import os
import sys
from tabulate import tabulate

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

DB_FILE = os.path.join(project_root, "phase_1_foundation", "idempotency.db")

def show_audit():
    if not os.path.exists(DB_FILE):
        print("Error: Database not found.")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT product, week, status, doc_id, message_id FROM runs ORDER BY week DESC, product ASC")
    rows = cursor.fetchall()
    conn.close()

    headers = ["Product", "ISO Week", "Status", "Doc ID", "Message ID"]
    print("\n--- Weekly Pulse Review Audit Log ---")
    if not rows:
        print("No runs found in history.")
    else:
        print(tabulate(rows, headers=headers, tablefmt="grid"))
    print(f"\nTotal runs tracked: {len(rows)}\n")

if __name__ == "__main__":
    # Ensure tabulate is installed
    try:
        from tabulate import tabulate
    except ImportError:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "tabulate"])
        from tabulate import tabulate
        
    show_audit()
