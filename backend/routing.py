from datetime import datetime
from pathlib import Path

import pandas as pd
import requests

from config import ONEMAP_TOKEN
from fetch_places import fetch_places
from descriptions import get_descriptions


FROM_STATION = "Orchard" #user choice of station
TO_STATION = "Bugis" #user choice of station
KIND = "foods"  #user choice of category


def load_stations():
    return pd.read_csv(Path(__file__).with_name("mrt_stations.csv"))


def station_coords(stations, name):
    row = stations.loc[stations["name"] == name].iloc[0]
    return float(row["lat"]), float(row["lon"])


def route_rail_stops(token, start_lat, start_lon, end_lat, end_lon):
    now = datetime.now()
    params = {
        "start": f"{start_lat},{start_lon}",
        "end": f"{end_lat},{end_lon}",
        "routeType": "pt",
        "mode": "rail",
        "date": now.strftime("%m-%d-%Y"),
        "time": now.strftime("%H:%M:%S"),
        "numItineraries": 1,
    }
    url = "https://www.onemap.gov.sg/api/public/routingsvc/route"
    response = requests.get(
        url,
        params=params,
        headers={"Authorization": token},
    )

    data = response.json()

    stops = []
    itineraries = data.get("plan", {}).get("itineraries", [])
    if not itineraries:
        return stops

    for leg in itineraries[0].get("legs", []):
        if leg.get("mode") not in ("SUBWAY", "RAIL", "TRAM"):
            continue

        _from = leg.get("from", {}).get("name")
        if _from and (not stops or stops[-1] != _from):
            stops.append(_from)

        for mid in leg.get("intermediateStops") or []:
            name = mid.get("name")
            if name and (not stops or stops[-1] != name):
                stops.append(name)

        to = leg.get("to", {}).get("name")
        if to and (not stops or stops[-1] != to):
            stops.append(to)

    return stops


def match_csv_station(stations, onemap_name):
    cleaned = (
        onemap_name.upper()
        .replace(" MRT STATION", "")
        .replace(" LRT STATION", "")
        .strip()
    )
    for name in stations["name"]:
        if name.upper() == cleaned or name.upper().replace("-", " ") == cleaned.replace("-", " "):
            return name
    return None


def main():

    stations = load_stations()

    start_lat, start_lon = station_coords(stations, FROM_STATION)
    end_lat, end_lon = station_coords(stations, TO_STATION)

    print(f"Routing {FROM_STATION} → {TO_STATION} ({KIND})")

    onemap_stops = route_rail_stops(ONEMAP_TOKEN, start_lat, start_lon, end_lat, end_lon)
    print("OneMap stops:", onemap_stops)

    all_descriptions = []
    for raw_name in onemap_stops:
        csv_name = match_csv_station(stations, raw_name)
        if not csv_name:
            print(f"  skip (not in CSV): {raw_name}")
            continue

        lat, lon = station_coords(stations, csv_name)
        df = fetch_places(lon, lat, KIND)
        descriptions = get_descriptions(df)
        print(f"\n{csv_name}: {len(descriptions)} places")
        all_descriptions.extend(descriptions)

    print(f"\nTotal attraction blurbs: {len(all_descriptions)}")


if __name__ == "__main__":
    main()
