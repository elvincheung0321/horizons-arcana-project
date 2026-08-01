from concurrent.futures import ThreadPoolExecutor, as_completed

from fetch_info import fetch_info

MAX_WORKERS = 6


def _from_info(xid, info, fallback_name=""):
    if not isinstance(info, dict):
        info = {}
    extracts = info.get("wikipedia_extracts") or {}
    text = extracts.get("text") if isinstance(extracts, dict) else None
    return {
        "xid": xid,
        "name": info.get("name") or fallback_name or "Unknown",
        "description": text or "No description available",
        "kinds": info.get("kinds", ""),
    }


def get_places(df):
    if df.empty or "properties.xid" not in df.columns:
        return []

    rows = df.drop_duplicates(subset="properties.xid", keep="first")
    records = []
    for _, row in rows.iterrows():
        xid = row["properties.xid"]
        fallback = ""
        if "properties.name" in rows.columns:
            raw = row["properties.name"]
            if isinstance(raw, str) and raw.strip():
                fallback = raw.strip()
        records.append((xid, fallback))

    return enrich_places(records)


def enrich_places(records):
    if not records:
        return []

    by_xid = {}
    workers = min(MAX_WORKERS, len(records))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(fetch_info, xid): (xid, fallback)
            for xid, fallback in records
        }
        for fut in as_completed(futures):
            xid, fallback = futures[fut]
            try:
                info = fut.result()
            except Exception:
                info = {}
            by_xid[xid] = _from_info(xid, info, fallback)

    return [by_xid[xid] for xid, _ in records]
