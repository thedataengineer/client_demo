# Graph-driven test suite

These tests are generated from the Breeze graphs, not hand-listed. The
functional graph supplies the endpoint + persona inventory; the architecture
graph's RBAC and audit claims are what the tests assert; the gateway rule
(`gateway/main.py`) supplies the expected status per cell.

## How the graph drives it

```
frontend/ui_ep01_<persona>_item-management.json   (functional-graph payloads)
        │  action.apis[] = {method, url, persona}
        ▼
tests/build_matrix.py  ──>  tests/graph_matrix.json   (18 cells, 6 endpoints)
        │
        ▼
tests/test_rbac.py  (parametrized over every cell)
```

Add an endpoint/persona to the functional graph, re-run the UI pass, then
`python build_matrix.py` — the matrix and the RBAC tests grow with no edits.

## What is asserted

| File | Asserts | Graph source |
|---|---|---|
| `test_smoke.py` | reads (`/`, `/api/items`, `/api/audit`) open to all personas | functional graph (every persona's GET actions) |
| `test_rbac.py` | Viewer write→403, User DELETE→403, Admin all→200, reads→200 | matrix + gateway rule |
| `test_audit_trail.py` | create/update/delete emit INSERT/UPDATE/DELETE audit rows; blocked write emits none | architecture graph "Immutable Audit Trail" |

## Run

```bash
# 1. bring up the app
docker compose up -d --build

# 2. (re)build the matrix from the graph payloads
uv run --python 3.13 python tests/build_matrix.py

# 3. run
uv run --python 3.13 --with pytest --with httpx python -m pytest tests
# or, against a non-default host:
GATEWAY_URL=http://localhost:8080 python -m pytest tests
```

The `client` fixture waits up to 60s for the gateway; if it never comes up
the suite skips rather than fails.
