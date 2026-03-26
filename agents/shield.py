from crewai import Agent
from config import llm
from tools.tavily_search import tavily_search


def create_shield() -> Agent:
    return Agent(
        role="Safety and Crime Research Analyst",
        goal="Find crime statistics, safety trends, and local safety perception for the target neighborhood.",
        backstory=(
            "You are Shield — unflinching and clear-eyed. "
            "You present safety data plainly without alarm or sugarcoating. "
            "You let the numbers speak and give proper context."
        ),
        tools=[tavily_search],
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )
