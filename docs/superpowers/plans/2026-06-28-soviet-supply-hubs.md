# Soviet Supply Hub Auto-Placement — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a zero-dependency Python pipeline that reads the mod's HOI4 map data and writes a new supply-hub + railway network over Soviet (SOV) territory satisfying the user's spacing/placement rules, with diagnostics for in-game verification.

**Architecture:** A small Python package `tools/supply_hubs/` with focused modules: a pure-Python BMP reader, parsers for the map/state files, a province adjacency graph + BFS, a classifier (candidates/VPs/crossroads), a greedy placement stage, a railway-wiring stage, an emitter that rewrites only SOV lines, and an SVG/diff renderer. An orchestrator runs the stages into an `out/` dir for review (`--apply` to write into `map/`).

**Tech Stack:** Python 3.14 standard library only (no numpy/Pillow required). pytest for tests. Output: `map/supply_nodes.txt`, `map/railways.txt`, plus SVG + markdown diagnostics.

**Companion spec:** [docs/superpowers/specs/2026-06-28-soviet-supply-hubs-design.md](../specs/2026-06-28-soviet-supply-hubs-design.md) — read it first.

## Global Constraints

- **Standard library only.** No numpy/Pillow/scipy dependency (they are NOT installed). numpy is an optional speed optimization only; never a hard import.
- **Mod root:** `c:/Users/adamg/Documents/Paradox Interactive/Hearts of Iron IV/mod/MFU-Updated`. All map paths are relative to it.
- **Only SOV lines change.** Non-SOV lines in `map/supply_nodes.txt` and `map/railways.txt` must keep identical content. The rest of `map/` is never written.
- **`map/buildings.txt` is NOT edited.** All 10,475 `supply_node` slots use trailing field `0` (position-matched). Verified in spec §6/§7-R1.
- **File formats (verbatim):**
  - `supply_nodes.txt`: one hub per line, `1 <province_id>` (leading `1` is a constant).
  - `railways.txt`: one segment per line, `<level> <count> <prov1> <prov2> ... <provN>`; the province list is a contiguous path of pairwise-adjacent provinces; `count` == number of provinces.
  - `definition.csv`: `<id>;<R>;<G>;<B>;<land|sea|lake>;<coastal_bool>;<terrain>;<continent>` (semicolon, no header).
  - state files (`history/states/*.txt`): contain `owner = TAG`, a `provinces = { id id ... }` block, and zero or more `victory_points = { <prov> <value> }` blocks.
  - `adjacencies.csv`: `From;To;Type;Through;...` header row present; `Type` is mostly `sea`/canal → ignored for the land graph.
- **Pilot scope:** provinces in states with `owner = SOV` (129 states). Spacing uniform 5–6 hops. Min separation ~4 hops. Snapping priority VP → crossroad → most central. Conservative deletion (only non-anchor hubs move/removed). Connect-over-reroute railways.
- **Map data change ⇒ requires a NEW game** to take effect; not save-compatible. User is the in-game verifier.
- **Safety:** the pipeline writes to `tools/supply_hubs/out/` by default; it only overwrites files under `map/` when run with `--apply`.

**Working directory for all commands below:** the mod root. Run pytest as `python -m pytest tools/supply_hubs/tests/ -v`.

---

## File Structure

```
tools/supply_hubs/
  __init__.py
  bmp.py            # pure-Python 24-bit BMP reader
  parse_map.py      # definition.csv, supply_nodes.txt, railways.txt, adjacencies.csv
  parse_states.py   # owner / provinces / victory_points from history/states/*.txt
  graph.py          # province adjacency + centroids (+ cache), land subgraph, BFS
  classify.py       # candidate set, VP set, crossroads, spacing stats
  place.py          # Approach A greedy placement
  wire.py           # railway connect + straighten + contiguity validation
  emit.py           # rewrite SOV-only supply_nodes/railways + validation gate
  render.py         # SVG overlay + markdown diff report
  run_pilot.py      # orchestrator (--apply to write into map/)
  tests/
    __init__.py
    conftest.py     # shared fixtures / tiny synthetic data
    test_bmp.py
    test_parse_map.py
    test_parse_states.py
    test_graph.py
    test_classify.py
    test_place.py
    test_wire.py
    test_emit.py
```

Each module has one responsibility and a small, explicit interface so tasks can be implemented and reviewed independently.

---

## Task 1: Package scaffold + pure-Python BMP reader

**Files:**
- Create: `tools/supply_hubs/__init__.py` (empty)
- Create: `tools/supply_hubs/tests/__init__.py` (empty)
- Create: `tools/supply_hubs/bmp.py`
- Test: `tools/supply_hubs/tests/test_bmp.py`

**Interfaces:**
- Produces: `read_bmp_rgb(path) -> tuple[int, int, list[tuple[int,int,int]]]` returning `(width, height, pixels)` where `pixels` is a row-major **top-down** list of `(R,G,B)`, length `width*height`, index `y*width + x`.
- Produces test helper `make_bmp_bytes(width, height, pixels) -> bytes` (in test file) to synthesize a 24-bit BMP.

- [ ] **Step 1: Write the failing test**

```python
# tools/supply_hubs/tests/test_bmp.py
import struct
from tools.supply_hubs.bmp import read_bmp_rgb


def make_bmp_bytes(width, height, pixels):
    """pixels: top-down row-major list of (R,G,B). Returns 24-bit BMP bytes."""
    row_stride = (width * 3 + 3) & ~3  # pad each row to 4 bytes
    pixel_array_size = row_stride * height
    file_size = 14 + 40 + pixel_array_size
    fh = b"BM" + struct.pack("<IHHI", file_size, 0, 0, 54)
    dib = struct.pack("<IiiHHIIiiII", 40, width, height, 1, 24, 0,
                      pixel_array_size, 2835, 2835, 0, 0)
    rows = []
    for y in range(height - 1, -1, -1):  # BMP stores bottom row first
        row = bytearray()
        for x in range(width):
            r, g, b = pixels[y * width + x]
            row += bytes((b, g, r))        # BMP is BGR
        row += b"\x00" * (row_stride - width * 3)
        rows.append(bytes(row))
    return fh + dib + b"".join(rows)


def test_reads_pixels_top_down_rgb(tmp_path):
    px = [(255, 0, 0), (0, 255, 0),
          (0, 0, 255), (10, 20, 30)]  # 2x2, top-down
    p = tmp_path / "t.bmp"
    p.write_bytes(make_bmp_bytes(2, 2, px))
    w, h, out = read_bmp_rgb(str(p))
    assert (w, h) == (2, 2)
    assert out == px


def test_handles_row_padding(tmp_path):
    # width 3 => row 9 bytes => padded to 12
    px = [(1, 1, 1), (2, 2, 2), (3, 3, 3)]
    p = tmp_path / "t.bmp"
    p.write_bytes(make_bmp_bytes(3, 1, px))
    w, h, out = read_bmp_rgb(str(p))
    assert (w, h) == (3, 1)
    assert out == px
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tools/supply_hubs/tests/test_bmp.py -v`
Expected: FAIL (ModuleNotFoundError: tools.supply_hubs.bmp). Create the empty `__init__.py` files first if the import path itself fails.

- [ ] **Step 3: Write minimal implementation**

