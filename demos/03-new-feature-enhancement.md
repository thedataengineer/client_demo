# Demo 3: New feature enhancement

**Scenario.** Product wants a new capability. Engineering's honest answer is "we
need to scope it," which means a few engineers read code for a week and still
miss an edge. The estimate is padded for the unknowns, and half the bugs ship
from places nobody knew the change reached.

**Claim to prove.** The graph does impact analysis before a line is written: it
names every persona, scenario, API, UI component, and file the feature touches,
and the test matrix grows from the graph so coverage tracks the feature
automatically.

**Worked feature.** Add item categories. A category is a new field on an item,
filterable in the list, shown in the row, and audited like every other mutation.
Small enough to demo, broad enough to hit every layer.

**Audience.** Product and engineering together, the people who negotiate scope and
estimates. **Run time.** 15 minutes.

---

## Beat 1: Scope from the graph, not from a reading marathon (4 min)

Ask the functional graph what "items" already touches, because the new field
rides the same paths:

```
Functional_Graph_Search("item create update list category field", KCE_Demo_Rebuild)
Get_complete_functional_graph(KCE_Demo_Rebuild)
```

The graph returns the exact surface a category field must follow:

- **User / Manage Items**: Add (`POST /api/items`), Browse (`GET /api/items`),
  Update, Remove.
- **System / Manage Items**: the server-side create/list/update/delete scenarios,
  each with its validation and audit step.

That is the impact list. No file reading produced it and nothing on it was
guessed.

## Beat 2: UI blast radius (3 min)

```
Design_Graph_Search("item row add item form item list", KCE_Demo_Rebuild)
```

Category touches `AddItemForm` (new input), `ItemRow` (display, via `ItemText` or
a new badge), and `ItemList` (filter control). Three components, named before the
designer opens Figma. The estimate now has a real component count instead of "the
UI, probably."

## Beat 3: Code blast radius (3 min)

```
Code_Graph_Search("Item model schema create_item ItemResponse", KCE_Demo_Rebuild)
Get_Code_File_Details("backend/app/models/item.py")
```

The chain to change is explicit: `models/item.py` (column + index),
`schemas/item.py` (`ItemResponse` field), `repositories/item_repository.py`
(create/query), `services/item_service.py` (pass-through), `api/routes.py` (query
param). Five files, in dependency order. That is the implementation plan, derived,
not invented.

## Beat 4: The audit guarantee comes for free, and the graph shows why (2 min)

Note what is NOT on the change list: the audit path. Because audit is a Postgres
trigger on the `items` table (`audit_trigger_func`), a category update is logged
without touching audit code. The architecture graph is how you assert that with
confidence instead of hoping. This is the kind of "do we need to update audit"
question that usually costs a meeting.

## Beat 5: Tests grow from the graph (3 min)

This is the closer. The RBAC matrix is generated from the functional graph's API
inventory:

```python
# tests/build_matrix.py walks every action.apis[] in the functional payloads
# -> (persona, method, path) -> tests/graph_matrix.json -> test_rbac.py
```

Add the category to the graph, re-run the UI pass, then:

```bash
uv run --python 3.13 python tests/build_matrix.py   # matrix regenerates
GATEWAY_URL=http://localhost:8080 \
  uv run --python 3.13 --with pytest --with httpx python -m pytest tests -q
```

New endpoint or persona in the graph means new cells in the matrix with no test
edits. Coverage follows the feature instead of lagging it. Show
`test_every_graph_endpoint_is_covered` in `test_rbac.py`: it fails the build if a
graph endpoint has no test, so "we forgot to test the new path" stops being
possible.

---

## The payoff line

Scoping moves from a week of reading to a query, and the estimate carries a real
list of personas, components, and files instead of a risk premium for the
unknown. The thing you scoped and the thing you tested are the same graph.

## Where this changes the estimate conversation

Hand product the impact list from Beat 1 to 3 directly. "Category is five backend
files, three components, six endpoint-persona test cells, zero audit work."
That is a defensible number in the room, not a number defended after the fact.

## The honest limit

The graph tells you what the feature touches. It does not tell you whether the
feature is worth building or whether the category taxonomy is right. Product still
owns the what and the why; the graph kills the "how much and where" guesswork.
