# SQL RAG Chat with Gemini

A lightweight Streamlit application that allows users to chat with their SQLite databases using Natural Language. This app uses **Gemini 2.5 Flash** to translate user questions into SQL queries, execute them, and summarize the results back into plain English.

## 🚀 Features

* **Natural Language to SQL**: No need to write complex queries; just ask questions like "Who are the top 5 customers by revenue?"
* **Dynamic Schema Extraction**: Automatically reads your SQLite `.db` file to understand tables and columns.
* **Conversational Interface**: Built with Streamlit's chat elements for a smooth user experience.
* **Privacy-Focused**: Includes an `atexit` cleanup routine to remove temporary database files after the session ends.

---

## 🛠️ Tech Stack

* **Frontend**: [Streamlit](https://streamlit.io/)
* **LLM**: [Google Gemini API](https://ai.google.dev/) (Gemini 2.5 Flash)
* **Database**: SQLite
* **Language**: Python

---

## 📥 Getting Started

### 1. Prerequisites

Ensure you have Python 3.8+ installed and a Google Gemini API Key. You can get a key at [Google AI Studio](https://aistudio.google.com/).

### 2. Installation

Clone this repository and install the required dependencies:

```bash
git clone https://github.com/your-username/sql-rag-gemini.git
cd sql-rag-gemini
pip install streamlit google-generativeai

```

### 3. Run the App

```bash
streamlit run app.py

```

---

## 📖 How to Use

1. **Enter API Key**: Paste your Gemini API key in the sidebar.
2. **Upload Database**: Upload any `.db` (SQLite) file via the sidebar.
3. **Chat**: Type your question in the chat box.
* *Example: "List all products that are out of stock."*
* *Example: "How many users signed up in December?"*



---

## 🔍 How it Works (The RAG Flow)

1. **Schema Context**: The app extracts the schema (Table names and Column types) from your uploaded file.
2. **SQL Generation**: Your question + the Schema are sent to Gemini to generate a valid `SELECT` query.
3. **Execution**: The generated SQL is executed locally on your SQLite file.
4. **Natural Language Summary**: The raw data results are sent back to Gemini to be formatted into a human-readable answer.

---

## ⚠️ Limitations & Security

* **Read-Only**: The system is prompted to only generate `SELECT` queries to prevent data modification.
* **File Size**: Performance depends on the size of the results returned to the LLM context window.

---

Would you like me to add a `requirements.txt` file content as well to make the setup even easier for your users?
