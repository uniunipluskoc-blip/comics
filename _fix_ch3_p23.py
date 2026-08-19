from PIL import Image, ImageDraw, ImageFont
import math
import numpy as np

src = r"C:\Users\UniplusUser02\Desktop\comics\Special lines and centres in triangles\similar-congruent-chapter-3-layout-fixed.png"
im = Image.open(src).convert("RGB")
a = np.array(im)

# Tile real parchment over the messy cream patches
def fill_parchment(arr, x0, y0, x1, y1, sample_y0, sample_y1):
    strip = arr[sample_y0:sample_y1, x0:x1].copy()
    h = sample_y1 - sample_y0
    y = y0
    while y < y1:
        take = min(h, y1 - y)
        arr[y : y + take, x0:x1] = strip[:take]
        y += take

# Use the still-clean strip under the SSS header (no vertex labels there)
fill_parchment(a, 441, 244, 753, 412, 448, 468)
fill_parchment(a, 441, 448, 753, 616, 448, 468)

im = Image.fromarray(a)
draw = ImageDraw.Draw(im)
font = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 12)
lab = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 12)
num = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 13)

INK = (24, 40, 58)
RED = (221, 63, 69)
BLUE = (38, 112, 197)
GREEN = (40, 161, 95)
PURPLE = (129, 64, 180)


def text_size(t, f):
    b = draw.textbbox((0, 0), t, font=f)
    return b[2] - b[0], b[3] - b[1]


def draw_dot(pt, col, r=3):
    x, y = pt
    draw.ellipse((x - r, y - r, x + r, y + r), fill=col)


