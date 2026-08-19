"""Build the recreated maze manga from clean generated artwork."""
from __future__ import annotations

import shutil
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(r"c:\Users\UniplusUser02\Desktop\comics")
ASSETS = Path(
    r"C:\Users\UniplusUser02\.cursor\projects"
    r"\c-Users-UniplusUser02-Desktop-comics\assets"
)
OUT = ROOT / "Special lines and centres in triangles"

NAVY = "#102c61"
BLUE = "#1769d2"
GREEN = "#159447"
RED = "#d93434"
GOLD = "#b8790b"
PURPLE = "#7540aa"
INK = "#172030"
CREAM = "#fffaf0"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    filename = "arialbd.ttf" if bold else "arial.ttf"
    return ImageFont.truetype(str(Path(r"C:\Windows\Fonts") / filename), size)


F10 = font(10)
F11 = font(11)
B10 = font(10, True)
B11 = font(11, True)
B12 = font(12, True)
B13 = font(13, True)
B15 = font(15, True)

CHAPTERS = {
    1: {
        "title": "MAZE OF TRIANGLES — 1: THE ENTRANCE GATE",
        "panels": [
            ("THE RUNE GATE", ("Kai", "A triangle gate?"), ("Emi", "It wants matching vertices.")),
            ("READ THE ORDER", ("Emi", "A matches D."), ("Ren", "Then B-E and C-F.")),
            ("MATCH THE SIDES", ("Ren", "So AB matches DE."), ("Kai", "And BC matches EF!")),
            ("TRAP ANSWER", ("Kai", "ABC matches DFE?"), ("Emi", "No! B would match F.")),
            ("GATE UNLOCKED", ("Emi", "Write ABC ~ DEF."), ("Kai", "Look—the gate is opening!")),
        ],
    },
    2: {
        "title": "MAZE OF TRIANGLES — 2: THE MIRROR CORRIDOR",
        "panels": [
            ("MIRROR SHAPES", ("Kai", "Why is my reflection larger?"), ("Emi", "Same shape, different size.")),
            ("ONE RATIO", ("Emi", "Each matching side is doubled."), ("Ren", "One ratio links them all.")),
            ("SCALE FACTOR", ("Ren", "The scale factor is 2."), ("Kai", "So every side doubles.")),
            ("MISSING LENGTH", ("Kai", "The unknown side is x."), ("Emi", "Scale 6 by 1.5: x = 9.")),
            ("MIRRORS ALIGNED", ("Ren", "The mirrors agree!"), ("Kai", "A hidden passage!")),
        ],
    },
    3: {
        "title": "MAZE OF TRIANGLES — 3: THE CRYSTAL BRIDGE",
        "panels": [
            ("ANGLE CRYSTAL", ("Kai", "Two angle marks glow."), ("Ren", "That proves AA similarity.")),
            ("PRISM OF SAS", ("Emi", "These side ratios match."), ("Ren", "The angle is included: SAS.")),
            ("THREE-SIDE RUNE", ("Ren", "All three ratios match."), ("Kai", "Then it is SSS.")),
            ("FALSE CLUE", ("Kai", "Equal angles mean congruent?"), ("Ren", "No—only shape is fixed.")),
            ("BRIDGE RESTORED", ("Emi", "The checkpoint is AA."), ("Kai", "The bridge is back—run!")),
        ],
    },
    4: {
        "title": "MAZE OF TRIANGLES — 4: THE TWIN STATUES",
        "panels": [
            ("IDENTICAL GUARDS", ("Kai", "The seals fit exactly."), ("Emi", "Same shape and same size.")),
            ("ORDER STILL MATTERS", ("Emi", "Keep the vertex order."), ("Ren", "A-D, B-E, C-F.")),
            ("EQUAL SIDES", ("Ren", "Three side pairs are equal."), ("Kai", "The tick marks confirm it.")),
            ("EQUAL ANGLES", ("Kai", "What about the angles?"), ("Emi", "Every matching angle is equal.")),
            ("STAIRS REVEALED", ("Ren", "Scale factor one."), ("Kai", "The statues are moving!")),
        ],
    },
    5: {
        "title": "MAZE OF TRIANGLES — 5: THE GEAR GATE",
        "panels": [
            ("THREE SIDE GEARS", ("Kai", "Three pairs of side gears!"), ("Ren", "That checkpoint is SSS.")),
            ("SSS CHECK", ("Emi", "Lengths 5, 7 and 8 match."), ("Kai", "Both shields are congruent.")),
            ("INCLUDED DIAL", ("Ren", "Two sides and one angle."), ("Emi", "Only if the angle is included.")),
            ("SAS CHECK", ("Emi", "Six, eight, and 60 degrees."), ("Ren", "Yes—SAS unlocks it.")),
            ("SSA TRAP", ("Kai", "Should I pull the SSA lever?"), ("Emi", "Stop! SSA is a trap.")),
        ],
    },
    6: {
        "title": "MAZE OF TRIANGLES — 6: THE FINAL SEAL",
        "panels": [
            ("ASA SEAL", ("Emi", "Two angles surround this side."), ("Ren", "That makes ASA.")),
            ("AAS SEAL", ("Kai", "Here the side is outside."), ("Ren", "Then the test is AAS.")),
            ("RIGHT-TRIANGLE DOOR", ("Kai", "A right-triangle door!"), ("Emi", "Use right angle, hypotenuse, side.")),
            ("FINAL COMPARISON", ("Emi", "Similar means same shape."), ("Ren", "Congruent also means same size.")),
            ("TREASURE VAULT", ("Kai", "We solved the final seal!"), ("Emi", "The treasure is our summary!")),
        ],
    },
}

