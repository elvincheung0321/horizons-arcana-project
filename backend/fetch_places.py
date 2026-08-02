import time
from urllib.parse import urlencode

import pandas as pd
import requests

from config import API_KEY


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

    return pd.DataFrame()


def fetch_places(lon, lat, kinds, radius=1000):
    #duplicates removed
    df = fetch_rate(lon, lat, kinds, "3", radius)

    if df.empty or "properties.xid" not in df.columns:
        return pd.DataFrame()

    df = df.drop_duplicates(subset="properties.xid", keep="first")


    if "properties.name" in df.columns:
        name_key = (
            df["properties.name"]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.casefold()
        )
        keep = (name_key == "") | ~name_key.duplicated(keep="first")
        df = df.loc[keep].reset_index(drop=True)

    return df
