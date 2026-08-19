from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


path = Path(
    r"C:\Users\UniplusUser02\Desktop\comics\Special lines and centres in triangles"
    r"\similar-congruent-chapter-6-layout-fixed.png"
)
image = Image.open(path).convert("RGB")
draw = ImageDraw.Draw(image)

cream = (249, 248, 240)
ink = (24, 40, 58)
red = (221, 63, 69)
green = (40, 161, 95)
blue = (38, 112, 197)
label_font = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 12)
number_font = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 10)
caption_font = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 9)
badge_font = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 10)

# Rebuild the RHS panel as two uncluttered 3-4-5 right triangles.
draw.rectangle((444, 493, 752, 599), fill=cream)
draw.text((452, 499), "Right angle at A and D", fill=(44, 112, 190), font=caption_font)
draw.text((452, 512), "Matching hypotenuse + one leg", fill=(43, 47, 52), font=caption_font)

left = [(520, 580), (520, 542), (550, 580)]   # A, C, B
right = [(640, 580), (640, 542), (670, 580)]  # D, F, E

for points in (left, right):
    draw.line([points[0], points[1], points[2], points[0]], fill=ink, width=4, joint="curve")
    for (x, y), colour in zip(points, (red, green, blue)):
        draw.ellipse((x - 3, y - 3, x + 3, y + 3), fill=colour)

# Standard square right-angle symbols at A and D.
draw.line([(520, 571), (529, 571), (529, 580)], fill=red, width=2)
draw.line([(640, 571), (649, 571), (649, 580)], fill=red, width=2)

for text, position, colour in [
    ("A", (507, 571), red), ("B", (557, 571), blue), ("C", (516, 525), green),
    ("D", (627, 571), red), ("E", (677, 571), blue), ("F", (636, 525), green),
]:
    draw.text(position, text, fill=colour, font=label_font)

# 3-4-5 lengths: 5 is the hypotenuse and 3 is the matching leg.
for text, position in [
    ("4", (507, 550)), ("5", (548, 550)), ("3", (532, 582)),
    ("4", (627, 550)), ("5", (668, 550)), ("3", (652, 582)),
]:
    draw.text(position, text, fill=(43, 47, 52), font=number_font)

draw.rounded_rectangle((452, 574, 493, 594), radius=3, outline=green, width=2)
draw.text((458, 578), "RHS", fill=green, font=badge_font)

image.save(path)
print(path)
