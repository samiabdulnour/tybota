"""Compare two saves of a Glyphs source: which glyphs changed, and how."""
import json

from . import plist


def _strip(glyph):
    g = json.loads(json.dumps(glyph))
    g.pop("lastChange", None)
    return g


def _layer(glyph, mid):
    return next((l for l in glyph["layers"] if l.get("layerId") == mid), {})


def _path_sig(shape):
    return tuple(sorted((n[0], n[1], n[2][0] == "o") for n in shape["nodes"]))


def describe(a, b, mid):
    notes = []
    for key in sorted(set(a) | set(b)):
        if key != "layers" and a.get(key) != b.get(key):
            notes.append(f"{key}: {a.get(key)!r} -> {b.get(key)!r}")
    la, lb = _layer(a, mid), _layer(b, mid)
    for key in sorted(set(la) | set(lb)):
        if la.get(key) == lb.get(key):
            continue
        if key == "shapes":
            pa = [s for s in la.get("shapes", []) if "nodes" in s]
            pb = [s for s in lb.get("shapes", []) if "nodes" in s]
            ca = [s for s in la.get("shapes", []) if "ref" in s]
            cb = [s for s in lb.get("shapes", []) if "ref" in s]
            if sorted(map(_path_sig, pa)) != sorted(map(_path_sig, pb)):
                notes.append(f"outline changed ({sum(len(s['nodes']) for s in pa)} -> {sum(len(s['nodes']) for s in pb)} nodes)")
            elif pa != pb:
                notes.append("same points, direction or start changed")
            if ca != cb:
                notes.append("components changed")
        elif key == "width":
            notes.append(f"width {la.get(key)} -> {lb.get(key)}")
        else:
            notes.append(f"{key} changed")
    return notes


def diff(path_a, path_b):
    A, B = plist.load(path_a), plist.load(path_b)
    mid = A["fontMaster"][0]["id"]
    ga = {g["glyphname"]: g for g in A["glyphs"]}
    gb = {g["glyphname"]: g for g in B["glyphs"]}
    lines = [f"Glyphs: {len(ga)} -> {len(gb)}"]
    if set(gb) - set(ga):
        lines.append("Added: " + " ".join(sorted(set(gb) - set(ga))))
    if set(ga) - set(gb):
        lines.append("Removed: " + " ".join(sorted(set(ga) - set(gb))))
    changed = [n for n in ga if n in gb and _strip(ga[n]) != _strip(gb[n])]
    lines.append(f"Changed: {len(changed)}")
    groups = {}
    for n in changed:
        groups.setdefault("; ".join(describe(_strip(ga[n]), _strip(gb[n]), mid)) or "other", []).append(n)
    for what, names in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        lines.append(f"- {what}: {' '.join(names)}")
    for key in sorted(set(A) | set(B)):
        if key != "glyphs" and A.get(key) != B.get(key):
            lines.append(f"Font-level change: {key}")
    return "\n".join(lines)
