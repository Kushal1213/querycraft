import streamlit as st
import os
import sqlite3
import google.generativeai as genai
from dotenv import load_dotenv

# Load API key
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize Gemini model
model = genai.GenerativeModel("gemini-2.0-flash")

# SQLite DB file
DB_FILE = "data.db"

# Get Gemini response for SQL generation
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

# Execute SQL and return result
def execute_sql(query, db_file=DB_FILE):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.commit()
        # If query is SELECT or SHOW-like
        if query.strip().lower().startswith("select"):
            col_names = [description[0] for description in cursor.description]
            return rows, col_names, None
        return None, None, "Executed successfully!"
    except Exception as e:
        return None, None, f"❌ Error: {e}"
    finally:
        conn.close()


# Streamlit UI
def main():
    st.set_page_config(page_title="IntelliSQL", layout="wide")
    st.sidebar.title("Navigation")
    pages = ["Home", "About", "Query Assistant"]
    selection = st.sidebar.radio("Go to", pages)

    if selection == "Home":
        st.markdown("<h1 style='color:#4CAF50;'>Welcome to IntelliSQL!</h1>", unsafe_allow_html=True)
        st.markdown("""
        <div style='padding:20px;'>
            <h3 style='color:#4CAF50;'>Query your database using natural language</h3>
            <p style='color:#ffffff;'>Powered by Google's Gemini AI and Streamlit, IntelliSQL makes database interaction as easy as having a conversation.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div style='padding:15px; border-left:4px solid #4CAF50;'>
                <h4 style='color:#4CAF50;'>✨ Key Features</h4>
                <ul style='color:#ffffff;'>
                    <li>Natural language to SQL conversion</li>
                    <li>Real-time query execution</li>
                    <li>Visual results display</li>
                    <li>Local SQLite database support</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style='padding:15px; border-left:4px solid #4CAF50;'>
                <h4 style='color:#4CAF50;'>🚀 Getting Started</h4>
                <ol style='color:#ffffff;'>
                    <li>Navigate to Query Assistant</li>
                    <li>Type your request in plain English</li>
                    <li>View and execute the generated SQL</li>
                    <li>See results instantly</li>
                </ol>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("""
        <div style='text-align:center; padding:10px;'>
            <p style='color:#ffffff;'>Try asking things like:</p>
            <p style='color:#ffffff;'><i>"Show all customers from New York"</i> or <i>"Create a products table with name, price and category"</i></p>
        </div>
        """, unsafe_allow_html=True)

    elif selection == "About":
        st.markdown("<h1 style='color:#4CAF50;'>About IntelliSQL</h1>", unsafe_allow_html=True)
        
        st.markdown("""
        <div style='padding:20px;'>
            <h3 style='color:#4CAF50;'>Smart Database Interaction</h3>
            <p style='color:#ffffff;'>IntelliSQL bridges the gap between natural language and database queries, making data access more intuitive than ever.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown("""
        <h3 style='color:#4CAF50;'>🔧 How It Works</h3>
        <div style='padding:10px; border-left:4px solid #4CAF50;'>
            <p style='color:#ffffff;'>The system uses Google's advanced Gemini AI model to understand your natural language requests 
            and convert them into precise SQL queries. These queries are then executed on your local SQLite 
            database, with results displayed in an easy-to-read format.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown("""
        <h3 style='color:#4CAF50;'>🛠️ Technology Stack</h3>
        <div style='display:flex; justify-content:space-between; flex-wrap:wrap;'>
            <div style='width:30%; padding:10px; margin:5px;'>
                <h4 style='color:#4CAF50;'>Google Gemini</h4>
                <p style='color:#ffffff;'>Advanced AI for natural language understanding</p>
            </div>
            <div style='width:30%; padding:10px; margin:5px;'>
                <h4 style='color:#4CAF50;'>SQLite</h4>
                <p style='color:#ffffff;'>Lightweight local database engine</p>
            </div>
            <div style='width:30%; padding:10px; margin:5px;'>
                <h4 style='color:#4CAF50;'>Streamlit</h4>
                <p style='color:#ffffff;'>Interactive web app framework</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown("""
        <div style='text-align:center; padding:20px;'>
            <h4 style='color:#4CAF50;'>💡 Note</h4>
            <p style='color:#ffffff;'>All database operations are performed locally on your machine. No data is sent to external servers except for the initial query conversion to Gemini.</p>
        </div>
        """, unsafe_allow_html=True)

    elif selection == "Query Assistant":
        st.markdown("<h1 style='color:#4CAF50;'>Intelligent Query Assistant</h1>", unsafe_allow_html=True)
        user_input = st.text_input("🔍 Enter your instruction (e.g., 'Add new table EMPLOYEE')")

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
