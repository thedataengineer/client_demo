# Demo 1: Knowledge transition

**Scenario.** The engineer who built this system is leaving in two weeks, or the
work is moving to a team that has never seen the code. There is no current
design doc. The usual outcome: weeks of shoulder-surfing, a wiki that is stale
the day it ships, and a six-month period where the new team is afraid to touch
anything.

**Claim to prove.** A new owner can answer "what does this system do, how, and
where" from the graph in an afternoon, and every answer links to the exact code.
The departing expert reviews answers instead of dictating them.

**Audience.** Engineering managers, delivery leads, anyone who has paid the cost
of a bad handover. **Run time.** 12 to 15 minutes.

---

## Beat 1: The problem, stated in their terms (2 min)

Open `backend/app/api/routes.py` and `gateway/main.py` side by side. Point out
that nothing here tells you the role rules, the audit guarantee, or why there are
two backend services. That knowledge lives in one person's head. Ask the room
what their last handover cost in weeks. Hold that number.

## Beat 2: What does it do, for whom (3 min)

Run against the functional graph:

```
Get_all_personas(KCE_Demo_Rebuild)
Get_complete_functional_graph(KCE_Demo_Rebuild)
```

On screen: two personas, four outcomes, ten scenarios, nine APIs. Read one
scenario aloud, "Update an item's completion status," and note it already
captures the 404-on-missing branch and the trigger-based audit write. That is
behavior a new hire would otherwise discover by breaking production.

The point to land: this is not a diagram someone drew. It was generated from the
code, so it is current by construction.

## Beat 3: Where is it implemented (3 min)

A new owner's first real question is always "where is the code for this." Go from
a functional node straight to the source:

```
Code_Graph_Search("create_item item creation persist audit", KCE_Demo_Rebuild)
Get_Code_File_Details("backend/app/services/item_service.py")
```

Trace the chain the graph shows: route → `ItemService.create_item` →
`ItemRepository.create` → commit → Postgres trigger writes `audit_logs`. The new
engineer just learned the n-tier convention without anyone explaining it.

## Beat 4: How do the pieces connect (3 min)

```
Get_All_architecture_Graph(KCE_Demo_Rebuild)
```

The gateway fronts two services and enforces roles before routing. `/api/audit`
goes to the extracted audit service; everything else to the backend. This is the
"why are there two services" answer that normally takes a whiteboard session with
the person who is leaving.

## Beat 5: The UI surface (2 min)

```
Design_Graph_Search("item row audit log persona selector", KCE_Demo_Rebuild)
```

Atoms up to template: `DeleteButton`, `StatusBadge`, `ItemRow`, `ItemList`,
`AuditLogList`, `DashboardLayout`. A front-end hire now knows the component
inventory and the nesting before opening a `.tsx` file.

## Beat 6: Prove the knowledge is correct, not just written (2 min)

```bash
GATEWAY_URL=http://localhost:8080 \
  uv run --python 3.13 --with pytest --with httpx python -m pytest tests -q
```

34 passing tests, generated from the same graph the new owner just read. The
handover artifact and the verification artifact are the same thing. A wiki cannot
make that claim.

---

## The payoff line

Handover stops being a transfer from a person and becomes a query against a
system. The expert's two weeks go to reviewing graph answers and correcting the
few that are wrong, not to narrating the whole system from memory.

## What the graph removed

- The "only Dave knows why" single point of failure.
- The stale-wiki tax: the graph regenerates from code, so it does not rot.
- The fear period: a new owner can check impact before touching anything, which
  is exactly Demo 3.

## If asked "what about tribal knowledge the code doesn't show"

Fair. The graph captures structure and behavior, not the business reason a rule
exists. Use the handover to enrich the graph with those reasons as citations on
the relevant nodes, so the next handover starts ahead of this one.
