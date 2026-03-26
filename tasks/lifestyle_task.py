from crewai import Task


def create_lifestyle_task(agent, context=[]) -> Task:
    return Task(
        description=(
            "Research lifestyle and liveability for {location}.\n"
            "1. Use overpass_tool with '{location}' to get POI counts for parks, gyms, "
            "restaurants, grocery stores, transit stops, and schools within 2km.\n"
            "2. Use tavily_search to find walkability score or transit quality information.\n"
            "3. Use tavily_search to find qualitative neighborhood character descriptions.\n"
            "Report POI counts prominently — they are ground-truth data."
        ),
        expected_output=(
            "A structured report including:\n"
            "- POI counts with named highlights (parks, gyms, restaurants, grocery, transit, schools)\n"
            "- Walkability summary\n"
            "- Qualitative neighborhood character description"
        ),
        agent=agent,
        context=context,
    )
