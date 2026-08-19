"""Wipe leftover SAS ghosts and redraw part 2 once."""
from __future__ import annotations

import math
import shutil
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

PATH = Path(
    r"c:\Users\User\OneDrive - The Education University of Hong Kong\桌面\comics"
    r"\Special lines and centres in triangles\similar-congruent-chapter-3-layout-fixed.png"
)
DESKTOP = Path(r"C:\Users\User\OneDrive - The Education University of Hong Kong\桌面")

PARCH = (248, 234, 200)
INK = (24, 40, 58)
RED = (221, 63, 69)
BLUE = (38, 112, 197)
GREEN = (40, 161, 95)
PURPLE = (129, 64, 180)
# Stay inside part 2 body; do not touch header 212-242 or part 3 at 416.
BODY = (442, 246, 752, 411)


def fnt(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", size)


def text_size(draw: ImageDraw.ImageDraw, text: str, font) -> tuple[int, int]:
    b = draw.textbbox((0, 0), text, font=font)
    return b[2] - b[0], b[3] - b[1]


def draw_dot(draw, pt, col, r=3) -> None:
    x, y = pt
    draw.ellipse((x - r, y - r, x + r, y + r), fill=col)


def label_vertex(draw, pt, letter, col, place, font) -> None:
    x, y = pt
    tw, th = text_size(draw, letter, font)
    if place == "L":
        draw.text((x - tw - 5, y - th // 2 - 1), letter, font=font, fill=col)
    elif place == "BR":
        draw.text((x + 6, y + 2), letter, font=font, fill=col)
    elif place == "T":
        draw.text((x - tw // 2, y - th - 5), letter, font=font, fill=col)


def angle_arc(draw, vertex, p1, p2, radius, col) -> None:
    vx, vy = vertex
    a1 = math.atan2(p1[1] - vy, p1[0] - vx)
    a2 = math.atan2(p2[1] - vy, p2[0] - vx)
    d = (a2 - a1) % (2 * math.pi)
    if d > math.pi:
        a1, a2 = a2, a1
        d = (a2 - a1) % (2 * math.pi)
    pts = []
    for i in range(12):
        t = a1 + d * i / 11
        pts.append((vx + radius * math.cos(t), vy + radius * math.sin(t)))
    draw.line(pts, fill=col, width=2)


def side_label(draw, p, q, interior, text, font, gap=13) -> None:
    mx, my = (p[0] + q[0]) / 2.0, (p[1] + q[1]) / 2.0
    vx, vy = interior[0] - mx, interior[1] - my
    length = math.hypot(vx, vy) or 1
    ox = mx - vx / length * gap
    oy = my - vy / length * gap
    tw, th = text_size(draw, text, font)
    draw.text((int(ox - tw / 2), int(oy - th / 2)), text, font=font, fill=INK)


def main() -> None:
    img = Image.open(PATH).convert("RGB")
    arr = np.array(img)
    x0, y0, x1, y1 = BODY
    arr[y0:y1, x0:x1] = np.array(PARCH, dtype=np.uint8)
    img = Image.fromarray(arr)
    draw = ImageDraw.Draw(img)
    lab = fnt(12)
    num = fnt(13)
    capf = fnt(12)

    u = 11
    base_y = 360
    B = (518, base_y)
    A = (B[0] - 4 * u, base_y)
    C = (
        int(B[0] + 6 * u * math.cos(math.radians(120))),
        int(B[1] - 6 * u * math.sin(math.radians(60))),
    )
    E = (688, base_y)
    D = (E[0] - 6 * u, base_y)
    F = (
        int(E[0] + 9 * u * math.cos(math.radians(120))),
        int(E[1] - 9 * u * math.sin(math.radians(60))),
    )
    A, B, C = (int(A[0]), int(A[1])), (int(B[0]), int(B[1])), (int(C[0]), int(C[1]))
    D, E, F = (int(D[0]), int(D[1])), (int(E[0]), int(E[1])), (int(F[0]), int(F[1]))

    draw.line([A, B, C, A], fill=INK, width=2)
    draw.line([D, E, F, D], fill=INK, width=2)
    angle_arc(draw, B, A, C, 14, PURPLE)
    angle_arc(draw, E, D, F, 16, PURPLE)

    for pt, letter, col, place in [
        (A, "A", RED, "L"),
        (B, "B", BLUE, "BR"),
        (C, "C", GREEN, "T"),
        (D, "D", RED, "L"),
        (E, "E", BLUE, "BR"),
        (F, "F", GREEN, "T"),
    ]:
        draw_dot(draw, pt, col)
        label_vertex(draw, pt, letter, col, place, lab)

    tw, _ = text_size(draw, "4", num)
    draw.text(((A[0] + B[0]) // 2 - tw // 2, A[1] + 6), "4", font=num, fill=INK)
    tw, _ = text_size(draw, "6", num)
    draw.text(((D[0] + E[0]) // 2 - tw // 2, D[1] + 6), "6", font=num, fill=INK)
    side_label(draw, B, C, A, "6", num, gap=14)
    side_label(draw, E, F, D, "9", num, gap=15)

    cap = "4/6 = 6/9;  angle B = angle E = 60 deg"
    tw, _ = text_size(draw, cap, capf)
    draw.text((441 + (753 - 441 - tw) // 2, 390), cap, font=capf, fill=PURPLE)

    img.save(PATH)
    shutil.copy2(PATH, DESKTOP / "similar-congruent-chapter-3-layout-fixed.png")
    print("ABC", A, B, C)
    print("DEF", D, E, F)


if __name__ == "__main__":
    main()