NAME_COLORS = {"Kai": RED, "Emi": GREEN, "Ren": BLUE}


def fit_source(src: Path) -> Image.Image:
    image = Image.open(src).convert("RGB")
    return image.resize((768, 1024), Image.Resampling.LANCZOS)


def rounded_text_box(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    speaker: str,
    text: str,
) -> None:
    draw.rounded_rectangle(box, radius=8, fill=(255, 255, 255, 238), outline="#d6c8aa", width=2)
    x1, y1, x2, _ = box
    draw.text((x1 + 8, y1 + 5), f"{speaker}:", font=B10, fill=NAME_COLORS[speaker])
    available = x2 - x1 - 62
    words = text.split()
    line = ""
    lines: list[str] = []
    for word in words:
        candidate = f"{line} {word}".strip()
        if draw.textlength(candidate, font=F10) <= available:
            line = candidate
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    draw.multiline_text((x1 + 55, y1 + 5), "\n".join(lines[:2]), font=F10, fill=INK, spacing=1)


def build_chapter(chapter: int) -> None:
    spec = CHAPTERS[chapter]
    source = ASSETS / f"maze-triangles-recreated-chapter-{chapter}.png"
    image = fit_source(source)
    draw = ImageDraw.Draw(image, "RGBA")

    draw.rounded_rectangle((8, 6, 430, 30), radius=6, fill=(11, 35, 70, 230), outline=(255, 255, 255, 150))
    draw.text((18, 11), spec["title"], font=B12, fill="white")

    for index, (heading, first, second) in enumerate(spec["panels"]):
        y = index * 204
        draw.rounded_rectangle((444, y + 8, 752, y + 38), radius=6, fill=(16, 44, 97, 245))
        draw.text((454, y + 16), f"{index + 1}. {heading}", font=B12, fill="white")
        rounded_text_box(draw, (10, y + 137, 216, y + 166), first[0], first[1])
        rounded_text_box(draw, (220, y + 168, 434, y + 198), second[0], second[1])

    output = OUT / f"similar-congruent-chapter-{chapter}-color.png"
    image.save(output, quality=95)


SUMMARY_SECTIONS = [
    (
        "SIMILAR — PROPERTIES",
        BLUE,
        [
            "Same shape; size may differ.",
            "Corresponding angles are equal.",
            "Corresponding sides are proportional.",
            "One scale factor links every side.",
        ],
    ),
    (
        "SIMILARITY TESTS",
        PURPLE,
        [
            "AA: two equal angle pairs",
            "SAS: proportional sides + included angle",
            "SSS: all three side pairs proportional",
        ],
    ),
    (
        "CONGRUENT — PROPERTIES",
        GREEN,
        [
            "Same shape and same size.",
            "All corresponding sides are equal.",
            "All corresponding angles are equal.",
            "Scale factor = 1.",
        ],
    ),
    (
        "CONGRUENCE TESTS",
        GOLD,
        [
            "SSS, SAS, ASA, AAS, RHS",
            "RHS: right angle, hypotenuse, one side",
            "Do not use SSA as a general test.",
        ],
    ),
]


def build_summary() -> None:
    source = ASSETS / "maze-triangles-recreated-quick-reference.png"
    image = fit_source(source)
    draw = ImageDraw.Draw(image, "RGBA")
    draw.rounded_rectangle((178, 66, 590, 110), radius=10, fill=(16, 44, 97, 235), outline=(255, 229, 164, 220), width=2)
    draw.text((384, 82), "THE TREASURE OF TRIANGLES", font=B15, fill="white", anchor="mm")
    draw.text((384, 101), "SIMILAR & CONGRUENT — QUICK REFERENCE", font=B10, fill="#ffe4a3", anchor="mm")

    starts = [178, 338, 498, 658]
    for y, (heading, color, bullets) in zip(starts, SUMMARY_SECTIONS):
        draw.rounded_rectangle((184, y, 584, y + 28), radius=6, fill=color)
        draw.text((196, y + 7), heading, font=B12, fill="white")
        for row, bullet in enumerate(bullets):
            draw.ellipse((196, y + 42 + row * 21, 201, y + 47 + row * 21), fill=color)
            draw.text((208, y + 36 + row * 21), bullet, font=F11, fill=INK)

    output = OUT / "similar-congruent-quick-reference-color.png"
    image.save(output, quality=95)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for number in range(1, 7):
        build_chapter(number)
    build_summary()
    print("Recreated maze manga artwork and text layout.")
