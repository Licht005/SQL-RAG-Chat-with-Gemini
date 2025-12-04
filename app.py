import streamlit as st
import google.generativeai as genai
import sqlite3
import os

# App title
st.title("SQL RAG Chat with Gemini")

# Input for Gemini API key
api_key = st.sidebar.text_input("Gemini API Key", type="password")
if not api_key:
    st.warning("Enter your Gemini API key in the sidebar to continue.")
    st.stop()

# Configure Gemini
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-flash')
# File uploader for SQLite DB
uploaded_file = st.sidebar.file_uploader("Upload SQLite DB (.db)", type="db")

# Initialize session state for chat history and DB connection
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'conn' not in st.session_state:
    st.session_state.conn = None
if 'schema' not in st.session_state:
    st.session_state.schema = ""

# Handle uploaded DB
if uploaded_file:
    # Save to temporary file
    temp_db_path = "temp.db"
    with open(temp_db_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Connect to DB
    st.session_state.conn = sqlite3.connect(temp_db_path)
    cursor = st.session_state.conn.cursor()
    
    # Extract schema for prompt context
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    schema_lines = []
    for table in tables:
        table_name = table[0]
        cursor.execute(f"PRAGMA table_info({table_name})")
        cols = cursor.fetchall()
        col_info = ", ".join([f"{col[1]} ({col[2]})" for col in cols])
        schema_lines.append(f"Table {table_name}: {col_info}")
    st.session_state.schema = "\n".join(schema_lines)
    
    st.sidebar.success("DB uploaded and schema extracted!")
    st.sidebar.text(st.session_state.schema)

# Display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
user_query = st.chat_input("Ask a question about the database...")
if user_query:
    if not st.session_state.conn:
        st.error("Upload a SQLite DB first!")
        st.stop()
    
    # Add user message to history
    st.session_state.chat_history.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)
    
    # Step 1: Generate SQL query using Gemini (retrieval step)
    sql_prompt = f"""
    You are an expert SQL query generator. Given the following database schema:
    {st.session_state.schema}
    
    Generate a valid SELECT SQL query to answer the user's question: "{user_query}"
    Only generate SELECT queries for safety. Output only the SQL query, nothing else.
    If the question can't be answered with the schema, output "Invalid query".
    """
    sql_response = model.generate_content(sql_prompt)
    sql_query = sql_response.text.strip().replace("```sql", "").replace("```", "").strip()
    
    # Step 2: Execute SQL on DB
    cursor = st.session_state.conn.cursor()
    try:
        cursor.execute(sql_query)
        results = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        result_str = f"Columns: {', '.join(column_names)}\nRows:\n" + "\n".join([str(row) for row in results])
    except Exception as e:
        result_str = f"Error executing SQL: {str(e)}"
    
    # Step 3: Generate natural language response using Gemini (augmentation step)
    nl_prompt = f"""
    You are a helpful assistant. Given the user's question: "{user_query}"
    SQL query generated: {sql_query}
    Query results: {result_str}
    
    Summarize the results in natural language. Be concise and directly answer the question.
    If there was an error or no results, explain politely.
    """
    nl_response = model.generate_content(nl_prompt)
    assistant_reply = nl_response.text.strip()
    
    # Add assistant message to history
    st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})
    with st.chat_message("assistant"):
        st.markdown(assistant_reply)


import atexit

# Function to clean up the temp database when the Python process exits
def cleanup_temp_db():
    if st.session_state.conn:
        try:
            st.session_state.conn.close()
        except:
            pass
    if os.path.exists("temp.db"):
        try:
            os.remove("temp.db")
        except PermissionError:
            pass

# Register the cleanup function to run when the script exits
atexit.register(cleanup_temp_db)

# Also close connection properly when a new DB is uploaded (prevents old lock)
if uploaded_file and st.session_state.conn:
    try:
        st.session_state.conn.close()
    except:
        pass
    if os.path.exists("temp.db"):
        try:
            os.remove("temp.db")
        except:
            pass  # ignore if still locked