```python
# tools/supply_hubs/bmp.py
import struct


def read_bmp_rgb(path):
    """Read a 24-bit uncompressed BMP. Returns (width, height, pixels)
    where pixels is top-down row-major list of (R,G,B)."""
    with open(path, "rb") as f:
        data = f.read()
    if data[:2] != b"BM":
        raise ValueError("not a BMP")
    pixel_offset = struct.unpack_from("<I", data, 10)[0]
    width = struct.unpack_from("<i", data, 18)[0]
    height = struct.unpack_from("<i", data, 22)[0]
    bpp = struct.unpack_from("<H", data, 28)[0]
    compression = struct.unpack_from("<I", data, 30)[0]
    if bpp != 24 or compression != 0:
        raise ValueError(f"unsupported BMP: bpp={bpp} compression={compression}")
    top_down = height < 0
    height = abs(height)
    row_stride = (width * 3 + 3) & ~3
    pixels = [None] * (width * height)
    for ry in range(height):
        src_y = ry if top_down else (height - 1 - ry)
        base = pixel_offset + src_y * row_stride
        for x in range(width):
            o = base + x * 3
            b, g, r = data[o], data[o + 1], data[o + 2]
            pixels[ry * width + x] = (r, g, b)
    return width, height, pixels
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tools/supply_hubs/tests/test_bmp.py -v`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add tools/supply_hubs/__init__.py tools/supply_hubs/tests/__init__.py tools/supply_hubs/bmp.py tools/supply_hubs/tests/test_bmp.py
git commit -m "feat(supply-hubs): pure-Python 24-bit BMP reader"
```

---

## Task 2: Map-file parsers (definition / supply_nodes / railways / adjacencies)

**Files:**
- Create: `tools/supply_hubs/parse_map.py`
- Test: `tools/supply_hubs/tests/test_parse_map.py`

**Interfaces:**
- Produces `Province = namedtuple("Province", "id r g b kind coastal terrain continent")` (`kind` in {"land","sea","lake"}).
- Produces `parse_definition(path) -> dict[int, Province]`.
- Produces `parse_supply_nodes(path) -> list[int]` (province ids, in file order).
- Produces `parse_railways(path) -> list[tuple[int, list[int]]]` → `(level, [prov,...])` per segment.
- Produces `parse_adjacencies(path) -> list[dict]` with keys `from,to,type,through` (lowercased `type`).

- [ ] **Step 1: Write the failing test**

```python
# tools/supply_hubs/tests/test_parse_map.py
from tools.supply_hubs.parse_map import (
    parse_definition, parse_supply_nodes, parse_railways, parse_adjacencies)


def test_parse_definition(tmp_path):
    p = tmp_path / "definition.csv"
    p.write_text("1;0;0;0;land;false;unknown;0\n"
                 "5;0;0;232;sea;true;ocean;0\n", encoding="utf-8")
    d = parse_definition(str(p))
    assert d[1].kind == "land" and d[1].terrain == "unknown"
    assert d[5].kind == "sea" and d[5].coastal is True
    assert (d[5].r, d[5].g, d[5].b) == (0, 0, 232)


def test_parse_supply_nodes(tmp_path):
    p = tmp_path / "supply_nodes.txt"
    p.write_text("1 39 \n1 70\n1 72\n", encoding="utf-8")
    assert parse_supply_nodes(str(p)) == [39, 70, 72]


def test_parse_railways(tmp_path):
    p = tmp_path / "railways.txt"
    p.write_text("2 4 11372 11343 9263 362 \n1 3 11164 162 6087\n",
                 encoding="utf-8")
    segs = parse_railways(str(p))
    assert segs[0] == (2, [11372, 11343, 9263, 362])
    assert segs[1] == (1, [11164, 162, 6087])


def test_parse_adjacencies_skips_header(tmp_path):
    p = tmp_path / "adjacencies.csv"
    p.write_text("From;To;Type;Through;start_x\n"
                 "12251;10321;sea;8313;-1\n", encoding="utf-8")
    a = parse_adjacencies(str(p))
    assert len(a) == 1 and a[0]["type"] == "sea" and a[0]["from"] == 12251
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tools/supply_hubs/tests/test_parse_map.py -v`
Expected: FAIL (ModuleNotFoundError: parse_map)

- [ ] **Step 3: Write minimal implementation**

```python
# tools/supply_hubs/parse_map.py
from collections import namedtuple

Province = namedtuple("Province", "id r g b kind coastal terrain continent")


def parse_definition(path):
    out = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(";")
            pid = int(parts[0])
            out[pid] = Province(pid, int(parts[1]), int(parts[2]), int(parts[3]),
                                parts[4], parts[5].lower() == "true",
                                parts[6], parts[7])
    return out


def parse_supply_nodes(path):
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            toks = line.split()
            if len(toks) >= 2:
                out.append(int(toks[1]))
    return out


def parse_railways(path):
    segs = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            toks = line.split()
            if len(toks) < 3:
                continue
            level = int(toks[0])
            count = int(toks[1])
            provs = [int(t) for t in toks[2:2 + count]]
            segs.append((level, provs))
    return segs


def parse_adjacencies(path):
    out = []
    with open(path, encoding="utf-8") as f:
        first = True
        for line in f:
            line = line.strip()
            if not line:
                continue
            if first:
                first = False
                if line.lower().startswith("from;"):
                    continue
            parts = line.split(";")
            if len(parts) < 4 or not parts[0].isdigit():
                continue
            out.append({"from": int(parts[0]), "to": int(parts[1]),
                        "type": parts[2].lower(), "through": parts[3]})
    return out
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tools/supply_hubs/tests/test_parse_map.py -v`
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add tools/supply_hubs/parse_map.py tools/supply_hubs/tests/test_parse_map.py
git commit -m "feat(supply-hubs): map-file parsers"
```

---

## Task 3: State parser (owner / provinces / victory points)

**Files:**
- Create: `tools/supply_hubs/parse_states.py`
- Test: `tools/supply_hubs/tests/test_parse_states.py`

**Interfaces:**
- Produces `StateInfo = namedtuple("StateInfo", "id owner provinces vps")` where `provinces` is `set[int]`, `vps` is `dict[int,int]` (province→value).
- Produces `parse_state_file(path) -> StateInfo`.
- Produces `load_states(states_dir) -> list[StateInfo]` (all `*.txt`).
- Produces `owner_by_province(states) -> dict[int,str]` and `vp_provinces(states) -> dict[int,int]`.

Notes: a state has at most one `owner` and one `provinces` block but possibly **multiple** `victory_points` blocks. Use a brace-tolerant token scan, not regex-per-line.

- [ ] **Step 1: Write the failing test**

```python
# tools/supply_hubs/tests/test_parse_states.py
from tools.supply_hubs.parse_states import (
    parse_state_file, owner_by_province, vp_provinces)


SAMPLE = """state = {
    id = 137
    name = "STATE_137"
    history = {
        owner = SOV
        victory_points = { 3686 20 }
        victory_points = {
            9680 1
        }
    }
    provinces = {
        705 3686 9680
    }
}
"""


def test_parse_state_file(tmp_path):
    p = tmp_path / "137-Crimea.txt"
    p.write_text(SAMPLE, encoding="utf-8")
    s = parse_state_file(str(p))
    assert s.id == 137
    assert s.owner == "SOV"
    assert s.provinces == {705, 3686, 9680}
    assert s.vps == {3686: 20, 9680: 1}


def test_owner_and_vp_indexes(tmp_path):
    p = tmp_path / "137-Crimea.txt"
    p.write_text(SAMPLE, encoding="utf-8")
    s = parse_state_file(str(p))
    assert owner_by_province([s])[705] == "SOV"
    assert vp_provinces([s]) == {3686: 20, 9680: 1}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tools/supply_hubs/tests/test_parse_states.py -v`
