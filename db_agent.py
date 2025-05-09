import os
import mysql.connector
from dotenv import load_dotenv
import requests
from datetime import datetime

# Configure logging
def log_message(message, level="info"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {level.upper()}: {message}"
    print(log_entry)
    with open("db_agent.log", "a", encoding='utf-8') as log_file:
        log_file.write(log_entry + "\n")

# Load configuration
def load_config():
    load_dotenv()
    config = {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", "3306"),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", ""),
        "database": os.getenv("DB_NAME", "dental_db")
    }
    
    # Check if we're using default values
    missing_vars = []
    if config["host"] == "localhost":
        missing_vars.append("DB_HOST")
    if config["user"] == "root":
        missing_vars.append("DB_USER")
    if not config["password"]:
        missing_vars.append("DB_PASSWORD")
    if config["database"] == "dental_db":
        missing_vars.append("DB_NAME")
    
    if missing_vars:
        log_message(f"Using default values for: {', '.join(missing_vars)}", "warning")
        print("\nWARNING: Using default database configuration.")
        print("To customize, create a .env file with these variables:")
        print("DB_HOST=your_host")
        print("DB_USER=your_username")
        print("DB_PASSWORD=your_password")
        print("DB_NAME=your_database")
        print("DB_PORT=3306 (optional)\n")
    
    return config

def get_db_connection(config):
    try:
        connection = mysql.connector.connect(**config)
        return connection
    except mysql.connector.Error as e:
        if e.errno == 1045:  # Access denied
            log_message("Database access denied. Please check your credentials.", "error")
            print("\nERROR: Could not connect to database. Please check your credentials in .env file.")
        elif e.errno == 1049:  # Unknown database
            log_message(f"Database '{config['database']}' does not exist.", "error")
            print(f"\nERROR: Database '{config['database']}' does not exist.")
            print("Please create the database or update DB_NAME in .env file.")
        else:
            log_message(f"Database connection error: {str(e)}", "error")
            print("\nERROR: Could not connect to database. Please check your configuration.")
        return None
    except Exception as e:
        log_message(f"Database connection failed: {str(e)}", "error")
        print("\nERROR: Failed to connect to database.")
        return None

def parse_query(query):
    """Convert natural language query to SQL query for the patients table"""
    query = query.lower().strip()
    
    # Extract patient name
    if "info about" in query or "information about" in query:
        name = query.split("about")[-1].strip()
        return {
            "type": "patient_info",
            "name": name,
            "sql": "SELECT * FROM patients WHERE patient_name LIKE %s"
        }
    elif "age of" in query:
        name = query.split("of")[-1].strip()
        return {
            "type": "patient_age",
            "name": name,
            "sql": "SELECT patient_name, age FROM patients WHERE patient_name LIKE %s"
        }
    # Add more patterns as needed
    return None

def execute_query(connection, query_info):
    if not connection:
        return "Database connection not available."
    
    try:
        cursor = connection.cursor(dictionary=True)
        if query_info["type"] in ["patient_info", "patient_age"]:
            search_term = f"%{query_info['name']}%"
            cursor.execute(query_info["sql"], (search_term,))
        results = cursor.fetchall()
        cursor.close()
        if not results:
            return "No data found in database."
        # Debug: print the keys of the first result
        print("DEBUG: Result keys:", list(results[0].keys()))
        return format_results(results, query_info["type"])
    except Exception as e:
        log_message(f"Query execution error: {str(e)}", "error")
        return "Error executing query."

def format_results(results, query_type):
    if query_type == "patient_info":
        formatted = []
        for patient in results:
            formatted.append(f"Patient Information:\n"
                            f"ID: {patient['id']}\n"
                            f"Name: {patient['patient_name']}\n"
                            f"Phone: {patient['phone']}\n"
                            f"Gender: {patient['gender']}\n"
                            f"Age: {patient['age']}\n"
                            f"Diseases: {patient['diseases']}\n"
                            f"Notes: {patient['notes']}\n"
                            f"Created: {patient['created_at']}\n"
                            f"Updated: {patient['updated_at']}")
        return "\n\n".join(formatted)
    elif query_type == "patient_age":
        formatted = []
        for patient in results:
            formatted.append(f"Name: {patient['patient_name']}\nAge: {patient['age']}")
        return "\n\n".join(formatted)
    return str(results)

