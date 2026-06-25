# core/tracker.py
import sqlite3, os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "jobs.db")

def _conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    with _conn() as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id          TEXT PRIMARY KEY,
                source      TEXT,
                title       TEXT,
                company     TEXT,
                url         TEXT,
                score       INTEGER,
                status      TEXT DEFAULT 'new',
                cover_letter TEXT,
                applied_at  TEXT,
                created_at  TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        c.commit()

def is_seen(job_id: str) -> bool:
    with _conn() as c:
        row = c.execute("SELECT 1 FROM jobs WHERE id=?", (job_id,)).fetchone()
        return row is not None

def save_job(job: dict, status="new", cover_letter=""):
    with _conn() as c:
        c.execute("""
            INSERT OR IGNORE INTO jobs (id, source, title, company, url, score, status, cover_letter)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            job["id"], job["source"], job["title"], job.get("company",""),
            job["url"], job.get("score", 0), status, cover_letter
        ))
        c.commit()

def mark_applied(job_id: str):
    with _conn() as c:
        c.execute("UPDATE jobs SET status='applied', applied_at=? WHERE id=?",
                  (datetime.utcnow().isoformat(), job_id))
        c.commit()

def get_stats() -> dict:
    with _conn() as c:
        total   = c.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
        applied = c.execute("SELECT COUNT(*) FROM jobs WHERE status='applied'").fetchone()[0]
        today   = c.execute(
            "SELECT COUNT(*) FROM jobs WHERE date(created_at)=date('now')"
        ).fetchone()[0]
    return {"total": total, "applied": applied, "today": today}

def get_all_jobs(limit=100) -> list[dict]:
    with _conn() as c:
        rows = c.execute("""
            SELECT id, source, title, company, url, score, status, applied_at, created_at
            FROM jobs ORDER BY created_at DESC LIMIT ?
        """, (limit,)).fetchall()
    cols = ["id","source","title","company","url","score","status","applied_at","created_at"]
    return [dict(zip(cols, r)) for r in rows]
