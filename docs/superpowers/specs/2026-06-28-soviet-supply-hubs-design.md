# Supply Hub Auto-Placement — Soviet Pilot (Design Spec)

**Date:** 2026-06-28
**Status:** Approved design, ready for implementation plan
**Scope of this spec:** Pilot over all Soviet (SOV) territory. The pipeline is built to generalize worldwide later, but only USSR output is written in the pilot.

---

## 1. Goal

Programmatically place/restructure HOI4 supply hubs and connecting railways across the mod map according to the user's rules, starting with a verifiable pilot over SOV territory. Output is new `map/supply_nodes.txt` and `map/railways.txt` entries for SOV territory only; the rest of the map is left byte-for-byte untouched.

## 2. Rules (acceptance criteria)

1. **Spacing** — every supply hub should have another supply hub ~5–6 tiles (province hops) away. Network should be spaced so no in-scope province is much more than ~6 hops from a hub.
2. **Conservative on existing hubs** — do not overwrite/move hubs that already sit on a victory point (VP) or a railway crossroad; treat those as fixed anchors. Hubs that are *not* on a VP/crossroad may be freely relocated or removed. Deletion overall should be conservative.
3. **Placement preference** — prefer hub locations on **VP → railway crossroad → most central province**, in that order. Rules 1 and 3 conflict; prefer 3 only when it doesn't break 1.
4. **Railways** — connect new/moved hubs into the rail network. Bias toward *connecting* (adding a short connector) over full rerouting. Straighten only clearly inefficient zig-zag segments. Keep new connectors at the railway level already used in that local area.
5. **Ignore** impassable terrain and unowned provinces (handled here via the SOV-owned + passable-land filter).
6. **Region scarcity** — sparser supply in empty regions (China/Siberia/southern Africa) at 6–8 hops. **Deferred for the pilot** (see §4): the Soviet pilot uses uniform 5–6 spacing to prove the pipeline; per-region scarcity is added at worldwide rollout.

## 3. Pilot parameters (decided with user)

| Parameter | Value |
|---|---|
| Pilot territory | All states with `owner = SOV` at 1936 start (129 states). Excludes separate puppet tags (Mongolia, Tannu Tuva). |
| Normal spacing | 5–6 hops (uniform across the whole pilot) |
| Scarce spacing | 6–8 hops — **not used in pilot**, deferred to rollout |
| Min separation | New hub placed no closer than ~4 hops to any existing hub (tunable) |
| Deletion policy | Conservative. Only relocate/remove "movable" hubs (not on VP and not on crossroad). |
| Railway policy | Connect > reroute. Straighten only clear zig-zags. New connectors inherit the local railway level. |
| Snapping priority | VP → railway crossroad → most central candidate |

## 4. Chosen approach: A — Greedy gap-filling with feature snapping

Rejected alternatives: **B Lattice/Poisson-disk** (most uniform but fights existing structure, weak on rule 2); **C Graph k-means relaxation** (smooth but moves existing hubs too much, hard to steer to VP/crossroad). A best honors "build on existing" + conservative deletion and is the most predictable/reviewable.

Algorithm:
1. **Anchors** = existing SOV hubs sitting on a VP or crossroad → fixed, never moved/removed.
2. **Movable** = existing SOV hubs not on a VP/crossroad → eligible for relocation/removal.
3. **Greedy fill:** multi-source BFS (hops) from all current hubs over the in-scope land graph. While any in-scope province is > 6 hops from its nearest hub, add one hub in the worst-served area, snapped to the best nearby province by priority VP → crossroad → most central, refusing placement within the ~4-hop min-separation of an existing hub. Repeat.
4. **Prune:** remove/relocate a *movable* hub only when another hub is within < 4 hops of it (redundant) AND removing it does not violate rule 1 for its neighbours.
5. **Target invariant:** every retained hub has at least one other hub within 5–6 hops, and coverage holds (no in-scope province far beyond ~6 hops).

## 5. Pipeline (stages)

### Stage 1 — Parse & model
- `map/definition.csv` → province table: `id;R;G;B;land|sea|lake;coastal;terrain;continent`.
- `history/states/*.txt` → per state: `owner = TAG`, `provinces = { id id ... }`, and one or more `victory_points = { prov value }` blocks. Build province→owner, province→VP(value), state→provinces.
- `map/supply_nodes.txt` → existing hubs, line format `1 <province_id>` (leading `1` is a constant marker).
- `map/railways.txt` → existing segments, line format `<level> <count> <prov1> <prov2> ... <provN>` where the province list is a contiguous path of adjacent provinces.
- `map/adjacencies.csv` → `From;To;Type;Through;...`. Mostly `sea` crossings/canals → **ignored** for the land graph. Only `land`-type special adjacencies (if any) are merged.