Expected: FAIL (ModuleNotFoundError: parse_states)

- [ ] **Step 3: Write minimal implementation**

```python
# tools/supply_hubs/parse_states.py
import glob
import os
import re
from collections import namedtuple

StateInfo = namedtuple("StateInfo", "id owner provinces vps")

_INT = re.compile(r"-?\d+")


def _find_block(text, key):
    """Return list of (start,end) content spans for every `key = { ... }`."""
    spans = []
    for m in re.finditer(re.escape(key) + r"\s*=\s*\{", text):
        i = m.end()
        depth = 1
        while i < len(text) and depth:
            c = text[i]
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
            i += 1
        spans.append((m.end(), i - 1))
    return spans


def parse_state_file(path):
    text = open(path, encoding="utf-8", errors="replace").read()
    sid_m = re.search(r"\bid\s*=\s*(\d+)", text)
    sid = int(sid_m.group(1)) if sid_m else -1
    owner_m = re.search(r"\bowner\s*=\s*([A-Za-z0-9_]+)", text)
    owner = owner_m.group(1) if owner_m else None

    provinces = set()
    pspans = _find_block(text, "provinces")
    if pspans:
        s, e = pspans[0]
        provinces = set(int(x) for x in _INT.findall(text[s:e]))

    vps = {}
    for s, e in _find_block(text, "victory_points"):
        nums = _INT.findall(text[s:e])
        for i in range(0, len(nums) - 1, 2):
            vps[int(nums[i])] = int(nums[i + 1])
    return StateInfo(sid, owner, provinces, vps)


def load_states(states_dir):
    out = []
    for p in sorted(glob.glob(os.path.join(states_dir, "*.txt"))):
        out.append(parse_state_file(p))
    return out


def owner_by_province(states):
    out = {}
    for s in states:
        if s.owner:
            for p in s.provinces:
                out[p] = s.owner
    return out


def vp_provinces(states):
    out = {}
    for s in states:
        out.update(s.vps)
    return out
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tools/supply_hubs/tests/test_parse_states.py -v`
Expected: PASS (2 passed)

- [ ] **Step 5: Sanity-check against real data, then commit**

