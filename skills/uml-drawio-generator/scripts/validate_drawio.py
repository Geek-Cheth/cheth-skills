#!/usr/bin/env python3
"""
Validate Draw.io (.drawio / mxfile XML) diagrams against the uml-drawio-generator skill rules.

Zero external dependencies (Python 3 standard library only).
Usage:
    python scripts/validate_drawio.py path/to/diagram.drawio [--strict]
"""

import argparse
import base64
import math
import sys
import urllib.parse
import xml.etree.ElementTree as ET
import zlib
from collections import defaultdict


def parse_style(style_str: str) -> dict:
    result = {}
    if not style_str:
        return result
    for part in style_str.split(";"):
        part = part.strip()
        if not part:
            continue
        if "=" in part:
            k, v = part.split("=", 1)
            result[k.strip()] = v.strip()
        else:
            result[part] = True
    return result


def load_graph_model(diagram_el: ET.Element):
    mgm = diagram_el.find("mxGraphModel")
    if mgm is not None:
        return mgm
    text = (diagram_el.text or "").strip()
    if not text:
        return None
    try:
        raw = base64.b64decode(text)
        xml_str = urllib.parse.unquote(zlib.decompress(raw, -15).decode("utf-8"))
        return ET.fromstring(xml_str)
    except Exception:
        return None


def get_abs_rect(cell_id: str, by_id: dict):
    """Return absolute (x, y, w, h) for a vertex cell, or None if not available."""
    c = by_id.get(cell_id)
    if c is None or c.attrib.get("vertex") != "1":
        return None
    g = c.find("mxGeometry")
    if g is None:
        return None
    x = float(g.attrib.get("x", 0))
    y = float(g.attrib.get("y", 0))
    w = float(g.attrib.get("width", 0))
    h = float(g.attrib.get("height", 0))
    parent_id = c.attrib.get("parent")
    seen = {cell_id}
    while parent_id and parent_id not in ("0", "1") and parent_id not in seen:
        seen.add(parent_id)
        p = by_id.get(parent_id)
        if p is None:
            break
        pg = p.find("mxGeometry")
        if pg is not None:
            x += float(pg.attrib.get("x", 0))
            y += float(pg.attrib.get("y", 0))
        parent_id = p.attrib.get("parent")
    return (x, y, w, h)


def get_parent_offset(cell_id: str, by_id: dict):
    """Return absolute (ox, oy) offset of cell's parent container."""
    c = by_id.get(cell_id)
    if c is None:
        return (0.0, 0.0)
    ox, oy = 0.0, 0.0
    parent_id = c.attrib.get("parent")
    seen = {cell_id}
    while parent_id and parent_id not in ("0", "1") and parent_id not in seen:
        seen.add(parent_id)
        p = by_id.get(parent_id)
        if p is None:
            break
        pg = p.find("mxGeometry")
        if pg is not None:
            ox += float(pg.attrib.get("x", 0))
            oy += float(pg.attrib.get("y", 0))
        parent_id = p.attrib.get("parent")
    return (ox, oy)


def rect_overlap(a, b, tol=1.0) -> bool:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return (
        ax + tol < bx + bw
        and bx + tol < ax + aw
        and ay + tol < by + bh
        and by + tol < ay + ah
    )


def rect_contains(outer, inner, tol=2.0) -> bool:
    ox, oy, ow, oh = outer
    ix, iy, iw, ih = inner
    return (
        ix >= ox - tol
        and iy >= oy - tol
        and ix + iw <= ox + ow + tol
        and iy + ih <= oy + oh + tol
    )


def port_abs_point(rect, px: float, py: float):
    x, y, w, h = rect
    return (x + w * px, y + h * py)


