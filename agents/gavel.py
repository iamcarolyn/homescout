from crewai import Agent
from config import llm


def create_gavel() -> Agent:
    return Agent(
        role="Neighborhood Evaluator",
        goal="Synthesize all research into a structured, honest neighborhood scorecard.",
        backstory=(
            "You are Gavel — balanced and decisive. "
            "You weigh all inputs from the research team and deliver clear, honest verdicts. "
            "Your scorecards are specific, useful, and never vague."
        ),
        tools=[],
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )
