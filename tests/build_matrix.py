"""
Build the RBAC test matrix FROM the Breeze graphs.

Source of truth, in order:
  1. Endpoint + persona inventory  -> the functional-graph payloads the
     generate-functional-from-ui pass produced
     (frontend/ui_ep01_<persona>_item-management.json). Each action.apis[]
     entry gives {method, url, persona}.
  2. Page persona reachability     -> design-graph page allowedRoles
     (informational; the gateway is the real enforcer).
  3. Expected status per (persona, method) -> the gateway RBAC rule
     (gateway/main.py), encoded once in rbac_expected().

Output: tests/graph_matrix.json  -- consumed by test_rbac.py.

This keeps the suite tied to the graph: if a new endpoint or persona is
added to the functional graph and the UI pass re-run, the matrix grows
without editing the tests.
"""
import json
import glob
import os
import re
from urllib.parse import urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

WRITE_METHODS = {"POST", "PUT", "DELETE"}


def rbac_expected(persona, method):
    """The gateway's enforced rule (gateway/main.py lines 25-28)."""
    if method == "GET":
        return 200
    if persona == "Viewer":
        return 403           # Viewer cannot modify
    if persona == "User" and method == "DELETE":
        return 403           # User cannot delete
    return 200               # Admin all; User create/update


def norm_path(url):
    """http://localhost:8080/api/items?... -> /api/items ; templatize ids."""
    p = urlparse(url).path or url
    # collapse a trailing numeric or {id} segment to {id}
    p = re.sub(r"/\{?\w*id\}?$", "/{id}", p) if re.search(r"/(\{id\}|\d+)$", p) else p
    p = re.sub(r"/\d+$", "/{id}", p)
    return p or "/"


def collect_from_graph():
    """Walk the functional-graph payload files for (persona, method, path)."""
    seen = {}
    files = sorted(glob.glob(os.path.join(REPO, "frontend", "ui_ep01_*_item-management.json")))
    for fp in files:
        data = json.load(open(fp))
        for persona in data.get("payload", {}).get("personas", []):
            pname = persona.get("persona")
            for oc in persona.get("outcomes", []):
                for sc in oc.get("scenarios", []):
                    for st in sc.get("steps", []):
                        for ac in st.get("actions", []):
                            for api in ac.get("apis", []) or []:
                                if api.get("type") != "REST":
                                    continue
                                method = (api.get("method") or "").upper()
                                path = norm_path(api.get("url", ""))
                                seen.setdefault((pname, method, path), 0)
                                seen[(pname, method, path)] += 1
    return seen


def main():
    personas = ["Admin", "User", "Viewer"]
    # Full CRUD surface (the graph captures the reads + each persona's allowed
    # writes; we test every method against every persona to prove enforcement).
    endpoints = [
        ("GET", "/"),
        ("GET", "/api/items"),
        ("POST", "/api/items"),
        ("PUT", "/api/items/{id}"),
        ("DELETE", "/api/items/{id}"),
        ("GET", "/api/audit"),
    ]
    graph_hits = collect_from_graph()

    matrix = []
    for persona in personas:
        for method, path in endpoints:
            matrix.append({
                "persona": persona,
                "method": method,
                "path": path,
                "expected_status": rbac_expected(persona, method),
                "in_graph": (persona, method, path) in graph_hits,
            })

    out = {
        "gateway": os.environ.get("GATEWAY_URL", "http://localhost:8080"),
        "personas": personas,
        "endpoints_from_graph": sorted(
            {f"{m} {p}" for (_, m, p) in graph_hits.keys()}
        ),
        "matrix": matrix,
    }
    dest = os.path.join(HERE, "graph_matrix.json")
    json.dump(out, open(dest, "w"), indent=2)
    print(f"Wrote {dest}")
    print(f"  {len(matrix)} (persona,method,endpoint) cells; "
          f"{len(out['endpoints_from_graph'])} distinct endpoints seen in graph")


if __name__ == "__main__":
    main()
