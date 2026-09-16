from pathlib import Path
from typing import Dict

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from visualization.registry import FEED_DEFAULTS, plant_descriptor
from visualization.simulate import simulate

STATIC_DIR = Path(__file__).resolve().parent / "static"

app = FastAPI(title="TheShire plant UI", version="0.1.0")


class SimulateRequest(BaseModel):
    feed: Dict[str, float] = Field(default_factory=dict)
    parameters: Dict[str, Dict[str, float]] = Field(default_factory=dict)


@app.get("/api/plant")
def get_plant():
    return plant_descriptor()


@app.post("/api/simulate")
def run_simulate(payload: SimulateRequest):
    feed = {**FEED_DEFAULTS, **payload.feed}
    try:
        return simulate(feed, payload.parameters)
    except (TypeError, ValueError, KeyError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
