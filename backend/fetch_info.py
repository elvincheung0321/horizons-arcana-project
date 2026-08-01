import requests
from urllib.parse import urlencode

from config import API_KEY


def fetch_info(xid):
    params = {"apikey": API_KEY}
    url = "http://api.opentripmap.com/0.1/en/places/xid/" + xid + "?" + urlencode(params)
    return requests.get(url).json()
