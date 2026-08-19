"""Compose Indices Club chapters 1–3 and the law card with a locked cast."""
from __future__ import annotations

import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ASSETS = Path(
    r"C:\Users\User\.cursor\projects"
    r"\c-Users-User-OneDrive-The-Education-University-of-Hong-Kong-comics\assets"
)
OUT = Path(
    r"c:\Users\User\OneDrive - The Education University of Hong Kong\桌面\comics"
    r"\Law of index\rule of Law of index"
)
DESKTOP = Path(r"C:\Users\User\OneDrive - The Education University of Hong Kong\桌面")
FONTS = Path(r"C:\Windows\Fonts")

W, H = 1024, 1536
TITLE_H = 40
FOOTER_H = 44
ROW = (H - TITLE_H - FOOTER_H) // 5  # 290
NAVY = (16, 36, 78)
INK = (22, 28, 40)
RED = (196, 42, 48)
BLUE = (28, 92, 188)
GREEN = (20, 132, 72)
GOLD = (196, 148, 48)
PURPLE = (112, 52, 168)
ZERO_C = (168, 120, 20)
WHITE = (255, 255, 255)

NAME = {
    "Member": GREEN,
    "Mentor": BLUE,
    "Rena": RED,
    "Zero": ZERO_C,
    "Referee": (70, 70, 86),
}


def font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    name = "timesbd.ttf" if bold else "times.ttf"
    return ImageFont.truetype(str(FONTS / name), size)


def fit_cover(src: Path, size: tuple[int, int]) -> Image.Image:
    im = Image.open(src).convert("RGB")
    tw, th = size
    scale = max(tw / im.width, th / im.height)
    nw, nh = max(1, int(im.width * scale)), max(1, int(im.height * scale))
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    x, y = (nw - tw) // 2, (nh - th) // 2
    return im.crop((x, y, x + tw, y + th))


def wrap(draw: ImageDraw.ImageDraw, text: str, f, max_w: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    cur = ""
    for w in words:
        trial = w if not cur else cur + " " + w
        if draw.textlength(trial, font=f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines or [text]


def parse_sup(text: str) -> list[tuple[str, bool]]:
    """Split 'x^{2n+3}' style text into (chunk, is_superscript) parts."""
    parts: list[tuple[str, bool]] = []
    i = 0
    buf = ""
    while i < len(text):
        if text[i] == "^":
            if buf:
                parts.append((buf, False))
                buf = ""
            i += 1
            if i < len(text) and text[i] == "{":
                end = text.index("}", i)
                parts.append((text[i + 1 : end], True))
                i = end + 1
            else:
                chunk = ""
                if i < len(text) and text[i] == "-":
                    chunk = "-"
                    i += 1
                while i < len(text) and (text[i].isalnum()):
                    chunk += text[i]
                    i += 1
                parts.append((chunk or "", True))
        else:
            buf += text[i]
            i += 1
    if buf:
        parts.append((buf, False))
    return parts


def text_width(draw: ImageDraw.ImageDraw, text: str, size: int, bold: bool = True) -> float:
    base = font(size, bold)
    sup = font(max(9, int(size * 0.62)), bold)
    w = 0.0
    for chunk, is_sup in parse_sup(text):
        w += draw.textlength(chunk, font=sup if is_sup else base)
    return w


def draw_eq(
    draw: ImageDraw.ImageDraw,
    xy: tuple[float, float],
    text: str,
    size: int,
    fill,
    bold: bool = True,
) -> None:
    x, y = xy
    base = font(size, bold)
    sup = font(max(9, int(size * 0.62)), bold)
    for chunk, is_sup in parse_sup(text):
        f = sup if is_sup else base
        yy = y - int(size * 0.32) if is_sup else y
        draw.text((x, yy), chunk, font=f, fill=fill)
        x += draw.textlength(chunk, font=f)


def bubble(draw: ImageDraw.ImageDraw, box, speaker: str, text: str) -> None:
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=10, fill=WHITE, outline="#d4c4a0", width=2)
    nf, tf = font(14), font(14, False)
    draw.text((x1 + 10, y1 + 6), f"{speaker}:", font=nf, fill=NAME[speaker])
    name_w = draw.textlength(f"{speaker}: ", font=nf)
    # keep spoken math readable with real superscripts on one or two lines
    lines = wrap(draw, text.replace("^", ""), tf, int(x2 - x1 - 20))
    # if the original used ^, draw the whole text as an equation line when it fits
    if "^" in text:
        draw_eq(draw, (x1 + 10 + name_w, y1 + 8), text, 14, INK, bold=False)
        return
    first = lines[0]
    if draw.textlength(first, font=tf) <= (x2 - x1 - name_w - 16):
        draw.text((x1 + 10 + name_w, y1 + 6), first, font=tf, fill=INK)
        rest = lines[1:]
        yy = y1 + 24
    else:
        rest = lines
        yy = y1 + 24
    for line in rest:
        draw.text((x1 + 10, yy), line, font=tf, fill=INK)
        yy += 18


def math_box(draw: ImageDraw.ImageDraw, box, text: str, color=NAVY) -> None:
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=8, fill=(240, 246, 255), outline=color, width=2)
    tw = text_width(draw, text, 17)
    draw_eq(draw, ((x1 + x2 - tw) / 2, y1 + 8), text, 17, color)