def load_schema(schema_path="schema.sql"):
    with open(schema_path, "r", encoding="utf-8") as f:
        return f.read()

def typeOfQuestion(user_question, full_schema, api_url, api_key):
    system_prompt = (
        "You are a classifier that determines whether a user query is related to a database or not.\n"
        "- If the question involves fetching, counting, searching, querying, or accessing data (e.g., patients, appointments, records), classify it as: DATABASE.\n"
        "- If the question is about general knowledge, advice, or not related to data retrieval, classify it as: GENERAL.\n"
        "when u asked about name if its famous person so its  GENERAL else it could be data base also could the name dont contain patient or hint like that but still DATABASE "
        "Only respond with one word: DATABASE or GENERAL."
    )
    user_prompt = (
        f"User question: {user_question}\n"
        f"Full schema:\n{full_schema}"
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    payload = {
        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "messages": messages,
        "temperature": 0,
        "max_tokens": 20,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    response = requests.post(api_url, headers=headers, json=payload, timeout=20)
    response.raise_for_status()
    classification = response.json()['choices'][0]['message']['content'].strip()
    return classification



def get_focused_schema(user_question, full_schema, api_url, api_key):
    system_prompt = (
        "You are a MySQL schema expert. Given the full database schema and a user question, "
        "analyze the schema and determine exactly which table(s) and column(s) contain the information needed to answer the question. "
        "If the requested information does not exist in the schema, say so clearly. "
        "Output only the relevant CREATE TABLE statement(s) and a one-line summary for the SQL LLM, e.g.: "
        "'The column diseases is in the patients table as patients.diseases.' "
        "If the information is not present, say: 'No table contains the requested column.'"
        f"This is the schema. Use it to decide the correct question type: {full_schema}"
    )
    user_prompt = (
        f"User question: {user_question}\n"
        f"Full schema:\n{full_schema}"
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    payload = {
        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "messages": messages,
        "temperature": 0,
        "max_tokens": 512,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    response = requests.post(api_url, headers=headers, json=payload, timeout=20)
    response.raise_for_status()
    focused_schema = response.json()['choices'][0]['message']['content'].strip()
    return focused_schema

def get_llm_sql(user_question, schema, api_url, api_key):
    system_prompt = (
        "You are an expert MySQL assistant. "
        "Carefully read the provided schema and summary. Only generate SQL for columns and tables that exist and are mentioned in the summary. "
        "If the summary says the column is only in one table, only generate a query for that table. "
        "Given the following database schema, generate one or more safe, SELECT SQL queries (no modifications) "
        "that answer the user's question. "
        "Before generating SQL, always check the schema to see which tables and columns actually exist for the requested information. "
        "If the information could be in more than one table, generate multiple separate SELECT queries (not a UNION), each one valid for a single table/column. "
        "Do not generate a query for a column or table that does not exist in the schema. "
        "Output each SQL query on a separate line, prefixed by 'SQL:'. "
        "When generating SQL, always use the exact name or value provided by the user in the WHERE clause, even if it looks unusual, contains titles, or is not a typical name. "
        "Never change, correct, or remove any part of the user's input value. "
        "If the user's question refers to a name, always check all relevant name columns in all tables (e.g., patient_name in patients, name in users), unless the question clearly specifies a table. Generate a separate SQL query for each possible column/table combination that could answer the question. "
        "If a table has an 'age' column but not a 'birthdate', and the user asks for birthdate, explain that only age is available and generate a query for age. If the user asks for birthdate and only age is available, return the age and explain that birthdate is not in the schema. "
        "dont genrate attrubiutes by your self Exemple id of patient is called id not patient_id and so on for other data so u need to check schema very well before gerate the sql"
        "- The database uses **MariaDB version 10.x**, which **does not support 'LIMIT' inside IN/ALL/ANY/SOME subqueries**."
        "- Always generate SQL queries compatible with **MariaDB 10.x syntax limitations**."
        "check"
        "Example:\n"
        "SQL: SELECT diseases FROM patients WHERE patient_name = 'Dr. Ottilie Kunde I';\n"
        "SQL: SELECT age FROM patients WHERE patient_name = 'Hardy Howell';\n"
        "If the user asks for birthdate and only age is available, respond: 'The database does not contain a birthdate column, but here is the age.'\n"
        "Only output the SQL queries, nothing else, unless you need to explain the lack of a birthdate column.\n\n"
        "- Ensure the SQL query does not include unnecessary escape characters like backslashes before the asterisk (`*`)." 
        "- Use `COUNT(*)` correctly without escaping the asterisk (e.g., `SELECT COUNT(*) FROM patients;`)."
        f"SCHEMA AND SUMMARY:\n{schema}\n"
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_question}
    ]
    payload = {
        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "messages": messages,
        "temperature": 0,
        "max_tokens": 512,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    response = requests.post(api_url, headers=headers, json=payload, timeout=20)
    response.raise_for_status()
    sql = response.json()['choices'][0]['message']['content'].strip()
    return sql

def execute_sql(connection, sql):
    cursor = connection.cursor(dictionary=True)
    cursor.execute(sql)
    results = cursor.fetchall()
    cursor.close()
    return results

def get_llm_answer(user_question, db_results, api_url, api_key):
    system_prompt = (
        "You are a helpful assistant. Given the user's question and the following database results, generate a clear, concise answer. "
        "If the results are empty, say you could not find the information in the database."
    )
    user_prompt = (
        f"User question: {user_question}\n"
        f"Database results: {db_results}"
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    payload = {
        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "messages": messages,
        "temperature": 0,
        "max_tokens": 256,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    response = requests.post(api_url, headers=headers, json=payload, timeout=20)
    response.raise_for_status()
    answer = response.json()['choices'][0]['message']['content'].strip()
    return answer

def main():
    try:
        config = load_config()
        connection = get_db_connection(config)
        if not connection:
            return
        print("\nDatabase Query Assistant (patients table)")
        print("You can ask questions like:")
        print("- 'Give me info about Ahmed'")
        print("- 'What is the age of Ahmed?'")
        print("- 'exit' to quit")
        api_key = os.getenv("TOGETHER_API_KEY")
        api_url = os.getenv("TOGETHER_API_URL", "https://api.together.xyz/v1/chat/completions")
        schema = load_schema("schema.sql")
        while True:
            question = input("\nYour question: ").strip()
            if question.lower() == "exit":
                print("Goodbye.")
                break
            if not question:
                continue
            try:
                full_schema = load_schema("schema.sql")
                classification = typeOfQuestion(question, full_schema, api_url, api_key)
                print(f"\ntype of question is :\n{classification}")
                focused_schema = get_focused_schema(question, full_schema, api_url, api_key)
                sql = get_llm_sql(question, focused_schema, api_url, api_key)
                sql = sql.replace("\\_", "_");
                print(f"\nGenerated SQL(s):\n{sql}")
                queries = [line.replace("SQL:", "").strip() for line in sql.splitlines() if line.strip().startswith("SQL:")]
                found = False
                for q in queries:
                    try:
                        results = execute_sql(connection, q)
                        if results and any(any(v not in (None, '', 0) for v in row.values()) for row in results):
                            print("\nResults:")
                            for row in results:
                                print(row)
                            # Pass to LLM for a natural language answer
                            answer = get_llm_answer(question, results, api_url, api_key)
                            print("\nLLM Answer:")
                            print(answer)
                            found = True
                            break
                    except mysql.connector.Error as db_err:
                        if getattr(db_err, 'errno', None) in (1054, 1146):
                            continue  # Try next query
                        else:
                            log_message(f"DB Error: {str(db_err)}", "error")
                            print("A database error occurred. Check logs for details.")
                            found = True
                            break
                if not found:
                    print("I could not find this information in the database.")
            except Exception as e:
                log_message(f"Error: {str(e)}", "error")
                print("Error occurred. Check logs for details.")
    except Exception as e:
        log_message(f"System error: {str(e)}", "critical")
        print("System error occurred. Check logs for details.")
    finally:
        if connection:
            connection.close()

if __name__ == "__main__":
    main() 