def build_edge_segments(edge_el, by_id, style):
    """Build explicit orthogonal segments from source port -> waypoints -> target port."""
    src_rect = get_abs_rect(edge_el.attrib.get("source"), by_id)
    tgt_rect = get_abs_rect(edge_el.attrib.get("target"), by_id)
    if not src_rect or not tgt_rect:
        return []
    try:
        ex, ey = float(style["exitX"]), float(style["exitY"])
        nx, ny = float(style["entryX"]), float(style["entryY"])
    except (KeyError, ValueError):
        return []

    p0 = port_abs_point(src_rect, ex, ey)
    p_end = port_abs_point(tgt_rect, nx, ny)
    ox, oy = get_parent_offset(edge_el.attrib.get("id"), by_id)

    geom = edge_el.find("mxGeometry")
    wpts = []
    if geom is not None:
        arr = geom.find("Array")
        if arr is not None:
            for pt in arr.findall("mxPoint"):
                if "x" in pt.attrib and "y" in pt.attrib:
                    wpts.append((float(pt.attrib["x"]) + ox, float(pt.attrib["y"]) + oy))

    pts = [p0] + wpts + [p_end]
    segs = []
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        # Only emit strictly horizontal or vertical segments (explicitly routed tracks)
        if abs(a[0] - b[0]) < 1.0 and abs(a[1] - b[1]) > 2.0:
            segs.append(("V", round(a[0], 1), min(a[1], b[1]), max(a[1], b[1])))
        elif abs(a[1] - b[1]) < 1.0 and abs(a[0] - b[0]) > 2.0:
            segs.append(("H", round(a[1], 1), min(a[0], b[0]), max(a[0], b[0])))
    return segs


def is_backdrop_box(cell, style, abs_rect, other_rects):
    """Detect intentional background zone containers (e.g., External Services backdrop)."""
    if "umlFrame" in style.get("shape", "") or "swimlane" in style:
        return True
    if style.get("container") == "1":
        return True
    # Rounded large backdrop with top-aligned label that encloses multiple behaviorAction/action boxes
    if style.get("verticalAlign") == "top" and "shape" not in style:
        enclosed = sum(
            1 for oid, orect in other_rects.items()
            if oid != cell.attrib.get("id") and rect_contains(abs_rect, orect)
        )
        if enclosed >= 2:
            return True
    return False


