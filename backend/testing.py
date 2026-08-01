import pandas as pd
from pathlib import Path

from fetch_places import fetch_places
from descriptions import get_places

station_name = "Orchard"
kinds_list = ["interesting_places", "shops", "foods", "amusements"]
kinds = kinds_list[0]

stations = pd.read_csv(Path(__file__).with_name("mrt_stations.csv"))
row = stations.loc[stations["name"] == station_name].iloc[0]
lon, lat = row["lon"], row["lat"]

df = fetch_places(lon, lat, kinds)
places = get_places(df)

if not places:
    print("No places found")
else:
    print(places)
    print(len(places))
