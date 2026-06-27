"""
Smoke: the read endpoints the functional graph says every persona can reach.
"""
import pytest
from conftest import headers

READ_ENDPOINTS = ["/", "/api/items", "/api/audit"]
PERSONAS = ["Admin", "User", "Viewer"]


@pytest.mark.parametrize("persona", PERSONAS)
@pytest.mark.parametrize("path", READ_ENDPOINTS)
def test_reads_open_to_all_personas(client, persona, path):
    r = client.get(path, headers=headers(persona))
    assert r.status_code == 200, f"{persona} GET {path} -> {r.status_code}"


def test_health_message(client):
    r = client.get("/", headers=headers("Admin"))
    body = r.json()
    assert "message" in body


def test_items_and_audit_are_lists(client):
    assert isinstance(client.get("/api/items", headers=headers("Admin")).json(), list)
    assert isinstance(client.get("/api/audit", headers=headers("Admin")).json(), list)