def label_vertex(pt, letter, col, place):
    x, y = pt
    tw, th = text_size(letter, lab)
    if place == "L":
        draw.text((x - tw - 4, y - th // 2 - 1), letter, font=lab, fill=col)
    elif place == "R":
        draw.text((x + 8, y - th // 2 + 1), letter, font=lab, fill=col)
    elif place == "T":
        draw.text((x - tw // 2, y - th - 5), letter, font=lab, fill=col)
    elif place == "BR":
        draw.text((x + 7, y + 3), letter, font=lab, fill=col)


def draw_triangle(pts, width=2):
    closed = pts + [pts[0]]
    draw.line(closed, fill=INK, width=width)


def angle_arc(vertex, p1, p2, radius, col):
    vx, vy = vertex
    a1 = math.atan2(p1[1] - vy, p1[0] - vx)
    a2 = math.atan2(p2[1] - vy, p2[0] - vx)
    # sweep the smaller interior angle
    d = (a2 - a1) % (2 * math.pi)
    if d > math.pi:
        a1, a2 = a2, a1
        d = (a2 - a1) % (2 * math.pi)
    steps = 10
    pts = []
    for i in range(steps + 1):
        t = a1 + d * i / steps
        pts.append((vx + radius * math.cos(t), vy + radius * math.sin(t)))
    draw.line(pts, fill=col, width=2)


def side_number(p, q, text, col, outward):
    mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
    dx, dy = q[0] - p[0], q[1] - p[1]
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L, dx / L
    # pick the outward side
    ox, oy = mx + nx * outward[0], my + ny * outward[1]
    # simpler: caller passes pixel offset
    tw, th = text_size(text, num)
    draw.text((ox - tw / 2, oy - th / 2), text, font=num, fill=col)


# ----- Panel 2: SAS, included 60 deg at B and E -----
# unit = 11 px; AB=4, BC=6 / DE=6, EF=9
u = 11
# B bottom-right of left triangle
B = (528, 364)
A = (B[0] - 4 * u, B[1])
ang = math.radians(120)  # 60 deg from BA (left)
C = (B[0] + 6 * u * math.cos(ang), B[1] - 6 * u * math.sin(math.radians(60)))
# E of larger triangle
E = (708, 368)
D = (E[0] - 6 * u, E[1])
F = (E[0] + 9 * u * math.cos(ang), E[1] - 9 * u * math.sin(math.radians(60)))

A = (int(A[0]), int(A[1]))
B = (int(B[0]), int(B[1]))
C = (int(C[0]), int(C[1]))
D = (int(D[0]), int(D[1]))
E = (int(E[0]), int(E[1]))
F = (int(F[0]), int(F[1]))

draw_triangle([A, B, C])
draw_triangle([D, E, F])
angle_arc(B, A, C, 14, PURPLE)
angle_arc(E, D, F, 16, PURPLE)
for pt, letter, col, place in [
    (A, "A", RED, "L"),
    (B, "B", BLUE, "BR"),
    (C, "C", GREEN, "T"),
    (D, "D", RED, "L"),
    (E, "E", BLUE, "BR"),
    (F, "F", GREEN, "T"),
]:
    draw_dot(pt, col)
    label_vertex(pt, letter, col, place)

# numbers: 4 on AB, 6 on BC; 6 on DE, 9 on EF
tw, th = text_size("4", num)
draw.text(((A[0] + B[0]) // 2 - tw // 2, A[1] + 6), "4", font=num, fill=INK)
tw, th = text_size("6", num)
draw.text((B[0] + 10, (B[1] + C[1]) // 2 - th // 2 - 4), "6", font=num, fill=INK)
tw, th = text_size("6", num)
draw.text(((D[0] + E[0]) // 2 - tw // 2, D[1] + 6), "6", font=num, fill=INK)
tw, th = text_size("9", num)
draw.text((E[0] + 10, (E[1] + F[1]) // 2 - th // 2 - 4), "9", font=num, fill=INK)

cap = "4/6 = 6/9;  angle B = angle E = 60 deg"
tw, th = text_size(cap, font)
draw.text((441 + (753 - 441 - tw) // 2, 394), cap, font=font, fill=PURPLE)

# ----- Panel 3: SSS 3-4-5 and 6-8-10, right angle at B/E -----
u3 = 10
B3 = (530, 568)
A3 = (B3[0] - 3 * u3, B3[1])
C3 = (B3[0], B3[1] - 4 * u3)
E3 = (700, 572)
D3 = (E3[0] - 6 * u3, E3[1])
F3 = (E3[0], E3[1] - 8 * u3)

draw_triangle([A3, B3, C3])
draw_triangle([D3, E3, F3])
# right-angle marks
def right_mark(v, p_h, p_v, s=7):
    hx, hy = p_h[0] - v[0], p_h[1] - v[1]
    vx, vy = p_v[0] - v[0], p_v[1] - v[1]
    hl = math.hypot(hx, hy) or 1
    vl = math.hypot(vx, vy) or 1
    hx, hy = hx / hl * s, hy / hl * s
    vx, vy = vx / vl * s, vy / vl * s
    p1 = (v[0] + hx, v[1] + hy)
    p2 = (v[0] + hx + vx, v[1] + hy + vy)
    p3 = (v[0] + vx, v[1] + vy)
    draw.line([p1, p2, p3], fill=INK, width=1)

right_mark(B3, A3, C3)
right_mark(E3, D3, F3)

for pt, letter, col, place in [
    (A3, "A", RED, "L"),
    (B3, "B", BLUE, "BR"),
    (C3, "C", GREEN, "T"),
    (D3, "D", RED, "L"),
    (E3, "E", BLUE, "BR"),
    (F3, "F", GREEN, "T"),
]:
    draw_dot(pt, col)
    label_vertex(pt, letter, col, place)

# 3 on AB, 4 on BC, 5 on AC; 6 on DE, 8 on EF, 10 on DF
tw, th = text_size("3", num)
draw.text(((A3[0] + B3[0]) // 2 - tw // 2, A3[1] + 6), "3", font=num, fill=INK)
tw, th = text_size("4", num)
draw.text((B3[0] + 7, (B3[1] + C3[1]) // 2 - th // 2), "4", font=num, fill=INK)
# 5 on hypotenuse, offset left/up
mx, my = (A3[0] + C3[0]) / 2, (A3[1] + C3[1]) / 2
tw, th = text_size("5", num)
draw.text((mx - tw - 6, my - th - 2), "5", font=num, fill=INK)

tw, th = text_size("6", num)
draw.text(((D3[0] + E3[0]) // 2 - tw // 2, D3[1] + 6), "6", font=num, fill=INK)
tw, th = text_size("8", num)
draw.text((E3[0] + 7, (E3[1] + F3[1]) // 2 - th // 2), "8", font=num, fill=INK)
mx, my = (D3[0] + F3[0]) / 2, (D3[1] + F3[1]) / 2
tw, th = text_size("10", num)
draw.text((mx - tw - 8, my - th - 2), "10", font=num, fill=INK)

cap3 = "3/6 = 4/8 = 5/10"
tw, th = text_size(cap3, font)
draw.text((441 + (753 - 441 - tw) // 2, 598), cap3, font=font, fill=GREEN)

im.save(src)
im.crop((380, 200, 768, 620)).save(r"C:\Users\UniplusUser02\Desktop\comics\ch3-p23-after.png")
print("ABC", A, B, C)
print("DEF", D, E, F)
print("SSS", A3, B3, C3, D3, E3, F3)
print("saved")
