"""Final pass: clear, mathematically correct geometry on maze triangle comics."""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(r"c:\Users\UniplusUser02\Desktop\comics\Special lines and centres in triangles")
INK = "#172030"
NAVY = "#102c61"
BLUE = "#1769d2"
GREEN = "#159447"
RED = "#d93434"
GOLD = "#c88713"
PURPLE = "#7b3fc6"
PANEL = "#fffaf0"
R, B, G = "#d93434", "#1769d2", "#159447"


def fnt(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "arialbd.ttf" if bold else "arial.ttf"
    return ImageFont.truetype(str(Path(r"C:\Windows\Fonts") / name), size)


F10, F11, B10, B11, B12, B13, B14 = fnt(10), fnt(11), fnt(10, True), fnt(11, True), fnt(12, True), fnt(13, True), fnt(14, True)


def diagram_canvas(draw: ImageDraw.ImageDraw, y: int) -> None:
    draw.rounded_rectangle((440, y + 84, 752, y + 192), radius=8, fill=PANEL, outline="#c8b896", width=1)


def tri_coords(ab: float, bc: float, ac: float, origin: tuple[int, int], unit: float):
    ox, oy = origin
    bx = ab * unit
    x = (ac * ac - bc * bc + ab * ab) / (2 * ab)
    h = math.sqrt(max(ac * ac - x * x, 0))
    return (ox, oy), (ox + int(bx), oy), (ox + int(x * unit), oy - int(h * unit))


def _same_side(p, a, b, c):
    return ((p[0] - b[0]) * (a[1] - b[1]) - (a[0] - b[0]) * (p[1] - b[1])) * (
        (c[0] - b[0]) * (a[1] - b[1]) - (a[0] - b[0]) * (c[1] - b[1])
    ) >= 0


def point_in_tri(pt, pts, pad=6):
    a, b, c = pts
    return _same_side(pt, a, b, c) and _same_side(pt, b, c, a) and _same_side(pt, c, a, b)


def outward_label(pts, i, dist=24):
    cx = sum(p[0] for p in pts) / 3
    cy = sum(p[1] for p in pts) / 3
    vx = pts[i][0] - cx
    vy = pts[i][1] - cy
    n = math.hypot(vx, vy) or 1
    ux, uy = vx / n, vy / n
    x = pts[i][0] + ux * dist
    y = pts[i][1] + uy * dist
    while point_in_tri((x, y), pts) and dist < 40:
        dist += 4
        x = pts[i][0] + ux * dist
        y = pts[i][1] + uy * dist
    return x, y


def draw_tri(
    draw: ImageDraw.ImageDraw,
    pts,
    labels=("A", "B", "C"),
    colors=(R, B, G),
    width=3,
):
    draw.line([pts[0], pts[1], pts[2], pts[0]], fill=INK, width=width, joint="curve")
    for i, (p, lab, col) in enumerate(zip(pts, labels, colors)):
        draw.ellipse((p[0] - 2, p[1] - 2, p[0] + 2, p[1] + 2), fill=col)
        lx, ly = outward_label(pts, i)
        draw.text((lx, ly), lab, font=B11, fill=col, anchor="mm")


def mid(p1, p2):
    return ((p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2)


def side_label(draw, p1, p2, text, d=14):
    mx, my = mid(p1, p2)
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    n = math.hypot(dx, dy) or 1
    nx, ny = -dy / n, dx / n
    draw.text((mx + nx * d, my + ny * d), text, font=B11, fill=INK, anchor="mm")


def ticks(draw, p1, p2, n, color=RED):
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    ln = math.hypot(dx, dy) or 1
    tx, ty, nx, ny = dx / ln, dy / ln, -dy / ln, dx / ln
    mx, my = mid(p1, p2)
    for i in range(n):
        s = (i - (n - 1) / 2) * 5
        cx, cy = mx + tx * s, my + ty * s
        draw.line((cx - nx * 5, cy - ny * 5, cx + nx * 5, cy + ny * 5), fill=color, width=2)


def arc(draw, v, p1, p2, r=11, color=BLUE, w=2):
    a1 = math.degrees(math.atan2(p1[1] - v[1], p1[0] - v[0]))
    a2 = math.degrees(math.atan2(p2[1] - v[1], p2[0] - v[0]))
    while a2 < a1:
        a2 += 360
    if a2 - a1 > 180:
        a1, a2 = a2, a1 + 360
    draw.arc((v[0] - r, v[1] - r, v[0] + r, v[1] + r), a1, a2, fill=color, width=w)


def right_angle(draw, v, p1, p2, s=9):
    def u(a, b):
        dx, dy = b[0] - a[0], b[1] - a[1]
        n = math.hypot(dx, dy) or 1
        return dx / n, dy / n

    u1, u2 = u(v, p1), u(v, p2)
    a = (v[0] + u1[0] * s, v[1] + u1[1] * s)
    b = (a[0] + u2[0] * s, a[1] + u2[1] * s)
    c = (v[0] + u2[0] * s, v[1] + u2[1] * s)
    draw.line((a, b, c), fill=BLUE, width=2)


def similar_pair(draw, y, s1, s2, unit=5.5, x1=458, x2=602):
    display_unit = unit * 1.5
    t1 = tri_coords(*s1, (x1, y + 156), display_unit)
    t2 = tri_coords(*s2, (x2, y + 156), display_unit)
    draw_tri(draw, t1)
    draw_tri(draw, t2, ("D", "E", "F"))
    return t1, t2


def congruent_pair(draw, y, sides, unit=5.8, x1=458, x2=602):
    display_unit = unit * 1.5
    t1 = tri_coords(*sides, (x1, y + 156), display_unit)
    t2 = tri_coords(*sides, (x2, y + 156), display_unit)
    draw_tri(draw, t1)
    draw_tri(draw, t2, ("D", "E", "F"))
    return t1, t2


def badge(draw, y, text, color=GREEN):
    draw.rounded_rectangle((452, y + 168, 452 + 8 + draw.textlength(text, font=B11), y + 188),
                           radius=5, fill="white", outline=color, width=2)
    draw.text((456, y + 171), text, font=B11, fill=color)


def note(draw, y, text, color=INK, x=452):
    draw.text((x, y + 170), text, font=B11, fill=color)


def fix(chapter, panels):
    path = OUT / f"similar-congruent-chapter-{chapter}-color.png"
    im = Image.open(path).convert("RGB")
    d = ImageDraw.Draw(im)
    for i, fn in enumerate(panels):
        diagram_canvas(d, i * 204)
        fn(d, i * 204)
    im.save(path)


# ---- Chapter 1 ----
def ch1():
    def p1(d, y):
        t1, t2 = similar_pair(d, y, (3, 4, 5), (3, 4, 5), 6.2)
        arc(d, t1[0], t1[1], t1[2], 10, R)
        arc(d, t2[0], t2[1], t2[2], 10, R)

    def p2(d, y):
        d.text((452, y + 96), "A - D    B - E    C - F", font=B13, fill=PURPLE)
        d.text((452, y + 122), "Triangle ABC ~ Triangle DEF", font=B12, fill=NAVY)
        d.text((452, y + 148), "first-first, second-second, third-third", font=F10, fill=INK)

    def p3(d, y):
        d.text((452, y + 100), "AB - DE", font=B12, fill=NAVY)
        d.text((452, y + 122), "BC - EF", font=B12, fill=NAVY)
        d.text((452, y + 144), "AC - DF", font=B12, fill=NAVY)
        d.line((452, y + 166, 742, y + 166), fill=GREEN, width=3)

    def p4(d, y):
        d.text((452, y + 98), "Triangle ABC ~ Triangle DFE", font=B11, fill=RED)
        d.line((450, y + 94, 742, y + 132), fill=RED, width=4)
        d.text((452, y + 142), "Wrong: B would match F.", font=B12, fill=RED)
        t1, _ = similar_pair(d, y, (3, 4, 5), (3, 4, 5), 5.5)
        d.text((452, y + 166), "Match colours at each vertex.", font=F10, fill=INK)

    def p5(d, y):
        similar_pair(d, y, (3, 4, 5), (3, 4, 5), 6.2)
        badge(d, y, "CHECKPOINT: C matches F")

    fix(1, [p1, p2, p3, p4, p5])


# ---- Chapter 2 ----
def ch2():
    def p1(d, y):
        t1, t2 = similar_pair(d, y, (3, 4, 5), (6, 8, 10), 5.2)
        arc(d, t1[0], t1[1], t1[2], 10, R)
        arc(d, t2[0], t2[1], t2[2], 10, R)
        note(d, y, "same shape; different size", BLUE)

    def p2(d, y):
        t1, t2 = similar_pair(d, y, (3, 4, 5), (6, 8, 10), 5.2)
        side_label(d, t1[0], t1[1], "3")
        side_label(d, t1[1], t1[2], "4")
        side_label(d, t1[0], t1[2], "5")
        side_label(d, t2[0], t2[1], "6")
        side_label(d, t2[1], t2[2], "8")
        side_label(d, t2[0], t2[2], "10")
        badge(d, y, "3/6 = 4/8 = 5/10", BLUE)

    def p3(d, y):
        d.text((452, y + 96), "3 x 2 = 6", font=B13, fill=BLUE)
        d.text((452, y + 118), "4 x 2 = 8", font=B13, fill=BLUE)
        d.text((452, y + 140), "5 x 2 = 10", font=B13, fill=BLUE)
        d.text((452, y + 166), "scale factor = 2", font=B12, fill=PURPLE)

    def p4(d, y):
        t1, t2 = similar_pair(d, y, (4, 6, 5), (6, 9, 7.5), 5.8)
        side_label(d, t1[0], t1[1], "4")
        side_label(d, t1[1], t1[2], "6")
        side_label(d, t2[0], t2[1], "6")
        side_label(d, t2[1], t2[2], "x")
        note(d, y, "6/4 = 1.5,  x = 6 x 1.5 = 9", GREEN)

    def p5(d, y):
        t1, t2 = similar_pair(d, y, (3, 4, 5), (6, 8, 10), 4.8)
        arc(d, t1[0], t1[1], t1[2], 9, R)
        arc(d, t2[0], t2[1], t2[2], 9, R)
        d.text((452, y + 96), "ANGLES: equal", font=B12, fill=BLUE)
        d.text((452, y + 118), "SIDES: proportional", font=B12, fill=GREEN)
        badge(d, y, "PASSAGE OPEN", GOLD)

    fix(2, [p1, p2, p3, p4, p5])


# ---- Chapter 3 ----
def ch3():
    def p1(d, y):
        t1, t2 = similar_pair(d, y, (3, 4, 5), (6, 8, 10), 5.0)
        arc(d, t1[0], t1[1], t1[2], 10, R)
        arc(d, t1[1], t1[0], t1[2], 10, B)
        arc(d, t2[0], t2[1], t2[2], 10, R)
        arc(d, t2[1], t2[0], t2[2], 10, B)
        badge(d, y, "AA", BLUE)

    def p2(d, y):
        sas_small = (4, 6, math.sqrt(28))
        sas_large = (6, 9, math.sqrt(63))
        t1, t2 = similar_pair(d, y, sas_small, sas_large, 5.5)
        side_label(d, t1[0], t1[1], "4")
        side_label(d, t1[1], t1[2], "6")
        side_label(d, t2[0], t2[1], "6")
        side_label(d, t2[1], t2[2], "9")
        arc(d, t1[1], t1[0], t1[2], 12, PURPLE, 3)
        arc(d, t2[1], t2[0], t2[2], 12, PURPLE, 3)
        note(d, y, "4/6 = 6/9; angle B = angle E = 60 deg", PURPLE)

    def p3(d, y):
        t1, t2 = similar_pair(d, y, (3, 4, 5), (6, 8, 10), 5.0)
        side_label(d, t1[0], t1[1], "3")
        side_label(d, t1[1], t1[2], "4")
        side_label(d, t1[0], t1[2], "5")
        side_label(d, t2[0], t2[1], "6")
        side_label(d, t2[1], t2[2], "8")
        side_label(d, t2[0], t2[2], "10")
        note(d, y, "3/6 = 4/8 = 5/10", GREEN)

    def p4(d, y):
        similar_pair(d, y, (3, 4, 5), (6, 8, 10), 3.8)
        d.text((452, y + 148), "AAA fixes SHAPE only.", font=B11, fill=BLUE)
        d.text((452, y + 166), "Similar, not congruent.", font=F10, fill=RED)

    def p5(d, y):
        t1, t2 = similar_pair(d, y, (4, 5, 4.5), (6, 7.5, 6.75), 5.0)
        arc(d, t1[0], t1[1], t1[2], 9, R)
        arc(d, t1[1], t1[0], t1[2], 9, B)
        arc(d, t2[0], t2[1], t2[2], 9, R)
        arc(d, t2[1], t2[0], t2[2], 9, B)
        d.text((452, y + 92), "70 deg at A and D", font=F10, fill=NAVY)
        d.text((452, y + 110), "50 deg at B and E", font=F10, fill=NAVY)
        badge(d, y, "SIMILAR BY AA", GREEN)

    fix(3, [p1, p2, p3, p4, p5])


# ---- Chapter 4 ----
def ch4():
    def p1(d, y):
        congruent_pair(d, y, (5, 6, 7), 5.8)
        note(d, y, "same shape + same size", GREEN)

    def p2(d, y):
        d.text((452, y + 96), "Triangle ABC congruent to DEF", font=B11, fill=PURPLE)
        d.text((452, y + 122), "A-D   B-E   C-F", font=B13, fill=NAVY)

    def p3(d, y):
        t1, t2 = congruent_pair(d, y, (5, 6, 7), 5.5)
        for t in (t1, t2):
            ticks(d, t[0], t[1], 1)
            ticks(d, t[1], t[2], 2)
            ticks(d, t[0], t[2], 3)
            side_label(d, t[0], t[1], "5")
            side_label(d, t[1], t[2], "6")
            side_label(d, t[0], t[2], "7")

    def p4(d, y):
        t1, t2 = congruent_pair(d, y, (5, 6, 7), 5.5)
        arc(d, t1[0], t1[1], t1[2], 10, R)
        arc(d, t1[1], t1[0], t1[2], 10, B)
        arc(d, t1[2], t1[0], t1[1], 10, G)
        arc(d, t2[0], t2[1], t2[2], 10, R)
        arc(d, t2[1], t2[0], t2[2], 10, B)
        arc(d, t2[2], t2[0], t2[1], 10, G)
        note(d, y, "all corresponding angles equal", BLUE)

    def p5(d, y):
        congruent_pair(d, y, (5, 6, 7), 5.0)
        d.text((452, y + 96), "Congruent => Similar", font=B11, fill=GREEN)
        d.text((452, y + 118), "scale factor = 1", font=B11, fill=NAVY)
        d.text((452, y + 140), "Similar need not be congruent", font=F10, fill=RED)

    fix(4, [p1, p2, p3, p4, p5])


# ---- Chapter 5 ----
def ch5():
    sas = (6, math.sqrt(52), 8)

    def p1(d, y):
        t1, t2 = congruent_pair(d, y, (5, 6, 7), 5.5)
        for t in (t1, t2):
            ticks(d, t[0], t[1], 1)
            ticks(d, t[1], t[2], 2)
            ticks(d, t[0], t[2], 3)
        badge(d, y, "SSS", GREEN)

    def p2(d, y):
        t1, t2 = congruent_pair(d, y, (5, 7, 8), 4.8)
        labels = (
            ((t1[0], t1[1], "5"), (t1[0], t1[2], "7"), (t1[1], t1[2], "8")),
            ((t2[0], t2[1], "5"), (t2[0], t2[2], "7"), (t2[1], t2[2], "8")),
        )
        for group in labels:
            for p1, p2, txt in group:
                side_label(d, p1, p2, txt, 16)
        note(d, y, "5=5, 7=7, 8=8", NAVY)

    def p3(d, y):
        t1, t2 = congruent_pair(d, y, sas, 5.0)
        side_label(d, t1[0], t1[1], "6")
        side_label(d, t1[0], t1[2], "8")
        side_label(d, t2[0], t2[1], "6")
        side_label(d, t2[0], t2[2], "8")
        arc(d, t1[0], t1[1], t1[2], 13, PURPLE, 3)
        arc(d, t2[0], t2[1], t2[2], 13, PURPLE, 3)
        d.text((452, y + 90), "angle A = angle D = 60 deg", font=F10, fill=PURPLE)
        note(d, y, "two sides + INCLUDED angle", PURPLE)

    def p4(d, y):
        t1, t2 = congruent_pair(d, y, sas, 5.0)
        for t in (t1, t2):
            side_label(d, t[0], t[1], "6")
            side_label(d, t[0], t[2], "8")
            arc(d, t[0], t[1], t[2], 13, PURPLE, 3)
        d.text((452, y + 92), "6=6, 8=8, angle=60 deg", font=F10, fill=NAVY)
        badge(d, y, "SAS", GREEN)

    def p5(d, y):
        t1 = tri_coords(5, 7, 6, (470, y + 156), 5.5)
        t2 = tri_coords(5, 7, 6, (610, y + 156), 5.5)
        draw_tri(d, t1)
        draw_tri(d, t2, ("D", "E", "F"))
        side_label(d, t1[0], t1[1], "5")
        side_label(d, t1[0], t1[2], "7")
        arc(d, t1[1], t1[0], t1[2], 11, RED, 3)
        d.text((452, y + 92), "SSA is NOT a general test.", font=B11, fill=RED)
        d.text((452, y + 112), "Angle is NOT between", font=F10, fill=INK)
        d.text((452, y + 128), "the two known sides.", font=F10, fill=INK)

    fix(5, [p1, p2, p3, p4, p5])


# ---- Chapter 6 ----
def ch6():
    def p1(d, y):
        t = tri_coords(5, 6, 4.5, (650, y + 166), 7.0)
        draw_tri(d, t)
        arc(d, t[0], t[1], t[2], 10, R)
        arc(d, t[1], t[0], t[2], 10, B)
        ticks(d, t[0], t[1], 2, GREEN)
        d.text((452, y + 92), "ANGLE - SIDE - ANGLE", font=B11, fill=BLUE)
        d.text((452, y + 110), "included side AB", font=F10, fill=GREEN)
        badge(d, y, "ASA", GREEN)

    def p2(d, y):
        t = tri_coords(5, 6, 4.5, (650, y + 166), 7.0)
        draw_tri(d, t)
        arc(d, t[0], t[1], t[2], 10, R)
        arc(d, t[1], t[0], t[2], 10, B)
        ticks(d, t[1], t[2], 2, PURPLE)
        d.text((452, y + 92), "ANGLE - ANGLE - SIDE", font=B11, fill=PURPLE)
        d.text((452, y + 110), "non-included side BC", font=F10, fill=PURPLE)
        badge(d, y, "AAS", GREEN)

    def p3(d, y):
        t1 = tri_coords(3, 5, 4, (500, y + 170), 8.0)
        t2 = tri_coords(3, 5, 4, (660, y + 170), 8.0)
        draw_tri(d, t1)
        draw_tri(d, t2, ("D", "E", "F"))
        for t in (t1, t2):
            right_angle(d, t[0], t[1], t[2])
            ticks(d, t[0], t[1], 1)
            ticks(d, t[0], t[2], 1)
            ticks(d, t[1], t[2], 2)
            side_label(d, t[0], t[1], "3", 20)
            side_label(d, t[0], t[2], "4", 20)
            side_label(d, t[1], t[2], "H=5", 20)
        d.text((452, y + 88), "Right angle at A and D", font=F10, fill=BLUE)
        d.text((452, y + 102), "Matching hypotenuse + one leg", font=F10, fill=INK)
        badge(d, y, "RHS", GREEN)

    def p4(d, y):
        t1 = tri_coords(3, 4, 5, (610, y + 174), 6.0)
        t2 = tri_coords(6, 8, 10, (680, y + 174), 6.0)
        draw_tri(d, t1)
        draw_tri(d, t2, ("D", "E", "F"))
        d.text((452, y + 92), "SIMILAR: same shape", font=B11, fill=BLUE)
        d.text((452, y + 112), "CONGRUENT: same shape+size", font=F10, fill=GREEN)
        d.text((452, y + 132), "Both: equal corresponding angles", font=F10, fill=PURPLE)

    def p5(d, y):
        d.text((452, y + 96), "FINAL SEAL ACCEPTED", font=B12, fill=GOLD)
        d.text((452, y + 120), "Treasure = summary scroll", font=F10, fill=NAVY)
        badge(d, y, "MAZE CLEARED", GREEN)

    fix(6, [p1, p2, p3, p4, p5])


def treasure():
    path = OUT / "similar-congruent-quick-reference-color.png"
    im = Image.open(path).convert("RGB")
    d = ImageDraw.Draw(im)
    # Mini reference triangles in each scroll section
    sections = [(210, 5.2), (415, 4.8), (620, 4.5), (825, 4.5)]
    for y0, u in sections:
        t = tri_coords(3, 4, 5, (560, y0 + 18), u)
        draw_tri(d, t, ("A", "B", "C"), width=2)
    im.save(path)


if __name__ == "__main__":
    ch1()
    ch2()
    ch3()
    ch4()
    ch5()
    ch6()
    print("Rebuilt all figures for clarity and correctness.")
