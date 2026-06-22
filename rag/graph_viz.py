import math


def render_subgraph_svg(subgraph, width=640, height=320):
    """
    Renders the matched_nodes + edges from graphrag.get_traversed_subgraph
    as an inline SVG. No fabricated data — if there are no matches,
    it says so honestly instead of drawing fake nodes.
    """

    matched_nodes = subgraph.get("matched_nodes", [])
    edges = subgraph.get("edges", [])

    if not matched_nodes:
        return None

    # Collect unique node set (matched + their neighbors)
    all_nodes = set(matched_nodes)
    for a, b in edges:
        all_nodes.add(a)
        all_nodes.add(b)

    all_nodes = list(all_nodes)
    n = len(all_nodes)

    cx, cy = width / 2, height / 2
    radius = min(width, height) / 2 - 70

    positions = {}
    for i, node in enumerate(all_nodes):
        angle = (2 * math.pi * i) / max(n, 1)
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        positions[node] = (x, y)

    svg_parts = [
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'style="width:100%;height:auto;font-family:JetBrains Mono, monospace;">'
    ]

    # edges first (so nodes render on top)
    for a, b in edges:
        if a in positions and b in positions:
            x1, y1 = positions[a]
            x2, y2 = positions[b]
            svg_parts.append(
                f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                f'stroke="#232B3D" stroke-width="1.4" />'
            )

    # nodes
    for node in all_nodes:
        x, y = positions[node]
        is_matched = node in matched_nodes
        fill = "#5EE6C8" if is_matched else "#1A2233"
        stroke = "#5EE6C8" if is_matched else "#3A4458"
        text_color = "#0B0E14" if is_matched else "#C3CAD9"
        r = 26 if is_matched else 20

        label = node if len(node) <= 14 else node[:12] + "…"

        svg_parts.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="1.5" '
            f'{"filter=\"drop-shadow(0 0 6px rgba(94,230,200,0.6))\"" if is_matched else ""} />'
        )
        svg_parts.append(
            f'<text x="{x:.1f}" y="{y + 38:.1f}" text-anchor="middle" '
            f'font-size="11" fill="{"#5EE6C8" if is_matched else "#8B95A8"}">{label}</text>'
        )

    svg_parts.append('</svg>')

    return "".join(svg_parts)