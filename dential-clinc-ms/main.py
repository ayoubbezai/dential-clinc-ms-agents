import os
from utils.logger import log_message
from utils.database.db_connector import get_db_connection,get_db_config
from utils.database.schema_loader import load_schema
from utils.sql_executor import execute_sql


from config import (
    GEMINI_API_KEY,
    TOGETHER_API_KEY,
    TOGETHER_API_URL,
    SCHEMA_PATH
)

from agents.general_question_answering_agent.general_question_answering_agent import llmForGeneralQuestions
from agents.database_question_processing_agent.generate_answer_from_db_results import generate_answer_from_db_results
from agents.database_question_processing_agent.get_sql_agent import generate_sql as get_llm_sql
from agents.database_question_processing_agent.question_agent import classify_and_handle_question as typeOfQuestion
from agents.database_question_processing_agent.question_improvement_agent import get_focused_schema
def main():
    connection = None  # Ensure that connection is initialized

    try:
        # Load schema from configured path
        schema = load_schema()
        config = get_db_config()

        connection = get_db_connection(config)  # Attempt to get the DB connection
        if not connection:
            print("Failed to connect to database.")
            return  # Exit if connection failed

        print("\nDatabase Query Assistant")
        print("Type your question or 'exit' to quit\n")

        while True:
            question = input("\nYour question: ").strip()
            if question.lower() in ('exit', 'quit'):
                print("Goodbye!")
                break
            if not question:
                continue

            try:
                # Step 1: Classify the question
                question_type = typeOfQuestion(question)
                print(f"Question type: {question_type}")

                if question_type != "DATABASE":
                    # Handle general (non-database) questions
                    response = llmForGeneralQuestions(question, GEMINI_API_KEY)
                    print(f"Gemini answer: {response}")
                    continue

                # Step 2: Refine question and generate SQL
                improved_question = get_focused_schema(question, schema, TOGETHER_API_URL, TOGETHER_API_KEY)
                print(f"Improved question: {improved_question}")

                sql = get_llm_sql(question, schema, TOGETHER_API_URL, TOGETHER_API_KEY)
                print(f"Generated SQL: {sql}")

                if not sql.startswith("SQL:"):
                    print("Could not generate a valid SQL query for this question.")
                    continue

                clean_sql = sql[4:].strip().replace("\\*", "*")
                print(f"\nExecuting SQL: {clean_sql}")

                results = execute_sql(connection, clean_sql)
                if not results:
                    print("No matching data found.")
                    continue

                print("\nResults:")
                print(results)

                # Step 3: Generate a final answer from database results
                answer = generate_answer_from_db_results(question, results, TOGETHER_API_URL, TOGETHER_API_KEY)
                print(f"LLM Answer: {answer}")

            except Exception as e:
                log_message(f"Error processing question: {str(e)}", "error")
                print("An error occurred. Please try a different question.")

    except Exception as e:
        log_message(f"System error: {str(e)}", "critical")
        print("A system error occurred. Check logs for details.")
    finally:
        if connection:
            connection.close()  # Close the connection if it was created

if __name__ == "__main__":
    main()