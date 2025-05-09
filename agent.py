import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)

base_prompt = (
    "You are a dental expert working on a dental website (MS). All questions you receive are dental-related. "
    "You must not answer any question that involves database lookups or specific patient information, as you are not connected to a database. "
    "There are other LLMs better suited for those tasks. "
    "Keep your answers short and concise unless the dentist specifically asks for a longer explanation. "
    "Avoid unnecessary elaboration. Only answer questions that can be addressed without external data.\n\n"
)

user_question = "What causes gingivitis?- with details"
prompt = base_prompt + user_question

model = genai.GenerativeModel("models/gemini-1.5-flash")
response = model.generate_content(prompt)

print("Gemini Response:\n", response.text)
