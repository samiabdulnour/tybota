import math

HEAD_TOPS = (500, 628, 670, 740)
FOOT_BOTTOMS = (0, -200)


def bracket_nodes(nodes, rise, run, k=0.58):
    """nodes: closed path as [x, y, t] with t in 'l', 'ls', 'c', 'cs', 'o' (cyclic order).
    Rounds the concave corner where a (near) vertical stem edge meets a slab serif at the head or foot of a stem.
    Crossbars and arms are left alone. Returns (new_nodes, number_of_corners)."""
    n = len(nodes)
    out = []
    count = 0
    for i in range(n):
        P, prev, nxt = nodes[i], nodes[i - 1], nodes[(i + 1) % n]
        done = False
        if P[2] == 'l' and nxt[2][0] == 'l' and prev[2][0] != 'o':
            vin = (P[0] - prev[0], P[1] - prev[1])
            vout = (nxt[0] - P[0], nxt[1] - P[1])
            cross = vin[0] * vout[1] - vin[1] * vout[0]
            if cross < 0:
                in_vert = abs(vin[0]) <= max(3, 0.03 * abs(vin[1])) and abs(vin[1]) >= 60
                in_horz = abs(vin[1]) < 0.5
                out_vert = abs(vout[0]) <= max(3, 0.03 * abs(vout[1])) and abs(vout[1]) >= 60
                out_horz = abs(vout[1]) < 0.5
                kind = None
                if in_vert and out_horz:
                    f2, f3 = nodes[(i + 2) % n], nodes[(i + 3) % n]
                    face = (f2[0] - nxt[0], f2[1] - nxt[1])
                    face_ok = f2[2][0] == 'l' and abs(face[0]) < 0.5 and 44 <= abs(face[1]) <= 60
                    outer = (f3[0] - f2[0], f3[1] - f2[1]) if f3[2][0] == 'l' else None
                    fy = (nxt[1], f2[1])
                    lh, lv = abs(vout[0]), abs(vin[1])
                    head = vin[1] > 0
                    kind = 'in'
                elif in_horz and out_vert:
                    f2, f3 = nodes[i - 2], nodes[i - 3]
                    face = (prev[0] - f2[0], prev[1] - f2[1])
                    face_ok = prev[2][0] == 'l' and f2[2][0] != 'o' and abs(face[0]) < 0.5 and 44 <= abs(face[1]) <= 60
                    outer = (f2[0] - f3[0], f2[1] - f3[1]) if (f2[2][0] == 'l' and f3[2][0] != 'o') else None
                    fy = (f2[1], prev[1])
                    lh, lv = abs(vin[0]), abs(vout[1])
                    head = vout[1] < 0
                    kind = 'out'
                ok = False
                if kind and face_ok and lh >= 30:
                    if head:
                        top = max(fy)
                        zone = any(abs(top - z) <= 4 for z in HEAD_TOPS)
                        covers = outer is not None and abs(outer[1]) < 0.5 and abs(outer[0]) >= lh + 40
                        ok = zone and covers
                    else:
                        bottom = min(fy)
                        ok = any(abs(bottom - z) <= 4 for z in FOOT_BOTTOMS)
                if ok:
                    r_run = min(run, lh - 14)
                    r_rise = min(rise, lv * 0.45)
                    d_in = r_rise if kind == 'in' else r_run
                    d_out = r_run if kind == 'in' else r_rise
                    lin, lout = math.hypot(vin[0], vin[1]), math.hypot(vout[0], vout[1])
                    uin = (vin[0] / lin, vin[1] / lin)
                    uout = (vout[0] / lout, vout[1] / lout)
                    A = (P[0] - uin[0] * d_in, P[1] - uin[1] * d_in)
                    B = (P[0] + uout[0] * d_out, P[1] + uout[1] * d_out)
                    h1 = (A[0] + uin[0] * d_in * k, A[1] + uin[1] * d_in * k)
                    h2 = (B[0] - uout[0] * d_out * k, B[1] - uout[1] * d_out * k)
                    out.append([float(round(A[0])), float(round(A[1])), 'ls'])
                    out.append([float(round(h1[0])), float(round(h1[1])), 'o'])
                    out.append([float(round(h2[0])), float(round(h2[1])), 'o'])
                    out.append([float(round(B[0])), float(round(B[1])), 'cs'])
                    count += 1
                    done = True
        if not done:
            out.append(P)
    return out, count


def bracketed(font, rise, run):
    """Install bracketed outlines as in-memory overrides on a Font. Returns {glyph: corners}.
    The file on disk is not touched."""
    import copy

    done = {}
    for name in list(font.G):
        layer = font.layer(name)
        if not any("nodes" in s for s in layer.get("shapes", [])):
            continue
        new = copy.deepcopy(layer)
        count = 0
        for shape in new["shapes"]:
            if "nodes" in shape and shape.get("closed", 0) == 1:
                shape["nodes"], k = bracket_nodes(shape["nodes"], rise, run)
                count += k
        if count:
            font.override[name] = new
            done[name] = count
    return done
