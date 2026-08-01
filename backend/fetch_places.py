import requests
from urllib.parse import urlencode
import pandas as pd

from config import API_KEY


def fetch_rate(lon, lat, kinds, rate, radius):
    params = {
        "radius": radius,
        "lon": lon,
        "lat": lat,
        "kinds": kinds,
        "apikey": API_KEY,
        "rate": rate,
    }
    url = "http://api.opentripmap.com/0.1/en/places/radius?" + urlencode(params, safe=",")
    data = requests.get(url).json()
    features = data.get("features", [])
    if not features:
        return pd.DataFrame()
    return pd.json_normalize(features)


def fetch_places(lon, lat, kinds, radius=1000):
    df_heritage = fetch_rate(lon, lat, kinds, "3h", radius)
    df_other = fetch_rate(lon, lat, kinds, "3", radius)
    df = pd.concat([df_heritage, df_other], ignore_index=True)

    if df.empty or "properties.xid" not in df.columns:
        return pd.DataFrame()

    return df.drop_duplicates(subset="properties.xid", keep="first")
