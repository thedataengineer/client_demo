"""
Audit trail: the architecture graph's "Immutable Audit Trail" node claims
every items mutation is captured by a DB trigger and surfaced via
GET /api/audit. These tests prove it end-to-end through the gateway.
"""
import uuid
from conftest import headers


def _audit_rows(client):
    r = client.get("/api/audit", headers=headers("Admin"))
    assert r.status_code == 200
    return r.json()


def _has(rows, action, record_id):
    return any(
        row.get("action") == action and row.get("record_id") == record_id
        for row in rows
    )


def test_create_emits_insert_audit(client):
    name = f"aud-{uuid.uuid4().hex[:8]}"
    item = client.post(
        f"/api/items?name={name}&description=audit", headers=headers("Admin")
    ).json()
    rows = _audit_rows(client)
    assert _has(rows, "INSERT", item["id"]), "no INSERT audit row for created item"
    client.delete(f"/api/items/{item['id']}", headers=headers("Admin"))


def test_update_emits_update_audit(client, make_item):
    item = make_item()
    client.put(f"/api/items/{item['id']}?completed=true", headers=headers("Admin"))
    rows = _audit_rows(client)
    assert _has(rows, "UPDATE", item["id"]), "no UPDATE audit row for toggled item"


def test_delete_emits_delete_audit(client):
    name = f"aud-{uuid.uuid4().hex[:8]}"
    item = client.post(
        f"/api/items?name={name}&description=audit", headers=headers("Admin")
    ).json()
    client.delete(f"/api/items/{item['id']}", headers=headers("Admin"))
    rows = _audit_rows(client)
    assert _has(rows, "DELETE", item["id"]), "no DELETE audit row for removed item"


def test_denied_write_creates_no_audit(client, make_item):
    """A Viewer POST is blocked at the gateway (403) -> no audit row, no item."""
    before = len(_audit_rows(client))
    name = f"deny-{uuid.uuid4().hex[:8]}"
    r = client.post(f"/api/items?name={name}&description=x", headers=headers("Viewer"))
    assert r.status_code == 403
    after = len(_audit_rows(client))
    assert after == before, "blocked write must not produce an audit row"
