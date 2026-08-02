# SG In Between

Pick two Singapore MRT stations and discover places along the route

## Stack

- **Backend:** FastAPI(Python),OneMap for rail route finding, OpenTripMap for finding places with coordinates
- **Frontend:** HTML/CSS/JS with Leaflet for the map

## Setup

1. Get API keys:
   - [OneMap](https://www.onemap.gov.sg/apidocs/) — OneMap API Key
   - [OpenTripMap](https://dev.opentripmap.org/docs) — OpenTripMap API Key

2. Configure the backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

```
***Get your own OneMap and OpenTripMap API keys and set them in your environment or hardcode them in the config.py***

## Run locally

In `backend/`:

```bash
export OPENTRIPMAP_API_KEY=...
export ONEMAP_TOKEN=...
uvicorn app:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000).

## API
- Used OneMap and OpenTripMap


| Params    | Notes                                              |
|----------|----------------------------------------------------|
| `from`   | Start station name                                 |
| `to`     | End station name (must be different from `from`)         |
| `kind`   | `interesting_places`, `shops`, `foods`, `amusements` (amusements aren't very common in singapore finding no places is normal)|
| `radius` | Search radius in meters (200–2000, default 1000) (basically how far you want to walk)  |

## Deploy

We use Render, a free cloud hosting website to deploy this onto a website

