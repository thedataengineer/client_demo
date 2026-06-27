"""
RBAC enforcement, driven by tests/graph_matrix.json (built by build_matrix.py
from the functional graph + the gateway rule).

Every (persona, method, endpoint) cell asserts the gateway returns the
expected status. Writes use a freshly-created item so allowed deletes/updates
operate on a real row and denied ones (403) leave it intact.
"""
import json
import os
import uuid
import pytest
from conftest import headers

HERE = os.path.dirname(os.path.abspath(__file__))
MATRIX = json.load(open(os.path.join(HERE, "graph_matrix.json")))["matrix"]


def _id(cell):
    return f"{cell['persona']}-{cell['method']}-{cell['path']}"


@pytest.mark.parametrize("cell", MATRIX, ids=[_id(c) for c in MATRIX])
def test_rbac_cell(client, make_item, cell):
    persona, method, path = cell["persona"], cell["method"], cell["path"]
    expected = cell["expected_status"]
    h = headers(persona)

    if method == "GET":
        r = client.get(path, headers=h)

    elif method == "POST":
        name = f"rbac-{uuid.uuid4().hex[:8]}"
        r = client.post(f"/api/items?name={name}&description=rbac", headers=h)
        if r.status_code == 200:                       # clean up allowed creates
            client.delete(f"/api/items/{r.json()['id']}", headers=headers("Admin"))

    elif method == "PUT":
        item = make_item()
        r = client.put(f"/api/items/{item['id']}?completed=true", headers=h)

    elif method == "DELETE":
        item = make_item()
        r = client.delete(f"/api/items/{item['id']}", headers=h)

    assert r.status_code == expected, (
        f"{persona} {method} {path} -> {r.status_code}, expected {expected}: {r.text}"
    )


def test_every_graph_endpoint_is_covered():
    """Guard: the graph's endpoint inventory is fully represented in the matrix."""
    data = json.load(open(os.path.join(HERE, "graph_matrix.json")))
    covered = {f"{c['method']} {c['path']}" for c in data["matrix"]}
    for ep in data["endpoints_from_graph"]:
        assert ep in covered, f"graph endpoint {ep} missing from test matrix"
