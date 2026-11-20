#!/usr/bin/env python3
"""emdash-mindmap - auto MindMap from a markdown file for EmDash.

Parses ATX headings + list items into a tree and emits a self-contained
SVG mindmap (no dependencies, tiny RAM: streams lines, holds only the tree).
Mirrors obsidian-mindmap-nextgen core: hierarchy, per-level colors,
collapsible nodes (click), depth limit.

  emdash-mindmap FILE [--depth N] [--out map.svg]
"""
import html
import re
import sys

COLORS = ["#e8e8e8", "#7dd3fc", "#86efac", "#fde68a", "#fca5a5", "#c4b5fd"]
W, LH, XSTEP = 220, 30, 200


def parse(path):
    """-> (roots, ) list of (level, text). Headings + list items."""
    nodes = []
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip("\n")
            m = re.match(r"^(#{1,6})\s+(.*)", line)
            if m:
                nodes.append((len(m.group(1)) - 1, m.group(2).strip()))
                continue
            m = re.match(r"^(\s*)[-*+]\s+(.*)", line)
            if m:
                nodes.append((len(m.group(1)) // 2 + 1, m.group(2).strip()))
    return nodes


def build(nodes, maxdepth=6):
    """Flat (level, text) -> nested dicts clipped to maxdepth."""
    roots, stack = [], []
    for level, text in nodes:
        if level > maxdepth:
            continue
        node = {"text": text, "children": [], "level": level}
        while stack and stack[-1]["level"] >= level:
            stack.pop()
        if stack:
            stack[-1]["children"].append(node)
        else:
            roots.append(node)
        stack.append(node)
    return roots


def layout(roots):
    """Assign y positions; returns (svg_body, height)."""
    parts = []
    y = [30]

    def walk(nodes, depth, x):
        for n in nodes:
            cy = y[0]
            y[0] += LH
            color = COLORS[min(depth, len(COLORS) - 1)]
            label = html.escape(n["text"][:40])
            parts.append(
                f'<g class="node" data-d="{depth}">'
                f'<line x1="{x}" y1="{cy}" x2="{x + XSTEP}" y2="{cy}" stroke="#555"/>'
                f'<rect x="{x + XSTEP}" y="{cy - 11}" width="{W}" height="22" rx="4" fill="{color}" fill-opacity="0.15" stroke="{color}"/>'
                f'<text x="{x + XSTEP + 8}" y="{cy + 4}" font-size="12" fill="{color}">{label}</text>'
                f"</g>")
            if n["children"]:
                walk(n["children"], depth + 1, x + XSTEP + W)
    walk(roots, 0, 20)
    return "".join(parts), y[0] + 20


def render(roots, title):
    body, height = layout(roots)
    width = 20 + 4 * (XSTEP + W)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" font-family="monospace">
<title>{html.escape(title)}</title>
<style>.node{{cursor:pointer}}.node.hidden{{display:none}}text{{pointer-events:none}}</style>
{body}
<script><![CDATA[
document.querySelectorAll('.node').forEach(g=>g.addEventListener('click',e=>{{
  const d=+g.dataset.d;let s=g.nextElementSibling,n=0;
  while(s&&+s.dataset.d>d){{s.classList.toggle('hidden');s=s.nextElementSibling}}
  e.stopPropagation();
}}));
]]></script>
</svg>
"""


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        sys.exit("usage: emdash-mindmap FILE [--depth N] [--out map.svg]")
    depth, out = 6, None
    if "--depth" in argv:
        depth = int(argv[argv.index("--depth") + 1])
    if "--out" in argv:
        out = argv[argv.index("--out") + 1]
    roots = build(parse(argv[0]), depth)
    svg = render(roots, argv[0])
    if out:
        open(out, "w").write(svg)
        print(out)
    else:
        print(svg)


if __name__ == "__main__":
    main(sys.argv[1:])
