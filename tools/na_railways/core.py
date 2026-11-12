"""Shared map context for the North Africa tools: raster, adjacency, region, projection, station resolver."""
import math
import mapdata as M
import geo
import network

R = geo.Raster()
ADJ = R.adjacency()
CENT, PROV = R.cent, R.prov
PASS = {p for p in ADJ if PROV[p]['type'] == 'land'}
STATES = M.load_states()
VP = M.load_loc_vp()
P2S = {p: s for s, v in STATES.items() for p in v['provinces']}

REGION_STATES = [446, 447, 452, 453, 456, 457, 552, 824, 448, 449, 450, 451, 661, 662, 663, 273,
                 458, 665, 459, 460, 513, 461, 462, 290, 783, 514, 699, 549, 551, 812, 767]
INSIDE = {p for s in REGION_STATES for p in STATES[s]['provinces']}
for p, v in PROV.items():  # stateless African land provinces inside the map box (Siwa etc.)
    if p not in P2S and v['type'] == 'land' and v['continent'] == 5 and p in CENT:
        x, y = CENT[p]
        if geo.BOX[0] <= x <= 3420 and geo.BOX[1] <= y <= geo.BOX[3] and 2600 <= x:
            INSIDE.add(p)

# ---- projection with local residual correction (IDW over anchor cities)
ANCH = [(30.04, 31.24, 7011), (31.20, 29.92, 4076), (31.26, 32.30, 10869), (29.97, 32.55, 4073),
        (24.09, 32.90, 11999), (25.70, 32.64, 7073), (15.50, 32.56, 12806), (19.62, 37.22, 12725),
        (32.89, 13.19, 1149), (32.12, 20.07, 11954), (36.80, 10.18, 11969), (36.75, 3.06, 1145),
        (35.70, -0.63, 7132), (33.57, -7.59, 7069), (34.74, 10.76, 7162), (27.18, 31.18, 11974),
        (37.27, 9.87, 9994), (13.18, 30.22, 10827), (30.01, 31.21, 3996), (30.83, 28.95, 1071),
        (31.35, 27.23, 11967), (31.63, -8.01, 4108), (33.88, 10.10, 7005), (36.90, 7.77, 7081),
        (35.56, 6.17, 12034)]
RES = []
for lat, lon, pid in ANCH:
    x, y = geo.project(lat, lon)
    RES.append((x, y, CENT[pid][0] - x, CENT[pid][1] - y))


def proj(lat, lon):
    x, y = geo.project(lat, lon)
    sw = sx = sy = 0.0
    for ax, ay, rx, ry in RES:
        d2 = (x - ax) ** 2 + (y - ay) ** 2
        w = 1.0 / (d2 + 25.0) ** 1.0
        sw += w
        sx += w * rx
        sy += w * ry
    # damp far-away correction so it only acts near anchors
    near = min(math.hypot(x - ax, y - ay) for ax, ay, _, _ in RES)
    damp = max(0.0, 1.0 - near / 140.0)
    return x + damp * sx / sw, y + damp * sy / sw


def nearest_passable(x, y, maxr=30):
    best = None
    for r in range(0, maxr):
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if max(abs(dx), abs(dy)) != r:
                    continue
                pid = R.at(x + dx, y + dy)
                if pid in PASS:
                    return pid
    return best


PINS = dict(network.PINS)
PINS.update(getattr(network, 'EXTRA_PINS', {}))
PINS.update({'Kantara East': 13702})


def resolve(name, lat, lon):
    if name in PINS:
        return PINS[name], 'pin'
    x, y = proj(lat, lon)
    pid = R.at(x, y)
    if pid in PASS:
        return pid, 'proj'
    return nearest_passable(x, y), 'snap'


def label(pid):
    n = VP.get(pid)
    s = P2S.get(pid)
    sn = STATES[s]['name'] if s else 'nostate'
    return f"{pid}" + (f" {n}" if n else '') + f" ({sn})"


