"""Make Ch1 Zero iris match the dark brown of Ch2/Ch3. Iris disc only."""
from __future__ import annotations

import shutil
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(
    r"c:\Users\User\OneDrive - The Education University of Hong Kong\桌面\comics"
    r"\Law of index\rule of Law of index"
)
DESK = Path(r"C:\Users\User\OneDrive - The Education University of Hong Kong\桌面")
INSPECT = Path(r"c:\Users\User\OneDrive - The Education University of Hong Kong\桌面\comics\_inspect")
PAGE = ROOT / "indices-club-chapter-1-color.png"

# Sampled from the user's Ch2/Ch3 dark-iris crop (center ~72,32,35; dark mean ~58,43,40)
# and Ch3 Zero irises — dark chocolate, slight red, almost no yellow.
BROWN = np.array([50.0, 31.0, 30.0], dtype=np.float32)
CX, CY = 190.0, 970.5
RX, RY = 5.6, 5.0


def luma(a: np.ndarray) -> np.ndarray:
    a = a.astype(np.float32)
    return 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]


def iris_disc(shape: tuple[int, int]) -> np.ndarray:
    h, w = shape
    yy, xx = np.ogrid[:h, :w]
    return ((xx - CX) / RX) ** 2 + ((yy - CY) / RY) ** 2 <= 1.0


def main() -> None:
    INSPECT.mkdir(exist_ok=True)
    img = np.array(Image.open(PAGE).convert("RGB"))
    before = img.copy()
    y = luma(img)
    r = img[..., 0].astype(np.float32)
    g = img[..., 1].astype(np.float32)
    b = img[..., 2].astype(np.float32)

    disc = iris_disc(img.shape[:2])
    highlight = (r > 180) & (g > 150) & (b > 95) & (y > 145)
    lash = y < 14
    # leftover gold / olive / already-dyed brown inside the disc
    iris = disc & ~highlight & ~lash
    print("iris pixels", int(iris.sum()))
    if iris.any():
        print("mean before", img[iris].mean(0))

    out = img.astype(np.float32)
    y_new = np.clip(20.0 + (y - 18.0) * 0.20, 18.0, 48.0)
    k = y_new / float(luma(BROWN[None, None, :])[0, 0])
    dyed = np.clip(BROWN * k[..., None], 0, 255)
    m = iris.astype(np.float32)[..., None]
    out = np.clip(out * (1.0 - m) + dyed * m, 0, 255).astype(np.uint8)
    if iris.any():
        print("mean after", out[iris].mean(0))

    Image.fromarray(out).save(PAGE, quality=95)
    shutil.copy2(PAGE, DESK / PAGE.name)

    def dump(name: str, arr: np.ndarray, box: tuple[int, int, int, int], scale: int) -> None:
        y1, y2, x1, x2 = box
        Image.fromarray(arr[y1:y2, x1:x2]).resize(
            ((x2 - x1) * scale, (y2 - y1) * scale), Image.NEAREST
        ).save(INSPECT / name)

    dump("match_eye_before.png", before, (950, 1010, 155, 220), 6)
    dump("match_eye_after.png", out, (950, 1010, 155, 220), 6)
    dump("match_inset_after.png", out, (860, 1165, 0, 280), 2)
    vis = out.copy()
    vis[iris] = [255, 0, 255]
    dump("match_iris_mask.png", vis, (950, 1010, 155, 220), 6)
    print("saved", PAGE)
    print("copied", DESK / PAGE.name)


if __name__ == "__main__":
    main()