Run a throwaway check (do not commit this command's output):
```bash
python -c "from tools.supply_hubs.parse_states import load_states, owner_by_province; s=load_states('history/states'); o=owner_by_province(s); print('SOV provinces:', sum(1 for v in o.values() if v=='SOV'))"
```
Expected: a few thousand SOV provinces (sanity: 129 SOV states).

```bash
git add tools/supply_hubs/parse_states.py tools/supply_hubs/tests/test_parse_states.py
git commit -m "feat(supply-hubs): state parser (owner/provinces/VPs)"
```

---

## Task 4: Province adjacency graph + centroids + cache + BFS

**Files:**
- Create: `tools/supply_hubs/graph.py`
- Test: `tools/supply_hubs/tests/test_graph.py`

**Interfaces:**
- Produces `build_adjacency(width, height, pixels, rgb_to_pid, wrap_x=True) -> tuple[dict[int,set[int]], dict[int,tuple[float,float]]]` → `(adjacency, centroids)`. `rgb_to_pid` maps `(R,G,B)->pid`; unknown colors are skipped.
- Produces `land_subgraph(adjacency, provinces) -> dict[int,set[int]]` keeping only edges where both endpoints are `kind=="land"` (uses the `provinces` dict from Task 2).
- Produces `bfs_hops(adjacency, sources:set[int], limit=None) -> dict[int,int]` (multi-source; distance 0 at every source).
- Produces `shortest_path(adjacency, src, dst) -> list[int] | None` (BFS path, inclusive).
- Produces cache helpers `save_graph(path, adjacency, centroids)` / `load_graph(path)` using JSON (province ids as strings).

- [ ] **Step 1: Write the failing test**

```python
# tools/supply_hubs/tests/test_graph.py
from tools.supply_hubs.graph import (
    build_adjacency, bfs_hops, shortest_path, land_subgraph)
from tools.supply_hubs.parse_map import Province


def _prov(pid, kind="land"):
    return Province(pid, 0, 0, 0, kind, False, "plains", "0")


def test_adjacency_and_wrap():
    # 3x1 image: A | B | C  with colors mapped to pids 1,2,3
    pixels = [(1, 1, 1), (2, 2, 2), (3, 3, 3)]
    rgb = {(1, 1, 1): 1, (2, 2, 2): 2, (3, 3, 3): 3}
    adj, cent = build_adjacency(3, 1, pixels, rgb, wrap_x=True)
    assert adj[1] == {2, 3}   # 1-2 horizontal, 1-3 via wrap
    assert adj[2] == {1, 3}
    assert cent[1] == (0.0, 0.0)
    assert cent[2] == (1.0, 0.0)


def test_no_wrap():
    pixels = [(1, 1, 1), (2, 2, 2), (3, 3, 3)]
    rgb = {(1, 1, 1): 1, (2, 2, 2): 2, (3, 3, 3): 3}
    adj, _ = build_adjacency(3, 1, pixels, rgb, wrap_x=False)
    assert adj[1] == {2}
    assert adj[3] == {2}


def test_bfs_and_path():
    adj = {1: {2}, 2: {1, 3}, 3: {2, 4}, 4: {3}}
    d = bfs_hops(adj, {1})
    assert d == {1: 0, 2: 1, 3: 2, 4: 3}
    assert shortest_path(adj, 1, 4) == [1, 2, 3, 4]
    # multi-source
    d2 = bfs_hops(adj, {1, 4})
    assert d2[2] == 1 and d2[3] == 1


def test_land_subgraph_drops_sea():
    adj = {1: {2}, 2: {1, 3}, 3: {2}}
    provs = {1: _prov(1, "land"), 2: _prov(2, "sea"), 3: _prov(3, "land")}
    sub = land_subgraph(adj, provs)
    assert 2 not in sub
    assert sub[1] == set() and sub[3] == set()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tools/supply_hubs/tests/test_graph.py -v`
Expected: FAIL (ModuleNotFoundError: graph)

- [ ] **Step 3: Write minimal implementation**

```python
# tools/supply_hubs/graph.py
import json
from collections import deque


def build_adjacency(width, height, pixels, rgb_to_pid, wrap_x=True):
    adjacency = {}
    sx = {}
    sy = {}
    cnt = {}

    def pid_at(x, y):
        return rgb_to_pid.get(pixels[y * width + x])

    def link(a, b):
        if a is None or b is None or a == b:
            return
        adjacency.setdefault(a, set()).add(b)
        adjacency.setdefault(b, set()).add(a)

    for y in range(height):
        for x in range(width):
            p = pid_at(x, y)
            if p is not None:
                sx[p] = sx.get(p, 0) + x
                sy[p] = sy.get(p, 0) + y
                cnt[p] = cnt.get(p, 0) + 1
                if x + 1 < width:
                    link(p, pid_at(x + 1, y))
                if y + 1 < height:
                    link(p, pid_at(x, y + 1))
        if wrap_x and width > 1:
            link(pid_at(0, y), pid_at(width - 1, y))

    centroids = {p: (sx[p] / cnt[p], sy[p] / cnt[p]) for p in cnt}
    for p in list(adjacency):
        adjacency.setdefault(p, set())
    return adjacency, centroids


def land_subgraph(adjacency, provinces):
    def is_land(pid):
        pr = provinces.get(pid)
        return pr is not None and pr.kind == "land"
    sub = {}
    for a, nbrs in adjacency.items():
        if not is_land(a):
            continue
        sub[a] = set(b for b in nbrs if is_land(b))
    return sub


def bfs_hops(adjacency, sources, limit=None):
    dist = {s: 0 for s in sources if s in adjacency}
    q = deque(dist)
    while q:
        u = q.popleft()
        if limit is not None and dist[u] >= limit:
            continue
        for v in adjacency.get(u, ()):
            if v not in dist:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist


def shortest_path(adjacency, src, dst):
    if src == dst:
        return [src]
    prev = {src: None}
    q = deque([src])
    while q:
        u = q.popleft()
        for v in adjacency.get(u, ()):
            if v not in prev:
                prev[v] = u
                if v == dst:
                    path = [v]
                    while prev[path[-1]] is not None:
                        path.append(prev[path[-1]])
                    return path[::-1]
                q.append(v)
    return None


def save_graph(path, adjacency, centroids):
    obj = {"adj": {str(k): sorted(v) for k, v in adjacency.items()},
           "cent": {str(k): list(v) for k, v in centroids.items()}}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f)


def load_graph(path):
    obj = json.load(open(path, encoding="utf-8"))
    adjacency = {int(k): set(v) for k, v in obj["adj"].items()}
    centroids = {int(k): tuple(v) for k, v in obj["cent"].items()}
    return adjacency, centroids
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tools/supply_hubs/tests/test_graph.py -v`
Expected: PASS (4 passed)

- [ ] **Step 5: Build the REAL graph once and cache it (performance gate)**

Create `tools/supply_hubs/build_cache.py` (a one-shot script, committed for reproducibility):
```python
# tools/supply_hubs/build_cache.py
import time
from tools.supply_hubs.bmp import read_bmp_rgb
from tools.supply_hubs.parse_map import parse_definition
from tools.supply_hubs.graph import build_adjacency, save_graph

t = time.time()
defs = parse_definition("map/definition.csv")
rgb = {(p.r, p.g, p.b): p.id for p in defs.values()}
w, h, px = read_bmp_rgb("map/provinces.bmp")
print(f"bmp {w}x{h} read in {time.time()-t:.1f}s")
adj, cent = build_adjacency(w, h, px, rgb, wrap_x=True)
save_graph("tools/supply_hubs/out/graph.json", adj, cent)
print(f"provinces in graph: {len(adj)}; total {time.time()-t:.1f}s")
```
Run (create the out dir first): `mkdir -p tools/supply_hubs/out && python tools/supply_hubs/build_cache.py`
Expected: prints `bmp 5632x2048`, then a province count near ~13,700 within a couple of minutes. **If this is too slow (>5 min)**, optimize the inner loop (e.g., row-pair scanning with `zip`, or optional numpy path guarded by `try: import numpy`). Record the runtime.

- [ ] **Step 6: Commit**

```bash
git add tools/supply_hubs/graph.py tools/supply_hubs/tests/test_graph.py tools/supply_hubs/build_cache.py
git commit -m "feat(supply-hubs): adjacency graph, centroids, BFS, cache"
```
(`out/` should be git-ignored — add `tools/supply_hubs/out/` to `.gitignore` in this commit.)

---

## Task 5: Classifier — candidates, VP set, crossroads, spacing stats

**Files:**
- Create: `tools/supply_hubs/classify.py`
- Test: `tools/supply_hubs/tests/test_classify.py`

**Interfaces:**
- Consumes: `land_subgraph`, `bfs_hops` (Task 4); `owner_by_province`, `vp_provinces` (Task 3); existing hubs list (Task 2); railway segments (Task 2).
- Produces `candidates(owner_map, provinces, tag="SOV") -> set[int]` = land provinces owned by `tag`.
- Produces `rail_graph(segments) -> dict[int,set[int]]` (consecutive provinces in each segment are linked).
- Produces `crossroads(segments, min_degree=3) -> set[int]` (provinces with rail-degree ≥ `min_degree`).
- Produces `spacing_stats(land_adj, hubs, scope) -> dict` with `{"max":..,"hist":{dist:count}, "uncovered":[pids dist>6]}` over `scope` provinces.

- [ ] **Step 1: Write the failing test**

```python
# tools/supply_hubs/tests/test_classify.py
from tools.supply_hubs.classify import (
    candidates, rail_graph, crossroads, spacing_stats)
from tools.supply_hubs.parse_map import Province


def _p(pid, kind="land"):
    return Province(pid, 0, 0, 0, kind, False, "plains", "0")


def test_candidates_land_owned_only():
    provs = {1: _p(1), 2: _p(2, "sea"), 3: _p(3)}
    owner = {1: "SOV", 2: "SOV", 3: "GER"}
    assert candidates(owner, provs, "SOV") == {1}


def test_rail_graph_and_crossroads():
    segs = [(1, [10, 20, 30]), (1, [40, 20, 50]), (1, [20, 60])]
    rg = rail_graph(segs)
    assert rg[20] == {10, 30, 40, 50, 60}
    assert crossroads(segs, min_degree=3) == {20}


def test_spacing_stats():
    land = {1: {2}, 2: {1, 3}, 3: {2, 4}, 4: {3, 5},
            5: {4, 6}, 6: {5, 7}, 7: {6, 8}, 8: {7}}
    scope = set(land)
    st = spacing_stats(land, {1}, scope)
    assert st["max"] == 7
    assert 8 in st["uncovered"]   # dist 7 > 6
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tools/supply_hubs/tests/test_classify.py -v`
Expected: FAIL (ModuleNotFoundError: classify)

- [ ] **Step 3: Write minimal implementation**

```python
# tools/supply_hubs/classify.py
from collections import Counter
from tools.supply_hubs.graph import bfs_hops


def candidates(owner_map, provinces, tag="SOV"):
    out = set()
    for pid, who in owner_map.items():
        pr = provinces.get(pid)
        if who == tag and pr is not None and pr.kind == "land":
            out.add(pid)
    return out


def rail_graph(segments):
    g = {}
    for _level, provs in segments:
        for a, b in zip(provs, provs[1:]):
            g.setdefault(a, set()).add(b)
            g.setdefault(b, set()).add(a)
    return g


def crossroads(segments, min_degree=3):
    g = rail_graph(segments)
    return {p for p, nb in g.items() if len(nb) >= min_degree}


def spacing_stats(land_adj, hubs, scope, threshold=6):
    dist = bfs_hops(land_adj, set(hubs))
    hist = Counter()
    uncovered = []
    mx = 0
    for p in scope:
        d = dist.get(p)
        if d is None:
            uncovered.append(p)
            continue
        hist[d] += 1
        mx = max(mx, d)
        if d > threshold:
            uncovered.append(p)
    return {"max": mx, "hist": dict(hist), "uncovered": uncovered}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tools/supply_hubs/tests/test_classify.py -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add tools/supply_hubs/classify.py tools/supply_hubs/tests/test_classify.py
git commit -m "feat(supply-hubs): classifier (candidates, crossroads, spacing stats)"
```

---

## Task 6: Hub placement (Approach A — greedy gap-fill + snapping)

**Files:**
- Create: `tools/supply_hubs/place.py`
- Test: `tools/supply_hubs/tests/test_place.py`

**Interfaces:**
- Consumes: `land_adj` (land subgraph restricted to the region of interest), `bfs_hops`, `shortest_path` (Task 4); `candidates`, `crossroads` (Task 5); `vp_provinces` (Task 3); centroids (Task 4).
- Produces `place_hubs(land_adj, scope, existing_hubs, vp_set, crossroad_set, centroids, *, target=6, min_sep=4) -> dict` returning `{"hubs": set[int], "added": [...], "removed": [...], "anchors": set[int]}`.
- Snap priority within the snap radius: VP > crossroad > most-central (min mean-distance to scope, tie-broken by centroid). Min separation enforced in hops via `bfs_hops`.

Algorithm (encode exactly):
1. `anchors = {h for h in existing_hubs if h in vp_set or h in crossroad_set}`.
2. `hubs = set(existing_hubs)`; `movable = hubs - anchors`.
3. **Fill loop:** compute `dist = bfs_hops(land_adj, hubs)`. Find `worst = argmax over scope of dist` (uncovered/unreachable treated as +inf, skip unreachable). If `dist[worst] <= target`: stop. Else gather `snap_pool` = provinces within 2 hops of `worst` (via `bfs_hops(land_adj,{worst},limit=2)`) intersected with `scope`; filter to those whose min-hop to any current hub `>= min_sep`; pick best by priority; if none qualifies, fall back to `worst` itself if it satisfies `min_sep`, else mark `worst` covered (skip) to guarantee termination. Add chosen to `hubs` and `added`.
4. **Prune loop:** for each `m in sorted(movable)`: if some other hub is within `< min_sep` hops of `m` AND removing `m` keeps every scope province that had `m` as nearest still within `target` of another hub, remove `m` (record in `removed`).
5. Return result.

- [ ] **Step 1: Write the failing test**

```python
# tools/supply_hubs/tests/test_place.py
from tools.supply_hubs.place import place_hubs


def _line(n):
    """path 1-2-...-n as land adjacency."""
    adj = {}
    for i in range(1, n + 1):
        adj[i] = set()
        if i > 1:
            adj[i].add(i - 1)
        if i < n:
            adj[i].add(i + 1)
    return adj


def test_fills_gaps_to_target():
    adj = _line(20)
    scope = set(adj)
    res = place_hubs(adj, scope, existing_hubs={1}, vp_set=set(),
                     crossroad_set=set(), centroids={}, target=6, min_sep=4)
    # every scope province must be within 6 of some hub
    from tools.supply_hubs.graph import bfs_hops
    d = bfs_hops(adj, res["hubs"])
    assert max(d[p] for p in scope) <= 6
    assert 1 in res["hubs"]  # seed preserved


def test_snaps_to_vp_when_available():
    adj = _line(20)
    scope = set(adj)
    # put a VP at province 8 so the first fill near the middle prefers it
    res = place_hubs(adj, scope, existing_hubs={1}, vp_set={8},
                     crossroad_set=set(), centroids={}, target=6, min_sep=4)
    assert 8 in res["hubs"]


def test_anchor_on_vp_never_removed():
    adj = _line(8)
    res = place_hubs(adj, set(adj), existing_hubs={1, 2}, vp_set={1},
                     crossroad_set=set(), centroids={}, target=6, min_sep=4)
    assert 1 in res["hubs"]  # 1 is a VP anchor
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tools/supply_hubs/tests/test_place.py -v`
Expected: FAIL (ModuleNotFoundError: place)

- [ ] **Step 3: Write minimal implementation**

```python
# tools/supply_hubs/place.py
from tools.supply_hubs.graph import bfs_hops


def _nearest_hub_dist(land_adj, hubs, who):
    d = bfs_hops(land_adj, {who})
    return min((d[h] for h in hubs if h in d), default=None)


def _centrality(land_adj, p, scope):
    d = bfs_hops(land_adj, {p})
    vals = [d[s] for s in scope if s in d]
    return sum(vals) / len(vals) if vals else float("inf")


def _pick(snap_pool, vp_set, crossroad_set, land_adj, scope, centroids):
    vps = [p for p in snap_pool if p in vp_set]
    if vps:
        return min(vps, key=lambda p: _centrality(land_adj, p, scope))
    xroads = [p for p in snap_pool if p in crossroad_set]
    if xroads:
        return min(xroads, key=lambda p: _centrality(land_adj, p, scope))
    return min(snap_pool, key=lambda p: (_centrality(land_adj, p, scope),
                                         centroids.get(p, (0, 0))))


def place_hubs(land_adj, scope, existing_hubs, vp_set, crossroad_set,
               centroids, *, target=6, min_sep=4):
    anchors = {h for h in existing_hubs if h in vp_set or h in crossroad_set}
    hubs = set(existing_hubs)
    movable = hubs - anchors
    added, removed = [], []
    skipped = set()

    while True:
        dist = bfs_hops(land_adj, hubs)
        worst, worst_d = None, target
        for p in scope:
            if p in skipped:
                continue
            d = dist.get(p)
            if d is None:
                continue  # unreachable from network; skip in pilot
            if d > worst_d:
                worst, worst_d = p, d
        if worst is None:
            break
        local = bfs_hops(land_adj, {worst}, limit=2)
        snap_pool = [p for p in local if p in scope
                     and (_nearest_hub_dist(land_adj, hubs, p) or 99) >= min_sep]
        if snap_pool:
            choice = _pick(snap_pool, vp_set, crossroad_set, land_adj,
                           scope, centroids)
            hubs.add(choice)
            added.append(choice)
        else:
            skipped.add(worst)  # cannot place without violating min_sep

    for m in sorted(movable):
        others = hubs - {m}
        nd = _nearest_hub_dist(land_adj, others, m)
        if nd is not None and nd < min_sep:
            dist_without = bfs_hops(land_adj, others)
            ok = all(dist_without.get(p, 99) <= target for p in scope
                     if p not in skipped)
            if ok:
                hubs.discard(m)
                removed.append(m)

    return {"hubs": hubs, "added": added, "removed": removed, "anchors": anchors}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tools/supply_hubs/tests/test_place.py -v`
Expected: PASS (3 passed). Note: `_centrality` does a BFS per candidate — fine for tests and acceptable for the SOV scope; if the real run is slow, cache per-province BFS or restrict scope to the SOV bounding region (optimize in Task 10, not now).

- [ ] **Step 5: Commit**

```bash
git add tools/supply_hubs/place.py tools/supply_hubs/tests/test_place.py
git commit -m "feat(supply-hubs): greedy hub placement (Approach A)"
```

---

## Task 7: Railway wiring (connect + straighten + contiguity validation)

**Files:**
- Create: `tools/supply_hubs/wire.py`
- Test: `tools/supply_hubs/tests/test_wire.py`

**Interfaces:**
- Consumes: `land_adj`, `shortest_path` (Task 4); existing railway segments (Task 2).
- Produces `network_nodes(segments) -> set[int]` (all provinces on any railway).
- Produces `local_level(segments, near_pid, land_adj) -> int` — level of the segment nearest `near_pid` (BFS over rail-node membership; default 1).
- Produces `connect_hubs(land_adj, segments, new_hubs, network) -> list[tuple[int,list[int]]]` — one new segment per new hub: shortest land path to the nearest network node, at the local level. Skips hubs already on the network.
- Produces `straighten(land_adj, segments, in_scope_set, factor=0.6) -> list[tuple[int,list[int]]]` — for each fully-in-scope segment whose path length > shortest_path length / `factor`, replace with the shortest path (same level). Returns the full updated segment list.
- Produces `validate_contiguous(land_adj, segments) -> list[str]` — list of error strings for any non-adjacent consecutive pair (empty == valid).

- [ ] **Step 1: Write the failing test**

```python
# tools/supply_hubs/tests/test_wire.py
from tools.supply_hubs.wire import (
    network_nodes, connect_hubs, straighten, validate_contiguous)


def _grid_line(n):
    adj = {}
    for i in range(1, n + 1):
        adj[i] = set()
        if i > 1:
            adj[i].add(i - 1)
        if i < n:
            adj[i].add(i + 1)
    return adj


def test_network_nodes():
    segs = [(2, [1, 2, 3]), (1, [3, 4])]
    assert network_nodes(segs) == {1, 2, 3, 4}


def test_connect_new_hub_to_network():
    adj = _grid_line(10)
    segs = [(2, [1, 2, 3])]            # network = {1,2,3}
    new = connect_hubs(adj, segs, new_hubs={6}, network={1, 2, 3})
    assert len(new) == 1
    level, path = new[0]
    assert path[0] == 3 and path[-1] == 6   # connects nearest node 3 -> 6
    assert level == 2                        # inherits local level
    assert validate_contiguous(adj, new) == []


def test_straighten_detour():
    # adjacency where 1-2-3-4 exists AND a direct 1-4 shortcut
    adj = {1: {2, 4}, 2: {1, 3}, 3: {2, 4}, 4: {3, 1}}
    segs = [(1, [1, 2, 3, 4])]   # length 4, shortest is [1,4] length 2
    out = straighten(adj, segs, in_scope_set={1, 2, 3, 4}, factor=0.6)
    assert out[0][1] == [1, 4]


def test_validate_flags_gap():
    adj = {1: {2}, 2: {1}, 5: set()}
    errs = validate_contiguous(adj, [(1, [1, 2, 5])])
    assert errs and "2" in errs[0] and "5" in errs[0]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tools/supply_hubs/tests/test_wire.py -v`
Expected: FAIL (ModuleNotFoundError: wire)

- [ ] **Step 3: Write minimal implementation**

```python
# tools/supply_hubs/wire.py
from tools.supply_hubs.graph import bfs_hops, shortest_path


def network_nodes(segments):
    out = set()
    for _level, provs in segments:
        out.update(provs)
    return out


def local_level(segments, near_pid, land_adj):
    d = bfs_hops(land_adj, {near_pid})
    best_level, best_d = 1, None
    for level, provs in segments:
        md = min((d[p] for p in provs if p in d), default=None)
        if md is not None and (best_d is None or md < best_d):
            best_d, best_level = md, level
    return best_level


def connect_hubs(land_adj, segments, new_hubs, network):
    out = []
    net = set(network)
    for h in new_hubs:
        if h in net:
            continue
        d = bfs_hops(land_adj, {h})
        target = min((n for n in net if n in d), key=lambda n: d[n],
                     default=None)
        if target is None:
            continue  # unreachable; leave for manual review
        path = shortest_path(land_adj, target, h)
        if path and len(path) >= 2:
            out.append((local_level(segments, target, land_adj), path))
            net.update(path)
    return out


def straighten(land_adj, segments, in_scope_set, factor=0.6):
    out = []
    for level, provs in segments:
        if len(provs) >= 3 and all(p in in_scope_set for p in provs):
            sp = shortest_path(land_adj, provs[0], provs[-1])
            if sp and len(sp) < len(provs) * factor:
                out.append((level, sp))
                continue
        out.append((level, provs))
    return out


def validate_contiguous(land_adj, segments):
    errs = []
    for level, provs in segments:
        for a, b in zip(provs, provs[1:]):
            if b not in land_adj.get(a, ()):
                errs.append(f"segment level {level}: {a} -> {b} not adjacent")
    return errs
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tools/supply_hubs/tests/test_wire.py -v`
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add tools/supply_hubs/wire.py tools/supply_hubs/tests/test_wire.py
git commit -m "feat(supply-hubs): railway wiring, straighten, contiguity validation"
```

---

## Task 8: Emit — rewrite SOV-only lines + validation gate

**Files:**
- Create: `tools/supply_hubs/emit.py`
- Test: `tools/supply_hubs/tests/test_emit.py`

**Interfaces:**
- Consumes: existing hubs/segments + owner map + new hub set + new/updated segments.
- Produces `emit_supply_nodes(original_hubs, new_sov_hubs, owner_map) -> list[str]` — keeps every non-SOV hub line verbatim (`1 <pid>`), then emits one `1 <pid>` line per province in `new_sov_hubs` (sorted). Returns list of lines (no trailing spaces).
- Produces `emit_railways(original_segments, new_segments, owner_map) -> list[str]` — keeps every segment that is NOT fully-SOV verbatim; replaces fully-SOV segments with `new_segments` (which are the rewritten in-scope set). Each line `"<level> <count> <p1> <p2> ...".`
- Produces `is_sov_segment(provs, owner_map) -> bool` (all provinces SOV-owned).
- Produces `validate_output(provinces, owner_map, land_adj, hub_lines, rail_lines) -> list[str]` — errors if any hub province is missing/non-land/non-SOV, any duplicate hub, any railway non-contiguous, or any level outside 1–5.

- [ ] **Step 1: Write the failing test**

```python
# tools/supply_hubs/tests/test_emit.py
from tools.supply_hubs.emit import (
    emit_supply_nodes, emit_railways, is_sov_segment)


def test_emit_supply_nodes_keeps_non_sov():
    owner = {10: "SOV", 11: "GER", 20: "SOV"}
    # original hubs: 11 (GER, keep) and 10 (SOV, replace by new set {20})
    lines = emit_supply_nodes([11, 10], {20}, owner)
    assert "1 11" in lines       # non-SOV kept
    assert "1 20" in lines       # new SOV hub
    assert "1 10" not in lines   # old SOV hub dropped
    assert all(not l.endswith(" ") for l in lines)


def test_is_sov_segment():
    owner = {1: "SOV", 2: "SOV", 3: "GER"}
    assert is_sov_segment([1, 2], owner) is True
    assert is_sov_segment([1, 3], owner) is False


def test_emit_railways_replaces_only_sov():
    owner = {1: "SOV", 2: "SOV", 7: "GER", 8: "GER"}
    original = [(2, [1, 2]), (1, [7, 8])]
    new_sov = [(2, [1, 2, 2])]  # rewritten in-scope set (illustrative)
    lines = emit_railways(original, new_sov, owner)
    assert "1 2 7 8" in lines             # non-SOV kept verbatim
    assert any(l.startswith("2 ") and l.endswith("2") for l in lines)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tools/supply_hubs/tests/test_emit.py -v`
Expected: FAIL (ModuleNotFoundError: emit)

- [ ] **Step 3: Write minimal implementation**

```python
# tools/supply_hubs/emit.py
from tools.supply_hubs.wire import validate_contiguous


def emit_supply_nodes(original_hubs, new_sov_hubs, owner_map):
    lines = []
    for pid in original_hubs:
        if owner_map.get(pid) != "SOV":
            lines.append(f"1 {pid}")
    for pid in sorted(new_sov_hubs):
        lines.append(f"1 {pid}")
    return lines


def is_sov_segment(provs, owner_map):
    return all(owner_map.get(p) == "SOV" for p in provs)


def _fmt_segment(level, provs):
    return f"{level} {len(provs)} " + " ".join(str(p) for p in provs)


def emit_railways(original_segments, new_segments, owner_map):
    lines = []
    for level, provs in original_segments:
        if not is_sov_segment(provs, owner_map):
            lines.append(_fmt_segment(level, provs))
    for level, provs in new_segments:
        lines.append(_fmt_segment(level, provs))
    return lines


def validate_output(provinces, owner_map, land_adj, hub_lines, rail_lines):
    errs = []
    seen = set()
    for l in hub_lines:
        pid = int(l.split()[1])
        if pid in seen:
            errs.append(f"duplicate hub {pid}")
        seen.add(pid)
        pr = provinces.get(pid)
        if pr is None or pr.kind != "land":
            errs.append(f"hub {pid} not a land province")
    segs = []
    for l in rail_lines:
        toks = l.split()
        level = int(toks[0])
        if not (1 <= level <= 5):
            errs.append(f"railway bad level {level}")
        segs.append((level, [int(t) for t in toks[2:]]))
    errs.extend(validate_contiguous(land_adj, segs))
    return errs
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tools/supply_hubs/tests/test_emit.py -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add tools/supply_hubs/emit.py tools/supply_hubs/tests/test_emit.py
git commit -m "feat(supply-hubs): emit SOV-only output + validation gate"
```

---

## Task 9: Render — SVG overlay + markdown diff report

**Files:**
- Create: `tools/supply_hubs/render.py`
- Test: `tools/supply_hubs/tests/test_render.py`

**Interfaces:**
- Produces `render_svg(path, centroids, *, old_hubs, new_hubs, segments, vps, width=5632, height=2048, scale=0.25)` — writes an SVG with: railway segments as polylines (province centroids), old hubs as grey dots, new hubs as red dots, anchor/kept hubs as green dots, VP provinces as small blue marks. Pure string output, no deps.
- Produces `diff_report(before_stats, after_stats, added, removed) -> str` (markdown): counts + before/after spacing histograms.

Render is mostly visual; the test only checks it produces well-formed, non-empty SVG/markdown so the stage can't silently no-op.

- [ ] **Step 1: Write the failing test**

```python
# tools/supply_hubs/tests/test_render.py
from tools.supply_hubs.render import render_svg, diff_report


def test_render_svg_writes_file(tmp_path):
    p = tmp_path / "o.svg"
    render_svg(str(p), centroids={1: (10, 10), 2: (40, 40)},
               old_hubs={1}, new_hubs={2}, segments=[(1, [1, 2])],
               vps={1: 5}, width=100, height=100, scale=1.0)
    txt = p.read_text(encoding="utf-8")
    assert txt.startswith("<svg") or txt.lstrip().startswith("<?xml")
    assert "polyline" in txt and "circle" in txt


def test_diff_report_markdown():
    before = {"max": 9, "hist": {1: 2, 9: 1}, "uncovered": [7]}
    after = {"max": 6, "hist": {1: 3, 6: 1}, "uncovered": []}
    md = diff_report(before, after, added=[5, 6], removed=[3])
    assert "added" in md.lower() and "2" in md  # 2 added
    assert "removed" in md.lower()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tools/supply_hubs/tests/test_render.py -v`
Expected: FAIL (ModuleNotFoundError: render)

- [ ] **Step 3: Write minimal implementation**

```python
# tools/supply_hubs/render.py
def render_svg(path, centroids, *, old_hubs, new_hubs, segments, vps,
               width=5632, height=2048, scale=0.25):
    W, H = width * scale, height * scale

    def xy(pid):
        c = centroids.get(pid)
        return None if c is None else (c[0] * scale, c[1] * scale)

    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" '
             f'height="{H:.0f}" viewBox="0 0 {W:.0f} {H:.0f}">',
             f'<rect width="{W:.0f}" height="{H:.0f}" fill="#0b1320"/>']
    for _level, provs in segments:
        pts = [xy(p) for p in provs]
        pts = [q for q in pts if q]
        if len(pts) >= 2:
            d = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
            parts.append(f'<polyline points="{d}" fill="none" '
                         f'stroke="#888" stroke-width="0.6"/>')
    for pid in vps:
        q = xy(pid)
        if q:
            parts.append(f'<rect x="{q[0]-0.8:.1f}" y="{q[1]-0.8:.1f}" '
                         f'width="1.6" height="1.6" fill="#3b7"/>')
    for group, color in ((old_hubs - new_hubs, "#999"),
                         (old_hubs & new_hubs, "#2c2"),
                         (new_hubs - old_hubs, "#e33")):
        for pid in group:
            q = xy(pid)
            if q:
                parts.append(f'<circle cx="{q[0]:.1f}" cy="{q[1]:.1f}" '
                             f'r="1.4" fill="{color}"/>')
    parts.append("</svg>")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))


