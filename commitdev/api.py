import requests
from commitdev.config import get_token

BASE_URL = "https://commitdev.name.ng/api"


def _headers():
    token_data = get_token()
    
    if not token_data:
        return {}
    
    access_token = token_data.get('access_token')
    
    if not access_token:
        return {}
    return {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }


def get(path: str):
    res = requests.get(f"{BASE_URL}{path}", headers=_headers())
    res.raise_for_status()
    return res.json()


def post(path: str, data=None):
    res = requests.post(f"{BASE_URL}{path}", json=data or {}, headers=_headers())
    res.raise_for_status()
    return res.json()