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
        "also never return other answer only DATABASE or GENERAL. if dont know return the closest"
        
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
        "You are a **SQL Query Preprocessor** with two key tasks: **question refinement** and **schema validation**. "
        "Your output will be used by another LLM to generate accurate SQL queries. Follow these steps precisely:\n\n"

        "1. **Correct & Improve the Question** (for SQL generation):\n"
        "   - Fix grammar/spelling but preserve intent.\n"
        "   - Replace vague terms with **exact schema column/table names**.\n"
        "   - Disambiguate phrasing (e.g., 'last year' → 'WHERE date >= DATE_SUB(NOW(), INTERVAL 1 YEAR)').\n\n"

        "2. **Schema Validation & Mapping**:\n"
        "   - Identify required tables/columns from the schema.\n"
        "   - If a field is missing, explicitly state it.\n"
        "   - Map colloquial terms to schema fields (e.g., 'heart disease' → `diagnoses.condition`).\n\n"

        "3. **Output Strict Format (JSON for Parsing)**:\n"
        "```json\n"
        "{\n"
        "   \"refined_question\": \"Clear, schema-aware question for SQL generation\",\n"
        "   \"schema_reference\": {\n"
        "       \"tables\": [\"table1\", \"table2\"],\n"
        "       \"columns\": {\"question_term\": \"schema.column\"}\n"
        "   },\n"
        "   \"missing_data\": [\"field1\", \"field2\"]  // If any\n"
        "}\n"
        "```\n\n"

        "**Example Input/Output**:\n"
        "- User Question: \"how many patient got heart disease?\"\n"
        "- Output:\n"
        "```json\n"
        "{\n"
        "   \"refined_question\": \"Count patients with `diagnoses.condition` containing 'cardiovascular' or 'heart disease' in the `diagnoses` table\",\n"
        "   \"schema_reference\": {\n"
        "       \"tables\": [\"patients\", \"diagnoses\"],\n"
        "       \"columns\": {\"heart disease\": \"diagnoses.condition\"}\n"
        "   },\n"
        "   \"missing_data\": []\n"
        "}\n"
        "```\n\n"

        f"**Schema for Validation**:\n{full_schema}"
    )

    user_prompt = (
        f"Original question: {user_question}\n"
        "Please correct any language issues and validate against the schema."
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
        "Given the following database schema, generate THE SINGLE MOST RELEVANT safe SELECT SQL query (no modifications) "
        "that answers the user's question. "
        "Before generating SQL, always check the schema to see which tables and columns actually exist for the requested information. "
        "Choose the most appropriate single query that would answer the question - do not generate multiple alternatives. "
        "Do not generate a query for a column or table that does not exist in the schema. "
        "Output format: Exactly one line starting with 'SQL:' followed by the single best query.\n"
        "When generating SQL, always use the exact name or value provided by the user in the WHERE clause, even if it looks unusual, contains titles, or is not a typical name. "
        "Never change, correct, or remove any part of the user's input value. "
        "If the user's question refers to a name, choose the most likely table containing that name (e.g., prefer patient_name in patients over name in users for medical queries). "
        "If a table has an 'age' column but not a 'birthdate', and the user asks for birthdate, return a query for age with explanation. "
        "Never generate attributes yourself (e.g., use 'id' not 'patient_id' if that's what's in the schema).\n"
        "MariaDB 10.x limitations:\n"
        "- No 'LIMIT' inside IN/ALL/ANY/SOME subqueries\n"
        "- Ensure queries are compatible with MariaDB 10.x syntax\n\n"
        "Correct examples:\n"
        "SQL: SELECT diseases FROM patients WHERE patient_name LIKE '%John%';\n"
        "SQL: SELECT age FROM patients WHERE patient_name = 'Mary Smith';\n\n"
        "Incorrect examples:\n"
        "Multiple queries (WRONG):\n"
        "SQL: SELECT name FROM users WHERE name LIKE '%John%';\n"
        "SQL: SELECT patient_name FROM patients WHERE patient_name LIKE '%John%';\n\n"
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
    sql_response = response.json()['choices'][0]['message']['content'].strip()
    
    # Force single query output - take the first one if multiple are generated
    for line in sql_response.splitlines():
        if line.strip().startswith("SQL:"):
            return line.strip()
    
    return sql_response  # fallback

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
        "max_tokens": 512,
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
            
        print("\nDatabase Query Assistant")
        print("Type your question or 'exit' to quit\n")
        
        api_key = os.getenv("TOGETHER_API_KEY")
        api_url = os.getenv("TOGETHER_API_URL", "https://api.together.xyz/v1/chat/completions")
        schema = load_schema("schema.sql")

        while True:
            question = input("\nYour question: ").strip()
            if question.lower() in ('exit', 'quit'):
                print("Goodbye!")
                break
            if not question:
                continue

            try:
                # Step 1: Classify question
                question_type = typeOfQuestion(question, schema, api_url, api_key)
                if question_type != "DATABASE":
                    print("This question doesn't appear to be about database data.")
                    continue

                # Step 2: Generate single optimized SQL query
                improvedQuestion = get_focused_schema(question, schema, api_url, api_key)
                print(f"improvedQuestion: {improvedQuestion}")
                sql = get_llm_sql(improvedQuestion, schema, api_url, api_key)
                if not sql.startswith("SQL:"):
                    print("Could not generate a valid SQL query for this question.")
                    continue

                # Clean and execute the single query
                clean_sql = sql[4:].strip().replace("\\*", "*")
                print(f"\nExecuting: {clean_sql}")
                
                results = execute_sql(connection, clean_sql)
                if not results:
                    print("No matching data found.")
                    continue

                # Display formatted results
                print("\nResults:")
                
                answer = get_llm_answer(question, results, api_url, api_key)
                print(f"llm answer is {answer}")

            except Exception as e:
                log_message(f"Error processing question: {str(e)}", "error")
                print("An error occurred. Please try a different question.")

    except Exception as e:
        log_message(f"System error: {str(e)}", "critical")
        print("A system error occurred. Check logs for details.")
    finally:
        if connection:
            connection.close()

if __name__ == "__main__":
    main() 