def compose_chapter(title: str, panels: list[Path], lines: list, footer: str, dest: Path) -> None:
    page = Image.new("RGB", (W, H), (10, 14, 24))
    for i, src in enumerate(panels):
        y = TITLE_H + i * ROW
        page.paste(fit_cover(src, (W, ROW)), (0, y))

    d = ImageDraw.Draw(page)
    d.rectangle((0, 0, W, TITLE_H), fill=NAVY)
    d.text((18, 11), title, font=font(18), fill=WHITE)

    for i, items in enumerate(lines):
        y = TITLE_H + i * ROW
        for kind, *rest in items:
            if kind == "b":
                speaker, text, box = rest
                x1, y1, x2, y2 = box
                bubble(d, (x1, y + y1, x2, y + y2), speaker, text)
            elif kind == "m":
                text, box, col = rest
                x1, y1, x2, y2 = box
                math_box(d, (x1, y + y1, x2, y + y2), text, col)

    d.rectangle((0, H - FOOTER_H, W, H), fill=(8, 10, 16))
    fw = font(14)
    tw = d.textlength(footer, font=fw)
    d.text(((W - tw) / 2, H - 32), footer, font=fw, fill=GOLD)

    dest.parent.mkdir(parents=True, exist_ok=True)
    page.save(dest, quality=95)
    shutil.copy2(dest, DESKTOP / dest.name)
    print("saved", dest.name)


def chapter1() -> None:
    panels = [
        ASSETS / "ic-ch1-p1-door.png",
        ASSETS / "ic-ch1-p2-multiply.png",
        ASSETS / "ic-ch1-p3-divide.png",
        ASSETS / "ic-ch1-p4-power.png",
        ASSETS / "ic-ch1-p5-pass.png",
    ]
    lines = [
        [
            ("b", "Rena", "Entry trial. Show you know the laws — or the door stays shut.", (18, 8, 640, 52)),
            ("b", "Member", "I'm ready.", (18, 58, 220, 96)),
            ("b", "Mentor", "Same base first. Always.", (640, 230, 1004, 278)),
        ],
        [
            ("b", "Mentor", "Same base — multiply means add the indices.", (18, 8, 560, 52)),
            ("b", "Member", "So x^3 × x^4 = x^7.", (18, 230, 360, 278)),
            ("m", "x^3 × x^4 = x^7", (680, 12, 1004, 50), BLUE),
        ],
        [
            ("b", "Mentor", "Division? Subtract the indices.", (18, 8, 430, 52)),
            ("b", "Member", "p^7 ÷ p^2 = p^5.", (18, 230, 320, 278)),
            ("m", "p^7 ÷ p^2 = p^5", (680, 12, 1004, 50), BLUE),
        ],
        [
            ("b", "Mentor", "Power of a power — multiply the indices.", (18, 8, 560, 52)),
            ("b", "Member", "(m^6)^2 = m^{12}.", (18, 230, 320, 278)),
            ("m", "(m^6)^2 = m^{12}", (700, 12, 1004, 50), BLUE),
            ("b", "Mentor", "Stay sharp. Someone is watching.", (640, 230, 1004, 278)),
        ],
        [
            ("b", "Member", "(-3t^2)^3 = -27t^6.", (18, 8, 380, 52)),
            ("m", "(-3t^2)^3 = -27t^6", (400, 8, 760, 50), GREEN),
            ("b", "Rena", "You passed.", (780, 8, 1004, 52)),
        ],
    ]
    compose_chapter(
        "INDICES CLUB  —  1: ENTRY TRIAL",
        panels,
        lines,
        "SAME BASE → ADD.    DIVIDE → SUBTRACT.    POWER → MULTIPLY.",
        OUT / "indices-club-chapter-1-color.png",
    )


