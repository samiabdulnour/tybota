"""A tiny rasteriser that sets text in a font's own outlines and writes a PNG. No dependencies."""
import math
import struct
import unicodedata
import zlib

from .font import spans


class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.px = [[0.0] * w for _ in range(h)]

    def draw(self, pls, ox, oy, scale, ss=3):
        """pls in font units; (ox, oy) is the pixel position of the font origin on the baseline."""
        if not pls:
            return
        ys = [p[1] for pl in pls for p in pl]
        top = int(math.floor(oy - max(ys) * scale)) - 1
        bot = int(math.ceil(oy - min(ys) * scale)) + 1
        for row in range(max(0, top), min(self.h, bot)):
            line = self.px[row]
            for k in range(ss):
                yy = (oy - (row + (k + 0.5) / ss)) / scale
                for a, b in spans(pls, yy):
                    a, b = ox + a * scale, ox + b * scale
                    for i in range(max(0, int(math.floor(a))), min(self.w - 1, int(math.floor(b))) + 1):
                        cov = min(b, i + 1) - max(a, i)
                        if cov > 0:
                            line[i] += cov / ss

    def hline(self, y, x0, x1, shade=0.18):
        if 0 <= y < self.h:
            for x in range(max(0, x0), min(self.w, x1)):
                self.px[y][x] = max(self.px[y][x], shade)

    def save(self, path):
        raw = bytearray()
        for row in self.px:
            raw.append(0)
            raw.extend(max(0, min(255, int(round(255 * (1 - min(1.0, v)))))) for v in row)

        def chunk(tag, data):
            return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

        png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", self.w, self.h, 8, 0, 0, 0, 0))
               + chunk(b"IDAT", zlib.compress(bytes(raw), 6)) + chunk(b"IEND", b""))
        with open(path, "wb") as fh:
            fh.write(png)


def char_map(font):
    """{character: glyph name} from the font's code points."""
    out = {}
    for name, g in font.G.items():
        u = g.get("unicode")
        for cp in (u if isinstance(u, list) else [u] if u is not None else []):
            out.setdefault(chr(cp), name)
    return out


def glyph_names(font, text):
    """Glyph names for a string. '/name' picks a glyph by name, as in a Glyphs Edit tab."""
    cmap = char_map(font)
    names, missing, i = [], [], 0
    text = unicodedata.normalize("NFC", text)
    while i < len(text):
        ch = text[i]
        if ch == "/" and i + 1 < len(text) and text[i + 1] != " ":
            j = i + 1
            while j < len(text) and text[j] not in " /":
                j += 1
            name = text[i + 1:j]
            if name in font.G:
                names.append(name)
                i = j + 1 if j < len(text) and text[j] == " " else j
                continue
        if ch in cmap:
            names.append(cmap[ch])
        else:
            missing.append(ch)
        i += 1
    return names, missing


def proof(rows, path, scale=0.2, margin=24, asc=930, desc=290, guides=(0,)):
    """rows: list of lists of (Font, glyph name). Each row is one line of the image."""
    widths = [sum(f.width(n) for f, n in row) * scale + 2 * margin for row in rows]
    W = int(max(widths)) + 1
    rowh = int((asc + desc) * scale)
    cv = Canvas(W, rowh * len(rows) + 2 * margin)
    for r, row in enumerate(rows):
        oy = margin + r * rowh + asc * scale
        for g in guides:
            cv.hline(int(round(oy - g * scale)), margin // 2, W - margin // 2)
        x = margin
        for f, n in row:
            cv.draw(f.polys(n), x, oy, scale)
            x += f.width(n) * scale
    cv.save(path)
    return W, cv.h
