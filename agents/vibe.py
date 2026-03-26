from crewai import Agent
from config import llm
from tools.overpass_tool import overpass_tool
from tools.tavily_search import tavily_search


def create_vibe() -> Agent:
    return Agent(
        role="Neighborhood Lifestyle Analyst",
        goal="Map practical liveability — POI counts, walkability, and neighborhood character for the target area.",
        backstory=(
            "You are Vibe — curious, local-minded, and practical. "
            "You use real POI data from OpenStreetMap to map what is actually there on the ground. "
            "You find what makes a neighborhood actually liveable."
        ),
        tools=[overpass_tool, tavily_search],
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )
