import sqlite3
import pandas as pd
from datetime import datetime

# =========================
# DATABASE CONFIG
# =========================

DB_FILE = "data.db"

# Dangerous SQL keywords
BLOCKED_KEYWORDS = [
    "drop",
    "delete",
    "truncate",
    "alter",
    "update",
    "replace",
    "grant",
    "revoke"
]


# =========================
# DATABASE INITIALIZATION
# =========================

def init_database():
    """
    Initialize database and create tables.
    """

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # =========================
    # STUDENTS TABLE
    # =========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        class TEXT NOT NULL,
        marks INTEGER NOT NULL,
        company TEXT,
        placement_package REAL,
        city TEXT
    )
    """)

    # =========================
    # QUERY HISTORY TABLE
    # =========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS QueryHistory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_prompt TEXT,
        generated_sql TEXT,
        execution_time REAL,
        created_at TEXT
    )
    """)

    # =========================
    # CHECK EXISTING DATA
    # =========================

    cursor.execute("SELECT COUNT(*) FROM Students")
    count = cursor.fetchone()[0]

    # =========================
    # INSERT SAMPLE DATA
    # =========================

    if count == 0:

        students_data = [
            ('Sijo', 'BTech', 75, 'JSW', 5.5, 'Bangalore'),
            ('Lijo', 'MTech', 69, 'TCS', 7.2, 'Chennai'),
            ('Rijo', 'BSc', 79, 'WIPRO', 6.0, 'Hyderabad'),
            ('Sibin', 'MSc', 89, 'INFOSYS', 8.1, 'Pune'),
            ('Dilsha', 'MCom', 99, 'Cyient', 10.5, 'Delhi'),
            ('Arjun', 'BTech', 91, 'Google', 22.0, 'Bangalore'),
            ('Kiran', 'MBA', 85, 'Amazon', 18.0, 'Mumbai'),
            ('Meera', 'BCA', 72, 'Accenture', 4.5, 'Noida'),
            ('Rahul', 'MCA', 95, 'Microsoft', 25.0, 'Hyderabad'),
            ('Sneha', 'BTech', 88, 'Adobe', 19.0, 'Gurgaon'),
            ('Ananya', 'MBA', 92, 'Deloitte', 12.0, 'Mumbai'),
            ('Vikram', 'BSc', 67, 'Capgemini', 4.2, 'Chennai'),
            ('Priya', 'MTech', 94, 'Oracle', 20.0, 'Bangalore'),
            ('Rohan', 'BCA', 81, 'IBM', 9.0, 'Pune'),
            ('Neha', 'MCA', 90, 'Meta', 30.0, 'Hyderabad')
        ]

        cursor.executemany("""
        INSERT INTO Students
        (name, class, marks, company, placement_package, city)
        VALUES (?, ?, ?, ?, ?, ?)
        """, students_data)

    conn.commit()
    conn.close()


# =========================
# SAFE QUERY VALIDATION
# =========================

def is_safe_query(query):
    """
    Prevent dangerous SQL execution.
    """

    query_lower = query.lower()

    for keyword in BLOCKED_KEYWORDS:
        if keyword in query_lower:
            return False

    return True


# =========================
# EXECUTE SQL
# =========================

def execute_sql(query):
    """
    Execute SQL query safely.
    """

    if not query.strip():
        return None, None, "⚠️ Empty query."

    if not is_safe_query(query):
        return None, None, "❌ Unsafe query blocked."

    conn = sqlite3.connect(DB_FILE)

    try:
        df = pd.read_sql_query(query, conn)

        return df, list(df.columns), None

    except Exception as e:
        return None, None, f"❌ SQL Error: {str(e)}"

    finally:
        conn.close()


# =========================
# QUERY HISTORY
# =========================

def save_query_history(user_prompt, generated_sql, execution_time):
    """
    Save query history.
    """

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO QueryHistory
    (user_prompt, generated_sql, execution_time, created_at)
    VALUES (?, ?, ?, ?)
    """, (
        user_prompt,
        generated_sql,
        execution_time,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()


def get_query_history():
    """
    Fetch query history.
    """

    conn = sqlite3.connect(DB_FILE)

    df = pd.read_sql_query("""
    SELECT *
    FROM QueryHistory
    ORDER BY id DESC
    """, conn)

    conn.close()

    return df


# =========================
# DATABASE SCHEMA
# =========================

def get_schema():
    """
    Get database schema dynamically.
    """

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type='table'
    """)

    tables = cursor.fetchall()

    schema = ""

    for table in tables:

        table_name = table[0]

        cursor.execute(f"PRAGMA table_info({table_name})")

        columns = cursor.fetchall()

        schema += f"\n📌 TABLE: {table_name}\n"

        for col in columns:
            schema += f"   • {col[1]} ({col[2]})\n"

    conn.close()

    return schema


# =========================
# ANALYTICS HELPERS
# =========================

def get_dashboard_metrics():

    conn = sqlite3.connect(DB_FILE)

    total_students = pd.read_sql_query(
        "SELECT COUNT(*) AS total FROM Students",
        conn
    ).iloc[0]["total"]

    average_marks = pd.read_sql_query(
        "SELECT AVG(marks) AS avg_marks FROM Students",
        conn
    ).iloc[0]["avg_marks"]

    highest_package = pd.read_sql_query(
        "SELECT MAX(placement_package) AS max_package FROM Students",
        conn
    ).iloc[0]["max_package"]

    total_companies = pd.read_sql_query(
        "SELECT COUNT(DISTINCT company) AS companies FROM Students",
        conn
    ).iloc[0]["companies"]

    conn.close()

    return {
        "total_students": total_students,
        "average_marks": round(average_marks, 2),
        "highest_package": highest_package,
        "total_companies": total_companies
    }


# =========================
# CHART DATA
# =========================

def get_company_distribution():

    conn = sqlite3.connect(DB_FILE)

    df = pd.read_sql_query("""
    SELECT company, COUNT(*) AS total_students
    FROM Students
    GROUP BY company
    ORDER BY total_students DESC
    """, conn)

    conn.close()

    return df


def get_class_performance():

    conn = sqlite3.connect(DB_FILE)

    df = pd.read_sql_query("""
    SELECT class, AVG(marks) AS average_marks
    FROM Students
    GROUP BY class
    ORDER BY average_marks DESC
    """, conn)

    conn.close()

    return df


# =========================
# SEARCH SUGGESTIONS
# =========================

def get_sample_prompts():

    return [
        "Show all students",
        "Top 5 students by marks",
        "Average marks by class",
        "Students placed in Google",
        "Highest placement package",
        "Students from Bangalore",
        "Company-wise student count",
        "Students scoring above 90",
        "Average package by company",
        "Top companies hiring students"
    ]


# =========================
# RESET DATABASE
# =========================

def reset_database():

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS Students")
    cursor.execute("DROP TABLE IF EXISTS QueryHistory")

    conn.commit()
    conn.close()

    init_database()


# =========================
# MAIN
# =========================

if __name__ == "__main__":

    init_database()

    print("✅ QueryCraft Database Initialized Successfully")