def diff_report(before_stats, after_stats, added, removed):
    def hist(h):
        return " ".join(f"{k}:{h['hist'].get(k,0)}"
                        for k in range(0, max(h["hist"] or [0]) + 1))
    return (
        f"# Soviet supply hub diff\n\n"
        f"- hubs added: {len(added)}\n"
        f"- hubs removed: {len(removed)}\n"
        f"- max hop-distance before: {before_stats['max']} -> "
        f"after: {after_stats['max']}\n"
        f"- uncovered (>6) before: {len(before_stats['uncovered'])} -> "
        f"after: {len(after_stats['uncovered'])}\n\n"
        f"## spacing histogram (dist:count)\n"
        f"- before: {hist(before_stats)}\n"
        f"- after:  {hist(after_stats)}\n")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tools/supply_hubs/tests/test_render.py -v`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add tools/supply_hubs/render.py tools/supply_hubs/tests/test_render.py
git commit -m "feat(supply-hubs): SVG overlay + diff report"
```

---

## Task 10: Orchestrator + end-to-end dry run on real data

**Files:**
- Create: `tools/supply_hubs/run_pilot.py`
- Modify: `.gitignore` (ensure `tools/supply_hubs/out/` ignored)

**Interfaces:**
- Consumes every module above.
- Produces a CLI: `python tools/supply_hubs/run_pilot.py [--apply]`. Without `--apply`, writes proposed `supply_nodes.txt`, `railways.txt`, `pilot.svg`, `diff.md` into `tools/supply_hubs/out/`. With `--apply`, also overwrites `map/supply_nodes.txt` and `map/railways.txt`.

