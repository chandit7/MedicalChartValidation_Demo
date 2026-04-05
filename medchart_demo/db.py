import sqlite3
import json
from datetime import datetime

DB_PATH = "medchart.db"

def init_db():
    """Initialize database with results table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id   TEXT NOT NULL,
            filename    TEXT NOT NULL,
            decision    TEXT NOT NULL,
            confidence  REAL NOT NULL,
            gap_score   REAL,
            disc_count  INTEGER DEFAULT 0,
            flags       TEXT,
            reasoning   TEXT,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    print("[OK] Database initialized")

def save_result(member_id, filename, decision, confidence, gap_score, disc_count, flags_list, reasoning_dict):
    """Save validation result to database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    flags_str = " | ".join([f["msg"] for f in flags_list]) if flags_list else ""
    reasoning_str = json.dumps(reasoning_dict)
    
    cursor.execute("""
        INSERT INTO results (member_id, filename, decision, confidence, gap_score, disc_count, flags, reasoning)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (member_id, filename, decision, confidence, gap_score, disc_count, flags_str, reasoning_str))
    
    conn.commit()
    conn.close()

def get_all_results():
    """Fetch all results as list of dicts."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM results ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def get_summary():
    """Get summary counts by decision type."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as total FROM results")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM results WHERE decision = 'approved'")
    approved = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM results WHERE decision = 'rejected'")
    rejected = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM results WHERE decision = 'manual_review'")
    manual_review = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "total": total,
        "approved": approved,
        "rejected": rejected,
        "manual_review": manual_review
    }

# Made with Bob
