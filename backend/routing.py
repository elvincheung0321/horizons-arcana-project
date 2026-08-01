from datetime import datetime
from pathlib import Path

import pandas as pd
import requests

from config import ONEMAP_TOKEN
from fetch_places import fetch_places
from descriptions import get_places


FROM_STATION = "Orchard"
TO_STATION = "Bugis"
KIND = "foods"
RADIUS = 1000


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


def find_along_route(from_station, to_station, kind="foods", radius=1000):
    stations = load_stations()

    if from_station not in set(stations["name"]) or to_station not in set(stations["name"]):
        raise ValueError("Unknown station name")

    start_lat, start_lon = station_coords(stations, from_station)
    end_lat, end_lon = station_coords(stations, to_station)

    onemap_stops = route_rail_stops(ONEMAP_TOKEN, start_lat, start_lon, end_lat, end_lon)

    matched_stops = []
    places = []
    seen_xids = set()

    for raw_name in onemap_stops:
        csv_name = match_csv_station(stations, raw_name)
        if not csv_name:
            continue

        matched_stops.append(csv_name)
        lat, lon = station_coords(stations, csv_name)
        df = fetch_places(lon, lat, kind, radius=radius)
        for place in get_places(df):
            if place["xid"] in seen_xids:
                continue
            seen_xids.add(place["xid"])
            places.append({**place, "station": csv_name})

    return {
        "from": from_station,
        "to": to_station,
        "kind": kind,
        "radius": radius,
        "stops": matched_stops,
        "places": places,
    }


def main():
    result = find_along_route(FROM_STATION, TO_STATION, KIND, RADIUS)
    print(f"Routing {result['from']} → {result['to']} ({result['kind']})")
    print("Stops:", result["stops"])
    print(f"Total places: {len(result['places'])}")
    for place in result["places"]:
        print(f"\n[{place['station']}] {place['name']}")
        print(place["description"])


if __name__ == "__main__":
    main()
