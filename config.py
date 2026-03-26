import os
from dotenv import load_dotenv
from crewai import LLM

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

llm = LLM(model="gemini/gemini-2.5-flash-lite", api_key=GEMINI_API_KEY)
