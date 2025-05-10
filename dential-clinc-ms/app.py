from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from utils.logger import log_message
from utils.database.db_connector import get_db_connection, get_db_config
from utils.database.schema_loader import load_schema
from utils.sql_executor import execute_sql
from config import GEMINI_API_KEY, TOGETHER_API_KEY, TOGETHER_API_URL

from agents.general_question_answering_agent.general_question_answering_agent import llmForGeneralQuestions
from agents.database_question_processing_agent.generate_answer_from_db_results import generate_answer_from_db_results
from agents.database_question_processing_agent.get_sql_agent import generate_sql as get_llm_sql
from agents.database_question_processing_agent.question_agent import classify_and_handle_question as typeOfQuestion
from agents.database_question_processing_agent.question_improvement_agent import get_focused_schema

app = FastAPI()
schema = load_schema()
db_config = get_db_config()
connection = get_db_connection(db_config)

class QuestionInput(BaseModel):
    question: str

@app.post("/ask")
def ask_question(payload: QuestionInput):
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        question_type = typeOfQuestion(question)
        if question_type != "DATABASE":
            response = llmForGeneralQuestions(question, GEMINI_API_KEY)
            return {"type": "general", "response": response}

        improved_question = get_focused_schema(question, schema, TOGETHER_API_URL, TOGETHER_API_KEY)
        sql = get_llm_sql(improved_question, schema,GEMINI_API_KEY)



        if not sql.startswith("SQL:"):
            raise HTTPException(status_code=400, detail="Failed to generate valid SQL")

        clean_sql = sql[4:].strip().replace("\\*", "*").replace("\\_", "_")
        results = execute_sql(connection, clean_sql)

        if not results:
            return {"type": "database", "sql": clean_sql, "results": [], "answer": "No matching data found."}

        answer = generate_answer_from_db_results(clean_sql,question, results, TOGETHER_API_URL, TOGETHER_API_KEY)
        return {"type": "database", "sql": clean_sql, "results": results, "answer": answer}

    except Exception as e:
        log_message(f"API error: {str(e)}", "error")
        raise HTTPException(status_code=500, detail="Internal error occurred")
