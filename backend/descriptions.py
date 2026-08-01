from fetch_info import fetch_info


def get_places(df):
    if df.empty or "properties.xid" not in df.columns:
        return []

    df = df.drop_duplicates(subset="properties.xid", keep="first")
    places = []
    for xid in df["properties.xid"]:
        info = fetch_info(xid)
        places.append(
            {
                "xid": xid,
                "name": info.get("name") or "Unknown",
                "description": info.get("wikipedia_extracts", {}).get(
                    "text", "No description available"
                ),
                "kinds": info.get("kinds", ""),
            }
        )
    return places
