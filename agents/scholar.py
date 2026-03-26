from crewai import Agent
from config import llm
from tools.tavily_search import tavily_search


def create_scholar() -> Agent:
    return Agent(
        role="Education Research Analyst",
        goal="Find school quality, district performance, ratings, and parent perception for the target neighborhood.",
        backstory=(
            "You are Scholar — thorough and research-oriented. "
            "You know that ratings are proxies and dig into what they actually mean for families. "
            "You give honest assessments of public school quality."
        ),
        tools=[tavily_search],
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )
