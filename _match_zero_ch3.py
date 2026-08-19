"""Restore Ch.1–2, then match Zero hair + iris to Chapter 3 only."""
from __future__ import annotations

import shutil
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image

BACKUP = Path(
    r"C:\Users\User\Downloads\comics-20260811T110120Z-1-001\comics"
    r"\Law of index\rule of Law of index"
)
ROOT = Path(
    r"c:\Users\User\OneDrive - The Education University of Hong Kong\桌面\comics"
    r"\Law of index\rule of Law of index"
)
DESKTOP = Path(r"C:\Users\User\OneDrive - The Education University of Hong Kong\桌面")
CH3 = ROOT / "indices-club-chapter-3-color.png"
IRIS = np.array([41.0, 32.0, 26.0], dtype=np.float32)


def luma(rgb: np.ndarray) -> np.ndarray:
    return 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]


def feather(mask: np.ndarray, rounds: int = 2) -> np.ndarray:
    soft = mask.astype(np.float32)
    for _ in range(rounds):
        pad = np.pad(soft, 1, mode="edge")
        soft = (
            pad[1:-1, 1:-1] * 4
            + pad[:-2, 1:-1]
            + pad[2:, 1:-1]
            + pad[1:-1, :-2]
            + pad[1:-1, 2:]
        ) / 8.0
    return np.clip(soft, 0, 1)


def blobs(mask: np.ndarray, lo: int, hi: int) -> np.ndarray:
    h, w = mask.shape
    vis = np.zeros_like(mask)
    keep = np.zeros_like(mask)
    ys, xs = np.where(mask)
    for sy, sx in zip(ys, xs):
        if vis[sy, sx]:
            continue
        q = deque([(int(sy), int(sx))])
        vis[sy, sx] = True
        cells = [(int(sy), int(sx))]
        while q:
            cy, cx = q.popleft()
            for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                ny, nx = cy + dy, cx + dx
                if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not vis[ny, nx]:
                    vis[ny, nx] = True
                    q.append((ny, nx))
                    cells.append((ny, nx))
        if lo <= len(cells) <= hi:
            for cy, cx in cells:
                keep[cy, cx] = True
    return keep


def dye_hair(img: np.ndarray, alpha: np.ndarray) -> np.ndarray:
    y = luma(img.astype(np.float32))
    sh = np.array([175, 122, 65], np.float32)
    md = np.array([216, 164, 106], np.float32)
    hi = np.array([246, 208, 161], np.float32)
    t = np.clip((y - 70) / 160.0, 0, 1)[..., None]
    target = np.where(t < 0.5, sh + (md - sh) * (t * 2), md + (hi - md) * ((t - 0.5) * 2))
    ty = luma(target)
    scale = np.clip(y / np.maximum(ty, 1.0), 0.75, 1.25)[..., None]
    dyed = np.clip(target * scale, 0, 255)
    a = alpha[..., None]
    return np.clip(img.astype(np.float32) * (1 - a) + dyed * a, 0, 255).astype(np.uint8)


def dye_iris(img: np.ndarray, alpha: np.ndarray) -> np.ndarray:
    y = luma(img.astype(np.float32))
    scale = np.clip(y / 48.0, 0.55, 1.65)[..., None]
    dyed = np.clip(IRIS * scale, 0, 255)
    a = alpha[..., None]
    return np.clip(img.astype(np.float32) * (1 - a) + dyed * a, 0, 255).astype(np.uint8)


def save(path: Path, img: np.ndarray) -> None:
    Image.fromarray(img).save(path, quality=95)
    shutil.copy2(path, DESKTOP / path.name)
    print("saved", path.name)


def restore(name: str) -> np.ndarray:
    src = BACKUP / name
    dst = ROOT / name
    shutil.copy2(src, dst)
    return np.array(Image.open(dst).convert("RGB"))


def ch1() -> None:
    img = restore("indices-club-chapter-1-color.png")
    r, g, b = [img[..., i].astype(np.float32) for i in range(3)]
    y = luma(img.astype(np.float32))
    mx = np.maximum(np.maximum(r, g), b)
    mn = np.minimum(np.minimum(r, g), b)
    chroma = mx - mn

    zone = np.zeros(img.shape[:2], dtype=bool)
    zone[860:1165, 0:250] = True
    white = (r > 230) & (g > 220) & (b > 200)
    hair = zone & ~white & (y > 70) & (y < 238) & (
        ((chroma < 48) & (np.abs(r - g) < 26) & (np.abs(g - b) < 36))
        | ((b > r + 2) & (b > g - 6) & (chroma < 70) & (y < 220))  # lavender/blue-silver
    )
    hair = blobs(hair, 25, 30000)
    print("ch1 hair", int(hair.sum()))

    # iris: only the small amber disc next to a dark pupil, inside the eye socket
    eye = np.zeros(img.shape[:2], dtype=bool)
    y1, y2, x1, x2 = 948, 1012, 148, 208
    crop = img[y1:y2, x1:x2]
    cr, cg, cb = [crop[..., i].astype(np.float32) for i in range(3)]
    cy = luma(crop.astype(np.float32))
    gold = (cr > 145) & (cg > 85) & (cb < 105) & (cr > cb + 35) & (cg > cb + 15) & (cy < 195)
    pupil = cy < 55
    # keep gold that touches the pupil neighborhood
    pad = np.pad(pupil, 4, constant_values=False)
    near = np.zeros_like(pupil)
    h, w = pupil.shape
    for dy in range(-4, 5):
        for dx in range(-4, 5):
            near |= pad[4 + dy : 4 + dy + h, 4 + dx : 4 + dx + w]
    iris = blobs(gold & near, 4, 180)
    eye[y1:y2, x1:x2] = iris
    print("ch1 iris", int(iris.sum()))

    img = dye_hair(img, feather(hair, 2))
    img = dye_iris(img, feather(eye, 1))
    save(ROOT / "indices-club-chapter-1-color.png", img)


def ch2() -> None:
    img = restore("indices-club-chapter-2-color.png")
    r, g, b = [img[..., i].astype(np.float32) for i in range(3)]
    y = luma(img.astype(np.float32))
    mx = np.maximum(np.maximum(r, g), b)
    mn = np.minimum(np.minimum(r, g), b)
    chroma = mx - mn

    zone = np.zeros(img.shape[:2], dtype=bool)
    for y1, y2, x1, x2 in [(20, 350, 0, 430), (386, 625, 0, 450), (667, 905, 0, 480), (1148, 1435, 0, 400)]:
        zone[y1:y2, x1:x2] = True
    hair = zone & (y > 70) & (y < 238) & (chroma < 45) & (np.abs(r - g) < 24) & (np.abs(g - b) < 30)
    hair &= ~((r > 236) & (g > 236) & (b > 236))
    hair &= ~((b > r + 16) & (b > g + 6))
    hair = blobs(hair, 40, 40000)
    print("ch2 hair", int(hair.sum()))

    face = np.zeros(img.shape[:2], dtype=bool)
    for y1, y2, x1, x2 in [(50, 200, 80, 280), (410, 540, 90, 300), (700, 840, 80, 300), (1175, 1320, 20, 240)]:
        face[y1:y2, x1:x2] = True
    red = face & (r > 125) & (r < 230) & (g < 90) & (b < 90) & (r > g + 45) & (r > b + 45)
    iris = blobs(red, 5, 120)
    print("ch2 iris", int(iris.sum()))

    img = dye_hair(img, feather(hair, 2))
    img = dye_iris(img, feather(iris, 1))
    save(ROOT / "indices-club-chapter-2-color.png", img)


def law() -> None:
    # keep current card; only retouch a tiny eye if still amber
    path = ROOT / "indices-club-laws-card-color.png"
    img = np.array(Image.open(path).convert("RGB"))
    y1, y2, x1, x2 = 930, 1010, 780, 900
    crop = img[y1:y2, x1:x2]
    cr, cg, cb = [crop[..., i].astype(np.float32) for i in range(3)]
    cy = luma(crop.astype(np.float32))
    amber = (cr > 130) & (cg > 80) & (cb < 115) & (cr > cb + 25) & (cy < 175) & (cy > 60)
    pupil = cy < 50
    pad = np.pad(pupil, 3, constant_values=False)
    near = np.zeros_like(pupil)
    h, w = pupil.shape
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            near |= pad[3 + dy : 3 + dy + h, 3 + dx : 3 + dx + w]
    iris = blobs(amber & near, 3, 80)
    print("law iris", int(iris.sum()))
    if iris.any():
        eye = np.zeros(img.shape[:2], dtype=bool)
        eye[y1:y2, x1:x2] = iris
        img = dye_iris(img, feather(eye, 1))
        save(path, img)


def main() -> None:
    ch1()
    ch2()
    law()
    print("done")


if __name__ == "__main__":
    main()
