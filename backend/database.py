import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "tickets.db"


def get_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT NOT NULL,
            subsystem TEXT NOT NULL,
            priority TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    columns = {
        row["name"]
        for row in conn.execute("PRAGMA table_info(tickets)").fetchall()
    }
    if "issue_type" in columns:
        conn.execute("ALTER TABLE tickets RENAME TO tickets_legacy")
        conn.execute("""
            CREATE TABLE tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                subsystem TEXT NOT NULL,
                priority TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            INSERT INTO tickets (id, query, subsystem, priority, status, created_at)
            SELECT id, query, subsystem, priority, status, created_at
            FROM tickets_legacy
        """)
        conn.execute("DROP TABLE tickets_legacy")

    conn.commit()
    conn.close()


def create_ticket(query, subsystem, priority):
    conn = get_connection()

    cursor = conn.execute("""
        INSERT INTO tickets
        (query, subsystem, priority)
        VALUES (?, ?, ?)
    """, (query, subsystem, priority))

    ticket_id = cursor.lastrowid

    conn.commit()

    ticket = conn.execute(
        "SELECT * FROM tickets WHERE id = ?",
        (ticket_id,)
    ).fetchone()

    conn.close()

    return dict(ticket)


def get_all_tickets():
    conn = get_connection()

    rows = conn.execute("""
        SELECT *
        FROM tickets
        ORDER BY created_at DESC, id DESC
    """).fetchall()

    conn.close()

    return [dict(row) for row in rows]


def update_ticket_status(ticket_id, status):
    conn = get_connection()

    cursor = conn.execute("""
        UPDATE tickets
        SET status = ?
        WHERE id = ?
    """, (status, ticket_id))

    conn.commit()
    conn.close()

    return cursor.rowcount > 0