Orchestration order:
1. Parse definition, states, supply_nodes, railways. Build `owner_map`, `vp_map`.
2. Load cached graph (`out/graph.json`) — error out with a clear message if missing (run `build_cache.py` first).
3. `land_adj = land_subgraph(adjacency, provinces)`.
4. `scope = candidates(owner_map, provinces, "SOV")`. **Performance scope:** restrict `land_adj` passed to placement to the connected land component(s) touching `scope` plus a small hop margin, so per-candidate BFS stays cheap.
5. `xroads = crossroads(segments)`, `vp_set = set(vp_map)`.
6. `existing_sov_hubs = [h for h in supply_nodes if owner_map.get(h)=="SOV"]`.
7. `before = spacing_stats(land_adj, existing_sov_hubs, scope)`.
8. `placed = place_hubs(region_adj, scope, existing_sov_hubs, vp_set, xroads, centroids)`.
9. Railways: `network = network_nodes(segments)`; `new_links = connect_hubs(land_adj, segments, placed["added"], network)`; build the in-scope segment set = (fully-SOV existing segments after `straighten`) + `new_links`; the rest stay verbatim via `emit_railways`.
10. `after = spacing_stats(land_adj, placed["hubs"], scope)`.
11. Emit lines, run `validate_output`; **abort on any error** (print them).
12. Write `out/` artifacts always; if `--apply`, write `map/` files.
13. Print summary (added/removed/uncovered before/after) and the artifact paths.

