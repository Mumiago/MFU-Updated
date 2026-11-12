"""Place historically important supply hubs across North Africa, spaced apart.

Usage: python hubs.py [--apply] [--out DIR]
Dry run by default (report.md + preview PNGs + supply_nodes.new.txt in --out).
--apply rewrites map/supply_nodes.txt (new game required).
Existing region hubs are kept as spacing anchors, except those listed in REPLACE.
"""
import os
import sys
import math
import collections
import mapdata as M
import geo
import render
from core import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
APPLY = '--apply' in sys.argv
if '--out' in sys.argv:
    OUT = sys.argv[sys.argv.index('--out') + 1]
os.makedirs(OUT, exist_ok=True)

KM_PER_PX = 6.0
# min km to any other hub, by importance (5 capital/major, 4 pivot, 3 secondary, 2 minor)
MIN_KM = {5: 110, 4: 150, 3: 180, 2: 230}

# (name, lat, lon, score, pinned province or None, why)
CANDIDATES = [
    ('Cairo', 30.04, 31.24, 5, 7011, 'capital; British Middle East base and rail hub'),
    ('Marsa Matruh', 31.35, 27.23, 4, 11967, 'terminus of the Alexandria-Matruh railway (1936); Western Desert advanced base'),
    ('Al Jaghbub', 29.75, 24.52, 4, 13244, 'Giarabub oasis fortress on the Egypt-Libya frontier'),
    ('Constantine', 36.37, 6.61, 4, 12051, 'eastern Algerian rail junction and base (Ouled Rahmoun gauge break)'),
    ('Tebessa', 35.40, 8.12, 4, None, 'Torch/Tunisia forward supply base and rail terminus'),
    ('Aswan', 24.09, 32.90, 4, 11999, 'Egyptian railhead; Shellal transfer to the Nile steamers for Sudan'),
    ('Port Sudan', 19.62, 37.22, 4, 12725, 'Sudan\'s only real port and railway terminus on the Red Sea'),
    ('El Alamein', 30.83, 28.95, 4, 1071, 'railway halt, box and pipeline terminus (1942)'),
    ('Tunis', 36.80, 10.18, 5, 11969, 'capital and standard/metre-gauge junction'),
    ('Sfax', 34.74, 10.76, 4, 7162, 'phosphate port and rail hub'),
    ('Marrakech', 31.63, -8.01, 3, 4108, 'southern Morocco rail terminus and capital'),
    ('Fez', 34.03, -5.00, 3, None, 'inland Moroccan rail junction (Taza gap)'),
    ('Oujda', 34.68, -1.91, 3, None, 'Moroccan-Algerian frontier rail junction'),
    ('Setif', 36.19, 5.41, 3, None, 'highland rail town; Torch LOC HQ moved here 28 Nov 1942'),
    ('Sirte', 31.21, 16.59, 3, None, 'midpoint of the Via Balbia between Tripoli and Benghazi'),
    ('Jalo', 29.03, 21.55, 3, 10785, 'Jalo/Augila oases: Italian garrison, LRDG base'),
    ('Kufra', 24.20, 23.30, 3, None, 'deep-desert oasis group; Free French/LRDG/SDF base'),
    ('Sebha', 27.04, 14.43, 3, None, 'Fezzan capital and Italian Saharan garrison'),
    ('Asyut', 27.18, 31.18, 3, 11974, 'Upper Egypt rail and Nile hub'),
    ('Atbara', 17.70, 33.97, 3, None, 'Sudan Railways HQ/workshops; junction for Port Sudan'),
    ('Kassala', 15.45, 36.40, 3, None, 'eastern Sudan rail junction at the Eritrean frontier'),
    ('El Obeid', 13.18, 30.22, 3, 10827, 'western Sudan railhead (Kordofan)'),
    ('Derna', 32.77, 22.64, 3, 1204, 'Cyrenaican port and airfield'),
    ('Suez', 29.97, 32.55, 3, 4073, 'Red Sea end of the Canal'),
    ('Kasserine', 35.17, 8.83, 3, 1141, 'Tunisian front junction (Feb 1943)'),
    ('Siwa', 29.20, 25.52, 3, 13242, 'oasis, LRDG base'),
    ('Sidi Barrani', 31.60, 25.92, 2, 9989, 'coastal village next to Matruh (user: too close)'),
    ('El Fasher', 13.63, 25.35, 2, None, 'Darfur capital; Takoradi air route stage'),
    ('Colomb-Bechar', 31.62, -2.22, 2, None, 'Saharan narrow-gauge railhead'),
    ('Biskra', 34.85, 5.73, 2, None, 'Saharan gateway and railhead'),
    ('Misrata', 32.38, 15.09, 2, None, 'Tripolitanian port'),
    ('Kharga', 25.45, 30.55, 2, None, 'Egyptian Western Oases railway terminus'),
]
FORCE_SKIP = {'Sidi Barrani'}
REPLACE = {'Marsa Matruh': [7079]}      # Sollum hub is 2 hops from Matruh: Matruh replaces it

# ---- supply_node slots per province (buildings.txt positions -> province raster)
SLOTS = collections.Counter()
SLOTPOS = collections.defaultdict(list)
for ln in open(os.path.join(M.ROOT, 'map', 'buildings.txt'), encoding='utf-8', errors='replace'):
    if ';supply_node;' in ln:
        p = ln.split(';')
        x, y = float(p[2]), 2048 - float(p[4])
        pid = R.at(x, y)
        SLOTS[pid] += 1
        SLOTPOS[pid].append((x, y))

