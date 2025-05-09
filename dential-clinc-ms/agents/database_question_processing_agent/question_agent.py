from utils.question_classifier import typeOfQuestion
from utils.logger import log_message
from config import TOGETHER_API_KEY,TOGETHER_API_URL, SCHEMA_PATH

def classify_and_handle_question(user_question):
    """
    Classifies the user question and takes action based on the classification.
    """
    # Load schema from file
    with open(SCHEMA_PATH, "r", encoding="utf-8") as schema_file:
        full_schema = schema_file.read()

    # Step 1: Classify the question
    question_type = typeOfQuestion(user_question, full_schema, TOGETHER_API_URL,TOGETHER_API_KEY)

    # Step 2: Log the classification result
    log_message(f"Classified question: '{user_question}' as {question_type}")

    # Step 3: Take action based on classification
    if question_type == "DATABASE":
        handle_database_query(user_question)
    else:
        handle_general_query(user_question)
    return question_type


def handle_database_query(user_question):
    """
    Handle the database-related query.
    You can expand this to actually query a database, etc.
    """
    log_message(f"Handling database query: {user_question}")
    # Add your database query logic here, for example:
    # query = f"SELECT * FROM patients WHERE patient_name LIKE '%{user_question}%'"
    # result = execute_database_query(query)
    # log_message(f"Database query result: {result}")


def handle_general_query(user_question):
    """
    Handle general knowledge-related queries.
    """
    log_message(f"Handling general query: {user_question}")
    # Add your general knowledge handling logic here, for example:
    # result = get_general_knowledge_answer(user_question)
    # log_message(f"General query result: {result}")
