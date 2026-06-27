# Demo setup and query cheat sheet

Read this once. The four demo scripts assume the environment below is live and
that you can run Breeze graph queries from the Breeze chat.

## The app under demo

`KCE_Demo_Rebuild` is a small item-tracker, deliberately rebuilt to carry the
patterns enterprises actually argue about: an API gateway, an extracted audit
microservice, role enforcement, and a database-trigger audit trail. Small enough
to read in one sitting, structured enough that the graphs have something real to
say.

| Layer | Path | What it is |
|---|---|---|
| Frontend | `frontend/` | React SPA, persona selector, item CRUD, audit view |
| Gateway | `gateway/main.py` | Single entry point. RBAC + strangler-fig routing |
| Backend | `backend/` | FastAPI, n-tier (routes → service → repository), items CRUD |
| Audit service | `backend-audit/` | Extracted microservice, read side of the audit log |
| Database | Postgres | `items` table + `audit_logs`, populated by `audit_trigger_func` |
| Tests | `tests/` | Graph-driven suite: the matrix is built FROM the graph |

Bring it up and confirm green before any demo:

```bash
docker compose up -d --build
uv run --python 3.13 python tests/build_matrix.py
GATEWAY_URL=http://localhost:8080 \
  uv run --python 3.13 --with pytest --with httpx python -m pytest tests -q
# expect: 34 passed
```

If `/api/audit` returns 502, the `audit` container is down. `docker compose up -d audit`.

## The four Breeze graphs and what each answers

| Graph | Answers | Primary tools |
|---|---|---|
| Functional | What does the system do, for whom, through which API | `Get_complete_functional_graph`, `Functional_Graph_Search`, `Get_all_personas` |
| Design | What UI components exist and how they nest | `Design_Graph_Search`, `Get_all_Design_By_Label` |
| Architecture | How services, routes, and data stores connect | `Get_All_architecture_Graph`, `Get_Architecture_Nodes_By_Label` |
| Code | Where is X implemented, what calls Y | `Code_Graph_Search`, `Get_Code_File_Details` |

Project handle for every query: `KCE_Demo_Rebuild`, uuid
`9b021702-0353-4075-8dd8-c6a9c04e84da`.

## Current functional graph at a glance

Two personas, four outcomes, nine APIs. Memorize this; it is the spine of three
of the four demos.

- **User** → Manage Items → {Add, Browse, Update completion, Remove}
- **System** → Monitor System Audit Activity → Retrieve audit log entries
- **System** → Manage Items → {Create, List, Update, Delete} with trigger-based audit
- **System** → Monitor System Health → health probe

APIs: `GET /`, `GET /api/items`, `POST /api/items`, `PUT /api/items/{id}`,
`DELETE /api/items/{id}`, `GET /api/audit`.

## Three lines that sell every demo

1. The graph is generated from the code, not hand-written, so it does not drift.
2. Every claim on screen is a node you can click to the exact file and line.
3. The test suite is built from the same graph, so "documented" and "verified"
   are the same artifact.
