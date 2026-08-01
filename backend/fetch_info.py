import threading
import time
from urllib.parse import urlencode

import requests

from config import API_KEY

_local = threading.local()


def _session():
    if not hasattr(_local, "session"):
        _local.session = requests.Session()
    return _local.session


def fetch_info(xid, retries=3):
    params = {"apikey": API_KEY}
    url = "http://api.opentripmap.com/0.1/en/places/xid/" + str(xid) + "?" + urlencode(params)

    for attempt in range(retries):
        try:
            response = _session().get(url, timeout=20)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and "error" not in data:
                    return data
            time.sleep(0.35 * (attempt + 1))
        except requests.RequestException:
            time.sleep(0.35 * (attempt + 1))

    return {}
