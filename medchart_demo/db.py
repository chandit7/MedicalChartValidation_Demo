import sqlite3
import json
from datetime import datetime
import pandas as pd

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

def get_results_for_analysis(days=30):
    """Get recent results for trend analysis."""
    conn = sqlite3.connect(DB_PATH)
    query = f"""
        SELECT * FROM results 
        WHERE created_at >= datetime('now', '-{days} days')
        ORDER BY created_at DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_historical_baseline(days=90):
    """Get historical metrics for comparison."""
    conn = sqlite3.connect(DB_PATH)
    query = f"""
        SELECT 
            DATE(created_at) as date,
            decision,
            COUNT(*) as count,
            AVG(confidence) as avg_confidence,
            AVG(gap_score) as avg_gap_score
        FROM results
        WHERE created_at >= datetime('now', '-{days} days')
        GROUP BY DATE(created_at), decision
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_daily_summary():
    """Get summary for last 24 hours."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN decision = 'approved' THEN 1 ELSE 0 END) as approved,
            SUM(CASE WHEN decision = 'rejected' THEN 1 ELSE 0 END) as rejected,
            SUM(CASE WHEN decision = 'manual_review' THEN 1 ELSE 0 END) as manual_review
        FROM results
        WHERE created_at >= datetime('now', '-1 day')
    """)
    
    row = cursor.fetchone()
    conn.close()
    
    return {
        'total': row[0],
        'approved': row[1],
        'rejected': row[2],
        'manual_review': row[3]
    }

def get_30day_average():
    """Get 30-day average metrics."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            COUNT(*) / 30.0 as avg_total,
            SUM(CASE WHEN decision = 'approved' THEN 1 ELSE 0 END) / 30.0 as avg_approved,
            SUM(CASE WHEN decision = 'rejected' THEN 1 ELSE 0 END) / 30.0 as avg_rejected,
            SUM(CASE WHEN decision = 'manual_review' THEN 1 ELSE 0 END) / 30.0 as avg_manual_review
        FROM results
        WHERE created_at >= datetime('now', '-30 days')
    """)
    
    row = cursor.fetchone()
    conn.close()
    
    return {
        'avg_total': row[0] or 0,
        'avg_approved': row[1] or 0,
        'avg_rejected': row[2] or 0,
        'avg_manual_review': row[3] or 0
    }