- [ ] **Step 1: Write the orchestrator**

```python
# tools/supply_hubs/run_pilot.py
import os
import sys
from tools.supply_hubs.parse_map import (
    parse_definition, parse_supply_nodes, parse_railways)
from tools.supply_hubs.parse_states import (
    load_states, owner_by_province, vp_provinces)
from tools.supply_hubs.graph import load_graph, land_subgraph, bfs_hops
from tools.supply_hubs.classify import candidates, crossroads, spacing_stats
from tools.supply_hubs.place import place_hubs
from tools.supply_hubs.wire import network_nodes, connect_hubs, straighten
from tools.supply_hubs.emit import (
    emit_supply_nodes, emit_railways, is_sov_segment, validate_output)
from tools.supply_hubs.render import render_svg, diff_report

OUT = "tools/supply_hubs/out"


def region_restrict(land_adj, scope, margin=8):
    keep = set(bfs_hops(land_adj, set(scope), limit=margin))
    return {a: {b for b in nb if b in keep}
            for a, nb in land_adj.items() if a in keep}


def main(apply=False):
    os.makedirs(OUT, exist_ok=True)
    provinces = parse_definition("map/definition.csv")
    states = load_states("history/states")
    owner = owner_by_province(states)
    vp_map = vp_provinces(states)
    hubs0 = parse_supply_nodes("map/supply_nodes.txt")
    segs0 = parse_railways("map/railways.txt")

    if not os.path.exists(f"{OUT}/graph.json"):
        sys.exit("Missing out/graph.json — run build_cache.py first.")
    adjacency, centroids = load_graph(f"{OUT}/graph.json")
    land_adj = land_subgraph(adjacency, provinces)

    scope = candidates(owner, provinces, "SOV")
    region_adj = region_restrict(land_adj, scope)
    xroads = crossroads(segs0)
    vp_set = set(vp_map)
    sov_hubs = [h for h in hubs0 if owner.get(h) == "SOV"]

    before = spacing_stats(region_adj, sov_hubs, scope)
    placed = place_hubs(region_adj, scope, sov_hubs, vp_set, xroads, centroids)

    network = network_nodes(segs0)
    new_links = connect_hubs(region_adj, segs0, placed["added"], network)
    straightened = straighten(region_adj,
                              [(lv, pr) for lv, pr in segs0
                               if is_sov_segment(pr, owner)],
                              scope)
    new_sov_segments = straightened + new_links

    after = spacing_stats(region_adj, placed["hubs"], scope)

    hub_lines = emit_supply_nodes(hubs0, placed["hubs"], owner)
    rail_lines = emit_railways(segs0, new_sov_segments, owner)
    errs = validate_output(provinces, owner, land_adj, hub_lines, rail_lines)
    if errs:
        print("VALIDATION ERRORS:")
        print("\n".join(errs[:50]))
        sys.exit(1)

    open(f"{OUT}/supply_nodes.txt", "w", encoding="utf-8").write(
        "\n".join(hub_lines) + "\n")
    open(f"{OUT}/railways.txt", "w", encoding="utf-8").write(
        "\n".join(rail_lines) + "\n")
    render_svg(f"{OUT}/pilot.svg", centroids, old_hubs=set(sov_hubs),
               new_hubs=placed["hubs"], segments=new_sov_segments, vps=vp_map)
    open(f"{OUT}/diff.md", "w", encoding="utf-8").write(
        diff_report(before, after, placed["added"], placed["removed"]))

    print(f"added {len(placed['added'])} removed {len(placed['removed'])} "
          f"hubs; uncovered {len(before['uncovered'])} -> "
          f"{len(after['uncovered'])}; artifacts in {OUT}/")
    if apply:
        open("map/supply_nodes.txt", "w", encoding="utf-8").write(
            "\n".join(hub_lines) + "\n")
        open("map/railways.txt", "w", encoding="utf-8").write(
            "\n".join(rail_lines) + "\n")
        print("APPLIED to map/.")


if __name__ == "__main__":
    main(apply="--apply" in sys.argv)
```

