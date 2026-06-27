# Breeze demo scripts on KCE_Demo_Rebuild

Four presenter scripts. Each takes one enterprise problem, runs it against the
Breeze graphs of this app, and ends with a number a decision-maker can use. All
four are grounded in the same live app and the same graph-driven test suite, so
the demos compound: the audience sees one system answer four different questions.

Read `00-setup-and-cheatsheet.md` first. It brings the app up, lists the four
graphs, and gives the query handles every script reuses.

| # | Script | Problem it kills | Graphs leaned on |
|---|---|---|---|
| 00 | Setup and cheat sheet | "Is it running" | All, plus query reference |
| 01 | Knowledge transition | Handover lives in one person's head | Functional, Code, Architecture, Design |
| 02 | Legacy modernization | Fear of cutting an unknown monolith | Architecture, Code, Functional |
| 03 | New feature enhancement | Scoping by week-long code reading | Functional, Design, Code |
| 04 | App rationalization | Overlap by opinion, not measurement | Functional, Architecture, Design, Code (two projects) |

## The through-line

The same fact carries all four: the graph is generated from code, so it does not
drift, and the test suite is built from the same graph, so documented and verified
are one artifact. Knowledge transition reads the graph, modernization cuts against
it, enhancement scopes from it, rationalization diffs two of them. One system,
four returns.

## Run order for a full session

00 (setup, 5 min) → 01 (handover) → 03 (enhancement) → 02 (modernization) → 04
(rationalization). 01 and 03 build intuition for what the graph knows; 02 and 04
spend that intuition on the higher-stakes portfolio decisions.
