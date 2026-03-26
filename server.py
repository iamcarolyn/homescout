"""FastAPI SSE streaming endpoint for HomeScout."""
import json
import queue
import re
import threading
import time
from typing import Any, Generator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from crew import build_crew

app = FastAPI(title="HomeScout API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

TIMEOUT_SECONDS = 180
MAX_MESSAGE_LENGTH = 500


def truncate(text: str, max_len: int = MAX_MESSAGE_LENGTH) -> str:
    if len(text) > max_len:
        return text[:max_len] + "..."
    return text


def parse_scorecard(text: str) -> dict:
    """Extract score fields from Gavel's output via regex."""
    result = {}
    patterns = {
        "price_score": r"PRICE SCORE:\s*(\d+)/10\s*[—-]\s*(.+)",
        "school_score": r"SCHOOL SCORE:\s*(\d+)/10\s*[—-]\s*(.+)",
        "safety_score": r"SAFETY SCORE:\s*(\d+)/10\s*[—-]\s*(.+)",
        "lifestyle_score": r"LIFESTYLE SCORE:\s*(\d+)/10\s*[—-]\s*(.+)",
        "overall_verdict": r"OVERALL VERDICT:\s*(.+)",
        "summary": r"SUMMARY:\s*(.+(?:\n.+)*)",
    }
    for key, pattern in patterns.items():
        m = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if m:
            if key.endswith("_score") and key != "overall_verdict":
                result[key] = {"score": int(m.group(1)), "rationale": m.group(2).strip()}
            else:
                result[key] = m.group(1).strip()

    # Extract strengths and concerns
    strengths_m = re.search(r"KEY STRENGTHS:\s*\n((?:\s*[-•]\s*.+\n?)+)", text, re.IGNORECASE)
    if strengths_m:
        result["key_strengths"] = [
            line.strip().lstrip("-•").strip()
            for line in strengths_m.group(1).strip().splitlines()
            if line.strip()
        ]

    concerns_m = re.search(r"KEY CONCERNS:\s*\n((?:\s*[-•]\s*.+\n?)+)", text, re.IGNORECASE)
    if concerns_m:
        result["key_concerns"] = [
            line.strip().lstrip("-•").strip()
            for line in concerns_m.group(1).strip().splitlines()
            if line.strip()
        ]

    return result


def sse_event(data: dict) -> str:
    return f"data: {json.dumps(data)}\n\n"


AGENT_SEQUENCE = ["Brick", "Scholar", "Shield", "Vibe", "Gavel"]


def stream_crew(location: str, event_queue: queue.Queue) -> None:
    """Run crew in background thread, push events to queue."""
    final_output = {"text": ""}
    state = {"agent_index": 0}

    def current_agent() -> str:
        return AGENT_SEQUENCE[min(state["agent_index"], len(AGENT_SEQUENCE) - 1)]

    def step_callback(step_output: Any) -> None:
        try:
            if hasattr(step_output, "output"):
                message = truncate(str(step_output.output))
            elif hasattr(step_output, "thought"):
                message = truncate(str(step_output.thought))
            else:
                message = truncate(str(step_output))
            event_queue.put({"type": "step", "agent": current_agent(), "message": message})
        except Exception as e:
            event_queue.put({"type": "system", "agent": "System", "message": f"Step callback error: {e}"})

    def task_callback(task_output: Any) -> None:
        try:
            raw = getattr(task_output, "raw", str(task_output))
            final_output["text"] = str(raw)
            event_queue.put({"type": "task_complete", "agent": current_agent(), "message": "Task complete."})
            state["agent_index"] += 1
        except Exception as e:
            event_queue.put({"type": "system", "agent": "System", "message": f"Task callback error: {e}"})

    try:
        event_queue.put({"type": "system", "agent": "System", "message": f"Starting research for: {location}"})
        crew = build_crew(step_callback=step_callback, task_callback=task_callback)
        result = crew.kickoff(inputs={"location": location})
        scorecard_text = str(result)
        scorecard_dict = parse_scorecard(scorecard_text)
        event_queue.put({"type": "done", "scorecard": scorecard_dict, "raw": scorecard_text, "error": None})
    except Exception as e:
        event_queue.put({"type": "done", "scorecard": {}, "raw": "", "error": str(e)})
    finally:
        event_queue.put(None)  # sentinel


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/scout")
async def scout(request: Request) -> StreamingResponse:
    body = await request.json()
    location = body.get("location", "").strip()
    if not location:
        return StreamingResponse(
            iter([sse_event({"type": "done", "scorecard": {}, "error": "No location provided"})]),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    event_queue: queue.Queue = queue.Queue()
    thread = threading.Thread(target=stream_crew, args=(location, event_queue), daemon=True)
    thread.start()

    def generate() -> Generator[str, None, None]:
        deadline = time.time() + TIMEOUT_SECONDS
        while True:
            remaining = deadline - time.time()
            if remaining <= 0:
                yield sse_event({"type": "done", "scorecard": {}, "error": "Timeout after 180 seconds"})
                break
            try:
                event = event_queue.get(timeout=min(remaining, 5))
                if event is None:
                    break
                yield sse_event(event)
                if event.get("type") == "done":
                    break
            except queue.Empty:
                # heartbeat keep-alive
                yield ": keepalive\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
