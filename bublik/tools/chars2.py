"""Персонажи 2.0: Бублик (бублик) и Пончик (пончик)."""

import math
import random

from PIL import Image, ImageChops, ImageDraw

from look import DOUGH, DOUGH_HI, ICING, INK, SEED

S = 700
CX = CY = 350
R = 214
HOLE = 86

# Плечо и кисть относительно центра спрайта.
POSES = {
    "idle": ((-118, 18, -168, 155), (118, 22, 172, 148)),
    "talk": ((-118, 18, -180, 110), (96, -6, 196, 8)),
    "point": ((-120, 40, -170, 150), (150, 50, 268, -20)),
    "shock": ((-96, -8, -180, -125), (100, -14, 186, -136)),
    "hold": ((-88, 6, -205, 36), (118, 28, 168, 150)),
    "orange": ((-70, 36, -155, 168), (70, 36, 158, 168)),
}

_cache = {}


def ring_mask(outer, inner, cx=CX, cy=CY):
    m = Image.new("L", (S, S), 0)
    d = ImageDraw.Draw(m)
    d.ellipse([cx - outer, cy - outer, cx + outer, cy + outer], fill=255)
    if inner > 0:
        d.ellipse([cx - inner, cy - inner, cx + inner, cy + inner], fill=0)
    return m


def _limb(d, a, b, fill, width):
    d.line([a, b], fill=INK, width=width + 10)
    d.line([a, b], fill=fill, width=width)


def _hand(d, p, fill, rad):
    x, y = p
    d.ellipse([x - rad - 4, y - rad - 4, x + rad + 4, y + rad + 4], fill=INK)
    d.ellipse([x - rad, y - rad, x + rad, y + rad], fill=fill)
    if rad > 30:
        d.arc([x - rad + 8, y - 6, x + rad - 8, y + rad - 6], 20, 160, fill=(180, 70, 20), width=3)
        d.arc([x - 10, y - 4, x + 16, y + 18], 200, 20, fill=(180, 70, 20), width=3)


def _eyes(d, expr, blink):
    wide = expr in ("shock", "wow")
    ew, eh = (36, 40) if wide else (28, 32)
    eye_y = CY - 128
    for side in (-1, 1):
        x = CX + side * 76
        if blink or expr == "shut":
            d.arc([x - ew, eye_y - 8, x + ew, eye_y + 18], 200, 340, fill=INK, width=7)
            continue
        hh = int(eh * (0.5 if expr == "squint" else 1))
        d.ellipse([x - ew, eye_y - hh, x + ew, eye_y + hh], fill=(255, 255, 255), outline=INK, width=4)
        ir = 18 if wide else 15
        d.ellipse([x - ir, eye_y - ir + 2, x + ir, eye_y + ir + 2], fill=(102, 62, 36), outline=INK, width=2)
        d.ellipse([x - 7, eye_y - 3, x + 7, eye_y + 11], fill=INK)
        d.ellipse([x - 12, eye_y - 14, x - 3, eye_y - 5], fill=(255, 255, 255))


def _brows(d, expr):
    eye_y = CY - 128
    y = eye_y - 46
    if expr == "shock":
        y -= 16
    elif expr == "wow":
        y -= 8
    for side in (-1, 1):
        x = CX + side * 76
        if expr == "worry":
            y1 = y + (4 if side < 0 else 14)
            y2 = y + (14 if side < 0 else 4)
            d.line([(x - 30, y1), (x + 28, y2)], fill=INK, width=7)
        elif expr == "happy":
            d.arc([x - 30, y - 16, x + 30, y + 18], 200, 340, fill=INK, width=7)
        else:
            d.arc([x - 30, y - 8, x + 30, y + 22], 206, 338, fill=INK, width=7)


