from crewai import Task


def create_school_task(agent, context=[]) -> Task:
    return Task(
        description=(
            "Research school quality for {location}.\n"
            "Use tavily_search to find:\n"
            "- Names of elementary, middle, and high schools serving the area\n"
            "- GreatSchools ratings or state performance data where available\n"
            "- School district context and any notable performance trends\n"
            "- Parent perception or reviews if available\n"
            "Use the property context to identify the correct school district."
        ),
        expected_output=(
            "A structured report including:\n"
            "- School names with ratings or performance notes\n"
            "- District context and overall performance level\n"
            "- Plain summary of overall school quality for the area"
        ),
        agent=agent,
        context=context,
    )