def validate_diagram(diagram_el: ET.Element, idx: int):
    errors = []
    warnings = []
    tab_name = diagram_el.attrib.get("name", f"Tab-{idx}")
    prefix = f"[{tab_name}]"

    mgm = load_graph_model(diagram_el)
    if mgm is None:
        errors.append(f"{prefix} Could not parse <mxGraphModel>.")
        return errors, warnings

    if mgm.attrib.get("grid") != "1" or mgm.attrib.get("gridSize") != "10":
        warnings.append(f"{prefix} Recommended grid='1' and gridSize='10' on <mxGraphModel>.")

    cells = mgm.findall(".//mxCell")
    by_id = {}
    for c in cells:
        cid = c.attrib.get("id")
        if cid is None:
            errors.append(f"{prefix} Found <mxCell> missing id attribute.")
            continue
        if cid in by_id:
            errors.append(f"{prefix} Duplicate mxCell id '{cid}'.")
        by_id[cid] = c

    vertices = [c for c in cells if c.attrib.get("vertex") == "1"]
    edges = [c for c in cells if c.attrib.get("edge") == "1"]

    frames = []
    swimlanes = []
    diamonds = []
    notes = []
    behavior_actions = []
    regular_vertices = []

    abs_rects = {}
    styles = {}

    for v in vertices:
        vid = v.attrib.get("id")
        st_str = v.attrib.get("style", "")
        st = parse_style(st_str)
        styles[vid] = st
        rect = get_abs_rect(vid, by_id)
        if rect is not None:
            abs_rects[vid] = rect

        parent = v.attrib.get("parent")
        if parent and parent not in by_id:
            errors.append(f"{prefix} Vertex '{vid}' references missing parent '{parent}'.")

        # 1. No images allowed
        if st.get("shape") == "image" or "image=data:" in st_str or "image=http" in st_str:
            errors.append(f"{prefix} Forbidden image detected on vertex '{vid}'. Images must be excluded.")

        shape = st.get("shape", "")
        if shape == "umlFrame":
            frames.append(v)
        elif "swimlane" in st:
            swimlanes.append(v)
        elif "rhombus" in st:
            diamonds.append(v)
        elif shape in ("note2", "note"):
            notes.append(v)
        elif "behaviorAction" in shape:
            behavior_actions.append(v)
        elif not ("text" in st or "edgeLabel" in st):
            regular_vertices.append(v)

        # Grid alignment check
        g = v.find("mxGeometry")
        if g is not None and not ("edgeLabel" in st):
            for attr in ("x", "y", "width", "height"):
                if attr in g.attrib:
                    val = float(g.attrib[attr])
                    if abs(val % 10) > 1e-6 and abs((val % 10) - 10) > 1e-6:
                        warnings.append(f"{prefix} Vertex '{vid}' {attr}={val} is not on the 10px grid.")

    # 2. Outer UML Frame required
    if len(frames) == 0:
        errors.append(f"{prefix} Missing outer UML Frame (shape=umlFrame).")
    else:
        frame_rect = abs_rects.get(frames[0].attrib.get("id"))
        if frame_rect:
            for vid, vrect in abs_rects.items():
                if vid == frames[0].attrib.get("id"):
                    continue
                if "edgeLabel" in styles.get(vid, {}):
                    continue
                if not rect_contains(frame_rect, vrect, tol=2.0):
                    errors.append(
                        f"{prefix} Vertex '{vid}' ({vrect}) extends outside outer umlFrame ({frame_rect})."
                    )

    # 3. Swimlane checks (Activity diagrams)
    is_activity = len(swimlanes) > 0
    if is_activity:
        lane_rects = sorted(
            [(l.attrib.get("id"), abs_rects[l.attrib.get("id")]) for l in swimlanes if l.attrib.get("id") in abs_rects],
            key=lambda item: item[1][0],
        )
        ys = {r[1] for _, r in lane_rects}
        hs = {r[3] for _, r in lane_rects}
        if len(ys) > 1:
            errors.append(f"{prefix} Swimlanes do not share the same y coordinate: {ys}.")
        if len(hs) > 1:
            errors.append(f"{prefix} Swimlanes do not share the same height: {hs}.")
        for i in range(len(lane_rects) - 1):
            lid_a, ra = lane_rects[i]
            lid_b, rb = lane_rects[i + 1]
            if abs((ra[0] + ra[2]) - rb[0]) > 1.0:
                warnings.append(
                    f"{prefix} Swimlanes '{lid_a}' and '{lid_b}' are not flush side-by-side "
                    f"({ra[0] + ra[2]} vs {rb[0]})."
                )
        # Ensure lane children stay within lane bounds
        for v in vertices:
            vid = v.attrib.get("id")
            p = v.attrib.get("parent")
            if p in [l.attrib.get("id") for l in swimlanes] and vid in abs_rects and p in abs_rects:
                if not rect_contains(abs_rects[p], abs_rects[vid], tol=1.0):
                    errors.append(f"{prefix} Vertex '{vid}' extends outside its parent swimlane '{p}'.")

    # 4. Diamond standard size (40x40) and empty value in activity diagrams
    for d in diamonds:
        did = d.attrib.get("id")
        g = d.find("mxGeometry")
        w = float(g.attrib.get("width", 0)) if g is not None else 0
        h = float(g.attrib.get("height", 0)) if g is not None else 0
        if abs(w - 40.0) > 0.1 or abs(h - 40.0) > 0.1:
            errors.append(
                f"{prefix} Diamond '{did}' has size {w:g}x{h:g}; standard size MUST be 40x40."
            )
        val = (d.attrib.get("value") or "").strip()
        if is_activity and val != "":
            errors.append(
                f"{prefix} Activity diamond '{did}' contains text {val!r}; "
                "diamonds in activity diagrams must be empty (put conditions as [guards] on outgoing edges)."
            )

    # 5. Edge checks: dangling refs, jumpStyle=arc, explicit ports, unique ports, diamond degree, collinear overlaps
    port_owners = defaultdict(list)  # (node_id, round(px,3), round(py,3)) -> [edge_id]
    flow_in = defaultdict(list)
    flow_out = defaultdict(list)
    all_segments = []

    for e in edges:
        eid = e.attrib.get("id")
        src = e.attrib.get("source")
        tgt = e.attrib.get("target")
        st_str = e.attrib.get("style", "")
        st = parse_style(st_str)
        is_note_link = st.get("dashed") == "1" and st.get("endArrow") == "none"

        if not src or src not in by_id:
            errors.append(f"{prefix} Edge '{eid}' has missing or dangling source '{src}'.")
        if not tgt or tgt not in by_id:
            errors.append(f"{prefix} Edge '{eid}' has missing or dangling target '{tgt}'.")

        # Mandatory orthogonal + arc jump
        if st.get("edgeStyle") != "orthogonalEdgeStyle":
            errors.append(f"{prefix} Edge '{eid}' missing edgeStyle=orthogonalEdgeStyle.")
        if st.get("jumpStyle") != "arc":
            errors.append(f"{prefix} Edge '{eid}' missing jumpStyle=arc (mandatory for line crossings).")

        # Mandatory explicit ports
        missing_ports = [k for k in ("exitX", "exitY", "entryX", "entryY") if k not in st]
        if missing_ports:
            errors.append(f"{prefix} Edge '{eid}' missing explicit port attributes: {missing_ports}.")
        else:
            try:
                ex, ey = round(float(st["exitX"]), 3), round(float(st["exitY"]), 3)
                nx, ny = round(float(st["entryX"]), 3), round(float(st["entryY"]), 3)
                if src:
                    port_owners[(src, ex, ey)].append((eid, "exit"))
                if tgt:
                    port_owners[(tgt, nx, ny)].append((eid, "entry"))
            except ValueError:
                errors.append(f"{prefix} Edge '{eid}' has non-numeric port coordinate.")

        if not is_note_link:
            if src:
                flow_out[src].append(e)
            if tgt:
                flow_in[tgt].append(e)

        # Check waypoints inside frame & collect segments
        geom = e.find("mxGeometry")
        ox, oy = get_parent_offset(eid, by_id)
        if geom is not None and frames:
            frame_rect = abs_rects.get(frames[0].attrib.get("id"))
            arr = geom.find("Array")
            if arr is not None and frame_rect:
                for pt in arr.findall("mxPoint"):
                    if "x" in pt.attrib and "y" in pt.attrib:
                        px, py = float(pt.attrib["x"]) + ox, float(pt.attrib["y"]) + oy
                        if not rect_contains(frame_rect, (px, py, 0, 0), tol=2.0):
                            errors.append(
                                f"{prefix} Edge '{eid}' waypoint ({px:g},{py:g}) lies outside outer umlFrame."
                            )

        segs = build_edge_segments(e, by_id, st)
        for seg in segs:
            all_segments.append((eid, seg))

    # 6. Zero port collisions (never join several lines at the same point!)
    for (nid, px, py), owners in port_owners.items():
        if len(owners) > 1:
            desc = ", ".join(f"{eid}({kind})" for eid, kind in owners)
            errors.append(
                f"{prefix} Port collision on node '{nid}' at ({px}, {py}): {desc}. "
                "Never join multiple lines at the same point; use distinct ports or insert a separate 40x40 merge/router diamond."
            )

    # 7. Diamond degree limits & bracketed guard check
    diamond_ids = {d.attrib.get("id") for d in diamonds}
    for did in diamond_ids:
        inc = flow_in[did]
        outc = flow_out[did]
        if len(inc) + len(outc) > 4:
            errors.append(
                f"{prefix} Diamond '{did}' has {len(inc)} incoming + {len(outc)} outgoing flow edges (max 4). "
                "Chain a separate 40x40 diamond instead."
            )
        if len(outc) > 3:
            errors.append(
                f"{prefix} Diamond '{did}' has {len(outc)} outgoing flow edges (max 3). "
                "Use a cascading second 40x40 diamond for extra branches."
            )
        if len(inc) > 3:
            errors.append(
                f"{prefix} Diamond '{did}' has {len(inc)} incoming flow edges (max 3). "
                "Use a cascading second 40x40 merge diamond."
            )
        if is_activity and len(outc) >= 2:
            for oe in outc:
                val = (oe.attrib.get("value") or "").strip()
                tgt = oe.attrib.get("target")
                # Allow unlabeled handoff only when cascading directly into another diamond
                if not val and tgt not in diamond_ids:
                    warnings.append(
                        f"{prefix} Decision edge '{oe.attrib.get('id')}' from diamond '{did}' has no [guard] label."
                    )
                elif val and not (val.startswith("[") and val.endswith("]")):
                    warnings.append(
                        f"{prefix} Decision edge '{oe.attrib.get('id')}' label {val!r} should be wrapped in [brackets]."
                    )

    # 8. Overlapping sibling shape bounding boxes
    backdrops = {
        v.attrib.get("id")
        for v in vertices
        if v.attrib.get("id") in abs_rects
        and is_backdrop_box(v, styles[v.attrib.get("id")], abs_rects[v.attrib.get("id")], abs_rects)
    }
    checkable = [
        v.attrib.get("id")
        for v in vertices
        if v.attrib.get("id") in abs_rects
        and v.attrib.get("id") not in backdrops
        and "edgeLabel" not in styles.get(v.attrib.get("id"), {})
        and "text" not in styles.get(v.attrib.get("id"), {})
    ]
    for i in range(len(checkable)):
        for j in range(i + 1, len(checkable)):
            a_id, b_id = checkable[i], checkable[j]
            # Skip parent-child pairs
            if by_id[a_id].attrib.get("parent") == b_id or by_id[b_id].attrib.get("parent") == a_id:
                continue
            if rect_overlap(abs_rects[a_id], abs_rects[b_id], tol=1.0):
                errors.append(
                    f"{prefix} Overlapping shapes: '{a_id}' {abs_rects[a_id]} overlaps '{b_id}' {abs_rects[b_id]}."
                )

    # 9. Collinear overlapping edge segments (distinct edges sharing the same track)
    for i in range(len(all_segments)):
        eid_a, (orient_a, coord_a, start_a, end_a) = all_segments[i]
        for j in range(i + 1, len(all_segments)):
            eid_b, (orient_b, coord_b, start_b, end_b) = all_segments[j]
            if eid_a == eid_b or orient_a != orient_b:
                continue
            if abs(coord_a - coord_b) <= 2.0:
                overlap_len = min(end_a, end_b) - max(start_a, start_b)
                if overlap_len > 8.0:
                    errors.append(
                        f"{prefix} Collinear overlapping edge segments: '{eid_a}' and '{eid_b}' "
                        f"overlap along {orient_a}={coord_a:g} for {overlap_len:.0f}px. "
                        "Separate parallel tracks by at least 30-40px."
                    )

    return errors, warnings