def _mouth(d, mouth, expr):
    x, y = CX, CY + 146
    if mouth <= 0:
        if expr == "shock":
            d.ellipse([x - 18, y - 18, x + 18, y + 20], fill=(96, 40, 46), outline=INK, width=4)
        elif expr == "worry":
            d.arc([x - 30, y - 6, x + 30, y + 28], 200, 340, fill=INK, width=6)
        else:
            d.arc([x - 36, y - 26, x + 36, y + 22], 15, 165, fill=INK, width=7)
        return
    h = {1: 16, 2: 30, 3: 36}[min(mouth, 3)]
    w = {1: 24, 2: 32, 3: 26}[min(mouth, 3)]
    d.ellipse([x - w, y - h, x + w, y + h], fill=(92, 36, 44), outline=INK, width=4)
    if mouth >= 2:
        d.chord([x - 14, y - 2, x + 14, y + h], 0, 180, fill=(226, 110, 128))


def _seeds(im):
    rng = random.Random(2)
    d = ImageDraw.Draw(im)
    for _ in range(20):
        ang = rng.uniform(0, math.tau)
        rad = rng.uniform(HOLE + 26, R - 30)
        x = CX + math.cos(ang) * rad
        y = CY + math.sin(ang) * rad
        if abs(x - CX) < 130 and y < CY - 30:
            continue
        if abs(x - CX) < 90 and y > CY + 60:
            continue
        d.ellipse([x - 9, y - 5, x + 9, y + 5], fill=SEED, outline=(196, 164, 112))


def _icing(dough_m):
    region = Image.new("L", (S, S), 0)
    rd = ImageDraw.Draw(region)
    rd.rectangle([0, 0, S, CY - 6], fill=255)
    for i in range(-10, S, 36):
        rd.pieslice([i, CY - 28, i + 46, CY + 28], 0, 180, fill=255)
    icing_a = ImageChops.multiply(dough_m, region)
    layer = Image.new("RGBA", (S, S), ICING + (255,))
    layer.putalpha(icing_a)
    glaze_m = Image.new("L", (S, S), 0)
    gd = ImageDraw.Draw(glaze_m)
    gd.arc([CX - 130, CY - 175, CX + 30, CY - 30], 200, 10, fill=210, width=18)
    gd.arc([CX - 20, CY - 150, CX + 130, CY - 20], 190, 20, fill=160, width=12)
    glaze_m = ImageChops.multiply(glaze_m, icing_a)
    glaze = Image.new("RGBA", (S, S), (255, 255, 255, 255))
    glaze.putalpha(glaze_m)
    layer = Image.alpha_composite(layer, glaze)
    rng = random.Random(4)
    colors = [(255, 210, 64), (80, 190, 255), (255, 255, 255), (110, 210, 120), (190, 130, 255)]
    sp = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sp)
    for i in range(18):
        ang = rng.uniform(-2.7, -0.45)
        rad = rng.uniform(HOLE + 28, R - 38)
        x = int(CX + math.cos(ang) * rad)
        y = int(CY + math.sin(ang) * rad)
        if not (0 <= x < S and 0 <= y < S) or icing_a.getpixel((x, y)) < 100:
            continue
        col = colors[i % len(colors)]
        sd.rounded_rectangle([x - 8, y - 3, x + 8, y + 3], radius=2, fill=col + (255,))
    layer = Image.alpha_composite(layer, sp)
    return layer


def _bite(body):
    ang = -0.42
    bx = CX + math.cos(ang) * (R - 6)
    by = CY + math.sin(ang) * (R - 6)
    a = body.getchannel("A")
    ImageDraw.Draw(a).ellipse([bx - 54, by - 48, bx + 54, by + 48], fill=0)
    body.putalpha(a)
    ImageDraw.Draw(body).arc(
        [bx - 54, by - 48, bx + 54, by + 48], 30, 250, fill=(120, 70, 40, 255), width=7
    )


