import httpx
from app.config import get_settings

settings = get_settings()

HEADERS = {
    "apikey": settings.supabase_anon_key,
    "Authorization": f"Bearer {settings.supabase_anon_key}",
    "Content-Type": "application/json",
}


def _url(table: str) -> str:
    return f"{settings.supabase_url}/rest/v1/{table}"


def fetch_all_jerseys():
    with httpx.Client(timeout=10) as client:
        resp = client.get(_url("jerseys"), headers=HEADERS,
                          params={"select": "*"})
        resp.raise_for_status()
        return resp.json()


def search_jerseys(query: str):
    with httpx.Client(timeout=10) as client:
        resp = client.get(_url("jerseys"), headers=HEADERS, params={
                          "select": "*", "name": f"ilike.%{query}%"})
        resp.raise_for_status()
        return resp.json()


def fetch_shipping_batches():
    with httpx.Client(timeout=10) as client:
        # Fetch active batch first
        resp = client.get(_url("shipping_batches"), headers=HEADERS, params={
                          "is_active": "eq.true", "select": "*"})
        resp.raise_for_status()
        return resp.json()


def insert_handover(record: dict):
    headers = {**HEADERS, "Prefer": "return=representation"}
    with httpx.Client(timeout=10) as client:
        return client.post(_url("handover_requests"), headers=headers, json=record).json()
