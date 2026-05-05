import sqlite3
import os

DB_FILE = os.path.join(os.path.dirname(__file__), "idempotency.db")

def init_db():
    """Initializes the SQLite database and creates the runs table if it doesn't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create the runs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS runs (
            product TEXT,
            week TEXT,
            status TEXT,
            doc_id TEXT,
            message_id TEXT,
            PRIMARY KEY (product, week)
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_FILE}")

def get_run_status(product: str, week: str) -> str:
    """Gets the status of a specific run."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT status FROM runs WHERE product = ? AND week = ?', (product, week))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else "missing"

def update_run_status(product: str, week: str, status: str, doc_id: str = None, message_id: str = None):
    """Updates or inserts the status of a specific run."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO runs (product, week, status, doc_id, message_id)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(product, week) DO UPDATE SET
            status = excluded.status,
            doc_id = excluded.doc_id,
            message_id = excluded.message_id
    ''', (product, week, status, doc_id, message_id))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