def draw_char(kind, pose, expr, mouth, blink):
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    limb = DOUGH if kind == "bublik" else (244, 198, 154)
    hand_fill = (255, 140, 42) if pose == "orange" else limb
    hand_r = 46 if pose == "orange" else 22

    for side in (-1, 1):
        hip = (CX + side * 64, CY + R - 36)
        foot = (CX + side * 82, CY + R + 112)
        _limb(d, hip, foot, limb, 30)
        d.ellipse([foot[0] - 28, foot[1] - 12, foot[0] + 32, foot[1] + 16], fill=INK)
        d.ellipse([foot[0] - 24, foot[1] - 8, foot[0] + 28, foot[1] + 12], fill=(96, 60, 40))

    hands = []
    for spec in POSES[pose]:
        p1 = (CX + spec[0], CY + spec[1])
        p2 = (CX + spec[2], CY + spec[3])
        _limb(d, p1, p2, limb, 32)
        hands.append(p2)

    ink_m = ring_mask(R, HOLE - 12)
    dough_m = ring_mask(R - 10, HOLE)
    ink_layer = Image.new("RGBA", (S, S), INK + (255,))
    ink_layer.putalpha(ink_m)
    dough_col = DOUGH if kind == "bublik" else (238, 190, 138)
    dough_layer = Image.new("RGBA", (S, S), dough_col + (255,))
    dough_layer.putalpha(dough_m)
    body = Image.alpha_composite(ink_layer, dough_layer)

    hi_m = Image.new("L", (S, S), 0)
    ImageDraw.Draw(hi_m).ellipse([CX - 160, CY - 200, CX + 10, CY - 20], fill=150)
    hi_m = ImageChops.multiply(hi_m, dough_m)
    hi = Image.new("RGBA", (S, S), DOUGH_HI + (255,))
    hi.putalpha(hi_m)
    body = Image.alpha_composite(body, hi)

    sh_m = Image.new("L", (S, S), 0)
    ImageDraw.Draw(sh_m).ellipse([CX - 40, CY + 30, CX + 200, CY + 210], fill=100)
    sh_m = ImageChops.multiply(sh_m, dough_m)
    sh = Image.new("RGBA", (S, S), (150, 86, 40, 255))
    sh.putalpha(sh_m)
    body = Image.alpha_composite(body, sh)
    # Дырка бублика — объём, а не второе окно в фон.
    cavity = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cavity)
    rim, pit = ((220, 184, 140), (196, 154, 108)) if kind == "bublik" else ((236, 206, 176), (214, 176, 146))
    cd.ellipse([CX - HOLE + 4, CY - HOLE + 4, CX + HOLE - 4, CY + HOLE - 4], fill=rim + (255,))
    cd.ellipse([CX - HOLE + 26, CY - HOLE + 18, CX + HOLE - 16, CY + HOLE - 8], fill=pit + (255,))
    cd.arc([CX - HOLE + 2, CY - HOLE + 2, CX + HOLE - 2, CY + HOLE - 2], 200, 10, fill=(255, 236, 210, 230), width=6)
    body = Image.alpha_composite(body, cavity)

    if kind == "ponchik":
        body = Image.alpha_composite(body, _icing(dough_m))
        _bite(body)
    im = Image.alpha_composite(im, body)
    if kind == "bublik":
        _seeds(im)

    fd = ImageDraw.Draw(im)
    _eyes(fd, expr, blink)
    _brows(fd, expr)
    _mouth(fd, mouth, expr)

    blush = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    bd = ImageDraw.Draw(blush)
    col = (255, 150, 170, 110) if kind == "ponchik" else (232, 140, 110, 80)
    for side in (-1, 1):
        x = CX + side * 76
        bd.ellipse([x - 20, CY - 86, x + 20, CY - 66], fill=col)
    im = Image.alpha_composite(im, blush)

    hd = ImageDraw.Draw(im)
    for p in hands:
        _hand(hd, p, hand_fill, hand_r)
    return im, hands


def sprite(kind, pose, expr, mouth, blink, scale):
    scale = round(float(scale), 2)
    key = (kind, pose, expr, int(mouth), bool(blink), scale)
    hit = _cache.get(key)
    if hit:
        return hit
    raw_key = key[:-1]
    raw = _cache.get(raw_key)
    if raw is None:
        raw = draw_char(kind, pose, expr, mouth, blink)
        _cache[raw_key] = raw
    img, hands = raw
    if abs(scale - 1) > 0.01:
        img = img.resize((max(1, int(S * scale)), max(1, int(S * scale))), Image.Resampling.LANCZOS)
    _cache[key] = (img, hands)
    return img, hands


def hand_world(hand, cx, cy, scale):
    return (cx + (hand[0] - CX) * scale, cy + (hand[1] - CY) * scale)
