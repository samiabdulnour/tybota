"""Read-only model of a Glyphs source file (format 3) with the geometry an audit needs."""
import collections
import math
import os
import xml.etree.ElementTree as ET

from . import plist

GLYPHDATA_CANDIDATES = [
    "/Applications/Glyphs 4.app/Contents/Frameworks/GlyphsCore.framework/Versions/A/Resources/GlyphData.xml",
    "/Applications/Glyphs 3.app/Contents/Frameworks/GlyphsCore.framework/Versions/A/Resources/GlyphData.xml",
]


def glyph_data(path=None):
    """Glyphs' own glyph database as {name: attributes}; empty if Glyphs is not installed."""
    for cand in ([path] if path else []) + [os.environ.get("TYBOTA_GLYPHDATA")] + GLYPHDATA_CANDIDATES:
        if cand and os.path.exists(cand):
            return {el.get("name"): dict(el.attrib) for el in ET.parse(cand).getroot()}
    return {}


def cubic(p0, p1, p2, p3, t):
    mt = 1 - t
    a, b, c, d = mt ** 3, 3 * mt * mt * t, 3 * mt * t * t, t ** 3
    return (a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1])


def droots(a, b, c, d):
    """Parameters in (0, 1) where one coordinate of a cubic has an extreme."""
    A, B, C = d - 3 * c + 3 * b - a, 2 * (c - 2 * b + a), b - a
    out = []
    if abs(A) < 1e-9:
        if abs(B) > 1e-9:
            out.append(-C / B)
    else:
        disc = B * B - 4 * A * C
        if disc >= 0:
            s = math.sqrt(disc)
            out += [(-B + s) / (2 * A), (-B - s) / (2 * A)]
    return [t for t in out if 1e-6 < t < 1 - 1e-6]


def path_segments(nodes, closed=True):
    """('L', p0, p1) and ('C', p0, p1, p2, p3) for a Glyphs node list."""
    n = len(nodes)
    segs = []
    for i in (range(n) if closed else range(1, n)):
        t = nodes[i][2][0]
        if t == "o":
            continue
        pt = lambda k: (float(nodes[k % n][0]), float(nodes[k % n][1]))
        if t == "l":
            if nodes[i - 1][2][0] != "o":
                segs.append(("L", pt(i - 1), pt(i)))
        elif t == "c":
            segs.append(("C", pt(i - 3), pt(i - 2), pt(i - 1), pt(i)))
    return segs


def seg_bounds(s):
    if s[0] == "L":
        pts = [s[1], s[2]]
    else:
        pts = [s[1], s[4]]
        for t in droots(s[1][0], s[2][0], s[3][0], s[4][0]) + droots(s[1][1], s[2][1], s[3][1], s[4][1]):
            pts.append(cubic(s[1], s[2], s[3], s[4], t))
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return (min(xs), min(ys), max(xs), max(ys))


def flatten(nodes, closed=True, steps=20):
    pl = []
    for s in path_segments(nodes, closed):
        if s[0] == "L":
            pl.append(s[2])
        else:
            pl += [cubic(s[1], s[2], s[3], s[4], k / steps) for k in range(1, steps + 1)]
    return pl


def area(pl):
    return sum(pl[i - 1][0] * pl[i][1] - pl[i][0] * pl[i - 1][1] for i in range(len(pl))) / 2


def inside(p, pl):
    x, y = p
    c = False
    for i in range(len(pl)):
        a, b = pl[i - 1], pl[i]
        if (a[1] > y) != (b[1] > y) and x < a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1]):
            c = not c
    return c


def xform(comp):
    px, py = comp.get("pos", (0, 0))
    sx, sy = comp.get("scale", (1, 1))
    ang = math.radians(comp.get("angle", 0))
    ca, sa = math.cos(ang), math.sin(ang)

    def f(p):
        x, y = p[0] * sx, p[1] * sy
        return (x * ca - y * sa + px, x * sa + y * ca + py)

    return f


