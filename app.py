# Updated `app.py` for QueryCraft

````python
import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import os
import time
from dotenv import load_dotenv

from sql import (
    init_database,
    execute_sql,
    get_schema,
    save_query_history,
    get_query_history,
    get_dashboard_metrics,
    get_company_distribution,
    get_class_performance,
    get_sample_prompts
)


# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="QueryCraft AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================
# CUSTOM CSS
# =========================

st.markdown("""
<style>

.main {
    background-color: #0e1117;
}

.stApp {
    background: linear-gradient(to right, #0f172a, #111827);
    color: white;
}

.block-container {
    padding-top: 2rem;
}

.metric-card {
    background: rgba(255,255,255,0.05);
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    border: 1px solid rgba(255,255,255,0.1);
}

.query-box {
    background: rgba(255,255,255,0.05);
    padding: 20px;
    border-radius: 15px;
}

.sql-box {
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)


# =========================
# LOAD ENV VARIABLES
# =========================

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    st.error("❌ GOOGLE_API_KEY not found in .env file")
    st.stop()


# =========================
# GEMINI CONFIG
# =========================

try:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
except Exception as e:
    st.error(f"Gemini Error: {e}")
    st.stop()


# =========================
# INITIALIZE DATABASE
# =========================

init_database()


# =========================
# AI SQL GENERATION
# =========================


def generate_sql(user_prompt):

    schema = get_schema()

    prompt = f"""
    You are an expert SQLite SQL generator.

    DATABASE SCHEMA:
    {schema}

    RULES:
    1. Generate ONLY SQLite SQL.
    2. Do NOT include markdown.
    3. Do NOT include explanation.
    4. Only generate SELECT queries.
    5. Use correct table and column names.

    USER REQUEST:
    {user_prompt}
    """

    response = model.generate_content(prompt)

    sql_query = response.text.strip()

    sql_query = sql_query.replace("```sql", "")
    sql_query = sql_query.replace("```", "")

    return sql_query.strip()


# =========================
# SIDEBAR
# =========================

st.sidebar.title("🚀 QueryCraft AI")

menu = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Dashboard",
        "🤖 AI Query Assistant",
        "📊 Analytics",
        "🧠 Query History",
        "📚 Database Schema"
    ]
)

st.sidebar.markdown("---")

st.sidebar.subheader("💡 Sample Prompts")

sample_prompts = get_sample_prompts()

for prompt in sample_prompts:
    st.sidebar.caption(f"• {prompt}")


# =========================
# DASHBOARD
# =========================

if menu == "🏠 Dashboard":

    st.title("🚀 QueryCraft AI Dashboard")
    st.markdown("AI Powered Natural Language SQL Assistant")

    metrics = get_dashboard_metrics()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("👨‍🎓 Students", metrics["total_students"])

    with col2:
        st.metric("📈 Average Marks", metrics["average_marks"])

    with col3:
        st.metric("💼 Companies", metrics["total_companies"])

    with col4:
        st.metric("💰 Highest Package", f'{metrics["highest_package"]} LPA')

    st.markdown("---")

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:

        st.subheader("🏢 Company Distribution")

        company_df = get_company_distribution()

        fig = px.bar(
            company_df,
            x="company",
            y="total_students"
        )

        st.plotly_chart(fig, use_container_width=True)

    with chart_col2:

        st.subheader("📚 Class Performance")

        class_df = get_class_performance()

        fig2 = px.pie(
            class_df,
            names="class",
            values="average_marks"
        )

        st.plotly_chart(fig2, use_container_width=True)


# =========================
# AI QUERY ASSISTANT
# =========================

elif menu == "🤖 AI Query Assistant":

    st.title("🤖 AI SQL Assistant")

    user_prompt = st.text_area(
        "Enter your query in plain English",
        placeholder="Example: Show top 5 students by marks"
    )

    if st.button("🚀 Generate & Execute Query"):

        if not user_prompt.strip():
            st.warning("Please enter a query.")

        else:

            with st.spinner("Generating SQL query using Gemini AI..."):

                start_time = time.time()

                sql_query = generate_sql(user_prompt)

                execution_time = round(time.time() - start_time, 2)

                st.subheader("🧠 Generated SQL")
                st.code(sql_query, language="sql")

                df, cols, error = execute_sql(sql_query)

                save_query_history(
                    user_prompt,
                    sql_query,
                    execution_time
                )

                if error:
                    st.error(error)

                else:

                    st.success(f"✅ Query executed in {execution_time} sec")

                    st.subheader("📊 Query Result")

                    st.dataframe(
                        df,
                        use_container_width=True
                    )

                    csv = df.to_csv(index=False).encode('utf-8')

                    st.download_button(
                        "⬇ Download CSV",
                        csv,
                        "query_results.csv",
                        "text/csv"
                    )

                    if len(df.columns) >= 2:

                        st.subheader("📈 Visualization")

                        numeric_cols = df.select_dtypes(include='number').columns

                        if len(numeric_cols) > 0:

                            chart = px.bar(
                                df,
                                x=df.columns[0],
                                y=numeric_cols[0]
                            )

                            st.plotly_chart(
                                chart,
                                use_container_width=True
                            )


# =========================
# ANALYTICS
# =========================

elif menu == "📊 Analytics":

    st.title("📊 Analytics Dashboard")

    company_df = get_company_distribution()
    class_df = get_class_performance()

    st.subheader("🏢 Company-wise Student Count")

    fig = px.bar(
        company_df,
        x="company",
        y="total_students"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📚 Average Marks by Class")

    fig2 = px.line(
        class_df,
        x="class",
        y="average_marks",
        markers=True
    )

    st.plotly_chart(fig2, use_container_width=True)


# =========================
# QUERY HISTORY
# =========================

elif menu == "🧠 Query History":

    st.title("🧠 Query History")

    history_df = get_query_history()

    if history_df.empty:
        st.info("No query history found.")

    else:
        st.dataframe(history_df, use_container_width=True)


# =========================
# DATABASE SCHEMA
# =========================

elif menu == "📚 Database Schema":

    st.title("📚 Database Schema")

    schema = get_schema()

    st.code(schema)

````