def chapter2() -> None:
    panels = [
        ASSETS / "ic-ch2-p1-ambush.png",
        ASSETS / "ic-ch2-p2-negative.png",
        ASSETS / "ic-ch2-p3-shield.png",
        ASSETS / "ic-ch2-p4-compare.png",
        ASSETS / "ic-ch2-p5-hold.png",
    ]
    lines = [
        [
            ("b", "Zero", "Try surviving this — all to the zero!", (18, 8, 500, 52)),
            ("b", "Member", "Does everything disappear? Even (-2)^0?", (520, 8, 1004, 52)),
            ("b", "Mentor", "Anything non-zero to the power zero is 1. Even that.", (520, 228, 1004, 280)),
        ],
        [
            ("b", "Zero", "Negative index — become negative!", (18, 8, 460, 52)),
            ("b", "Member", "-25...?", (18, 58, 200, 96)),
            ("b", "Mentor", "Wrong. A negative index means reciprocal.", (500, 8, 1004, 52)),
            ("m", "5^{-2} = 1/5^2 = 1/25", (600, 228, 1004, 276), BLUE),
        ],
        [
            ("b", "Zero", "y^{-9} ÷ y^{-5}", (18, 8, 280, 52)),
            ("b", "Member", "(-9) − (-5) = -4. So y^{-4} = 1/y^4.", (300, 8, 860, 52)),
            ("b", "Mentor", "You saw through it.", (700, 230, 1004, 278)),
        ],
        [
            ("b", "Mentor", "Compare (2a^2)^{-3} and (-2a^2)^{-3}.", (18, 8, 560, 52)),
            ("m", "(2a^2)^{-3} = 1/(8a^6)", (18, 230, 400, 276), BLUE),
            ("m", "(-2a^2)^{-3} = −1/(8a^6)", (420, 230, 840, 276), PURPLE),
            ("b", "Member", "Both become reciprocals — but an odd power keeps the minus sign.", (18, 58, 820, 108)),
        ],
        [
            ("b", "Member", "Negative index — flip. Zero index — one.", (18, 8, 560, 52)),
            ("b", "Mentor", "Hold those two lines.", (580, 8, 900, 52)),
        ],
    ]
    compose_chapter(
        "INDICES CLUB  —  2: ZERO'S AMBUSH",
        panels,
        lines,
        "ZERO → ONE.    NEGATIVE → RECIPROCAL.",
        OUT / "indices-club-chapter-2-color.png",
    )


def chapter3() -> None:
    panels = [
        ASSETS / "ic-ch3-p1-arena.png",
        ASSETS / "ic-ch3-p2-round1.png",
        ASSETS / "ic-ch3-p3-round2.png",
        ASSETS / "ic-ch3-p4-final.png",
        ASSETS / "ic-ch3-p5-winner.png",
    ]
    lines = [
        [
            ("b", "Referee", "Final match — Rena versus Zero. Different bases. Different chaos.", (18, 8, 720, 52)),
            ("b", "Rena", "I'll translate them into one language.", (18, 230, 480, 278)),
        ],
        [
            ("m", "3^{2n} × 27", (18, 8, 250, 50), RED),
            ("b", "Rena", "Rewrite. 27 = 3^3. Then 3^{2n} × 3^3 = 3^{2n+3}.", (270, 8, 920, 56)),
            ("m", "3^{2n+3}", (800, 230, 1004, 276), BLUE),
        ],
        [
            ("m", "4^{3n} × 16^n", (18, 8, 300, 50), RED),
            ("b", "Rena", "16^n = 4^{2n}. Same base first. Always. 4^{3n} × 4^{2n} = 4^{5n}.", (320, 8, 1004, 56)),
            ("m", "4^{5n}", (800, 230, 1004, 276), BLUE),
        ],
        [
            ("m", "81^{n-1} × 3^{n-1} ÷ 9^{n-2}", (18, 8, 460, 50), RED),
            ("b", "Rena", "81 = 3^4 and 9 = 3^2. So 3^{4(n-1)} × 3^{n-1} ÷ 3^{2(n-2)} = 3^{3n-1}.", (18, 56, 780, 114)),
            ("m", "3^{3n-1}", (800, 56, 1004, 102), BLUE),
            ("b", "Member", "That's the Indices Club way!", (18, 230, 420, 278)),
        ],
        [
            ("b", "Zero", "I treated zero like emptiness... and negatives like mere minus signs.", (18, 8, 720, 56)),
            ("b", "Rena", "Laws aren't tricks. They're honesty with the base.", (18, 230, 560, 278)),
            ("b", "Referee", "Winner — Rena!", (720, 230, 1004, 278)),
        ],
    ]
    compose_chapter(
        "INDICES CLUB  —  3: FINAL MATCH  ·  SAME ROOT",
        panels,
        lines,
        "DIFFERENT BASES → REWRITE, THEN COMBINE.",
        OUT / "indices-club-chapter-3-color.png",
    )