def spans(pls, c, axis=1):
    """Ink spans along a scanline. axis=1: horizontal line y=c; axis=0: vertical line x=c."""
    o = 1 - axis
    hits = []
    for pl in pls:
        for i in range(len(pl)):
            a, b = pl[i - 1], pl[i]
            ya, yb = a[axis], b[axis]
            if (ya <= c < yb) or (yb <= c < ya):
                t = (c - ya) / (yb - ya)
                hits.append((a[o] + t * (b[o] - a[o]), 1 if yb > ya else -1))
    hits.sort()
    out, w, start = [], 0, None
    for x, d in hits:
        if w == 0:
            start = x
        w += d
        if w == 0 and start is not None:
            if x - start > 0.01:
                out.append((start, x))
            start = None
    return out


def runs(pls, lo, hi, axis=1, step=2.0, minlen=60, maxw=260):
    """Straight stems: spans that stay the same over consecutive scanlines. Returns (a, b, start, end)."""
    active, done, c = {}, [], lo
    while c <= hi:
        keys = set((round(a * 2) / 2, round(b * 2) / 2) for a, b in spans(pls, c + 0.137, axis))
        for k in keys:
            if k in active:
                active[k][1] = c
            else:
                active[k] = [c, c]
        for k in list(active):
            if k not in keys:
                s, e = active.pop(k)
                done.append((k[0], k[1], s, e))
        c += step
    done += [(k[0], k[1], s, e) for k, (s, e) in active.items()]
    return sorted(r for r in done if r[3] - r[2] >= minlen and r[1] - r[0] <= maxw)


class Font:
    def __init__(self, path):
        self.path = path
        self.F = plist.load(path)
        if self.F.get(".formatVersion") != 3:
            raise ValueError("Only Glyphs format version 3 files are supported (save from Glyphs 3 or 4)")
        self.master = self.F["fontMaster"][0]
        self.mid = self.master["id"]
        self.G = collections.OrderedDict((g["glyphname"], g) for g in self.F["glyphs"])
        self.override = {}

    # --- raw access -------------------------------------------------------------------
    def layer(self, name):
        if name in self.override:
            return self.override[name]
        for l in self.G[name]["layers"]:
            if l.get("layerId") == self.mid:
                return l
        return None

    def width(self, name):
        return self.layer(name)["width"]

    def paths(self, name):
        return [s for s in self.layer(name).get("shapes", []) if "nodes" in s]

    def comps(self, name):
        return [s for s in self.layer(name).get("shapes", []) if "ref" in s]

    def anchors(self, name):
        return {a["name"]: tuple(a.get("pos", (0, 0))) for a in self.layer(name).get("anchors", [])}

    def metrics(self):
        """{'ascender': (pos, over), 'cap height': ..., 'x-height': ..., 'baseline': ..., 'descender': ...}"""
        out = {}
        for kind, val in zip(self.F.get("metrics", []), self.master.get("metricValues", [])):
            if kind.get("type") and "filter" not in kind:
                out[kind["type"]] = (val.get("pos", 0), val.get("over", 0))
        return out

    # --- resolved geometry ------------------------------------------------------------
    def segments(self, name, f=None, depth=0):
        out = []
        if name not in self.G or depth > 6:
            return out
        for sh in self.layer(name).get("shapes", []):
            if "nodes" in sh:
                for s in path_segments(sh["nodes"], sh.get("closed", 0) == 1):
                    out.append((s[0],) + tuple(f(p) if f else p for p in s[1:]))
            elif "ref" in sh:
                g = xform(sh)
                out += self.segments(sh["ref"], (lambda p, g=g, f=f: f(g(p))) if f else g, depth + 1)
        return out

    def polys(self, name, steps=20, f=None, depth=0):
        out = []
        if name not in self.G or depth > 6:
            return out
        for sh in self.layer(name).get("shapes", []):
            if "nodes" in sh:
                if sh.get("closed", 0) == 1:
                    pl = flatten(sh["nodes"], True, steps)
                    out.append([f(p) for p in pl] if f else pl)
            elif "ref" in sh:
                g = xform(sh)
                out += self.polys(sh["ref"], steps, (lambda p, g=g, f=f: f(g(p))) if f else g, depth + 1)
        return out

    def bounds(self, name):
        bs = [seg_bounds(s) for s in self.segments(name)]
        if not bs:
            return None
        return (min(b[0] for b in bs), min(b[1] for b in bs), max(b[2] for b in bs), max(b[3] for b in bs))

    def sidebearings(self, name):
        b = self.bounds(name)
        return (None, None) if b is None else (b[0], self.width(name) - b[2])
