import sqlite3
import pandas as pd
from datetime import datetime

DB_FILE = "data.db"


# =========================
# DATABASE INITIALIZATION
# =========================

def init_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Students Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        class TEXT,
        marks INTEGER,
        company TEXT,
        placement_package REAL
    )
    """)

    # Query History Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS QueryHistory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_prompt TEXT,
        generated_sql TEXT,
        timestamp TEXT
    )
    """)

    # Insert sample data if empty
    cursor.execute("SELECT COUNT(*) FROM Students")
    count = cursor.fetchone()[0]

    if count == 0:
        sample_data = [
            ('Sijo', 'BTech', 75, 'JSW', 5.5),
            ('Lijo', 'MTech', 69, 'TCS', 7.2),
            ('Rijo', 'BSc', 79, 'WIPRO', 6.0),
            ('Sibin', 'MSc', 89, 'INFOSYS', 8.1),
            ('Dilsha', 'MCom', 99, 'Cyient', 10.5),
            ('Arjun', 'BTech', 91, 'Google', 22.0),
            ('Kiran', 'MBA', 85, 'Amazon', 18.0),
            ('Meera', 'BCA', 72, 'Accenture', 4.5),
            ('Rahul', 'MCA', 95, 'Microsoft', 25.0),
            ('Sneha', 'BTech', 88, 'Adobe', 19.0)
        ]

        cursor.executemany("""
        INSERT INTO Students
        (name, class, marks, company, placement_package)
        VALUES (?, ?, ?, ?, ?)
        """, sample_data)

    conn.commit()
    conn.close()


# =========================
# SAFE SQL EXECUTION
# =========================

DANGEROUS_KEYWORDS = [
    "drop",
    "delete",
    "truncate",
    "alter",
    "update"
]


def is_safe_query(query):
    query_lower = query.lower()

    for keyword in DANGEROUS_KEYWORDS:
        if keyword in query_lower:
            return False

    return True


def execute_sql(query):
    if not is_safe_query(query):
        return None, None, "❌ Unsafe query blocked!"

    conn = sqlite3.connect(DB_FILE)

    try:
        df = pd.read_sql_query(query, conn)

        return df, list(df.columns), None

    except Exception as e:
        return None, None, f"❌ SQL Error: {e}"

    finally:
        conn.close()


# =========================
# QUERY HISTORY
# =========================

def save_query_history(user_prompt, generated_sql):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO QueryHistory
    (user_prompt, generated_sql, timestamp)
    VALUES (?, ?, ?)
    """, (
        user_prompt,
        generated_sql,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()


def get_query_history():
    conn = sqlite3.connect(DB_FILE)

    df = pd.read_sql_query("""
    SELECT * FROM QueryHistory
    ORDER BY id DESC
    """, conn)

    conn.close()

    return df


# =========================
# DATABASE SCHEMA
# =========================

def get_schema():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT name FROM sqlite_master
    WHERE type='table'
    """)

    tables = cursor.fetchall()

    schema = ""

    for table in tables:
        table_name = table[0]

        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()

        schema += f"\nTable: {table_name}\n"

        for col in columns:
            schema += f"- {col[1]} ({col[2]})\n"

    conn.close()

    return schema


# =========================
# ANALYTICS FUNCTIONS
# =========================

def get_student_metrics():
    conn = sqlite3.connect(DB_FILE)

    total_students = pd.read_sql_query(
        "SELECT COUNT(*) as count FROM Students",
        conn
    ).iloc[0]["count"]

    avg_marks = pd.read_sql_query(
        "SELECT AVG(marks) as avg_marks FROM Students",
        conn
    ).iloc[0]["avg_marks"]

    highest_package = pd.read_sql_query(
        "SELECT MAX(placement_package) as max_package FROM Students",
        conn
    ).iloc[0]["max_package"]

    total_companies = pd.read_sql_query(
        "SELECT COUNT(DISTINCT company) as companies FROM Students",
        conn
    ).iloc[0]["companies"]

    conn.close()

    return {
        "total_students": total_students,
        "avg_marks": round(avg_marks, 2),
        "highest_package": highest_package,
        "total_companies": total_companies
    }


# =========================
# AUTO INITIALIZE DATABASE
# =========================

if __name__ == "__main__":
    init_database()
    print("✅ Database initialized successfully.")
