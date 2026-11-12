"""Read HOI4 map data (definition.csv, provinces.bmp, state files) in pure Python."""
import os
import re
import struct
import pickle
from itertools import groupby

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
CACHE = os.path.join(os.path.dirname(__file__), 'cache.pkl')


def load_definition():
    prov = {}
    with open(os.path.join(ROOT, 'map', 'definition.csv'), encoding='utf-8', errors='replace') as f:
        for line in f:
            p = line.strip().split(';')
            if len(p) < 8 or not p[0].isdigit():
                continue
            pid = int(p[0])
            prov[pid] = dict(rgb=(int(p[1]), int(p[2]), int(p[3])), type=p[4], coastal=p[5] == 'true',
                             terrain=p[6], continent=int(p[7]) if p[7].isdigit() else 0)
    return prov


def scan_bmp(prov):
    """Return per-province area/centroid (image coords, y down) for the whole map."""
    color2id = {v['rgb']: k for k, v in prov.items()}
    path = os.path.join(ROOT, 'map', 'provinces.bmp')
    with open(path, 'rb') as f:
        hdr = f.read(54)
        w, h = struct.unpack('<ii', hdr[18:26])
        off = struct.unpack('<I', hdr[10:14])[0]
        rowsize = (w * 3 + 3) // 4 * 4
        f.seek(off)
        data = f.read(rowsize * h)
    area, sx, sy = {}, {}, {}
    minx, maxx, miny, maxy = {}, {}, {}, {}
    for file_row in range(h):
        y = h - 1 - file_row
        row = data[file_row * rowsize: file_row * rowsize + w * 3]
        b, g, r = row[0::3], row[1::3], row[2::3]
        x = 0
        for col, grp in groupby(zip(r, g, b)):
            n = sum(1 for _ in grp)
            pid = color2id.get(col)
            if pid is not None:
                area[pid] = area.get(pid, 0) + n
                sx[pid] = sx.get(pid, 0) + (2 * x + n - 1) * n / 2
                sy[pid] = sy.get(pid, 0) + y * n
                if pid not in minx or x < minx[pid]:
                    minx[pid] = x
                if pid not in maxx or x + n - 1 > maxx[pid]:
                    maxx[pid] = x + n - 1
                if pid not in miny or y < miny[pid]:
                    miny[pid] = y
                if pid not in maxy or y > maxy[pid]:
                    maxy[pid] = y
            x += n
    cent = {p: (sx[p] / area[p], sy[p] / area[p]) for p in area}
    bbox = {p: (minx[p], miny[p], maxx[p], maxy[p]) for p in area}
    return dict(width=w, height=h, area=area, cent=cent, bbox=bbox)


def load_all(force=False):
    if not force and os.path.exists(CACHE):
        with open(CACHE, 'rb') as f:
            return pickle.load(f)
    prov = load_definition()
    scan = scan_bmp(prov)
    out = dict(prov=prov, scan=scan)
    with open(CACHE, 'wb') as f:
        pickle.dump(out, f)
    return out


def load_loc_vp():
    names = {}
    path = os.path.join(ROOT, 'localisation', 'english', 'victory_points_l_english.yml')
    pat = re.compile(r'^\s*VICTORY_POINTS_(\d+):\d*\s+"(.*)"')
    with open(path, encoding='utf-8-sig') as f:
        for line in f:
            m = pat.match(line)
            if m:
                names[int(m.group(1))] = m.group(2)
    return names


def load_states():
    """state id -> dict(file, owner, provinces, category)."""
    states = {}
    d = os.path.join(ROOT, 'history', 'states')
    for fn in os.listdir(d):
        m = re.match(r'(\d+)-(.*)\.txt$', fn)
        if not m:
            continue
        txt = open(os.path.join(d, fn), encoding='utf-8', errors='replace').read()
        sid = int(m.group(1))
        pm = re.search(r'provinces\s*=\s*\{([^}]*)\}', txt)
        provs = [int(x) for x in pm.group(1).split()] if pm else []
        om = re.search(r'\bowner\s*=\s*([A-Z0-9]{3})', txt)
        states[sid] = dict(file=fn, name=m.group(2), provinces=provs, owner=om.group(1) if om else None)
    return states


if __name__ == '__main__':
    import time
    t = time.time()
    d = load_all(force=True)
    print('scanned', len(d['scan']['area']), 'provinces in', round(time.time() - t, 1), 's')
