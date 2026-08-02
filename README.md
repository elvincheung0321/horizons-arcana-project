# SG In Between

Pick two Singapore MRT stations and discover places along the route — interesting spots, shops, food, or amusements.

## Stack

- **Backend:** FastAPI(Python),OneMap for rail route finding, OpenTripMap for finding places with cords
- **Frontend:** HTML/CSS/JS with Leaflet

## Setup

1. Get API keys:
   - [OneMap](https://www.onemap.gov.sg/apidocs/) — ONEMAP_TOKEN
   - [OpenTripMap](https://dev.opentripmap.org/docs) — `OPENTRIPMAP_API_KEY`

2. Configure the backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp config.example.py config.py

```
***Get your own OneMap and OpenTripMap API keys and set them in your environment or hardcode them in the copied config.py***

Example `config.py`:

```python
API_KEY = os.environ["OPENTRIPMAP_API_KEY"]
ONEMAP_TOKEN = os.environ["ONEMAP_TOKEN"]
```

## Run locally

In `backend/`:

```bash
export OPENTRIPMAP_API_KEY=...
export ONEMAP_TOKEN=...
uvicorn app:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000).

## API



| Param    | Notes                                              |
|----------|----------------------------------------------------|
| `from`   | Start station name                                 |
| `to`     | End station name (must differ from `from`)         |
| `kind`   | `interesting_places`, `shops`, `foods`, `amusements` |
| `radius` | Search radius in metres (200–2000, default 1000)   |

## Deploy

We use Render, a free cloud hosting website to deploy this onto a website

