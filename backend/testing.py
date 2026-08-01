<<<<<<< HEAD
# backend/testing.py
import requests
from urllib.parse import urlencode
=======
>>>>>>> a77fc477a8dc87bca00c3c5dd8759b03c38a631e
import pandas as pd
from pathlib import Path

from fetch_places import fetch_places
from descriptions import get_descriptions

station_name = "Orchard" #user choice of station
kinds_list = ["shops", "foods", "amusements"]
kinds = kinds_list[1] #user choice of category

stations = pd.read_csv(Path(__file__).with_name("mrt_stations.csv"))
row = stations.loc[stations["name"] == station_name].iloc[0]
lon, lat = row["lon"], row["lat"]

df = fetch_places(lon, lat, kinds)

descriptions = get_descriptions(df)
if not descriptions:
    print("No places found")
else:
    print(descriptions)
    print(len(descriptions))


