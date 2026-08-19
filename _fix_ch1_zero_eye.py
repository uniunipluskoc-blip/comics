"""Restore Ch1, dye Zero hair blond (no box), recolor only the gold iris."""
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
DESK = Path(r"C:\Users\User\OneDrive - The Education University of Hong Kong\桌面")
INSPECT = Path(r"c:\Users\User\OneDrive - The Education University of Hong Kong\桌面\comics\_inspect")
PAGE = ROOT / "indices-club-chapter-1-color.png"
BROWN = np.array([62.0, 42.0, 27.0], dtype=np.float32)


def luma(a: np.ndarray) -> np.ndarray:
    a = a.astype(np.float32)
    return 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]


def feather(m: np.ndarray, n: int = 2) -> np.ndarray:
    s = m.astype(np.float32)
    for _ in range(n):
        p = np.pad(s, 1, mode="edge")
        s = (
            p[1:-1, 1:-1] * 4
            + p[:-2, 1:-1]
            + p[2:, 1:-1]
            + p[1:-1, :-2]
            + p[1:-1, 2:]
        ) / 8.0
    return np.clip(s, 0, 1)


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


def dye_blond(img: np.ndarray, a: np.ndarray) -> np.ndarray:
    y = luma(img)
    sh = np.array([175.0, 122.0, 65.0])
    md = np.array([216.0, 164.0, 106.0])
    hi = np.array([246.0, 208.0, 161.0])
    t = np.clip((y - 70) / 160.0, 0, 1)[..., None]
    target = np.where(t < 0.5, sh + (md - sh) * (t * 2), md + (hi - md) * ((t - 0.5) * 2))
    ty = luma(target)
    scale = np.clip(y / np.maximum(ty, 1.0), 0.75, 1.25)[..., None]
    dyed = np.clip(target * scale, 0, 255)
    return np.clip(img.astype(np.float32) * (1 - a[..., None]) + dyed * a[..., None], 0, 255).astype(
        np.uint8
    )


def iris_mask(img: np.ndarray) -> np.ndarray:
    mask = np.zeros(img.shape[:2], dtype=bool)
    y1, y2, x1, x2 = 964, 976, 186, 196
    crop = img[y1:y2, x1:x2].astype(np.float32)
    r, g, b = crop[..., 0], crop[..., 1], crop[..., 2]
    y = luma(crop)
    gold = (r - b > 70) & (b < 85) & (r > 130) & (y > 45) & (y < 190) & (r > g)
    highlight = (r > 185) & (g > 150) & (b > 90) & (y > 155)
    mask[y1:y2, x1:x2] = gold & ~highlight
    return mask


def dye_iris(img: np.ndarray, mask: np.ndarray) -> np.ndarray:
    out = img.astype(np.float32)
    y = luma(out)
    y_new = np.clip(30.0 + (y - 50.0) * 0.38, 28.0, 82.0)
    k = y_new / float(luma(BROWN[None, None, :])[0, 0])
    dyed = np.clip(BROWN * k[..., None], 0, 255)
    m = mask.astype(np.float32)[..., None]
    return np.clip(out * (1.0 - m) + dyed * m, 0, 255).astype(np.uint8)


def dump(name: str, arr: np.ndarray, box: tuple[int, int, int, int], scale: int) -> None:
    y1, y2, x1, x2 = box
    Image.fromarray(arr[y1:y2, x1:x2]).resize(
        ((x2 - x1) * scale, (y2 - y1) * scale), Image.NEAREST
    ).save(INSPECT / name)


def main() -> None:
    INSPECT.mkdir(exist_ok=True)
    img = np.array(Image.open(BACKUP / "indices-club-chapter-1-color.png").convert("RGB"))
    r, g, b = [img[:, :, i].astype(np.float32) for i in range(3)]
    y = luma(img)
    mx = np.maximum(np.maximum(r, g), b)
    mn = np.minimum(np.minimum(r, g), b)
    chroma = mx - mn

    zone = np.zeros(img.shape[:2], dtype=bool)
    zone[860:1165, 0:250] = True
    white = (r > 230) & (g > 220) & (b > 200)
    hair = zone & ~white & (y > 70) & (y < 238) & (
        ((chroma < 48) & (np.abs(r - g) < 26) & (np.abs(g - b) < 36))
        | ((b > r + 2) & (b > g - 6) & (chroma < 70) & (y < 220))
    )
    # keep skin and the drawn eyeball
    skin = (r > 145) & (g > 118) & (b > 108) & (r > g + 6) & ((r - b) < 50)
    eye = np.zeros_like(hair)
    eye[960:982, 178:210] = True
    hair &= ~skin & ~eye
    hair = blobs(hair, 25, 40000)
    print("hair pixels", int(hair.sum()))

    img = dye_blond(img, feather(hair, 2))

    iris = iris_mask(img)
    print("iris pixels", int(iris.sum()))
    if iris.any():
        print("iris mean before", img[iris].mean(0))
    img = dye_iris(img, iris)
    if iris.any():
        print("iris mean after", img[iris].mean(0))

    Image.fromarray(img).save(PAGE, quality=95)
    shutil.copy2(PAGE, DESK / PAGE.name)

    dump("fix_inset_after.png", img, (860, 1165, 0, 280), 2)
    dump("fix_eye_after.png", img, (950, 1010, 155, 220), 6)
    vis = img.copy()
    vis[iris] = [255, 0, 255]
    dump("fix_iris_mask.png", vis, (950, 1010, 155, 220), 6)
    print("saved", PAGE)
    print("copied", DESK / PAGE.name)


if __name__ == "__main__":
    main()
