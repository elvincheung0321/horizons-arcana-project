from fetch_info import fetch_info


def get_descriptions(df):
    if df.empty or "properties.xid" not in df.columns:
        return []

    df = df.drop_duplicates(subset="properties.xid", keep="first")
    descriptions = []
    for xid in df["properties.xid"]:
        info = fetch_info(xid)
        text = info.get("wikipedia_extracts", {}).get("text", "No description available")
        descriptions.append(text)
    return descriptions
