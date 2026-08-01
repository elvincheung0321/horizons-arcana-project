# backend/testing.py
import requests
from urllib.parse import urlencode
import pandas as pd
import os

lon = 103.835899
lat = 1.300946

base_params = {
    "radius": 1000,
    "lon": lon,
    "lat": lat,
    "kinds": "tourist_facilities,",
    "apikey": "5ae2e3f221c38a28845f05b6828bfeb528f61464302b6ce912c6006e",
}


def fetch_places(rate):
    params = {**base_params, "rate": rate}
    url = "http://api.opentripmap.com/0.1/en/places/radius?" + urlencode(params, safe=",")
    data = requests.get(url).json()
    return pd.json_normalize(data["features"])

df_heritage = fetch_places("3h")
df_other = fetch_places("3")

df = pd.concat([df_heritage, df_other], ignore_index=True)
df = df.drop_duplicates(subset="properties.xid", keep="first")
list = []
for feature in df["properties.name"]:
    list.append(feature)

print(list)
print(len(list))
