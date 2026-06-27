# Demo 4: Application rationalization with an adjacent app

**Scenario.** Two teams built two apps that do most of the same thing. After a
merger, a reorg, or just a decade of drift, the portfolio has overlap nobody can
quantify. Leadership wants to consolidate or retire one, but the rationalization
deck is built on interviews and gut feel, so the recommendation never survives the
first hard question: "how much actually overlaps."

**Claim to prove.** Put two apps' graphs side by side and the overlap is a
measured set, not an opinion. You can say which capabilities duplicate, which are
unique, what a consolidation target looks like, and what retirement actually
removes.

**Setup.** Both apps are live in Breeze.

- **App A** — `KCE_Demo_Rebuild`, uuid `9b021702-0353-4075-8dd8-c6a9c04e84da`.
- **App B** — `KCE_Adjacent_Tracker`, uuid `574c1cee-21d0-4d9f-8d3f-2b531902b1e7`.
  Codebase at `../kce-adjacent-tracker` (ports 8001 / 5174 / 5433). It is a real
  trim of app A: item CRUD only, no gateway, no RBAC, no audit. The appendix
  records how it was built if you need to rebuild it.

**Audience.** Portfolio owners, enterprise architects, the CFO's technical proxy
who signs off on retiring an app. **Run time.** 15 minutes.

---

## Beat 1: The portfolio, as data (2 min)

```
Call_List_Project_()
```

Two projects appear that both claim item management. The room already suspects
overlap. The graph is about to turn the suspicion into a number.

## Beat 2: Capability overlap, measured (4 min)

Pull both functional graphs and compare outcomes and APIs:

```
Get_complete_functional_graph(uuid="9b021702-0353-4075-8dd8-c6a9c04e84da")   # app A
Get_complete_functional_graph(uuid="574c1cee-21d0-4d9f-8d3f-2b531902b1e7")   # app B
```

The summary blocks alone make the case before you read a single scenario:

- **App A** — 4 personas (Admin, User, Viewer, System), 7 outcomes, 6 endpoints
  including `GET /api/audit`.
- **App B** — 2 personas (System, User), 3 outcomes, 5 endpoints, no audit.

Lay the outcomes side by side:

| Capability | App A (`KCE_Demo_Rebuild`) | App B (`KCE_Adjacent_Tracker`) |
|---|---|---|
| Manage Items (CRUD) | Yes, 4 endpoints | Yes, identical 4 endpoints |
| Item completion toggle | Yes | Yes |
| Health probe (`GET /`) | Yes | Yes |
| Audit trail (`GET /api/audit`, "Monitor System Audit Activity") | Yes, trigger-based | **No outcome, no endpoint** |
| Role enforcement (Admin / User / Viewer personas) | Yes, gateway-enforced | **No, single open User persona** |

The overlap is the top three rows: CRUD, completion, and health are duplicated
capability. The differentiators are the bottom two, audit and RBAC, and they exist
only in app A. That table is the rationalization case, and every cell links to the
scenario that backs it. The "No" cells are provable absences: B's graph has no
`Monitor System Audit Activity` outcome and no `Admin`/`Viewer` persona.

## Beat 3: Which app is the consolidation target (3 min)

The graph answers it by capability superset, not by which team shouts loudest.
App A is a strict superset: it does everything B does, plus audit and role
enforcement, behind a gateway that already abstracts routing. Consolidating onto
A and retiring B means you keep the audited, access-controlled path and lose
nothing B had.

Show the architecture graph to make the "A absorbs B" claim concrete:

```
Get_All_architecture_Graph(KCE_Demo_Rebuild)
```

B's traffic terminates at the same gateway contract A already exposes. There is no
new integration surface to build, only a cutover.

## Beat 4: What retirement actually removes (3 min)

Rationalization decks routinely undercount what dies with an app. Use B's graph as
the demolition checklist:

```
Get_complete_functional_graph(uuid="574c1cee-21d0-4d9f-8d3f-2b531902b1e7")
```

Every persona, endpoint, component, and file unique to B is a line item to migrate
or knowingly drop. For this pair the math is small and exact: B has 5 endpoints,
all 5 duplicated in A, 0 unique. K = 0. Retiring B removes no capability A does not
already cover, so the cutover is pure decommission, not migration. That is the
strongest rationalization verdict you can hand a CFO: the redundant app costs
money and adds nothing the survivor lacks.

## Beat 5: Prove the survivor still holds (2 min)

Before recommending retirement, prove app A carries the merged load without
regression:

```bash
GATEWAY_URL=http://localhost:8080 \
  uv run --python 3.13 --with pytest --with httpx python -m pytest tests -q
```

A's graph-driven suite is green, so the consolidation target is verified, not
assumed. You are recommending retirement of B onto a survivor whose behavior is
under test.

---

## The payoff line

Rationalization stops being a slide of opinions and becomes a set operation:
overlap is measured, the consolidation target is the capability superset, and the
cutover work is the small unique remainder the graph enumerates. The CFO gets a
number, not a narrative.

## The decision framing to leave on screen

- **Duplicated capability** (CRUD, completion, health): consolidate onto A, retire
  in B.
- **Unique to A** (audit, RBAC): the reason A is the survivor.
- **Unique to B**: none (K = 0). Retiring B is a clean decommission with no
  migration line item.

## The risk to name

Graph overlap proves functional duplication, not data duplication. Two apps that
do the same thing may hold different data with different retention or compliance
rules. Retire the app, but migrate or archive its data on purpose; the functional
graph does not see what the data obligations are.

---

## Appendix: how app B was built (for rebuild / reference)

App B already exists as Breeze project `KCE_Adjacent_Tracker`
(`574c1cee-21d0-4d9f-8d3f-2b531902b1e7`), codebase at `../kce-adjacent-tracker`.
It was produced by trimming app A:

1. **Codebase** — copied `backend/` and `frontend/` minus the audit surface:
   removed the audit model/repository/service/schema, dropped the
   `audit_trigger_func` trigger from `database.py`, deleted the persona selector
   and audit-log panel from `App.jsx`, and pointed the frontend straight at the
   backend (no gateway). Runs on shifted ports (8001 / 5174 / 5433) so it can sit
   beside app A.
2. **Project** — created via `Call_Create_Project_(name="KCE_Adjacent_Tracker")`;
   uuid saved to `../kce-adjacent-tracker/.breeze.json`.
3. **Functional graph** — authored the System (backend) and User (UI) subtrees
   from the trimmed code and upserted to `/functional-graph/v2/upsert`. Result:
   2 personas, 3 outcomes, 9 scenarios, 10 APIs, and no audit outcome or
   `/api/audit` endpoint, which is what makes Beat 2's diff real.

Verify any time:

```
Get_complete_functional_graph(uuid="574c1cee-21d0-4d9f-8d3f-2b531902b1e7")
```

Optional follow-up if a demo wants the UI-component diff in Beat 4 to be live as
well: run the design pass against `../kce-adjacent-tracker` so B's design graph
carries the item components but not `PersonaSelector`, `AuditLogEntry`, or
`AuditLogList`. The functional diff above already carries the rationalization
verdict without it.
