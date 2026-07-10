#!/usr/bin/env python3
"""Generate the corner field ornament for ryangoodwin.cv.

A grid of marks on a fixed pitch: a dot at every node, a cross at every
fourth. Each mark's opacity is a superellipse falloff anchored just outside
the lower-right corner, so the field is densest in the corner and gone before
it reaches the text.

Pitch is in CSS pixels and the SVG is emitted at its final rendered size, so
the pitch on screen is exactly PITCH -- lock it to the body line-height and
the field's rows land on the text baselines.
"""

import math
import random

W = H = 900
PITCH = 30          # css px; match the body line-height
CROSS_EVERY = 4     # a cross at every Nth node, on both axes

# Superellipse falloff: |dx/a|^n + |dy/b|^n, anchored off-canvas so we only
# ever see the shoulder of it, never the centre. Bottom-right corner.
FOCUS = (W + 70.0, H + 70.0)
A = B = 880.0
N = 3.4             # 2 = circle, ->inf = square. ~3.4 is the squircle.
GAMMA = 1.55        # falloff curve; >1 pulls the light back toward the corner

DOT_R = 0.9
DOT_ALPHA = 0.55
CROSS_ARM = 5.5
CROSS_W = 0.8
CROSS_ALPHA = 0.75

JITTER = 0.6        # px; kills moire, invisible on its own
MIN_ALPHA = 0.03    # below this a mark is not worth the bytes

THEMES = {
    "light": "#6f4e33",   # warm brown ink on ivory
    "dark": "#c9a24b",    # brass-gold on espresso
}


def falloff(x: float, y: float) -> float:
    dx = abs(x - FOCUS[0]) / A
    dy = abs(y - FOCUS[1]) / B
    u = (dx ** N + dy ** N) ** (1.0 / N)
    return max(0.0, min(1.0, 1.0 - u)) ** GAMMA


def build(color: str) -> str:
    rnd = random.Random(0x5EED)   # same field every build
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" fill="none">',
        f'<g fill="{color}" stroke="{color}" stroke-width="{CROSS_W}" '
        f'stroke-linecap="round">',
    ]

    cols = W // PITCH + 1
    rows = H // PITCH + 1
    for iy in range(rows):
        for ix in range(cols):
            x = ix * PITCH + rnd.uniform(-JITTER, JITTER)
            y = iy * PITCH + rnd.uniform(-JITTER, JITTER)
            f = falloff(x, y)
            if f <= 0:
                continue

            is_cross = ix % CROSS_EVERY == 0 and iy % CROSS_EVERY == 0
            a = f * (CROSS_ALPHA if is_cross else DOT_ALPHA)
            if a < MIN_ALPHA:
                continue

            if is_cross:
                out.append(
                    f'<path d="M{x - CROSS_ARM:.1f} {y:.1f}h{CROSS_ARM * 2:.1f}'
                    f'M{x:.1f} {y - CROSS_ARM:.1f}v{CROSS_ARM * 2:.1f}" '
                    f'opacity="{a:.3f}"/>'
                )
            else:
                out.append(
                    f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{DOT_R}" '
                    f'stroke="none" opacity="{a:.3f}"/>'
                )

    out.append("</g></svg>")
    return "".join(out)


for name, color in THEMES.items():
    path = f"/home/ryan/ryan-site/static/img/field-{name}.svg"
    svg = build(color)
    with open(path, "w") as fh:
        fh.write(svg)
    marks = svg.count("<circle") + svg.count("<path")
    print(f"{path}: {len(svg):,} bytes, {marks} marks")
