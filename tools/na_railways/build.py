"""Rebuild map/railways.txt for North Africa as a historical (1936-39) network.

Usage:  python build.py [--apply] [--out DIR]
Default is a dry run: writes preview PNGs, report.md and railways.new.txt into --out.
--apply additionally overwrites map/railways.txt (new game required in HOI4).
"""
import os
import sys
import math
import mapdata as M
import geo
import render
import network
from core import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
APPLY = '--apply' in sys.argv
if '--out' in sys.argv:
    OUT = sys.argv[sys.argv.index('--out') + 1]
os.makedirs(OUT, exist_ok=True)

# ---- route every line
cache = {}
line_paths = []
report = []
for ln in network.L:
    st = []
    for name, lat, lon in ln['stations']:
        pid, how = resolve(name, lat, lon)
        st.append((name, pid, how, proj(lat, lon)))
        cache[(name, pid)] = how
    path = []
    notes = []
    for (n1, p1, h1, a1), (n2, p2, h2, a2) in zip(st, st[1:]):
        if p1 == p2:
            notes.append(f"{n1}/{n2} share province {p1}")
            seg = [p1]
        else:
            seg = geo.route(ADJ, CENT, PASS, p1, p2, CENT[p1], CENT[p2], width=12.0)
            if seg is None:
                notes.append(f"NO ROUTE {n1}({p1}) -> {n2}({p2})")
                seg = [p1]
        if path and path[-1] == seg[0]:
            path.extend(seg[1:])
        else:
            path.extend(seg)
    line_paths.append((ln, path, st, notes))
    report.append(f"### {ln['name']}  (level {ln['level']})")
    report.append('stations: ' + '; '.join(f"{n}={pid}[{how}]" for n, pid, how, _ in st))
    report.append('path: ' + ' - '.join(str(p) for p in path))
    devs = []
    pts = [a for *_, a in st]
    for p in path:
        d = min(geo.seg_dev(CENT[p], a, b) for a, b in zip(pts, pts[1:])) if len(pts) > 1 else 0
        devs.append(d)
    if devs:
        report.append(f"max deviation from station polyline: {max(devs):.0f}px (~{max(devs)*6.5:.0f} km)")
    for n in notes:
        report.append('NOTE: ' + n)
    report.append('')

# ---- final link levels
levels = {}
for ln, path, _, _ in line_paths:
    for a, b in zip(path, path[1:]):
        if a == b:
            continue
        k = (min(a, b), max(a, b))
        levels[k] = max(levels.get(k, 0), ln['level'])

new_rows = []
emitted = set()
for ln, path, _, _ in line_paths:
    cur = []
    for a, b in zip(path, path[1:]):
        if a == b:
            continue
        k = (min(a, b), max(a, b))
        ok = (levels[k] == ln['level'] and k not in emitted)
        if ok:
            if cur and cur[-1] == a and len(cur) < 12:
                cur.append(b)
            else:
                if len(cur) >= 2:
                    new_rows.append((ln['level'], cur))
                cur = [a, b]
            emitted.add(k)
        else:
            if len(cur) >= 2:
                new_rows.append((ln['level'], cur))
            cur = []
    if len(cur) >= 2:
        new_rows.append((ln['level'], cur))

# ---- strip old in-region links
src = os.path.join(M.ROOT, 'map', 'railways.txt')
raw = open(src, 'rb').read()
crlf = b'\r\n' in raw
old_rows = []
for ln in raw.decode('utf-8').splitlines():
    t = ln.split()
    if t:
        old_rows.append((int(t[0]), list(map(int, t[2:]))))

kept, dropped_links, kept_links = [], 0, 0
for lv, path in old_rows:
    cur = [path[0]]
    for a, b in zip(path, path[1:]):
        if a in INSIDE or b in INSIDE:
            dropped_links += 1
            if len(cur) >= 2:
                kept.append((lv, cur))
            cur = [b]
        else:
            kept_links += 1
            cur.append(b)
    if len(cur) >= 2:
        kept.append((lv, cur))

# keep the existing Sinai->Palestine boundary row so the new Sinai line joins Palestine's network
final_rows = kept + new_rows
nl = '\r\n' if crlf else '\n'
text = nl.join(f"{lv} {len(p)} " + ' '.join(map(str, p)) + ' ' for lv, p in final_rows) + nl
open(os.path.join(OUT, 'railways.new.txt'), 'w', newline='').write(text)

summary = [f"old rows {len(old_rows)}, kept outside rows {len(kept)} ({kept_links} links), dropped in-region/boundary links {dropped_links}",
           f"new rows {len(new_rows)} ({len(levels)} links)", f"final rows {len(final_rows)}"]
open(os.path.join(OUT, 'report.md'), 'w', encoding='utf-8').write('\n'.join(summary) + '\n\n' + '\n'.join(report))
print('\n'.join(summary))

# ---- previews
VIEWS = {'maghreb_west': ((2640, 770, 2860, 900), 5), 'maghreb_east': ((2840, 740, 3060, 880), 5),
         'libya': ((2990, 820, 3260, 940), 4), 'egypt': ((3230, 840, 3390, 1030), 6),
         'sudan': ((3260, 1030, 3420, 1250), 5)}
old_links = []
for lv, path in old_rows:
    for a, b in zip(path, path[1:]):
        if a in INSIDE or b in INSIDE:
            old_links.append((a, b))
for vname, (box, sc) in VIEWS.items():
    cv = render.Canvas(R, box, sc)
    for a, b in old_links:
        if a in CENT and b in CENT:
            cv.line(CENT[a], CENT[b], (160, 160, 160), 1)
    cols = {1: (30, 90, 220), 2: (220, 110, 0), 3: (200, 0, 0)}
    for (a, b), lv in levels.items():
        if a in CENT and b in CENT:
            cv.line(CENT[a], CENT[b], cols.get(lv, (0, 0, 0)), 3)
    seen = set()
    for ln, path, st, _ in line_paths:
        for p in path:
            c = CENT.get(p)
            if c and box[0] <= c[0] <= box[2] and box[1] <= c[1] <= box[3] and p not in seen:
                seen.add(p)
                cv.dot(c, (0, 0, 0), 2)
                cv.text(c, str(p), (0, 0, 130), 1)
    cv.save(os.path.join(OUT, f'view_{vname}.png'))

if APPLY:
    open(src, 'w', newline='').write(text)
    print('APPLIED to', src)
