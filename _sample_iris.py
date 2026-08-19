from pathlib import Path

import numpy as np
from PIL import Image

root = Path(
    r"c:\Users\User\OneDrive - The Education University of Hong Kong\桌面\comics"
    r"\Law of index\rule of Law of index"
)
out = Path(r"c:\Users\User\OneDrive - The Education University of Hong Kong\桌面\comics\_inspect")
ch3 = np.array(Image.open(root / "indices-club-chapter-3-color.png").convert("RGB"))
ch1 = np.array(Image.open(root / "indices-club-chapter-1-color.png").convert("RGB"))

# ch3_p1_wide is ch3[50:200, 100:280] — eyes in upper-middle of face
# try a few tight windows
for name, box in [
    ("a", (85, 115, 155, 200)),
    ("b", (90, 120, 165, 210)),
    ("c", (95, 125, 145, 195)),
    ("d", (80, 110, 170, 220)),
    ("e", (100, 130, 160, 205)),
]:
    y1, y2, x1, x2 = box
    c = ch3[y1:y2, x1:x2]
    Image.fromarray(c).resize((c.shape[1] * 5, c.shape[0] * 5), Image.NEAREST).save(
        out / f"ch3eye_{name}.png"
    )
    print(name, box, "mean", c.mean(axis=(0, 1)))

# p2 face ch3[310:520, 40:280] — eyes around y~380-430
for name, box in [
    ("p2a", (370, 410, 90, 160)),
    ("p2b", (375, 415, 110, 180)),
    ("p2c", (380, 420, 130, 200)),
]:
    y1, y2, x1, x2 = box
    c = ch3[y1:y2, x1:x2]
    Image.fromarray(c).resize((c.shape[1] * 4, c.shape[0] * 4), Image.NEAREST).save(
        out / f"ch3eye_{name}.png"
    )
    print(name, box, "mean", c.mean(axis=(0, 1)))

print("ch1 current iris 964:976,186:196")
print(ch1[964:976, 186:196].mean(axis=(0, 1)))
print(ch1[964:976, 186:196])