def pill(draw: ImageDraw.ImageDraw, box, label: str, color) -> None:
    draw.rounded_rectangle(box, radius=7, fill=WHITE, outline=color, width=2)
    x1, y1, x2, y2 = box
    f = font(14)
    tw = draw.textlength(label, font=f)
    draw.text(((x1 + x2 - tw) / 2, y1 + 6), label, font=f, fill=color)


def law_card() -> None:
    dest = OUT / "indices-club-laws-card-color.png"
    page = fit_cover(ASSETS / "ic-law-card-scene.png", (W, H))
    d = ImageDraw.Draw(page)
    d.rectangle((0, 0, W, 56), fill=NAVY)
    d.text((24, 8), "INDICES CLUB  —  LAW CARD", font=font(22), fill=WHITE)
    d.text(
        (24, 34),
        "Member  ·  Mentor  ·  Rena (Captain)  ·  Zero (Aoi)",
        font=font(13, False),
        fill=(210, 220, 240),
    )

    scrolls = [
        (
            28,
            "1. PRODUCT & QUOTIENT",
            ["a^m × a^n = a^{m+n}", "a^m ÷ a^n = a^{m-n}"],
            "Same base: multiply → add; divide → subtract.",
        ),
        (
            268,
            "2. POWER OF A POWER",
            ["(a^m)^n = a^{mn}"],
            "Power of a power → multiply the indices.",
        ),
        (
            508,
            "3. ZERO & NEGATIVE",
            ["a^0 = 1   (a ≠ 0)", "a^{-n} = 1/a^n"],
            "Zero → one. Negative → reciprocal.",
        ),
        (
            748,
            "4. CHANGE OF BASE",
            ["3^{2n} × 27 = 3^{2n+3}", "4^{3n} × 16^n = 4^{5n}"],
            "Rewrite to the same base, then combine.",
        ),
    ]
    small = font(12, False)
    for x0, title, eqs, rule in scrolls:
        box = (x0, 430, x0 + 228, 690)
        d.rounded_rectangle(box, radius=10, fill=(255, 244, 214), outline=(160, 120, 64), width=2)
        d.rectangle((x0, 430, x0 + 228, 466), fill=NAVY)
        d.text((x0 + 8, 438), title, font=font(12), fill=WHITE)
        yy = 482
        for eq in eqs:
            draw_eq(d, (x0 + 12, yy), eq, 16, NAVY)
            yy += 34
        for i, line in enumerate(wrap(d, rule, small, 204)):
            d.text((x0 + 12, 610 + i * 16), line, font=small, fill=INK)

    # Labels sit on empty floor, not on faces. Match locked cast only.
    pill(d, (36, 118, 210, 150), "Member", GREEN)
    pill(d, (780, 118, 1000, 150), "Rena  ·  Captain", RED)
    pill(d, (36, 1468, 210, 1504), "Mentor", BLUE)
    pill(d, (780, 1468, 1000, 1504), "Zero  ·  Aoi", ZERO_C)

    d.rounded_rectangle((80, 1410, 500, 1454), radius=8, fill=WHITE, outline=NAVY, width=2)
    d.text((96, 1422), "Laws aren't tricks. Read the base, then the index.", font=font(13, False), fill=INK)
    d.rounded_rectangle((520, 1410, 940, 1454), radius=8, fill=WHITE, outline=GOLD, width=2)
    d.text((560, 1422), "Cast with clarity.", font=font(14, False), fill=NAVY)

    page.save(dest, quality=95)
    shutil.copy2(dest, DESKTOP / dest.name)
    print("saved", dest.name)


if __name__ == "__main__":
    chapter1()
    chapter2()
    chapter3()
    law_card()
    print("all Indices Club pages composed")
