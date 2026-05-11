import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import os
import time

import google.generativeai as genai

from dotenv import load_dotenv

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="QueryCraft AI",
    page_icon="🚀",
    layout="wide"
)

# =========================
# CUSTOM CSS
# =========================

st.markdown("""
<style>

.stApp {
    background-color: #0f172a;
    color: white;
}

h1, h2, h3 {
    color: #38bdf8;
}

[data-testid="stMetricValue"] {
    color: white;
}

</style>
""", unsafe_allow_html=True)

# =========================
# LOAD ENV
# =========================

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    st.error("❌ GOOGLE_API_KEY not found.")
    st.stop()

# =========================
# GEMINI CONFIG
# =========================

try:
    genai.configure(api_key=GOOGLE_API_KEY)

    # Updated working model
    model = genai.GenerativeModel("gemini-2.0-flash")

except Exception as e:
    st.error(f"Gemini setup error: {e}")
    st.stop()

# =========================
# DATABASE SETUP
# =========================

DB_FILE = "data.db"

# Delete old incompatible database automatically
if os.path.exists(DB_FILE):

    try:
        conn_test = sqlite3.connect(DB_FILE)
        cursor_test = conn_test.cursor()

        cursor_test.execute("PRAGMA table_info(Students)")
        columns = cursor_test.fetchall()

        column_names = [col[1] for col in columns]

        conn_test.close()

        # If old schema exists -> recreate database
        if "package" not in column_names:

            os.remove(DB_FILE)

    except:
        os.remove(DB_FILE)

# Create fresh connection
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Create Students table
cursor.execute("""
CREATE TABLE IF NOT EXISTS Students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    class TEXT,
    marks INTEGER,
    company TEXT,
    package REAL
)
""")

# Insert sample data only if table empty
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
        ('Rahul', 'MCA', 95, 'Microsoft', 25.0),
        ('Sneha', 'BTech', 88, 'Adobe', 19.0),
        ('Kiran', 'MBA', 84, 'Amazon', 18.5),
        ('Neha', 'MCA', 92, 'Meta', 30.0)
    ]

    cursor.executemany("""
    INSERT INTO Students
    (name, class, marks, company, package)
    VALUES (?, ?, ?, ?, ?)
    """, sample_data)

conn.commit()
# =========================
# AI SQL GENERATION
# =========================

def generate_sql(user_prompt):

    schema = """
    TABLE: Students

    columns:
    id, name, class, marks, company, package
    """

    prompt = f"""
    You are an SQLite expert.

    Convert English into SQL.

    RULES:
    - Return ONLY SQL
    - ONLY SELECT queries
    - No markdown
    - No explanation

    DATABASE:
    {schema}

    USER:
    {user_prompt}
    """

    response = model.generate_content(prompt)

    sql_query = response.text.strip()

    sql_query = sql_query.replace("```sql", "")
    sql_query = sql_query.replace("```", "")

    return sql_query.strip()

# =========================
# SAFE SQL EXECUTION
# =========================

BLOCKED = [
    "drop",
    "delete",
    "truncate",
    "alter",
    "update"
]

def execute_query(query):

    query_lower = query.lower()

    for word in BLOCKED:
        if word in query_lower:
            return None, "Unsafe query blocked."

    try:

        df = pd.read_sql_query(query, conn)

        return df, None

    except Exception as e:
        return None, str(e)

# =========================
# SIDEBAR
# =========================

st.sidebar.title("🚀 QueryCraft AI")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "AI SQL Assistant",
        "Analytics"
    ]
)

# =========================
# DASHBOARD
# =========================

if page == "Dashboard":

    st.title("🚀 QueryCraft Dashboard")

    total_students = pd.read_sql_query(
        "SELECT COUNT(*) as total FROM Students",
        conn
    ).iloc[0]["total"]

    avg_marks = pd.read_sql_query(
        "SELECT AVG(marks) as avg FROM Students",
        conn
    ).iloc[0]["avg"]

    highest_package = pd.read_sql_query(
        "SELECT MAX(package) as highest FROM Students",
        conn
    ).iloc[0]["highest"]

    companies = pd.read_sql_query(
        "SELECT COUNT(DISTINCT company) as total FROM Students",
        conn
    ).iloc[0]["total"]

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Students", total_students)
    c2.metric("Average Marks", round(avg_marks, 2))
    c3.metric("Highest Package", f"{highest_package} LPA")
    c4.metric("Companies", companies)

    st.markdown("---")

    chart_df = pd.read_sql_query("""
    SELECT company, COUNT(*) as total
    FROM Students
    GROUP BY company
    """, conn)

    fig = px.bar(
        chart_df,
        x="company",
        y="total",
        title="Company Distribution"
    )

    st.plotly_chart(fig, use_container_width=True)

# =========================
# AI ASSISTANT
# =========================

elif page == "AI SQL Assistant":

    st.title("🤖 AI SQL Assistant")

    user_prompt = st.text_area(
        "Enter your query",
        placeholder="Example: Show top students by marks"
    )

    if st.button("Generate SQL"):

        if user_prompt.strip() == "":
            st.warning("Please enter a prompt.")

        else:

            with st.spinner("Generating SQL..."):

                try:

                    start = time.time()

                    sql_query = generate_sql(user_prompt)

                    execution_time = round(time.time() - start, 2)

                    st.subheader("Generated SQL")

                    st.code(sql_query, language="sql")

                    df, error = execute_query(sql_query)

                    if error:
                        st.error(error)

                    else:

                        st.success(
                            f"Query executed successfully in {execution_time} sec"
                        )

                        st.dataframe(
                            df,
                            use_container_width=True
                        )

                        if len(df.columns) >= 2:

                            numeric_cols = df.select_dtypes(
                                include='number'
                            ).columns

                            if len(numeric_cols) > 0:

                                fig = px.bar(
                                    df,
                                    x=df.columns[0],
                                    y=numeric_cols[0]
                                )

                                st.plotly_chart(
                                    fig,
                                    use_container_width=True
                                )

                except Exception as e:
                    st.error(f"Error: {e}")

# =========================
# ANALYTICS
# =========================

elif page == "Analytics":

    st.title("📊 Analytics")

    marks_df = pd.read_sql_query("""
    SELECT class, AVG(marks) as avg_marks
    FROM Students
    GROUP BY class
    """, conn)

    fig = px.pie(
        marks_df,
        names="class",
        values="avg_marks",
        title="Average Marks by Class"
    )

    st.plotly_chart(fig, use_container_width=True)

# =========================
# CLOSE CONNECTION
# =========================

conn.close()
