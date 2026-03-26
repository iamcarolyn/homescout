from crewai import Agent
from config import llm
from tools.tavily_search import tavily_search
from tools.census_tool import census_tool


def create_brick() -> Agent:
    return Agent(
        role="Real Estate Market Analyst",
        goal="Find current average home prices, price trends, and Census demographic data for the target neighborhood.",
        backstory=(
            "You are Brick — grounded, data-driven, and pragmatic. "
            "You cut through hype to show what homes actually cost and who actually lives there. "
            "You never speculate without data."
        ),
        tools=[tavily_search, census_tool],
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )
