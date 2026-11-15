"""Read-only audit of a Glyphs source file. Produces a Markdown report; see docs/standards.md."""
import collections
import math
import re
import unicodedata

from . import charsets
from .font import Font, area, cubic, droots, flatten, glyph_data, inside, path_segments, runs, seg_bounds


class Audit:
    def __init__(self, path, languages=("english", "czech")):
        self.font = Font(path)
        self.languages = languages
        self.gd = glyph_data()
        f = self.font
        self.byuni = {}
        for name, g in f.G.items():
            u = g.get("unicode")
            for cp in (u if isinstance(u, list) else [u] if u is not None else []):
                self.byuni.setdefault(cp, []).append(name)
        self.sb = {n: f.sidebearings(n) for n in f.G}

    # ---- helpers ---------------------------------------------------------------------
    def kind(self, name):
        """(category, case) from Glyphs' database, falling back on Unicode."""
        d = self.gd.get(name) or self.gd.get(name.split(".")[0])
        if d:
            return d.get("category", "?"), d.get("case", "")
        u = self.font.G[name].get("unicode")
        if isinstance(u, int):
            cat = unicodedata.category(chr(u))
            if cat[0] == "L":
                return "Letter", "upper" if cat == "Lu" else "lower"
            if cat[0] == "N":
                return "Number", ""
            if cat[0] == "M":
                return "Mark", ""
        return "?", ""

    def is_mark(self, name):
        return name in self.font.G and any(k.startswith("_") for k in self.font.anchors(name))

    def base_of(self, name):
        bases = [c["ref"] for c in self.font.comps(name) if c["ref"] in self.font.G and not self.is_mark(c["ref"])]
        return bases[0] if len(bases) == 1 else None

    @staticmethod
    def names(items, limit=40):
        items = list(items)
        return " ".join(items[:limit]) + (f" … (+{len(items) - limit})" if len(items) > limit else "")

    # ---- sections --------------------------------------------------------------------
    def summary(self):
        f = self.font
        m = f.metrics()
        out = [f"- Family: {f.F.get('familyName')}", f"- Glyphs: {len(f.G)}, masters: {len(f.F['fontMaster'])}, units per em: {f.F.get('unitsPerEm')}"]
        out.append("- Metrics: " + ", ".join(f"{k} {v[0]} (overshoot {v[1]})" for k, v in m.items() if k != "italic angle"))
        return out

    def coverage(self):
        f = self.font
        sets = [("ASCII", charsets.ASCII)] + [(l.title(), charsets.LANGUAGES[l]) for l in self.languages]
        sets += [("Typographic punctuation", charsets.TYPOGRAPHIC), ("Nice to have", charsets.NICE_TO_HAVE)]
        out = []
        for label, chars in sets:
            missing = [c for c in chars if ord(c) not in self.byuni]
            empty = [self.byuni[ord(c)][0] for c in chars if ord(c) in self.byuni and not f.layer(self.byuni[ord(c)][0]).get("shapes")
                     and unicodedata.category(c) not in ("Zs", "Cf")]
            if not missing and not empty:
                out.append(f"- {label}: complete ({len(chars)})")
            else:
                shown = ", ".join(f"{c.strip() or 'space'} U+{ord(c):04X}" for c in missing)
                out.append(f"- {label}: missing {len(missing)} of {len(chars)}" + (f": {shown}" if missing else "") + (f"; empty: {self.names(empty)}" if empty else ""))
        dups = {f"U+{u:04X}": ns for u, ns in self.byuni.items() if len(ns) > 1}
        if dups:
            out.append(f"- Code points used twice: {dups}")
        return out

    def composites(self):
        f = self.font
        out = []
        missing = [f"{n} -> {c['ref']}" for n in f.G for c in f.comps(n) if c["ref"] not in f.G]
        if missing:
            out.append("- Components pointing at missing glyphs: " + ", ".join(missing))
        short, other = [], []
        for n in f.G:
            d = self.gd.get(n)
            have = [c["ref"] for c in f.comps(n)]
            if not d or not d.get("decompose") or not have or f.paths(n):
                continue
            want = [x.strip().replace(".case", "") for x in d["decompose"].split(",")]
            got = [x.replace(".case", "") for x in have]
            if sorted(got) == sorted(want):
                continue
            if set(got) < set(want) and len(got) < len(want):
                short.append(f"{n} (has {'+'.join(have)}, recipe {'+'.join(want)})")
            elif any(re.search(r"\.\d{3}$", x) for x in have):
                other.append(f"{n} (built on {'+'.join(have)})")
        if short:
            out.append("- Composites missing a part: " + "; ".join(short))
        if other:
            out.append("- Composites built on alternates: " + "; ".join(other))
        return out or ["- Nothing to report."]

    def anchors(self):
        f = self.font
        out, nomatch, bare = [], [], []
        for n in f.G:
            base = self.base_of(n)
            if base is None:
                continue
            ba = f.anchors(base)
            for c in f.comps(n):
                if c["ref"] in f.G and self.is_mark(c["ref"]):
                    wants = [k[1:] for k in f.anchors(c["ref"]) if k.startswith("_")]
                    if not any(w in ba for w in wants):
                        nomatch.append(f"{n} ({c['ref']} wants {'/'.join(wants)} on {base})")
        for n in f.G:
            if self.kind(n)[0] == "Letter" and f.paths(n):
                a = f.anchors(n)
                if not any(k.startswith("top") for k in a) or not any(k.startswith("bottom") for k in a):
                    bare.append(n)
        if nomatch:
            out.append("- Marks with no anchor to attach to: " + "; ".join(nomatch))
        if bare:
            out.append("- Drawn letters without a top or bottom anchor: " + self.names(bare))
        return out or ["- Nothing to report."]

    def edge_kind(self, segs, yref, top):
        kinds = set()
        for s in segs:
            b = seg_bounds(s)
            if abs((b[3] if top else b[1]) - yref) > 0.6:
                continue
            if s[0] == "L":
                kinds.add("flat" if abs(s[1][1] - s[2][1]) < 0.6 and abs(s[1][0] - s[2][0]) >= 10 else "point")
            else:
                ys = [s[1][1], s[4][1]]
                ext = max(ys) if top else min(ys)
                kinds.add("round" if abs(ext - yref) < 0.6 else "round, no node at the extreme")
        for k in ("flat", "round", "round, no node at the extreme", "point"):
            if k in kinds:
                return k
        return "?"

    def vertical(self):
        f = self.font
        m = f.metrics()
        zones = [(k, v[0]) for k, v in m.items() if k != "italic angle"]
        if not zones:
            return ["- No metrics found in the file."]
        groups = collections.defaultdict(list)
        for n in f.G:
            cat, case = self.kind(n)
            if cat not in ("Letter", "Number") or not f.paths(n):
                continue
            segs, b = f.segments(n), f.bounds(n)
            for top in (False, True):
                y = b[3] if top else b[1]
                zone = min(zones, key=lambda z: abs(y - z[1]))
                groups[(cat if cat == "Number" else case or "other", "top" if top else "bottom", zone[0], self.edge_kind(segs, y, top), round(y - zone[1]))].append(n)
        out = ["| Group | Edge | Line | Shape | Offset | Glyphs |", "|---|---|---|---|---|---|"]
        for k in sorted(groups, key=lambda k: (k[0], k[1], k[2], k[3], k[4])):
            out.append(f"| {k[0]} | {k[1]} | {k[2]} | {k[3]} | {k[4]:+d} | {self.names(groups[k], 30)} |")
        return out

    def stems(self):
        f = self.font
        V, H = collections.defaultdict(set), collections.defaultdict(set)
        for n in f.G:
            if self.kind(n)[0] not in ("Letter", "Number") or not f.paths(n) or f.comps(n):
                continue
            pl, b = f.polys(n), f.bounds(n)
            for a, c, s, e in runs(pl, b[1], b[3], axis=1, minlen=80, maxw=200):
                V[round((c - a) * 2) / 2].add(n)
            for a, c, s, e in runs(pl, b[0], b[2], axis=0, minlen=30, maxw=140):
                H[round((c - a) * 2) / 2].add(n)
        out = ["Straight vertical stems (width: glyphs):"]
        out += [f"- {w:g}: {self.names(sorted(V[w]), 30)}" for w in sorted(V)]
        out += ["", "Horizontal bars and serifs (thickness: glyphs):"]
        out += [f"- {w:g}: {self.names(sorted(H[w]), 30)}" for w in sorted(H)]
        return out

    def key_value(self, key, side):
        k = str(key).strip().lstrip("=")
        opp = k.startswith("|")
        k = k.lstrip("|")
        if k not in self.sb or self.sb[k][0] is None:
            return None
        l, r = self.sb[k]
        return (r if side == 0 else l) if opp else (l if side == 0 else r)

    def spacing(self):
        f = self.font
        out, sync, widths, neg = [], [], [], []
        for n, g in f.G.items():
            for side, key in ((0, g.get("metricLeft")), (1, g.get("metricRight"))):
                if key and self.sb[n][side] is not None:
                    want = self.key_value(key, side)
                    if want is not None and abs(want - self.sb[n][side]) > 0.6:
                        sync.append(f"{n} {'LR'[side]}SB {self.sb[n][side]:.0f}, key {key} gives {want:.0f}")
            base = self.base_of(n)
            if base and not f.paths(n) and self.kind(n)[0] == "Letter" and abs(f.width(n) - f.width(base)) > 0.5:
                widths.append(f"{n} {f.width(n):g} vs {base} {f.width(base):g}")
            l, r = self.sb[n]
            if l is not None and self.kind(n)[0] != "Mark" and not self.is_mark(n) and (l < -1 or r < -1):
                neg.append(f"{n} ({l:.0f}/{r:.0f})")
        pairs = [("parenleft", "parenright"), ("bracketleft", "bracketright"), ("braceleft", "braceright"), ("guilsinglleft", "guilsinglright"),
                 ("guillemetleft", "guillemetright"), ("less", "greater"), ("slash", "backslash")]
        mirror = [f"{a} {self.sb[a][0]:.0f}/{self.sb[a][1]:.0f} vs {b} {self.sb[b][0]:.0f}/{self.sb[b][1]:.0f}" for a, b in pairs
                  if a in self.sb and b in self.sb and self.sb[a][0] is not None and self.sb[b][0] is not None
                  and (abs(self.sb[a][0] - self.sb[b][1]) > 1 or abs(self.sb[a][1] - self.sb[b][0]) > 1)]
        if sync:
            out.append("- Metrics keys out of sync: " + "; ".join(sync))
        if widths:
            out.append("- Composites wider or narrower than their base: " + "; ".join(widths))
        if mirror:
            out.append("- Mirrored pairs that do not mirror: " + "; ".join(mirror))
        if neg:
            out.append("- Negative sidebearings: " + self.names(neg, 30))
        return out or ["- Nothing to report."]

    def kerning(self):
        f = self.font
        table = f.F.get("kerningLTR", {}).get(f.mid, {})
        pairs = [(l, r, v) for l, d in table.items() for r, v in d.items()]
        right = {g.get("kernRight") for g in f.G.values()}
        left = {g.get("kernLeft") for g in f.G.values()}
        dead = []
        for l, r, v in pairs:
            bad_l = (l.startswith("@MMK_L_") and l[7:] not in right) or (not l.startswith("@") and l not in f.G)
            bad_r = (r.startswith("@MMK_R_") and r[7:] not in left) or (not r.startswith("@") and r not in f.G)
            if bad_l or bad_r:
                dead.append(f"{l} {r} {v:g}")
        differ = []
        for n in f.G:
            base = self.base_of(n)
            if base and not f.paths(n) and self.kind(n)[0] == "Letter":
                a = (f.G[n].get("kernLeft"), f.G[n].get("kernRight"))
                b = (f.G[base].get("kernLeft"), f.G[base].get("kernRight"))
                if a != b:
                    differ.append(f"{n} {a[0]}/{a[1]} (base {base} {b[0]}/{b[1]})")
        out = [f"- Pairs: {len(pairs)}"]
        if dead:
            out.append("- Dead pairs (group without members, or missing glyph): " + "; ".join(dead))
        if differ:
            out.append("- Composites whose groups differ from their base: " + "; ".join(differ[:60]) + (f" … (+{len(differ) - 60})" if len(differ) > 60 else ""))
        return out

    def paths(self):
        f = self.font
        R = collections.defaultdict(list)
        total = 0
        for n in f.G:
            shapes = f.paths(n)
            fl = [flatten(s["nodes"], s.get("closed", 0) == 1) for s in shapes]
            for i, sh in enumerate(shapes):
                total += 1
                nodes, closed = sh["nodes"], sh.get("closed", 0) == 1
                if not closed:
                    R["Open paths"].append(n)
                if any(abs(v - round(v)) > 1e-6 for p in nodes for v in p[:2]):
                    R["Coordinates that are not whole numbers"].append(n)
                for s in path_segments(nodes, closed):
                    if s[0] == "L":
                        dx, dy = s[2][0] - s[1][0], s[2][1] - s[1][1]
                        ln = math.hypot(dx, dy)
                        if ln < 0.01:
                            R["Duplicate nodes"].append(n)
                        elif ln <= 6:
                            R["Segments of 6 units or less"].append(n)
                        elif ln > 25 and (0 < abs(dy) <= 3 and abs(dx) > 25 or 0 < abs(dx) <= 3 and abs(dy) > 25):
                            R["Lines 1 to 3 units off horizontal or vertical"].append(n)
                    else:
                        p0, p1, p2, p3 = s[1:]
                        b = seg_bounds(s)
                        ex = max(min(p0[0], p3[0]) - b[0], b[2] - max(p0[0], p3[0]), min(p0[1], p3[1]) - b[1], b[3] - max(p0[1], p3[1]))
                        if ex >= 1:
                            R["Missing extremes"].append(n)
                        if math.hypot(p1[0] - p0[0], p1[1] - p0[1]) < 0.01 or math.hypot(p3[0] - p2[0], p3[1] - p2[1]) < 0.01:
                            R["Zero-length handles"].append(n)
                if closed:
                    N = len(nodes)
                    for k, p in enumerate(nodes):
                        if p[2][0] != "o" and p[2].endswith("s"):
                            a, c = nodes[k - 1], nodes[(k + 1) % N]
                            v1, v2 = (p[0] - a[0], p[1] - a[1]), (c[0] - p[0], c[1] - p[1])
                            l1, l2 = math.hypot(*v1), math.hypot(*v2)
                            if l1 > 0.01 and l2 > 0.01:
                                ang = math.degrees(math.acos(max(-1, min(1, (v1[0] * v2[0] + v1[1] * v2[1]) / (l1 * l2)))))
                                if ang > 3:
                                    R["Smooth nodes with a kink"].append(n)
            closed = [(i, fl[i]) for i, s in enumerate(shapes) if s.get("closed", 0) == 1 and len(fl[i]) >= 3]
            for i, pl in closed:
                depth = sum(1 for j, o in closed if j != i and all(inside(q, o) for q in pl[::max(1, len(pl) // 12)]))
                a = area(pl)
                if abs(a) >= 1 and (a > 0) != (depth % 2 == 0):
                    R["Wrong path direction"].append(n)
        out = [f"- Paths checked: {total}"]
        for label in ("Open paths", "Wrong path direction", "Missing extremes", "Duplicate nodes", "Zero-length handles", "Smooth nodes with a kink",
                      "Lines 1 to 3 units off horizontal or vertical", "Segments of 6 units or less", "Coordinates that are not whole numbers"):
            if R[label]:
                names = list(collections.OrderedDict.fromkeys(R[label]))
                out.append(f"- {label}: {len(R[label])} in {len(names)} glyphs: {self.names(names, 40)}")
        if len(out) == 1:
            out.append("- Nothing to report.")
        return out

    def font_level(self):
        f = self.font
        F = f.F
        out = [f"- Features: {len(F.get('features', []))} ({' '.join(x.get('tag', '?') for x in F.get('features', []))}), classes: {len(F.get('classes', []))}, prefixes: {len(F.get('featurePrefixes', []))}"]
        if not F.get("features"):
            out.append("- No OpenType features in the file: ligatures and alternates cannot fire.")
        out.append("- Instances: " + "; ".join(f"{i.get('name')}{'' if i.get('exports', 1) else ' (not exported)'}" for i in F.get("instances", [])))
        stems = f.master.get("stemValues")
        if stems:
            out.append(f"- Stem values in Font Info: {stems}")
        suffixed = [n for n in f.G if re.search(r"\.\d{3}$", n)]
        if suffixed:
            out.append("- Numbered leftovers: " + self.names(suffixed))
        hidden = [n for n in f.G if f.G[n].get("export") == 0]
        if hidden:
            out.append("- Not exported: " + self.names(hidden))
        return out

    def report(self):
        parts = [("Summary", self.summary), ("Coverage", self.coverage), ("Composites", self.composites), ("Anchors", self.anchors),
                 ("Vertical metrics and overshoots", self.vertical), ("Stems", self.stems), ("Spacing", self.spacing), ("Kerning", self.kerning),
                 ("Paths", self.paths), ("Font level", self.font_level)]
        lines = ["# Audit", "", "Read from the saved file. Nothing was changed.", ""]
        for title, fn in parts:
            lines += [f"## {title}", ""] + fn() + [""]
        return "\n".join(lines)