### Stage 2 — Build adjacency graph (cached to disk)
- Parse `map/provinces.bmp` (5632×2048, 24-bit BMP). For each pixel, compare to its right and down neighbour; differing colors → the two provinces (looked up via RGB from definition.csv) are adjacent.
- **East–west wrap:** column 0 is adjacent to column 5631 (world map wraps). Must be handled or trans-dateline distances break (low impact for USSR interior but implement for correctness).
- Restrict graph to **passable land** (drop sea/lake; drop impassable — see §7).
- Merge any land-type special adjacencies from `adjacencies.csv`.
- Compute province **centroids** (mean pixel x,y) for rendering and central-province tie-breaks.
- Cache graph + centroids to a file in scratchpad so re-runs are fast.
- Tooling: prefer `pip install Pillow numpy` (pip 26.1.1 / Python 3.14 available). Pure-Python BMP parse is the fallback (one-time, slower).

### Stage 3 — Classify
- **Candidate set** = SOV-owned passable-land provinces.
- Mark **VP provinces** (from Stage 1).
- Compute **railway-crossroad provinces** = junctions where ≥2 distinct railway segments meet at a shared province, or rail-degree ≥3. (Source data: a province appears in up to 11 segments today, so junctions are well-defined.)
- Compute current hub-spacing stats over the candidate set (baseline histogram).

### Stage 4 — Place (Approach A, §4)
Produce the final hub set: anchors kept, gaps filled, redundant movables pruned.

### Stage 5 — Wire railways
- For each **new or moved** hub: land-BFS shortest path to the nearest node already on the rail network (an existing hub, or any province on a railway path). Add a railway segment along that path.
- **Level:** inherit the level of the nearest existing segment(s) in that area (sampled). Railway levels in use: 1 (most common) → 5.
- **Straighten:** for an existing segment whose path length ≫ graph-shortest path between its two endpoints, replace with the shortest path. Apply only to clear cases; never reroute a segment that is already near-optimal.
- **Validate:** every emitted segment must be a contiguous sequence of pairwise-adjacent provinces (HOI4 rejects non-contiguous railways). Re-check against the Stage-2 graph.

### Stage 6 — Emit & verify
- Rewrite **only SOV** lines in `map/supply_nodes.txt` and `map/railways.txt`; leave all non-SOV lines unchanged.
- **Validation gate:** every hub province exists, is land, is SOV-owned; no duplicate hubs; every railway segment contiguous and level in 1–5.
- **Diagnostics:** render before/after PNG overlays (hubs, railways, VPs over the province/terrain map) for visual review.
- **Diff report:** hubs added / moved / removed, segments added / straightened, spacing histogram before vs after.
- **In-game check:** supply/railway map changes require a **NEW game** (not save-compatible), same as landmark/map-data changes. User is the in-game verifier.

## 6. Files

**Read:** `map/definition.csv`, `map/provinces.bmp`, `map/supply_nodes.txt`, `map/railways.txt`, `map/adjacencies.csv`, `history/states/*.txt`, `common/terrain/00_terrain.txt` (impassable check).

**Written:** `map/supply_nodes.txt`, `map/railways.txt` (SOV entries only).

**Not written (verified):** `map/buildings.txt` — all 10,475 `supply_node` slots use trailing field `0` and are position-matched (~one per land province). Placing a hub on any land province reuses its existing slot; no buildings.txt edit expected. *Verify during pilot.*

**Artifacts (scratchpad / repo):** the pipeline Python script (checked in so placement is reproducible/tweakable), cached graph, diagnostic PNGs, diff report.

## 7. Assumptions & risks

| # | Item | Resolution |
|---|---|---|
| R1 | **buildings.txt hub↔slot matching is positional** (no per-province edit needed). | Verified slots are position-matched (trailing `0`). Confirm a placed hub renders in the pilot; if not, add/adjust a `supply_node` slot for that province. |
| R2 | **Impassable terrain** — `common/terrain/00_terrain.txt` defines no `is_impassable` (inherits vanilla). | Exclude via: not-SOV-owned filter + vanilla impassable terrain categories + (if needed) strategic-region impassable flags. Low risk inside USSR. |
| R3 | **Railway connectivity correctness** is the main gameplay risk — a hub only works if rail-connected to a supply source. | Bias to connecting over rerouting; always wire new hubs to the nearest network node; validate contiguity; user verifies supply flow in-game. |
| R4 | **No in-game playtest by the tool.** | Mitigate with format validation + diagnostic PNGs + diff report; iterate with user as verifier. |
| R5 | **East–west map wrap** in adjacency. | Implement column-0↔column-5631 adjacency in Stage 2. |
| R6 | **Greedy ≠ optimal**; rules are soft. | Acceptable; output is rule-consistent and reviewable, not hand-tuned-perfect. Parameters (spacing, min-sep, straighten threshold) are tunable. |

## 8. Out of scope (pilot) / future

- Worldwide rollout beyond SOV.
- Per-region scarcity tiers (6–8 hops for Siberia/Central Asia, possibly 8–10 for deep Arctic/Far East) — re-enable rule 6 after the pilot validates the pipeline.
- Soviet puppets (Mongolia, Tannu Tuva) unless requested.

## 9. Definition of done (pilot)

- New SOV hub network satisfies the 5–6 hop spacing invariant with conservative deletion.
- New connectors validated contiguous, at local rail level.
- Diff report + before/after PNGs produced.
- Non-SOV map data unchanged.
- User loads a new game and confirms placement/supply look right; iterate on parameters as needed.
