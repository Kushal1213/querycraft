import streamlit as st
import os
import sqlite3
import google.generativeai as genai
from dotenv import load_dotenv

# Load API key FIRST
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    st.error("Google API Key not found!")
    st.stop()

genai.configure(api_key=GOOGLE_API_KEY)

try:
    model = genai.GenerativeModel("gemini-1.5-flash")
except Exception as e:
    st.error(f"Gemini Model Error: {e}")
    st.stop()

# Auto-create database if it doesn't exist
if not os.path.exists("data.db"):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS Students (
        name VARCHAR(30), class VARCHAR(10), marks INT, company VARCHAR(30))""")
    cursor.executemany("INSERT INTO Students VALUES (?,?,?,?)", [
        ('Sijo','BTech',75,'JSW'), ('Lijo','MTech',69,'TCS'),
        ('Rijo','BSc',79,'WIPRO'), ('Sibin','MSc',89,'INFOSYS'),
        ('Dilsha','MCom',99,'Cyient')
    ])
    conn.commit()
    conn.close()

# SQLite DB file
DB_FILE = "data.db"

def get_sql_from_prompt(user_input):
    prompt = f"""
    You are an expert in SQL. Convert the user's English instruction into a correct SQLite SQL statement.
    The response must contain only the SQL code without any extra comments, markdown, or explanation.

    Examples:
    Q: Show all students.
    A: SELECT * FROM STUDENTS;

    Q: Create a table named EMPLOYEE with name, age and salary.
    A: CREATE TABLE EMPLOYEE (Name TEXT, Age INTEGER, Salary REAL);

    Now convert this:
    Q: {user_input}
    A:
    """
    response = model.generate_content(prompt)
    return response.text.strip().strip("```sql").strip("```").strip()

def execute_sql(query, db_file=DB_FILE):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.commit()
        if query.strip().lower().startswith("select"):
            col_names = [description[0] for description in cursor.description]
            return rows, col_names, None
        return None, None, "Executed successfully!"
    except Exception as e:
        return None, None, f"❌ Error: {e}"
    finally:
        conn.close()

def main():
    st.set_page_config(page_title="QueryCraft", layout="wide")
    st.sidebar.title("Navigation")
    pages = ["Home", "About", "Query Assistant"]
    selection = st.sidebar.radio("Go to", pages)

    if selection == "Home":
        st.markdown("<h1 style='color:#4CAF50;'>Welcome to QueryCraft!</h1>", unsafe_allow_html=True)
        st.markdown("""
        <div style='padding:20px;'>
            <h3 style='color:#4CAF50;'>Query your database using natural language</h3>
            <p style='color:#ffffff;'>Powered by Google's Gemini AI and Streamlit.</p>
        </div>""", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div style='padding:15px; border-left:4px solid #4CAF50;'>
                <h4 style='color:#4CAF50;'>✨ Key Features</h4>
                <ul style='color:#ffffff;'>
                    <li>Natural language to SQL conversion</li>
                    <li>Real-time query execution</li>
                    <li>Visual results display</li>
                    <li>SQLite database support</li>
                </ul>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div style='padding:15px; border-left:4px solid #4CAF50;'>
                <h4 style='color:#4CAF50;'>🚀 Getting Started</h4>
                <ol style='color:#ffffff;'>
                    <li>Navigate to Query Assistant</li>
                    <li>Type your request in plain English</li>
                    <li>View the generated SQL</li>
                    <li>See results instantly</li>
                </ol>
            </div>""", unsafe_allow_html=True)

    elif selection == "About":
        st.markdown("<h1 style='color:#4CAF50;'>About QueryCraft</h1>", unsafe_allow_html=True)
        st.markdown("""
        <div style='padding:20px;'>
            <h3 style='color:#4CAF50;'>Smart Database Interaction</h3>
            <p style='color:#ffffff;'>QueryCraft bridges the gap between natural language and database queries.</p>
        </div>""", unsafe_allow_html=True)
        st.markdown("""
        <h3 style='color:#4CAF50;'>🛠️ Technology Stack</h3>
        <div style='display:flex; justify-content:space-between; flex-wrap:wrap;'>
            <div style='width:30%; padding:10px;'><h4 style='color:#4CAF50;'>Google Gemini</h4><p style='color:#ffffff;'>AI for natural language understanding</p></div>
            <div style='width:30%; padding:10px;'><h4 style='color:#4CAF50;'>SQLite</h4><p style='color:#ffffff;'>Lightweight local database engine</p></div>
            <div style='width:30%; padding:10px;'><h4 style='color:#4CAF50;'>Streamlit</h4><p style='color:#ffffff;'>Interactive web app framework</p></div>
        </div>""", unsafe_allow_html=True)

    elif selection == "Query Assistant":
        st.markdown("<h1 style='color:#4CAF50;'>Intelligent Query Assistant</h1>", unsafe_allow_html=True)
        user_input = st.text_input("🔍 Enter your instruction (e.g., 'Show all students')")
        if st.button("Get Answer"):
            with st.spinner("Generating SQL..."):
                sql_query = get_sql_from_prompt(user_input)
                st.code(sql_query, language="sql")
                result, cols, msg = execute_sql(sql_query)
                if result is not None and cols is not None:
                    st.subheader("📊 Query Result:")
                    st.table([dict(zip(cols, row)) for row in result])
                elif msg:
                    if "error" in msg.lower():
                        st.error(str(msg))
                    else:
                        st.success(str(msg))

if __name__ == "__main__":
    main()
