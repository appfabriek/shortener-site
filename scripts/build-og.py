#!/usr/bin/env python3
"""Build the share image (1200x630) for every short-link domain.

The bare home as a picture: the name with its coloured TLD and the one line
from scripts/build-bare.py, in JetBrains Mono (fonts/). Writes
hosts/<host>/images/og.png, which the publish workflow copies to
/images/og.png on that host. Needs Pillow.
Run `python3 scripts/build-og.py` and commit the images with it.
"""

import importlib.util
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONT = str(ROOT / "fonts" / "jetbrains-mono-latin.woff2")
W, H = 1200, 630
X = 96  # left margin
INK = "#111111"
FAINT = "#B5B5B5"
MUTE = "#6B6B6B"
RULE = "#EDEDED"


def domains() -> dict:
    spec = importlib.util.spec_from_file_location("build_bare", ROOT / "scripts" / "build-bare.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.DOMAINS


def font(size: int, weight: int) -> ImageFont.FreeTypeFont:
    f = ImageFont.truetype(FONT, size)
    f.set_variation_by_axes([weight])
    return f


def wrap(draw: ImageDraw.ImageDraw, text: str, f: ImageFont.FreeTypeFont, width: int) -> list:
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if line and draw.textlength(trial, font=f) > width:
            lines.append(line)
            line = word
        else:
            line = trial
    return lines + [line]


def image(host: str, name: str, tld: str, dot: str, line: str, parent) -> Image.Image:
    img = Image.new("RGB", (W, H), "#FFFFFF")
    d = ImageDraw.Draw(img)

    # The name, as large as fits: name in ink, TLD in the domain's colour, "/…" faint.
    parts = [(name, INK), (tld, dot), ("/…", FAINT)]
    size = 132
    while size > 60:
        big = font(size, 600)
        if sum(d.textlength(t, font=big) for t, _ in parts) <= W - 2 * X:
            break
        size -= 4
    text = font(32, 400)
    body = wrap(d, line, text, W - 2 * X)
    note = parent  # the page adds "⟶"; the latin subset of the font has no arrow

    line_h = 50
    block = size + 56 + line_h * len(body) + (line_h + 8 if note else 0)
    y = (H - 64 - block) // 2  # centred above the footer rule

    x = X
    for t, colour in parts:
        d.text((x, y), t, font=big, fill=colour)
        x += d.textlength(t, font=big)

    y += size + 56
    for row in body:
        d.text((X, y), row, font=text, fill=INK)
        y += line_h
    if note:
        d.text((X, y + 8), note, font=text, fill=MUTE)

    # The quiet footer of the page: a rule and the host.
    d.line([(0, H - 64), (W, H - 64)], fill=RULE, width=2)
    small = font(22, 400)
    d.text((X, H - 46), host, font=small, fill=MUTE)
    return img


def main() -> None:
    for host, (name, tld, dot, line, parent, _console) in domains().items():
        target = ROOT / "hosts" / host / "images" / "og.png"
        target.parent.mkdir(parents=True, exist_ok=True)
        image(host, name, tld, dot, line, parent).save(target, "PNG", optimize=True)


if __name__ == "__main__":
    main()