- [ ] **Step 2: Ensure full test suite passes**

Run: `python -m pytest tools/supply_hubs/tests/ -v`
Expected: all tests PASS.

- [ ] **Step 3: Build the cache (if not already) and dry-run on real data**

```bash
mkdir -p tools/supply_hubs/out
python tools/supply_hubs/build_cache.py
python tools/supply_hubs/run_pilot.py
```
Expected: prints an "added/removed" summary with `uncovered` dropping toward 0; writes `out/supply_nodes.txt`, `out/railways.txt`, `out/pilot.svg`, `out/diff.md`. **No validation errors.** Open `out/pilot.svg` and `out/diff.md` and eyeball: hubs spread across SOV land, new red dots filling gaps, railways connecting them.

- [ ] **Step 4: Review checkpoint (STOP — hand to user)**

Do NOT run `--apply` yet. Present `out/pilot.svg` + `out/diff.md` to the user. Iterate on parameters (`target`, `min_sep`, `straighten factor`, crossroad `min_degree`) based on feedback. Only after the user approves the diagnostics do the next step.

- [ ] **Step 5: Apply + commit (after user approval)**

```bash
python tools/supply_hubs/run_pilot.py --apply
git add tools/supply_hubs/run_pilot.py .gitignore map/supply_nodes.txt map/railways.txt
git commit -m "feat(supply-hubs): apply Soviet supply-hub pilot"
```
Then the user loads a **new game** and verifies SOV supply in-game. Capture any in-game issues as follow-up parameter tweaks (re-run `--apply`, re-commit).

---

## Self-Review (completed during planning)

**Spec coverage:**
- Rule 1 (5–6 spacing) → Task 6 fill loop + Task 5 `spacing_stats`. ✓
- Rule 2 (conservative, anchors on VP/crossroad) → Task 6 `anchors`/`movable`/prune. ✓
- Rule 3 (VP > crossroad > central snapping) → Task 6 `_pick`. ✓
- Rule 4 (connect > reroute, straighten, keep level) → Task 7 `connect_hubs`/`straighten`/`local_level`. ✓
- Rule 5 (ignore impassable/unowned) → Task 5 `candidates` (SOV-owned land only); impassable handled by land filter (spec §7-R2). ✓
- Rule 6 (scarcity) → deferred per pilot decision; `target` is a single knob ready to vary by region later. ✓
- "Only SOV lines change" → Task 8 `emit_*` keep non-SOV verbatim. ✓
- "buildings.txt untouched" → never written; noted in constraints. ✓
- Diagnostics + diff + new-game verification → Tasks 9–10. ✓
- East–west wrap (spec §7-R5) → Task 4 `build_adjacency(wrap_x=True)` + test. ✓

**Placeholder scan:** none ("verify during pilot" notes are real verification steps, not deferred code).

**Type consistency:** `Province` namedtuple shared (Tasks 2,4,5,8); `land_adj` dict[int,set[int]] consistent across Tasks 4–8; segment tuple `(level, [provs])` consistent across Tasks 2,7,8,10; `place_hubs` return keys (`hubs/added/removed/anchors`) consumed consistently in Task 10. ✓

**Known tuning risks carried into execution (not blockers):**
- Placement per-candidate BFS cost → mitigated by `region_restrict`; optimize further only if the real run is slow.
- `straighten` `factor` and crossroad `min_degree` are first-cut values to tune against `out/pilot.svg`.
- Unreachable SOV provinces (islands with no land path to network) are skipped in the pilot and surfaced via `after["uncovered"]` for manual review.
