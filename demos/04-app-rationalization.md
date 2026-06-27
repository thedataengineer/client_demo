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

**Setup.** `KCE_Demo_Rebuild` is app A. App B is an adjacent item-tracker already
onboarded to Breeze (call it `KCE_Adjacent_Tracker`). If you do not have a second
project staged, the appendix shows how to stand one up in minutes from the same
codebase with the audit capability removed, so the diff has something to show.

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
Get_complete_functional_graph(KCE_Demo_Rebuild)        # app A
Get_complete_functional_graph(KCE_Adjacent_Tracker)    # app B
```

Lay the outcomes side by side:

| Capability | App A (KCE_Demo_Rebuild) | App B (Adjacent) |
|---|---|---|
| Manage Items (CRUD) | Yes, 4 endpoints | Yes, near-identical |
| Item completion toggle | Yes | Yes |
| Audit trail (`GET /api/audit`) | Yes, trigger-based | No |
| Role enforcement at gateway | Yes | Partial or none |
| Health probe | Yes | Yes |

The overlap is the top rows: CRUD and completion are duplicated capability. The
differentiators are audit and RBAC, and they live in app A. That table is the
rationalization case, and every cell links to the scenario that backs it.

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
Get_complete_functional_graph(KCE_Adjacent_Tracker)
Design_Graph_Search("...", KCE_Adjacent_Tracker)
Code_Graph_Search("...", KCE_Adjacent_Tracker)
```

Every persona, endpoint, component, and file unique to B is a line item to migrate
or knowingly drop. The graph turns "we think B is mostly redundant" into "B has N
endpoints, M of them duplicated in A, K unique; here are the K." The K is the only
real work in the cutover, and now it is enumerated.

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

- **Duplicated capability** (CRUD, completion): consolidate onto A, retire in B.
- **Unique to A** (audit, RBAC): the reason A is the survivor.
- **Unique to B** (the K endpoints): migrate or explicitly accept the loss. This
  is the only line item that costs real engineering.

## The risk to name

Graph overlap proves functional duplication, not data duplication. Two apps that
do the same thing may hold different data with different retention or compliance
rules. Retire the app, but migrate or archive its data on purpose; the functional
graph does not see what the data obligations are.

---

## Appendix: stand up the adjacent app for the demo

If you need app B staged, clone this repo to a second Breeze project and remove
the audit capability so the diff is real:

1. Create the project: `Call_Create_Project_(name="KCE_Adjacent_Tracker")`.
2. Point a copy of the codebase at it with `backend-audit/` and the
   `/api/audit` gateway route removed, plus the audit trigger dropped from the DB
   init.
3. Run the functional and design passes against the trimmed codebase so B's graph
   genuinely lacks the audit outcome and the `AuditLogList` component.

Now Beat 2's table is generated, not staged, and the overlap diff is live.
