# Demo 2: Legacy modernization

**Scenario.** A monolith has to come apart. Leadership wants microservices, or at
least a strangler-fig path off the big ball of mud. The blocker is never
ambition; it is fear. Nobody can say what calls what, so nobody can say what
breaks when you cut. Estimates are guesses and the first extraction takes a
quarter.

**Claim to prove.** The graph turns extraction from archaeology into a planned
move: find the seam, see the blast radius before cutting, and prove behavior
parity after. This app already carries one completed extraction, so you can show
the before and after on a real change.

**Audience.** Architects, platform leads, the people who own the migration
budget. **Run time.** 15 minutes.

---

## Beat 1: The seam is already in the graph (3 min)

The audit capability was pulled out of the backend into its own service. Show
that the architecture graph records the result, not a wish:

```
Get_All_architecture_Graph(KCE_Demo_Rebuild)
Get_Architecture_Nodes_By_Label("Service")
```

Gateway → backend for items, gateway → audit service for `/api/audit`. The
strangler-fig routing lives in `gateway/main.py` lines 30-33. Point at it:

```python
target_url = BACKEND_URL
if path.startswith("api/audit"):
    target_url = AUDIT_URL
```

One line of routing is the entire seam. The graph is how you found it without
reading the whole gateway.

## Beat 2: Find the next seam by coupling, not by guesswork (3 min)

Before extracting anything, ask the graph what a candidate touches. Use the audit
capability as the worked example:

```
Functional_Graph_Search("audit log DML trigger record_id", KCE_Demo_Rebuild)
Code_Graph_Search("audit_logs trigger audit_trigger_func", KCE_Demo_Rebuild)
```

The graph shows the audit read path is self-contained (its own service, its own
read model) but the write path is a Postgres trigger shared with the `items`
table. That shared trigger is the real coupling, and it is exactly the thing a
file-by-file reading misses until it bites you in production. You now have the
risk on the table before writing any code.

## Beat 3: Blast radius before the cut (3 min)

"If I move this, what else moves." Trace consumers from the functional graph:

```
Get_complete_functional_graph(KCE_Demo_Rebuild)
```

`GET /api/audit` has exactly one consumer surface: the System persona's "Monitor
System Audit Activity" outcome and the `AuditLogList` design component. Two
touch-points, both visible, both clickable to source. That is a scoped change,
and the graph let you say so with a number instead of a shrug.

## Beat 4: Make the cut (2 min)

This is the live edit, or a pre-staged branch if time is tight. The mechanics are
ordinary FastAPI; the point is that the graph scoped the work first. Show that the
gateway already abstracts the client from the topology: the frontend calls
`/api/audit` and never learns there are two services behind the gateway.

## Beat 5: Prove parity (4 min)

The fear in modernization is silent behavior change. Close it two ways.

Regenerate the functional graph after the change and diff personas, outcomes, and
APIs against the before. Same nine APIs, same outcomes means the contract held.

Then run the suite, which is built from the graph:

```bash
uv run --python 3.13 python tests/build_matrix.py
GATEWAY_URL=http://localhost:8080 \
  uv run --python 3.13 --with pytest --with httpx python -m pytest tests -q
```

`tests/test_audit_trail.py` asserts INSERT/UPDATE/DELETE rows still land after
the extraction, end to end through the gateway. Green means the extracted service
preserves the audit guarantee. You modernized and proved it in the same motion.

---

## The payoff line

Extraction risk is a function of unknown coupling. The graph makes coupling
visible before the cut and provable after it, so the first service out the door
takes days of planned work instead of a quarter of spelunking.

## Sequencing advice to give the room

Extract by coupling score, lowest first. The graph ranks candidates by how few
functional and design nodes they touch. Audit was a good first cut precisely
because the graph showed two consumers; do not let anyone start with the node
that has twenty.

## The risk to name out loud

The shared audit trigger is database-level coupling the service boundary does not
remove. Modernization that stops at the API layer and ignores the data layer
ships a distributed monolith. The graph surfaced that trigger in Beat 2; put it
on the migration backlog, do not paper over it.
