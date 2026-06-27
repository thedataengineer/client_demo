"""
Shared fixtures. Targets the running gateway (docker-compose), default
http://localhost:8080, override with GATEWAY_URL.
"""
import os
import time
import uuid
import httpx
import pytest

GATEWAY_URL = os.environ.get("GATEWAY_URL", "http://localhost:8080")


def headers(persona):
    return {"X-Persona": persona, "Content-Type": "application/json"}


@pytest.fixture(scope="session")
def base_url():
    return GATEWAY_URL


@pytest.fixture(scope="session")
def client(base_url):
    with httpx.Client(base_url=base_url, timeout=10.0) as c:
        # wait for the gateway + downstream to come up
        deadline = time.time() + 60
        while time.time() < deadline:
            try:
                r = c.get("/", headers=headers("Admin"))
                if r.status_code == 200:
                    break
            except httpx.HTTPError:
                pass
            time.sleep(1)
        else:
            pytest.skip(f"gateway not reachable at {GATEWAY_URL}")
        yield c


@pytest.fixture
def make_item(client):
    """Create an item as Admin; return its dict. Track for cleanup."""
    created = []

    def _make(name=None, description="pytest fixture item"):
        name = name or f"itm-{uuid.uuid4().hex[:8]}"
        r = client.post(
            f"/api/items?name={name}&description={description}",
            headers=headers("Admin"),
        )
        assert r.status_code == 200, f"setup create failed: {r.status_code} {r.text}"
        item = r.json()
        created.append(item["id"])
        return item

    yield _make

    for item_id in created:
        try:
            client.delete(f"/api/items/{item_id}", headers=headers("Admin"))
        except httpx.HTTPError:
            pass