src = os.path.join(M.ROOT, 'map', 'supply_nodes.txt')
raw = open(src, 'rb').read().decode('utf-8')
crlf = '\r\n' in raw
all_hubs = [int(l.split()[1]) for l in raw.splitlines() if l.strip()]
assert all_hubs == sorted(all_hubs), 'supply_nodes.txt not sorted'
existing = [h for h in all_hubs if h in INSIDE]
hubs = {h: 'existing' for h in existing}
removed = []


def km(p, q):
    return math.hypot(CENT[p][0] - CENT[q][0], CENT[p][1] - CENT[q][1]) * KM_PER_PX


def slot_km(pid, target):
    return min(math.hypot(x - target[0], y - target[1]) for x, y in SLOTPOS[pid]) * KM_PER_PX


def pick_province(pin, lat, lon, taken):
    """Best province (the pinned/resolved one or an adjacent one) whose supply_node slot is nearest the real place."""
    target = proj(lat, lon)
    base = pin if pin else resolve('?', lat, lon)[0]
    opts = []
    for q in [base] + sorted(ADJ.get(base, ())):
        if q in PASS and q in INSIDE and q in P2S and SLOTS[q] > 0 and q not in taken:
            opts.append((slot_km(q, target) - (35 if q == base else 0), q))
    if not opts:
        return None, f"{base}: no usable province or neighbour"
    opts.sort()
    q = opts[0][1]
    note = '' if q == base else f"(province {base} unusable; using neighbour {q})"
    return q, f"{note} slot {slot_km(q, target):.0f} km from the real place"


log = []
new_hubs = []
order = sorted(range(len(CANDIDATES)), key=lambda i: (-CANDIDATES[i][3], i))
for i in order:
    name, lat, lon, score, pin, why = CANDIDATES[i]
    if name in FORCE_SKIP:
        log.append(f"SKIP  {name}: excluded by request ({why})")
        continue
    pid, note = pick_province(pin, lat, lon, set(hubs))
    if pid is None:
        log.append(f"SKIP  {name}: {note}")
        continue
    drop = [h for h in REPLACE.get(name, []) if h in hubs]
    others = [h for h in hubs if h not in drop]
    near = min(others, key=lambda h: km(pid, h)) if others else None
    d = km(pid, near) if near else 1e9
    if near and (d < MIN_KM[score] or near == pid):
        nl = VP.get(near) or near
        log.append(f"SKIP  {name} (prov {pid}, score {score}): {d:.0f} km from hub {near} {nl} < {MIN_KM[score]} km")
        continue
    for h in drop:
        removed.append(h)
        del hubs[h]
        log.append(f"REMOVE hub {h} {VP.get(h) or ''} (replaced by {name})")
    hubs[pid] = name
    new_hubs.append(pid)
    log.append(f"ADD   {name}: province {pid} {VP.get(pid) or ''} {note}  nearest other hub {d:.0f} km  [{why}]")

# ---- write outputs
final = sorted((set(all_hubs) - set(removed)) | set(new_hubs))
nl = '\r\n' if crlf else '\n'
text = ''.join(f"1 {h} {nl}" for h in final)
open(os.path.join(OUT, 'supply_nodes.new.txt'), 'w', newline='').write(text)

# region summary with pairwise nearest distances
summ = ["hubs in region before: %d, removed %d, added %d, after %d" % (len(existing), len(removed), len(new_hubs), len(hubs))]
for h in sorted(hubs, key=lambda p: CENT[p][0]):
    others = [o for o in hubs if o != h]
    nn = min(others, key=lambda o: km(h, o))
    lat, lon = geo.unproject(*CENT[h])
    summ.append(f"{h:6d} {hubs[h]:14s} {VP.get(h) or '':16s} ({lat:5.1f},{lon:6.1f}) nearest {nn} {km(h, nn):4.0f} km {'NEW' if h in new_hubs else ''}")
open(os.path.join(OUT, 'hubs_report.md'), 'w', encoding='utf-8').write('\n'.join(summ) + '\n\n' + '\n'.join(log) + '\n')
print('\n'.join(log))
print()
print('\n'.join(summ))

VIEWS = {'west': ((2540, 760, 3000, 960), 3), 'center': ((2960, 800, 3320, 1000), 3), 'east_sudan': ((3200, 840, 3500, 1260), 2)}
for vname, (box, sc) in VIEWS.items():
    cv = render.Canvas(R, box, sc)
    for h in hubs:
        c = CENT[h]
        if box[0] <= c[0] <= box[2] and box[1] <= c[1] <= box[3]:
            cv.dot(c, (200, 0, 0) if h in new_hubs else (0, 60, 220), 5)
            cv.text(c, str(h), (0, 0, 0), 1)
    for h in removed:
        c = CENT[h]
        if box[0] <= c[0] <= box[2] and box[1] <= c[1] <= box[3]:
            cv.dot(c, (0, 0, 0), 4)
    cv.save(os.path.join(OUT, f'hubs_{vname}.png'))

if APPLY:
    open(src, 'w', newline='').write(text)
    print('APPLIED to', src)
