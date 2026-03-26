from crewai import Task


def create_property_task(agent, context=[]) -> Task:
    return Task(
        description=(
            "Research the real estate market for {location}.\n"
            "1. If {location} is not a zip code, use tavily_search to identify the primary zip code(s) for the area.\n"
            "2. Use census_tool with the zip code to retrieve Census ACS5 demographics.\n"
            "3. Use tavily_search to find current average/median list prices and recent price trend direction.\n"
            "Report your findings clearly with data sources."
        ),
        expected_output=(
            "A structured report including:\n"
            "- Median home value (from Census ACS5)\n"
            "- Average list price (from Tavily search)\n"
            "- Price trend direction (rising/stable/falling)\n"
            "- Owner-occupied vs renter-occupied ratio\n"
            "- Median household income\n"
            "- Data sources cited"
        ),
        agent=agent,
        context=context,
    )
