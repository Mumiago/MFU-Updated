"""Tiny pure-Python PNG renderer for province/rail previews."""
import zlib
import struct

FONT = {
    '0': ['111', '101', '101', '101', '111'], '1': ['010', '110', '010', '010', '111'],
    '2': ['111', '001', '111', '100', '111'], '3': ['111', '001', '111', '001', '111'],
    '4': ['101', '101', '111', '001', '001'], '5': ['111', '100', '111', '001', '111'],
    '6': ['111', '100', '111', '101', '111'], '7': ['111', '001', '010', '010', '010'],
    '8': ['111', '101', '111', '101', '111'], '9': ['111', '101', '111', '001', '111'],
    ':': ['000', '010', '000', '010', '000'],
}
TERRAIN = {
    'ocean': (150, 190, 225), 'water_fjords': (150, 190, 225), 'lakes': (120, 170, 215), 'unknown': (230, 230, 230),
    'desert': (238, 222, 170), 'plains': (200, 220, 150), 'forest': (120, 170, 110), 'hills': (190, 170, 120),
    'mountain': (170, 140, 110), 'urban': (200, 120, 120), 'jungle': (90, 150, 90), 'marsh': (150, 190, 170),
}


def _png(path, w, h, rows):
    raw = b''.join(b'\x00' + bytes(r) for r in rows)

    def chunk(t, d):
        c = struct.pack('>I', len(d)) + t + d
        return c + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    png = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)) \
        + chunk(b'IDAT', zlib.compress(raw, 6)) + chunk(b'IEND', b'')
    with open(path, 'wb') as f:
        f.write(png)


class Canvas:
    def __init__(self, raster, box, scale):
        self.R = raster
        self.x0, self.y0, self.x1, self.y1 = box
        self.s = scale
        self.w = (self.x1 - self.x0) * scale
        self.h = (self.y1 - self.y0) * scale
        self.px = [bytearray(self.w * 3) for _ in range(self.h)]
        self._base()

    def _set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = x * 3
            r = self.px[y]
            r[i], r[i + 1], r[i + 2] = c

    def _base(self):
        R, s = self.R, self.s
        prov = R.prov
        for yy in range(self.y0, self.y1):
            for xx in range(self.x0, self.x1):
                pid = R.grid[yy - R.y0][xx - R.x0]
                t = prov.get(pid, {}).get('terrain', 'unknown')
                typ = prov.get(pid, {}).get('type', 'land')
                c = TERRAIN.get(t, (230, 230, 230))
                if typ == 'sea':
                    c = (150, 190, 225)
                elif typ == 'lake':
                    c = (120, 170, 215)
                # boundary?
                edge = False
                if xx + 1 < R.x1 and R.grid[yy - R.y0][xx + 1 - R.x0] != pid:
                    edge = True
                if yy + 1 < R.y1 and R.grid[yy + 1 - R.y0][xx - R.x0] != pid:
                    edge = True
                if edge:
                    c = (90, 90, 90) if typ == 'land' else (130, 160, 190)
                bx, by = (xx - self.x0) * s, (yy - self.y0) * s
                for dy in range(s):
                    row = self.px[by + dy]
                    for dx in range(s):
                        i = (bx + dx) * 3
                        row[i], row[i + 1], row[i + 2] = c

    def line(self, p, q, color, width=2):
        s = self.s
        x0 = (p[0] - self.x0) * s + s / 2
        y0 = (p[1] - self.y0) * s + s / 2
        x1 = (q[0] - self.x0) * s + s / 2
        y1 = (q[1] - self.y0) * s + s / 2
        n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
        for i in range(n + 1):
            t = i / n if n else 0
            x = x0 + (x1 - x0) * t
            y = y0 + (y1 - y0) * t
            for dy in range(-(width // 2), width - width // 2):
                for dx in range(-(width // 2), width - width // 2):
                    self._set(int(x) + dx, int(y) + dy, color)

    def dot(self, p, color, r=3):
        s = self.s
        cx = int((p[0] - self.x0) * s + s / 2)
        cy = int((p[1] - self.y0) * s + s / 2)
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if dx * dx + dy * dy <= r * r:
                    self._set(cx + dx, cy + dy, color)

    def text(self, p, txt, color=(0, 0, 0), sc=1, dx=4, dy=-8):
        s = self.s
        cx = int((p[0] - self.x0) * s + s / 2) + dx
        cy = int((p[1] - self.y0) * s + s / 2) + dy
        for ch in txt:
            g = FONT.get(ch)
            if g:
                for ry, rowbits in enumerate(g):
                    for rx, b in enumerate(rowbits):
                        if b == '1':
                            for a in range(sc):
                                for b2 in range(sc):
                                    self._set(cx + rx * sc + a, cy + ry * sc + b2, color)
            cx += 4 * sc

    def save(self, path):
        _png(path, self.w, self.h, self.px)
