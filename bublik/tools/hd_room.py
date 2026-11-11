"""Фоны выпуска: кухня, ночь, радар, плакат, грядка."""

import math
import random

from PIL import Image, ImageDraw

from look import CARROT, H, INK, LEAF, W, font, grad, paste

_carrot_cache = {}


def carrot_sprite(height=420, bite=False):
    key = (height, bite)
    if key in _carrot_cache:
        return _carrot_cache[key]
    w = int(height * 0.42)
    im = Image.new("RGBA", (w, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    top = int(height * 0.28)
    body = [(w * 0.5, height * 0.96), (w * 0.16, top), (w * 0.84, top)]
    d.polygon(body, fill=CARROT)
    d.line(body + [body[0]], fill=INK, width=max(4, height // 70))
    for yy in (0.45, 0.62, 0.78):
        y = height * yy
        span = (1 - (y / height)) * w * 0.28
        d.arc([w * 0.5 - span, y - 10, w * 0.5 + span, y + 18], 10, 170, fill=(214, 90, 18), width=3)
    # Ботва.
    for ang, col in ((-0.9, LEAF), (-0.2, (40, 130, 54)), (0.5, (78, 170, 72))):
        x2 = w * 0.5 + math.sin(ang) * w * 0.55
        y2 = top - abs(math.cos(ang)) * height * 0.16
        d.line([(w * 0.5, top), (x2, y2)], fill=col, width=max(6, height // 40))
        d.ellipse([x2 - 16, y2 - 12, x2 + 18, y2 + 14], fill=col, outline=INK)
    if bite:
        d.ellipse([w * 0.35, top + 10, w * 0.85, top + height * 0.22], fill=(0, 0, 0, 0))
        # Надкус рисуем заливкой фона позже нельзя — оставим тёмную дугу.
        d.arc([w * 0.3, top, w * 0.9, top + height * 0.24], 200, 40, fill=(160, 70, 20, 255), width=6)
    _carrot_cache[key] = im
    return im


def _sky_stars(d, n, y1, y2, seed):
    rng = random.Random(seed)
    for _ in range(n):
        x, y = rng.randint(10, W - 10), rng.randint(y1, y2)
        r = rng.choice((1, 2, 2, 3))
        d.ellipse([x, y, x + r, y + r], fill=(255, 255, 240))


def kitchen(lamp=True):
    if lamp:
        im = grad((W, H), (255, 226, 196), (244, 206, 164)).convert("RGBA")
        wall_line = (214, 168, 120)
        floor = (186, 132, 78)
        plank = (150, 98, 56)
        cab = (168, 104, 60)
        door = (196, 132, 78)
        counter = (228, 190, 140)
        counter_top = (246, 220, 180)
    else:
        im = grad((W, H), (28, 36, 64), (16, 18, 36)).convert("RGBA")
        wall_line = (48, 56, 82)
        floor = (42, 34, 30)
        plank = (32, 26, 24)
        cab = (54, 42, 38)
        door = (70, 54, 46)
        counter = (62, 50, 44)
        counter_top = (82, 66, 56)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 1500, W, H], fill=floor)
    for x in range(0, W, 100):
        d.line([(x, 1500), (x, H)], fill=plank, width=4)
    d.rectangle([0, 742, W, 786], fill=(120, 74, 48) if lamp else (40, 32, 36))
    d.rounded_rectangle([30, 60, 1050, 360], radius=16, fill=cab, outline=INK, width=6)
    for x in range(52, 1000, 196):
        d.rounded_rectangle([x, 88, x + 176, 332], radius=10, fill=door, outline=INK, width=4)
        d.rounded_rectangle([x + 78, 190, x + 96, 236], radius=4, fill=(240, 210, 140) if lamp else (120, 100, 70))
    # Окно.
    d.rounded_rectangle([340, 400, 740, 730], radius=8, fill=(16, 24, 52), outline=(92, 62, 42), width=16)
    d.line([(540, 400), (540, 730)], fill=(92, 62, 42), width=8)
    d.line([(340, 565), (740, 565)], fill=(92, 62, 42), width=8)
    d.ellipse([560, 450, 650, 540], fill=(255, 236, 186))
    _sky_stars(d, 12, 420, 620, 5)
    d.rectangle([0, 786, W, 980], fill=counter)
    d.rectangle([0, 786, W, 812], fill=counter_top)
    # Плитка.
    tile = (236, 214, 190) if lamp else (70, 64, 72)
    for y in (820, 900):
        for x in range(20, W, 70):
            d.rectangle([x, y, x + 60, y + 60], outline=wall_line, width=2)
            _ = tile
    # Холодильник.
    d.rounded_rectangle([880, 470, 1064, 800], radius=14, fill=(232, 238, 242) if lamp else (70, 78, 88), outline=INK, width=5)
    d.line([(880, 640), (1064, 640)], fill=INK, width=4)
    d.rounded_rectangle([908, 540, 928, 600], radius=3, fill=(160, 170, 178))
    # Лампа.
    d.line([(540, 0), (540, 392)], fill=INK, width=5)
    d.pieslice([470, 360, 610, 500], 0, 180, fill=(255, 196, 70) if lamp else (70, 60, 48), outline=INK)
    if lamp:
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        gd.polygon([(540, 430), (180, 980), (900, 980)], fill=(255, 214, 120, 28))
        im = Image.alpha_composite(im, glow)
    return im


def draw_table(im):
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([50, 1268, 1030, 1620], radius=36, fill=(150, 96, 52), outline=INK, width=6)
    d.rounded_rectangle([80, 1290, 1000, 1388], radius=22, fill=(206, 150, 96))
    d.line([(80, 1340), (1000, 1340)], fill=(180, 124, 72), width=3)


def eye_icon(d, cx, cy, r, dim=False):
    d.ellipse([cx - r, cy - r * 0.62, cx + r, cy + r * 0.62], fill=(255, 255, 255), outline=INK, width=8)
    col = (90, 100, 110) if dim else (64, 150, 170)
    d.ellipse([cx - r * 0.42, cy - r * 0.42, cx + r * 0.42, cy + r * 0.42], fill=col, outline=INK, width=5)
    d.ellipse([cx - r * 0.16, cy - r * 0.16, cx + r * 0.16, cy + r * 0.16], fill=INK)
    d.ellipse([cx - r * 0.28, cy - r * 0.28, cx + r * 0.02, cy - r * 0.02], fill=(255, 255, 255))


def ban(d, cx, cy, r):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(214, 36, 48), width=16)
    d.line([(cx - r * 0.7, cy - r * 0.7), (cx + r * 0.7, cy + r * 0.7)], fill=(214, 36, 48), width=16)


def paint_shock(t, dur):
    im = kitchen(lamp=False)
    paste(im, carrot_sprite(560), 300, 760)
    d = ImageDraw.Draw(im)
    eye_icon(d, 730, 640, 150)
    ban(d, 730, 640, 188)
    return im


def paint_radar_reveal(t, dur):
    im = grad((W, H), (10, 16, 40), (24, 32, 58)).convert("RGBA")
    d = ImageDraw.Draw(im)
    _sky_stars(d, 30, 40, 700, 2)
    d.ellipse([760, 90, 980, 310], fill=(255, 236, 190))
    # Тарелка радара.
    open_k = min(1, t / max(0.4, dur * 0.45))
    d.polygon([(180, 980), (540, 860), (900, 980), (540, 1040)], fill=(70, 78, 90), outline=INK)
    d.rectangle([500, 1040, 580, 1320], fill=(90, 98, 112), outline=INK, width=4)
    # Луч.
    beam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(beam)
    reach = 200 + 700 * open_k
    bd.polygon([(540, 900), (540 - reach * 0.7, 900 - reach), (540 + reach * 0.15, 900 - reach)], fill=(80, 255, 160, 70))
    im = Image.alpha_composite(im, beam)
    # Морковь уезжает вбок.
    paste(im, carrot_sprite(380), 540 + int(360 * open_k), 620)
    return im


def paint_grandma(t, dur):
    im = kitchen(lamp=True)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([80, 430, 280, 700], radius=8, fill=(92, 60, 40), outline=INK, width=6)
    d.rectangle([100, 450, 260, 640], fill=(255, 236, 214))
    # Силуэт, не портрет живого человека.
    d.ellipse([145, 490, 215, 560], fill=(232, 190, 160), outline=INK, width=3)
    d.chord([130, 470, 230, 540], 200, 340, fill=(210, 170, 120), outline=INK)
    d.arc([150, 575, 210, 620], 20, 160, fill=INK, width=3)
    f = font(28)
    d.text((180, 652), "бабушка", font=f, fill=INK, anchor="mt")
    return im


def paint_dark_bite(t, dur):
    im = kitchen(lamp=False)
    return im


def _plane(d, x, y, s=1.0):
    d.polygon(
        [
            (x, y + 12 * s),
            (x + 36 * s, y),
            (x + 210 * s, y),
            (x + 246 * s, y + 16 * s),
            (x + 190 * s, y + 30 * s),
            (x + 36 * s, y + 26 * s),
        ],
        fill=(214, 220, 230),
        outline=INK,
    )
    d.polygon(
        [(x + 90 * s, y + 6 * s), (x + 170 * s, y - 48 * s), (x + 188 * s, y + 10 * s)],
        fill=(170, 180, 196),
        outline=INK,
    )
    d.polygon(
        [(x + 18 * s, y), (x + 6 * s, y - 40 * s), (x + 52 * s, y + 4 * s)],
        fill=(170, 180, 196),
        outline=INK,
    )


def paint_raid(t, dur, locked=False):
    im = grad((W, H), (8, 12, 34), (22, 30, 58)).convert("RGBA")
    d = ImageDraw.Draw(im)
    _sky_stars(d, 36, 30, 900, 3)
    d.ellipse([800, 80, 980, 260], fill=(255, 236, 186))
    # Город.
    rng = random.Random(3)
    x = 0
    d.rectangle([0, 1280, W, H], fill=(14, 16, 28))
    while x < W:
        bw = rng.randint(70, 150)
        bh = rng.randint(120, 360)
        d.rectangle([x, 1280 - bh, x + bw, 1280], fill=(28, 32, 48), outline=(12, 14, 24))
        for wy in range(1280 - bh + 18, 1264, 32):
            for wx in range(x + 14, x + bw - 16, 24):
                if rng.random() > 0.45:
                    d.rectangle([wx, wy, wx + 10, wy + 16], fill=(255, 206, 110))
        x += bw + 6
    px = 160 + int((t * 140) % 760)
    py = 300 + int(18 * math.sin(t * 2))
    # Прожекторы.
    beams = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(beams)
    ang = 0.4 * math.sin(t * 1.3)
    if locked:
        ang = -0.15
        px, py = 620, 340
    x0, y0 = 540, 1280
    x1 = x0 + math.sin(ang) * 980
    y1 = y0 - math.cos(ang) * 980
    bd.polygon([(x0 - 40, y0), (x1 - 70, y1), (x1 + 70, y1), (x0 + 40, y0)], fill=(255, 236, 150, 120))
    im = Image.alpha_composite(im, beams)
    d = ImageDraw.Draw(im)
    _plane(d, px, py, 1.15)
    if locked:
        d.ellipse([px + 40, py - 50, px + 200, py + 90], outline=(255, 80, 80), width=6)
    f = font(34)
    d.text((W // 2, 150), "1940", font=f, fill=(255, 255, 255), anchor="mt", stroke_width=4, stroke_fill=INK)
    return im


def paint_scope(t, dur):
    im = grad((W, H), (6, 16, 12), (4, 10, 8)).convert("RGBA")
    d = ImageDraw.Draw(im)
    cx, cy, r = 540, 760, 390
    d.ellipse([cx - r - 46, cy - r - 46, cx + r + 46, cy + r + 46], fill=(36, 42, 38), outline=INK, width=8)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(3, 24, 14))
    for k in (1, 2, 3):
        rr = r * k / 3
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=(24, 110, 60), width=3)
    d.line([(cx - r, cy), (cx + r, cy)], fill=(24, 110, 60), width=3)
    d.line([(cx, cy - r), (cx, cy + r)], fill=(24, 110, 60), width=3)
    sweep = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sweep)
    deg = (t * 140) % 360
    sd.pieslice([cx - r, cy - r, cx + r, cy + r], deg - 26, deg, fill=(70, 255, 150, 110))
    im = Image.alpha_composite(im, sweep)
    d = ImageDraw.Draw(im)
    pulse = 0.65 + 0.35 * math.sin(t * 9)
    bx, by = cx + 150, cy - 90
    br = int(18 * pulse)
    d.ellipse([bx - br, by - br, bx + br, by + br], fill=(190, 255, 190))
    f = font(40)
    d.text((cx, 250), "РАДАР НА БОРТУ", font=f, fill=(170, 255, 190), anchor="mt", stroke_width=4, stroke_fill=(0, 0, 0))
    d.text((cx, cy + r + 70), "не морковь", font=font(36), fill=(255, 220, 140), anchor="mt", stroke_width=4, stroke_fill=(0, 0, 0))
    return im


def paint_catseyes(t, dur):
    im = grad((W, H), (28, 20, 48), (48, 28, 36)).convert("RGBA")
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([120, 300, 960, 1180], radius=28, fill=(250, 236, 206), outline=INK, width=8)
    d.text((540, 360), "КОШАЧЬИ ГЛАЗА", font=font(52), fill=INK, anchor="mt")
    # Стилизованные глаза, не лицо реального человека.
    for dx in (-180, 180):
        eye_icon(d, 540 + dx, 620, 120)
    d.polygon([(540, 820), (470, 980), (610, 980)], fill=CARROT, outline=INK)
    d.ellipse([500, 760, 580, 830], fill=LEAF, outline=INK)
    d.text((540, 1040), "КАННИНГЕМ", font=font(40), fill=INK, anchor="mt")
    d.text((540, 1100), "прозвище, не диета", font=font(30), fill=(120, 60, 40), anchor="mt")
    return im


def paint_papers(t, dur):
    im = grad((W, H), (232, 214, 184), (206, 184, 156)).convert("RGBA")
    d = ImageDraw.Draw(im)
    rng = random.Random(1)
    for i, (x, y, rot) in enumerate(((160, 420, -8), (300, 560, 4), (180, 720, -2))):
        paper = Image.new("RGBA", (640, 360), (0, 0, 0, 0))
        pd = ImageDraw.Draw(paper)
        pd.rounded_rectangle([0, 0, 639, 359], radius=8, fill=(248, 244, 232), outline=INK, width=5)
        pd.rectangle([24, 24, 616, 70], fill=(40, 40, 40))
        pd.text((40, 90), "МОРКОВЬ И ЗОРКИЕ ГЛАЗА", font=font(32), fill=INK)
        for yy in range(160, 320, 28):
            pd.line([(36, yy), (580 - rng.randint(0, 80), yy)], fill=(180, 170, 150), width=6)
        paper = paper.rotate(rot, expand=True, resample=Image.Resampling.BICUBIC)
        im.alpha_composite(paper, (x, y))
    return im


def paint_pile(t, dur):
    im = grad((W, H), (255, 228, 196), (186, 140, 90)).convert("RGBA")
    # Гора моркови — процесс «ест гору».
    n = 7 + int(4 * min(1, t / max(dur, 0.2)))
    for i in range(n):
        paste(im, carrot_sprite(280 + (i % 3) * 40), 220 + (i % 5) * 140, 980 - (i % 4) * 70)
    d = ImageDraw.Draw(im)
    d.text((540, 280), "«ГОРА МОРКОВИ»", font=font(52), fill=(255, 255, 255), anchor="mt", stroke_width=6, stroke_fill=INK)
    return im


def paint_pilot(t, dur):
    im = grad((W, H), (20, 28, 48), (36, 32, 44)).convert("RGBA")
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([180, 340, 900, 1100], radius=24, fill=(48, 56, 72), outline=INK, width=6)
    # Шлем — значок лётчика, не портрет.
    d.ellipse([390, 460, 690, 760], fill=(70, 78, 90), outline=INK, width=8)
    d.rounded_rectangle([430, 560, 650, 700], radius=20, fill=(20, 24, 32))
    d.rectangle([470, 600, 610, 660], fill=(120, 220, 160))
    d.text((540, 800), "КАННИНГЕМ", font=font(44), fill=(255, 236, 190), anchor="mt")
    d.text((540, 880), "«так прятали радар»", font=font(36), fill=(255, 255, 255), anchor="mt")
    # Маленькая тарелка.
    d.polygon([(250, 1000), (330, 960), (410, 1000)], fill=(140, 220, 160), outline=INK)
    return im


def paint_garden(t, dur):
    im = grad((W, H), (140, 200, 255), (186, 224, 255)).convert("RGBA")
    d = ImageDraw.Draw(im)
    d.ellipse([760, 80, 980, 300], fill=(255, 214, 80), outline=INK, width=6)
    d.ellipse([120, 160, 340, 280], fill=(255, 255, 255))
    d.ellipse([180, 140, 400, 260], fill=(255, 255, 255))
    d.rectangle([0, 1180, W, H], fill=(88, 150, 72))
    for i, y in enumerate((1240, 1420, 1600)):
        d.rounded_rectangle([40, y, 1040, y + 90], radius=16, fill=(120, 78, 42), outline=INK, width=4)
        for x in range(80, 1000, 80):
            if (i + x) % 160 == 80:
                paste(im, carrot_sprite(150), x, y - 10)
    d = ImageDraw.Draw(im)
    d.text((540, 200), "ГРЯДКИ", font=font(64), fill=INK, anchor="mt", stroke_width=2, stroke_fill=(255, 255, 255))
    return im


def paint_poster(t, dur):
    im = kitchen(lamp=True)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([140, 400, 940, 1120], radius=12, fill=(255, 244, 220), outline=INK, width=8)
    d.rectangle([140, 400, 940, 470], fill=(196, 40, 48))
    d.text((540, 414), "МИНИСТЕРСТВО ЕДЫ", font=font(32), fill=(255, 255, 255), anchor="mt")
    d.text((540, 520), "МОРКОВЬ", font=font(78), fill=INK, anchor="mt")
    d.text((540, 630), "для зорких глаз", font=font(44), fill=(160, 48, 36), anchor="mt")
    eye_icon(d, 360, 860, 90)
    # Морковку дорисуем спрайтом поверх.
    paste(im, carrot_sprite(280), 700, 900)
    return im


def paint_shelves(t, dur, radar=False):
    im = grad((W, H), (210, 186, 156), (160, 130, 100)).convert("RGBA")
    d = ImageDraw.Draw(im)
    d.rectangle([40, 240, 1040, 1280], fill=(120, 78, 48), outline=INK, width=8)
    for y in (420, 680, 960):
        d.rectangle([70, y, 1010, y + 26], fill=(168, 116, 70), outline=INK, width=3)
    d.text((540, 280), "ПОЛКИ ПУСТЫЕ", font=font(48), fill=(255, 244, 220), anchor="mt")
    paste(im, carrot_sprite(180), 200, 390)
    if radar:
        d = ImageDraw.Draw(im)
        d.pieslice([760, 700, 1040, 1040], 200, 340, fill=(48, 56, 64), outline=INK, width=6)
        d.polygon([(860, 860), (980, 620), (1040, 700)], fill=(90, 255, 160, 180))
        d.text((820, 1080), "радар", font=font(36), fill=(220, 255, 220), anchor="mt", stroke_width=4, stroke_fill=(0, 0, 0))
    return im


def paint_beta(t, dur):
    im = grad((W, H), (255, 236, 214), (255, 210, 170)).convert("RGBA")
    d = ImageDraw.Draw(im)
    cx, cy, r = 540, 780, 280
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=CARROT, outline=INK, width=8)
    d.ellipse([cx - r + 50, cy - r + 40, cx + r - 50, cy + r - 70], fill=(255, 154, 64), outline=(214, 90, 20), width=4)
    d.ellipse([cx - 70, cy - 50, cx + 70, cy + 90], fill=(255, 196, 90), outline=INK, width=4)
    # Кристаллик «бета».
    appear = min(1, t / 0.4)
    d.text((cx, cy - 10), "β", font=font(int(40 + 80 * appear)), fill=INK, anchor="mm")
    d.text((540, 280), "БЕТА-КАРОТИН", font=font(58), fill=INK, anchor="mt")
    d.text((540, 1180), "внутри моркови", font=font(36), fill=(120, 60, 30), anchor="mt")
    return im


def paint_vitamin(t, dur):
    im = grad((W, H), (255, 244, 230), (232, 216, 196)).convert("RGBA")
    d = ImageDraw.Draw(im)
    d.text((540, 240), "ТЕЛО ДЕЛАЕТ ВИТАМИН А", font=font(40), fill=INK, anchor="mt")
    paste(im, carrot_sprite(360), 220, 780)
    # Стрелка растёт.
    grow = min(1, t / max(0.5, dur * 0.55))
    x2 = 300 + int(420 * grow)
    d.line([(320, 760), (x2, 760)], fill=INK, width=10)
    if grow > 0.7:
        d.polygon([(x2, 760), (x2 - 28, 740), (x2 - 28, 780)], fill=INK)
    d.ellipse([700, 560, 980, 840], fill=(255, 214, 90), outline=INK, width=8)
    d.text((840, 680), "А", font=font(120), fill=INK, anchor="mm")
    d.text((540, 1180), "только если его не хватает", font=font(34), fill=(120, 60, 30), anchor="mt")
    return im


def _side_eye(d, dim=False):
    d.ellipse([180, 520, 900, 980], fill=(255, 255, 255), outline=INK, width=8)
    d.pieslice([150, 560, 360, 940], 270, 90, fill=(186, 220, 230), outline=INK)
    d.ellipse([300, 650, 460, 850], fill=(210, 230, 240), outline=INK, width=6)
    col = (150, 150, 156) if dim else (255, 120, 110)
    d.chord([520, 560, 900, 960], 270, 90, fill=col, outline=INK, width=6)
    if not dim:
        d.line([(80, 640), (300, 700)], fill=(255, 214, 80), width=8)
        d.line([(80, 860), (300, 800)], fill=(255, 214, 80), width=8)
        d.line([(80, 750), (300, 750)], fill=(255, 236, 150), width=8)
    d.text((760, 760), "сетчатка", font=font(32), fill=INK, anchor="mm")


def paint_retina(t, dur):
    im = grad((W, H), (230, 242, 255), (255, 236, 220)).convert("RGBA")
    d = ImageDraw.Draw(im)
    d.text((540, 240), "СЕТЧАТКА ЛОВИТ СВЕТ", font=font(44), fill=INK, anchor="mt")
    _side_eye(d, dim=False)
    return im


def paint_dim(t, dur):
    im = grad((W, H), (40, 48, 70), (24, 26, 40)).convert("RGBA")
    d = ImageDraw.Draw(im)
    d.text((540, 240), "МАЛО ВИТАМИНА А", font=font(44), fill=(255, 255, 255), anchor="mt", stroke_width=4, stroke_fill=INK)
    _side_eye(d, dim=True)
    d.text((540, 1120), "ночью видно хуже", font=font(36), fill=(255, 220, 150), anchor="mt", stroke_width=4, stroke_fill=(0, 0, 0))
    return im


def paint_nosuper(t, dur):
    im = grad((W, H), (255, 236, 214), (255, 214, 180)).convert("RGBA")
    d = ImageDraw.Draw(im)
    d.text((540, 230), "СВЕРХЗРЕНИЯ НЕТ", font=font(52), fill=INK, anchor="mt")
    eye_icon(d, 400, 640, 140)
    paste(im, carrot_sprite(340), 760, 700)
    ban(d, 760, 560, 70)
    # Линейка «норма», не шкала супергероя.
    d.rounded_rectangle([180, 1040, 900, 1120], radius=20, fill=(255, 255, 255), outline=INK, width=5)
    d.rounded_rectangle([196, 1056, 520, 1104], radius=14, fill=(80, 170, 110))
    d.text((540, 1180), "норма и не выше", font=font(34), fill=INK, anchor="mt")
    return im


def paint_palms(t, dur):
    im = kitchen(lamp=True)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([700, 400, 1000, 760], radius=16, fill=(210, 230, 235), outline=INK, width=6)
    d.ellipse([790, 480, 910, 600], fill=(255, 186, 120), outline=INK, width=4)
    return im


def paint_skin(t, dur, label=False):
    im = grad((W, H), (255, 228, 210), (255, 196, 150)).convert("RGBA")
    d = ImageDraw.Draw(im)
    k = min(1, t / max(0.35, dur * 0.5))
    col = tuple(int((255, 220, 190)[i] * (1 - k) + (255, 140, 40)[i] * k) for i in range(3))
    d.ellipse([280, 420, 800, 1040], fill=col, outline=INK, width=8)
    d.ellipse([390, 560, 470, 640], fill=(255, 255, 255), outline=INK, width=4)
    d.ellipse([560, 560, 640, 640], fill=(255, 255, 255), outline=INK, width=4)
    d.arc([430, 760, 650, 900], 20, 160, fill=INK, width=6)
    d.text((540, 260), "КОЖА", font=font(48), fill=INK, anchor="mt")
    if label or k > 0.55:
        d.rounded_rectangle([230, 1120, 850, 1240], radius=18, fill=(255, 244, 220), outline=INK, width=5)
        d.text((540, 1152), "КАРОТИНЕМИЯ", font=font(40), fill=(180, 60, 20), anchor="mt")
    return im


def paint_eyesame(t, dur):
    im = kitchen(lamp=True)
    d = ImageDraw.Draw(im)
    d.text((540, 400), "ГЛАЗА ТЕ ЖЕ", font=font(48), fill=INK, anchor="mt", stroke_width=2, stroke_fill=(255, 255, 255))
    eye_icon(d, 540, 620, 80)
    return im


def paint_switch(t, dur):
    on = t < dur * 0.42
    im = kitchen(lamp=on)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([860, 980, 1000, 1220], radius=18, fill=(245, 240, 230), outline=INK, width=6)
    lever_y = 1040 if on else 1140
    d.rounded_rectangle([900, lever_y, 960, lever_y + 70], radius=10, fill=(40, 40, 40))
    d.text((780, 1080), "щёлк" if not on else "свет", font=font(36), fill=INK, anchor="rm")
    paste(im, carrot_sprite(180), 150, 900)
    return im


def paint_dark(t, dur):
    im = kitchen(lamp=False)
    d = ImageDraw.Draw(im)
    # Искорка, которая гаснет: сверхзрения не случилось.
    a = int(180 * max(0, 1 - t / max(dur, 0.3)))
    if a > 0:
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        gd.ellipse([470, 860, 610, 1000], fill=(255, 240, 180, a))
        im = Image.alpha_composite(im, glow)
    return im


def paint_send(t, dur):
    im = grad((W, H), (255, 214, 150), (255, 150, 120)).convert("RGBA")
    d = ImageDraw.Draw(im)
    d.text((540, 240), "ОТПРАВЬ", font=font(80), fill=(255, 255, 255), anchor="mt", stroke_width=8, stroke_fill=INK)
    # Бумажный самолётик.
    d.polygon([(240, 520), (760, 640), (280, 700)], fill=(255, 255, 255), outline=INK)
    d.line([(300, 600), (620, 640)], fill=INK, width=4)
    return im


def paint_car(t, dur):
    im = grad((W, H), (8, 12, 36), (20, 24, 48)).convert("RGBA")
    d = ImageDraw.Draw(im)
    _sky_stars(d, 20, 40, 500, 6)
    d.polygon([(0, 980), (1080, 980), (1080, 1920), (0, 1920)], fill=(24, 26, 32))
    d.polygon([(200, 980), (880, 980), (1080, 1500), (0, 1500)], fill=(36, 38, 46))
    for i in range(8):
        y = 1040 + i * 70
        x = 540 - i * 8
        if int(t * 8 + i) % 2 == 0:
            d.rectangle([x - 30, y, x + 30, y + 28], fill=(255, 214, 80))
    # Машина.
    d.rounded_rectangle([300, 1180, 820, 1360], radius=30, fill=(200, 40, 48), outline=INK, width=6)
    d.polygon([(380, 1180), (460, 1060), (680, 1060), (760, 1180)], fill=(170, 210, 220), outline=INK)
    d.ellipse([360, 1320, 470, 1430], fill=(30, 30, 30), outline=INK, width=5)
    d.ellipse([650, 1320, 760, 1430], fill=(30, 30, 30), outline=INK, width=5)
    d.ellipse([330, 1240, 390, 1300], fill=(255, 240, 160))
    paste(im, carrot_sprite(160), 600, 1140)
    d = ImageDraw.Draw(im)
    d.text((540, 220), "ЗА РУЛЁМ НОЧЬЮ", font=font(48), fill=(255, 255, 255), anchor="mt", stroke_width=5, stroke_fill=INK)
    return im


PAINT = {
    "shock": paint_shock,
    "radar_reveal": paint_radar_reveal,
    "grandma": paint_grandma,
    "dark_bite": paint_dark_bite,
    "raid": lambda t, dur: paint_raid(t, dur, False),
    "lock": lambda t, dur: paint_raid(t, dur, True),
    "scope": paint_scope,
    "catseyes": paint_catseyes,
    "papers": paint_papers,
    "pile": paint_pile,
    "pilot": paint_pilot,
    "garden": paint_garden,
    "poster": paint_poster,
    "shelves": lambda t, dur: paint_shelves(t, dur, False),
    "curtain": lambda t, dur: paint_shelves(t, dur, True),
    "beta": paint_beta,
    "vitamin": paint_vitamin,
    "retina": paint_retina,
    "dim": paint_dim,
    "nosuper": paint_nosuper,
    "palms": paint_palms,
    "skin": lambda t, dur: paint_skin(t, dur, False),
    "label": lambda t, dur: paint_skin(t, dur, True),
    "eyesame": paint_eyesame,
    "switch": paint_switch,
    "dark": paint_dark,
    "send": paint_send,
    "car": paint_car,
}
