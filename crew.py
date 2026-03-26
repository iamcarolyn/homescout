from crewai import Crew, Process

from agents.brick import create_brick
from agents.scholar import create_scholar
from agents.shield import create_shield
from agents.vibe import create_vibe
from agents.gavel import create_gavel

from tasks.property_task import create_property_task
from tasks.school_task import create_school_task
from tasks.safety_task import create_safety_task
from tasks.lifestyle_task import create_lifestyle_task
from tasks.scorecard_task import create_scorecard_task


def build_crew(step_callback=None, task_callback=None) -> Crew:
    brick = create_brick()
    scholar = create_scholar()
    shield = create_shield()
    vibe = create_vibe()
    gavel = create_gavel()

    property_task = create_property_task(brick)
    school_task = create_school_task(scholar, context=[property_task])
    safety_task = create_safety_task(shield, context=[property_task, school_task])
    lifestyle_task = create_lifestyle_task(vibe, context=[property_task, school_task, safety_task])
    scorecard_task = create_scorecard_task(gavel, context=[property_task, school_task, safety_task, lifestyle_task])

    return Crew(
        agents=[brick, scholar, shield, vibe, gavel],
        tasks=[property_task, school_task, safety_task, lifestyle_task, scorecard_task],
        process=Process.sequential,
        verbose=True,
        step_callback=step_callback,
        task_callback=task_callback,
    )
