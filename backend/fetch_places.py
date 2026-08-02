import json
import time
from pathlib import Path
from urllib.parse import urlencode

import pandas as pd
import requests

from config import API_KEY

# #region agent log
_DEBUG_LOG = Path(__file__).resolve().parent.parent / ".cursor" / "debug-59b7ca.log"


def _dbg(hypothesis_id, location, message, data, run_id="pre-fix"):
    try:
        _DEBUG_LOG.parent.mkdir(parents=True, exist_ok=True)
        with _DEBUG_LOG.open("a", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {
                        "sessionId": "59b7ca",
                        "runId": run_id,
                        "hypothesisId": hypothesis_id,
                        "location": location,
                        "message": message,
                        "data": data,
                        "timestamp": int(time.time() * 1000),
                    }
                )
                + "\n"
            )
    except Exception:
        pass


# #endregion


def fetch_rate(lon, lat, kinds, rate, radius, retries=4):
    params = {
        "radius": radius,
        "lon": lon,
        "lat": lat,
        "kinds": kinds,
        "apikey": API_KEY,
        "rate": rate,
    }
    url = "https://api.opentripmap.com/0.1/en/places/radius?" + urlencode(params, safe=",")

    for attempt in range(retries):
        response = requests.get(url, timeout=20)
        # #region agent log
        _dbg(
            "F",
            "fetch_places.py:fetch_rate",
            "OTM radius response",
            {
                "status": response.status_code,
                "rate": rate,
                "attempt": attempt,
                "kinds": kinds,
            },
        )
        # #endregion
        if response.status_code == 429:
            time.sleep(0.6 * (attempt + 1))
            continue
        if response.status_code != 200:
            return pd.DataFrame()
        data = response.json()
        if isinstance(data, dict) and data.get("error"):
            return pd.DataFrame()
        features = data.get("features", [])
        if not features:
            return pd.DataFrame()
        return pd.json_normalize(features)

    # #region agent log
    _dbg(
        "F",
        "fetch_places.py:fetch_rate",
        "OTM radius exhausted retries",
        {"rate": rate, "kinds": kinds},
    )
    # #endregion
    return pd.DataFrame()


def fetch_places(lon, lat, kinds, radius=1000):
    # Single rate filter cuts API calls in half vs fetching 3h + 3 separately.
    df = fetch_rate(lon, lat, kinds, "3", radius)

    if df.empty or "properties.xid" not in df.columns:
        return pd.DataFrame()

    return df.drop_duplicates(subset="properties.xid", keep="first")
