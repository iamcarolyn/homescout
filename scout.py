#!/usr/bin/env python3
"""CLI entry point for HomeScout."""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from crew import build_crew
from agents.brick import create_brick
from tasks.property_task import create_property_task
from crewai import Crew, Process
from config import llm


def slugify(text: str) -> str:
    return "".join(c if c.isalnum() else "-" for c in text.lower()).strip("-")


def main():
    parser = argparse.ArgumentParser(description="HomeScout — Neighborhood Research Crew")
    parser.add_argument("location", help="City, neighborhood, or zip code to research")
    parser.add_argument("--dry-run", action="store_true", help="Run Brick only and stop")
    args = parser.parse_args()

    location = args.location
    print(f"\n🏡 HomeScout — researching: {location}\n")

    if args.dry_run:
        print("DRY RUN: Running Brick only...\n")
        brick = create_brick()
        property_task = create_property_task(brick)
        dry_crew = Crew(
            agents=[brick],
            tasks=[property_task],
            process=Process.sequential,
            verbose=True,
        )
        result = dry_crew.kickoff(inputs={"location": location})
        print("\n--- DRY RUN COMPLETE ---")
        print(str(result))
        return

    crew = build_crew()
    result = crew.kickoff(inputs={"location": location})

    scorecard_text = str(result)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    slug = slugify(location)[:40]
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / f"scorecard_{timestamp}_{slug}.md"

    with open(output_file, "w") as f:
        f.write(f"# HomeScout Scorecard — {location}\n")
        f.write(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n")
        f.write(scorecard_text)

    print(f"\n✅ Scorecard saved to: {output_file}")


if __name__ == "__main__":
    main()
