"""Recolor Chapter 2 Zero hair to match Chapter 3 sandy blond."""
from __future__ import annotations

import shutil
from pathlib import Path

import numpy as np
from PIL import Image

CH2 = Path(
    r"c:\Users\User\OneDrive - The Education University of Hong Kong\桌面\comics"
    r"\Law of index\rule of Law of index\indices-club-chapter-2-color.png"
)
CH3 = Path(
    r"c:\Users\User\OneDrive - The Education University of Hong Kong\桌面\comics"
    r"\Law of index\rule of Law of index\indices-club-chapter-3-color.png"
)
DESKTOP = Path(r"C:\Users\User\OneDrive - The Education University of Hong Kong\桌面")


def luma(rgb: np.ndarray) -> np.ndarray:
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    return 0.299 * r + 0.587 * g + 0.114 * b


def ch3_hair_lut(ch3: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Median RGB of Chapter 3 Zero hair, binned by luminance."""
    regions = [
        (40, 200, 20, 300),
        (330, 520, 20, 280),
        (620, 820, 20, 280),
        (900, 1100, 20, 300),
        (1260, 1460, 40, 340),
    ]
    samples = []
    for y1, y2, x1, x2 in regions:
        crop = ch3[y1:y2, x1:x2].astype(np.float32)
        r, g, b = crop[..., 0], crop[..., 1], crop[..., 2]
        mx = np.maximum(np.maximum(r, g), b)
        mn = np.minimum(np.minimum(r, g), b)
        blond = (
            (r > 130)
            & (g > 90)
            & (b < r - 8)
            & (g > b + 8)
            & (r < 252)
            & ((r - b) > 25)
            & ((mx - mn) > 20)
            & ((mx - mn) < 160)
        )
        if blond.any():
            samples.append(crop[blond])
    hair = np.concatenate(samples, axis=0)
    y = luma(hair)
    bins = np.linspace(40, 250, 22)
    lut = np.zeros((len(bins), 3), dtype=np.float32)
    valid = np.zeros(len(bins), dtype=bool)
    for i in range(len(bins)):
        lo = bins[i] - 12
        hi = bins[i] + 12
        sel = (y >= lo) & (y < hi)
        if sel.sum() >= 8:
            lut[i] = np.median(hair[sel], axis=0)
            valid[i] = True
    # fill missing bins
    for i in range(len(bins)):
        if not valid[i]:
            near = np.where(valid)[0]
            j = near[np.argmin(np.abs(near - i))]
            lut[i] = lut[j]
    return bins, lut


def hair_mask(img: np.ndarray) -> np.ndarray:
    """Soft mask of Zero's silver hair in Chapter 2 panels 1, 2, 3, 5."""
    h, w = img.shape[:2]
    r = img[..., 0].astype(np.float32)
    g = img[..., 1].astype(np.float32)
    b = img[..., 2].astype(np.float32)
    mx = np.maximum(np.maximum(r, g), b)
    mn = np.minimum(np.minimum(r, g), b)
    chroma = mx - mn
    y = luma(img.astype(np.float32))

    silver = (
        (chroma < 42)
        & (y > 70)
        & (y < 242)
        & (np.abs(r - g) < 22)
        & (np.abs(g - b) < 28)
        & (np.abs(r - b) < 28)
        & ~((r > 236) & (g > 236) & (b > 236))  # speech-bubble white
        & ~((b > r + 18) & (b > g + 8))  # purple/blue energy
        & ~((r > 160) & (g > 120) & (b < 90))  # orange shards / tan band
    )

    # Zero lives on the left of panels 1, 2, 3, 5 only
    allowed = np.zeros((h, w), dtype=bool)
    bands = [
        (20, 350, 0, 470),  # panel 1
        (386, 625, 0, 470),  # panel 2
        (667, 905, 0, 500),  # panel 3
        (1148, 1435, 0, 430),  # panel 5
    ]
    for y1, y2, x1, x2 in bands:
        allowed[y1:y2, x1:x2] = True
    mask = silver & allowed

    # keep only reasonably large connected clumps (drop specks)
    from collections import deque

    vis = np.zeros_like(mask)
    keep = np.zeros_like(mask)
    ys, xs = np.where(mask)
    for sy, sx in zip(ys, xs):
        if vis[sy, sx]:
            continue
        q = deque([(sy, sx)])
        vis[sy, sx] = True
        cells = [(sy, sx)]
        while q:
            cy, cx = q.popleft()
            for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                ny, nx = cy + dy, cx + dx
                if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not vis[ny, nx]:
                    vis[ny, nx] = True
                    q.append((ny, nx))
                    cells.append((ny, nx))
        if len(cells) >= 40:
            for cy, cx in cells:
                keep[cy, cx] = True

    # feather
    soft = keep.astype(np.float32)
    for _ in range(2):
        pad = np.pad(soft, 1, mode="edge")
        soft = (
            pad[1:-1, 1:-1] * 4
            + pad[:-2, 1:-1]
            + pad[2:, 1:-1]
            + pad[1:-1, :-2]
            + pad[1:-1, 2:]
        ) / 8.0
    return np.clip(soft, 0, 1)


def apply(ch2: np.ndarray, alpha: np.ndarray, bins: np.ndarray, lut: np.ndarray) -> np.ndarray:
    y = luma(ch2.astype(np.float32))
    idx = np.clip(np.searchsorted(bins, y), 0, len(bins) - 1)
    target = lut[idx]
    # keep local contrast: scale target to source luminance
    t_y = luma(target)
    scale = np.divide(y, np.maximum(t_y, 1.0))
    scale = np.clip(scale, 0.72, 1.28)
    dyed = np.clip(target * scale[..., None], 0, 255)
    out = ch2.astype(np.float32)
    a = alpha[..., None]
    out = out * (1 - a) + dyed * a
    return np.clip(out, 0, 255).astype(np.uint8)


def main() -> None:
    ch2 = np.array(Image.open(CH2).convert("RGB"))
    ch3 = np.array(Image.open(CH3).convert("RGB"))
    bins, lut = ch3_hair_lut(ch3)
    alpha = hair_mask(ch2)
    out = apply(ch2, alpha, bins, lut)
    Image.fromarray(out).save(CH2, quality=95)
    shutil.copy2(CH2, DESKTOP / CH2.name)
    print("recolored hair pixels", float(alpha.sum()), "max a", float(alpha.max()))
    print("saved", CH2)
    print("copied", DESKTOP / CH2.name)


if __name__ == "__main__":
    main()
