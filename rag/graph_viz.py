import math


def render_subgraph_svg(subgraph, width=860, height=600, max_neighbors=18):
    """
    Renders the matched_nodes + edges from graphrag.get_traversed_subgraph
    as an inline SVG. No fabricated data — if there are no matches, it
    says so honestly instead of drawing fake nodes.

    Layout: hub-and-spoke. Matched nodes sit on a small inner ring near
    the center; their neighbors sit on a larger outer ring with enough
    angular spacing to keep labels legible. This matters once a query
    matches multiple concepts with many shared neighbors (a tight single
    ring becomes an unreadable knot of overlapping labels and crossing
    lines at that density).

    If a matched node has more neighbors than max_neighbors, only the
    first max_neighbors (in the order returned by the graph) are shown,
    and the truncation is reported back via the returned dict's
    "truncated" flag — so the UI can say so honestly rather than
    silently hiding data.

    Returns None if there are no matches, otherwise a dict:
        {"svg": <svg string>, "truncated": bool, "shown_neighbors": int}
    """

    matched_nodes = subgraph.get("matched_nodes", [])
    edges = subgraph.get("edges", [])

    if not matched_nodes:
        return None

    matched_set = set(matched_nodes)

    # Build neighbor list per matched node, deduplicated
    neighbors_by_match = {m: [] for m in matched_nodes}
    seen_pairs = set()

    for a, b in edges:
        # figure out which side is the matched node (edges are
        # (matched_node, neighbor) per get_traversed_subgraph's contract)
        if a in matched_set:
            m, nb = a, b
        elif b in matched_set:
            m, nb = b, a
        else:
            continue

        pair_key = (m, nb)
        if pair_key in seen_pairs or nb == m:
            continue
        seen_pairs.add(pair_key)
        neighbors_by_match[m].append(nb)

    # Cap neighbors per match if there are too many, keep a stable order
    truncated = False
    for m in neighbors_by_match:
        if len(neighbors_by_match[m]) > max_neighbors:
            neighbors_by_match[m] = neighbors_by_match[m][:max_neighbors]
            truncated = True

    # All unique neighbor nodes across all matches (for outer ring layout)
    all_neighbors = []
    seen = set()
    for m in matched_nodes:
        for nb in neighbors_by_match[m]:
            if nb not in seen:
                seen.add(nb)
                all_neighbors.append(nb)

    cx, cy = width / 2, height / 2

    inner_radius = 70 if len(matched_nodes) > 1 else 0
    outer_radius = min(width, height) / 2 - 90

    positions = {}

    # Matched nodes: small inner ring (or dead center if just one)
    n_matched = len(matched_nodes)
    for i, node in enumerate(matched_nodes):
        if n_matched == 1:
            positions[node] = (cx, cy)
        else:
            angle = (2 * math.pi * i) / n_matched
            positions[node] = (
                cx + inner_radius * math.cos(angle),
                cy + inner_radius * math.sin(angle),
            )

    # Neighbor nodes: outer ring, evenly spaced
    n_neighbors = len(all_neighbors)
    for i, node in enumerate(all_neighbors):
        angle = (2 * math.pi * i) / max(n_neighbors, 1)
        positions[node] = (
            cx + outer_radius * math.cos(angle),
            cy + outer_radius * math.sin(angle),
        )

    svg_parts = [
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'style="width:100%;height:auto;font-family:JetBrains Mono, monospace;">'
    ]

    # edges first, so nodes render on top
    for m in matched_nodes:
        for nb in neighbors_by_match[m]:
            if m in positions and nb in positions:
                x1, y1 = positions[m]
                x2, y2 = positions[nb]
                svg_parts.append(
                    f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                    f'stroke="#232B3D" stroke-width="1" />'
                )

    def draw_node(node, x, y, is_matched, angle=None):
        fill = "#5EE6C8" if is_matched else "#1A2233"
        stroke = "#5EE6C8" if is_matched else "#3A4458"
        r = 24 if is_matched else 16
        label_color = "#5EE6C8" if is_matched else "#8B95A8"
        font_size = 12 if is_matched else 10.5

        label = node if len(node) <= 16 else node[:14] + "…"

        # Position label based on angular position around the circle so
        # labels don't collide at the "equator" where adjacent nodes are
        # vertically close but horizontally crowded. Matched nodes (no
        # angle, near center) always label below.
        if angle is None:
            label_x, label_y, anchor = x, y + r + 14, "middle"
        else:
            cos_a, sin_a = math.cos(angle), math.sin(angle)
            offset = r + 8
            if abs(cos_a) > abs(sin_a):
                # left or right side of the circle
                if cos_a > 0:
                    label_x, anchor = x + offset, "start"
                else:
                    label_x, anchor = x - offset, "end"
                label_y = y + 4
            else:
                # top or bottom of the circle
                label_x, anchor = x, "middle"
                label_y = y + offset + 8 if sin_a > 0 else y - offset - 4

        parts = [
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="1.5" '
            f'{"filter=\"drop-shadow(0 0 6px rgba(94,230,200,0.6))\"" if is_matched else ""} />',
            f'<text x="{label_x:.1f}" y="{label_y:.1f}" text-anchor="{anchor}" '
            f'font-size="{font_size}" fill="{label_color}">{label}</text>',
        ]
        return "".join(parts)

    # neighbors first, matched nodes drawn last so they sit on top visually
    for i, node in enumerate(all_neighbors):
        x, y = positions[node]
        angle = (2 * math.pi * i) / max(n_neighbors, 1)
        svg_parts.append(draw_node(node, x, y, is_matched=False, angle=angle))

    for node in matched_nodes:
        x, y = positions[node]
        svg_parts.append(draw_node(node, x, y, is_matched=True, angle=None))

    svg_parts.append('</svg>')

    svg = "".join(svg_parts)

    return {"svg": svg, "truncated": truncated, "shown_neighbors": n_neighbors}