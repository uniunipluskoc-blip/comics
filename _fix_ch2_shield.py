"""Restore original Ch2 shield crop, then paint a clean geometric center (no hand)."""
from __future__ import annotations

import shutil
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(
    r"c:\Users\User\OneDrive - The Education University of Hong Kong\桌面\comics"
    r"\Law of index\rule of Law of index"
)
DESK = Path(r"C:\Users\User\OneDrive - The Education University of Hong Kong\桌面")
INSPECT = Path(r"c:\Users\User\OneDrive - The Education University of Hong Kong\桌面\comics\_inspect")
PAGE = ROOT / "indices-club-chapter-2-color.png"
BEFORE = INSPECT / "shield_before.png"

# original crop window
Y1, Y2, X1, X2 = 700, 850, 650, 850
# shield center in page coords
CX, CY = 752.0, 773.0


def restore_original_crop(page: np.ndarray) -> np.ndarray:
    crop = np.array(Image.open(BEFORE).convert("RGB"))
    page[Y1:Y2, X1:X2] = crop
    return page


def clean_center(page: np.ndarray) -> np.ndarray:
    """Paint a small clean magic-circle core over the blob only."""
    # local canvas around the blob
    y0, y1 = 735, 825
    x0, x1 = 705, 795
    h, w = y1 - y0, x1 - x0
    lcx, lcy = CX - x0, CY - y0

    base = page[y0:y1, x0:x1].copy()
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)

    # soft cyan glow disc
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for rad, col, a in (
        (38, (40, 140, 200), 90),
        (30, (70, 185, 230), 110),
        (22, (120, 220, 250), 130),
        (14, (180, 240, 255), 150),
        (7, (230, 250, 255), 170),
    ):
        gd.ellipse((lcx - rad, lcy - rad, lcx + rad, lcy + rad), fill=(*col, a))
    glow = glow.filter(ImageFilter.GaussianBlur(1.4))

    # concentric rings
    rings = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rings)
    for rad, width, col, a in (
        (34, 2, (90, 200, 240), 200),
        (26, 2, (170, 235, 255), 220),
        (18, 2, (100, 210, 245), 210),
        (11, 2, (210, 245, 255), 230),
        (5, 1, (240, 252, 255), 240),
    ):
        rd.ellipse(
            (lcx - rad, lcy - rad, lcx + rad, lcy + rad),
            outline=(*col, a),
            width=width,
        )

    # pentagram
    star = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(star)
    pts = []
    for k in range(5):
        ang = -np.pi / 2 + k * 2 * np.pi / 5
        pts.append((lcx + 24 * np.cos(ang), lcy + 24 * np.sin(ang)))
    # star by connecting every second vertex
    order = [0, 2, 4, 1, 3, 0]
    poly = [pts[i] for i in order]
    sd.line(poly, fill=(190, 240, 255, 230), width=2)

    # inner triangle
    tri = []
    for k in range(3):
        ang = -np.pi / 2 + k * 2 * np.pi / 3
        tri.append((lcx + 13 * np.cos(ang), lcy + 13 * np.sin(ang)))
    sd.line(tri + [tri[0]], fill=(220, 248, 255, 220), width=1)

    overlay = Image.alpha_composite(overlay, glow)
    overlay = Image.alpha_composite(overlay, rings)
    overlay = Image.alpha_composite(overlay, star)

    # soft circular alpha so edges blend into existing shield
    mask = Image.new("L", (w, h), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse((lcx - 36, lcy - 36, lcx + 36, lcy + 36), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(2.2))

    base_img = Image.fromarray(base).convert("RGBA")
    painted = Image.composite(overlay, base_img, mask)
    page[y0:y1, x0:x1] = np.array(painted.convert("RGB"))
    return page


def main() -> None:
    INSPECT.mkdir(exist_ok=True)
    page = np.array(Image.open(PAGE).convert("RGB"))
    page = restore_original_crop(page)
    page = clean_center(page)
    Image.fromarray(page).save(PAGE, quality=95)
    shutil.copy2(PAGE, DESK / PAGE.name)
    Image.fromarray(page[Y1:Y2, X1:X2]).save(INSPECT / "shield_after.png")
    Image.fromarray(page[740:820, 710:790]).resize((400, 400), Image.NEAREST).save(
        INSPECT / "shield_center_after2.png"
    )
    print("saved", PAGE)
    print("copied", DESK / PAGE.name)


if __name__ == "__main__":
    main()
