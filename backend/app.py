from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from routing import find_along_route

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
ALLOWED_KINDS = {"interesting_places", "shops", "foods", "amusements"}

app = FastAPI(title="Horizons Arcana")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/route")
def route(
    from_station: str = Query(..., alias="from"),
    to_station: str = Query(..., alias="to"),
    kind: str = Query("interesting_places"),
    radius: int = Query(1000, ge=200, le=2000),
):
    if from_station == to_station:
        raise HTTPException(status_code=400, detail="From and to stations must differ")
    if kind not in ALLOWED_KINDS:
        raise HTTPException(
            status_code=400,
            detail=f"kind must be one of: {', '.join(sorted(ALLOWED_KINDS))}",
        )
    try:
        return find_along_route(from_station, to_station, kind, radius)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Upstream error: {exc}") from exc


app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
