from crewai import Task


SAFETY_SCORING_GUIDE = """
SCORING GUIDE — apply this when Gavel scores safety:
- Score 7-9: Violent crime is low, even if property crime is above average.
- Score 4-6: Both property and violent crime are moderately above average.
- Score 1-3: Violent crime is significantly elevated — the only trigger for a low score.
- A crime index above the city average does NOT automatically mean unsafe.
  Always separate property crime from violent crime and weight violent crime more heavily.
- High-value neighbourhoods (e.g. Arcadia-type areas) typically have above-average property
  crime rates but low violent crime. This is normal and should not penalise the safety score.
""".strip()


def create_safety_task(agent, context=[]) -> Task:
    return Task(
        description=(
            "CRITICAL: Always search for crime data using the exact neighborhood name AND zip "
            "code provided. Do not use data from adjacent zip codes or similarly named areas. "
            "Arcadia Phoenix 85018 and Arcadia Phoenix 85008 are completely different "
            "neighborhoods with very different crime profiles. Always verify the zip code "
            "matches the user's input before using any crime statistic.\n\n"
            "Research safety and crime data for {location}.\n"
            "Use tavily_search to find:\n"
            "- Crime statistics at the neighbourhood level, not just city averages\n"
            "- Separate figures for property crime and violent crime where available\n"
            "- Trend direction (improving/stable/worsening)\n"
            "- Resident safety perception where available\n"
            "Use prior property and school context to confirm the correct geographic area.\n\n"
            f"{SAFETY_SCORING_GUIDE}"
        ),
        expected_output=(
            "A structured report including:\n"
            "- Property crime rate vs city/national average\n"
            "- Violent crime rate vs city/national average\n"
            "- Crime trend direction\n"
            "- Summary of resident safety perception"
        ),
        agent=agent,
        context=context,
    )