def main():
    parser = argparse.ArgumentParser(description="Validate a .drawio file against UML skill standards.")
    parser.add_argument("path", help="Path to the .drawio XML file")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    args = parser.parse_args()

    try:
        tree = ET.parse(args.path)
        root = tree.getroot()
    except Exception as exc:
        print(f"ERROR: Failed to parse XML '{args.path}': {exc}")
        return 2

    if root.tag == "mxGraphModel":
        diagrams = [ET.Element("diagram", {"name": "Page-1"})]
        diagrams[0].append(root)
    else:
        diagrams = root.findall(".//diagram")

    if not diagrams:
        print("ERROR: No <diagram> elements found in file.")
        return 2

    total_errors = []
    total_warnings = []
    for idx, d in enumerate(diagrams):
        errs, warns = validate_diagram(d, idx)
        total_errors.extend(errs)
        total_warnings.extend(warns)

    print(f"Checked {len(diagrams)} diagram tab(s) in '{args.path}'.")
    if total_warnings:
        print(f"\nWARNINGS ({len(total_warnings)}):")
        for w in total_warnings:
            print(f"  [WARN] {w}")
    if total_errors:
        print(f"\nERRORS ({len(total_errors)}):")
        for e in total_errors:
            print(f"  [ERR]  {e}")
        return 1

    if args.strict and total_warnings:
        return 1

    print("PASS: All UML Draw.io skill checks passed with 0 errors.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
