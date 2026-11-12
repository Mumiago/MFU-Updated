"""Geometry layer: lat/lon projection, cropped province raster, land adjacency, river snap."""
import os
import struct
import heapq
import math
import mapdata as M

# Affine fit (21 anchor cities, ~5 px RMS): pixel = f(lat, lon)
CX = (2785.6, 15.665, 0.581)
CY = (1451.8, -0.200, -18.144)
BOX = (2540, 700, 3500, 1340)   # x0, y0, x1, y1 (pixels, y down) covering Morocco..Sudan


def project(lat, lon):
    return CX[0] + CX[1] * lon + CX[2] * lat, CY[0] + CY[1] * lon + CY[2] * lat


def unproject(x, y):
    # solve 2x2
    a, b = CX[1], CX[2]
    c, d = CY[1], CY[2]
    rx, ry = x - CX[0], y - CY[0]
    det = a * d - b * c
    lon = (rx * d - b * ry) / det
    lat = (a * ry - c * rx) / det
    return lat, lon


class Raster:
    def __init__(self):
        d = M.load_all()
        self.prov = d['prov']
        self.cent = d['scan']['cent']
        self.area = d['scan']['area']
        color2id = {v['rgb']: k for k, v in self.prov.items()}
        x0, y0, x1, y1 = BOX
        self.x0, self.y0, self.x1, self.y1 = x0, y0, x1, y1
        path = os.path.join(M.ROOT, 'map', 'provinces.bmp')
        with open(path, 'rb') as f:
            hdr = f.read(54)
            w, h = struct.unpack('<ii', hdr[18:26])
            off = struct.unpack('<I', hdr[10:14])[0]
            rowsize = (w * 3 + 3) // 4 * 4
            grid = []
            for y in range(y0, y1):
                file_row = h - 1 - y
                f.seek(off + file_row * rowsize + x0 * 3)
                raw = f.read((x1 - x0) * 3)
                b, g, r = raw[0::3], raw[1::3], raw[2::3]
                grid.append([color2id.get(c, 0) for c in zip(r, g, b)])
        self.grid = grid
        self.rivers = None

    def at(self, x, y):
        xi, yi = int(round(x)) - self.x0, int(round(y)) - self.y0
        if 0 <= yi < len(self.grid) and 0 <= xi < len(self.grid[0]):
            return self.grid[yi][xi]
        return 0

    def load_rivers(self):
        path = os.path.join(M.ROOT, 'map', 'rivers.bmp')
        with open(path, 'rb') as f:
            hdr = f.read(54)
            w, h = struct.unpack('<ii', hdr[18:26])
            bpp = struct.unpack('<H', hdr[28:30])[0]
            off = struct.unpack('<I', hdr[10:14])[0]
            assert bpp == 8, bpp
            rowsize = (w + 3) // 4 * 4
            rows = []
            for y in range(self.y0, self.y1):
                f.seek(off + (h - 1 - y) * rowsize + self.x0)
                rows.append(f.read(self.x1 - self.x0))
        self.rivers = rows

    def river_provinces_near(self, x, y, radius=25):
        """Return province ids with river pixels near (x,y), nearest first."""
        if self.rivers is None:
            self.load_rivers()
        found = {}
        xi0, yi0 = int(round(x)) - self.x0, int(round(y)) - self.y0
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                xx, yy = xi0 + dx, yi0 + dy
                if 0 <= yy < len(self.rivers) and 0 <= xx < len(self.rivers[0]):
                    if self.rivers[yy][xx] != 255:
                        dist = dx * dx + dy * dy
                        pid = self.grid[yy][xx]
                        if pid and (pid not in found or dist < found[pid]):
                            found[pid] = dist
        return sorted(found, key=lambda p: found[p])

    def adjacency(self):
        adj = {}
        g = self.grid
        H, W = len(g), len(g[0])
        for yi in range(H):
            row = g[yi]
            nxt = g[yi + 1] if yi + 1 < H else None
            for xi in range(W):
                a = row[xi]
                if xi + 1 < W:
                    b = row[xi + 1]
                    if a != b and a and b:
                        adj.setdefault(a, set()).add(b)
                        adj.setdefault(b, set()).add(a)
                if nxt is not None:
                    b = nxt[xi]
                    if a != b and a and b:
                        adj.setdefault(a, set()).add(b)
                        adj.setdefault(b, set()).add(a)
        return adj


def dist(p, q):
    return math.hypot(p[0] - q[0], p[1] - q[1])


def seg_dev(p, a, b):
    """Distance from point p to segment ab (pixels)."""
    ax, ay = a
    bx, by = b
    px, py = p
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    if L2 == 0:
        return dist(p, a)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
    return dist(p, (ax + t * dx, ay + t * dy))


def route(adj, cent, passable, src, dst, a_pt, b_pt, width=14.0):
    """Corridor-guided Dijkstra between provinces src and dst. a_pt/b_pt are the pixel
    positions of the two stations; edges pay extra for straying from the straight line."""
    if src == dst:
        return [src]
    pq = [(0.0, src)]
    best = {src: 0.0}
    prev = {}
    while pq:
        c, u = heapq.heappop(pq)
        if u == dst:
            break
        if c > best.get(u, 1e18):
            continue
        for v in adj.get(u, ()):
            if v not in passable:
                continue
            step = dist(cent[u], cent[v])
            dev = seg_dev(cent[v], a_pt, b_pt)
            cost = c + step * (1.0 + (dev / width) ** 2)
            if cost < best.get(v, 1e18):
                best[v] = cost
                prev[v] = u
                heapq.heappush(pq, (cost, v))
    if dst not in prev and src != dst:
        return None
    path = [dst]
    while path[-1] != src:
        path.append(prev[path[-1]])
    return path[::-1]
