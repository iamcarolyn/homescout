from crewai import Task

SCORECARD_FORMAT = """
PRICE SCORE: X/10 — rationale
SCHOOL SCORE: X/10 — rationale
SAFETY SCORE: X/10 — rationale
LIFESTYLE SCORE: X/10 — rationale
OVERALL VERDICT: [Strong Buy / Consider / Proceed with Caution / Pass]
KEY STRENGTHS:
- item
KEY CONCERNS:
- item
SUMMARY: 2-3 sentences
""".strip()


VERDICT_RULES = """
VERDICT RULES — follow these exactly:
1. Compute the average of all four scores (Price + School + Safety + Lifestyle) / 4.
2. Choose the verdict solely from this average:
   - Strong Buy          = average 7.5 or above
   - Consider            = average 6.0 to 7.4
   - Proceed with Caution = average 4.0 to 5.9
   - Pass                = average below 4.0
3. PRICE SCORE reflects affordability only. High prices in a desirable, high-demand area
   are a market reality, NOT a red flag. Do not let a low price score drag the verdict
   below what the other scores justify.
4. "Proceed with Caution" must NOT be used solely because of a low price score.
   Reserve it for cases where Safety is genuinely poor (below 4) AND at least two other
   scores are below 5 — OR when the average falls in the 4.0–5.9 range by the formula above.
5. A neighbourhood with strong schools, good safety, and great lifestyle but high prices
   is a "Consider" or "Strong Buy", not a "Proceed with Caution".
""".strip()


def create_scorecard_task(agent, context=[]) -> Task:
    return Task(
        description=(
            "Synthesize all research from Brick, Scholar, Shield, and Vibe into a final "
            "neighborhood scorecard for {location}.\n\n"
            "Score each domain 1-10 with a brief rationale.\n\n"
            f"{VERDICT_RULES}\n\n"
            "List 2-4 KEY STRENGTHS and 2-4 KEY CONCERNS.\n"
            "Write a 2-3 sentence SUMMARY.\n\n"
            "Your output MUST use this EXACT format — server.py parses it with regex:\n\n"
            f"{SCORECARD_FORMAT}"
        ),
        expected_output=SCORECARD_FORMAT,
        agent=agent,
        context=context,
    )
