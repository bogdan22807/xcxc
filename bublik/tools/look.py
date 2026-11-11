"""Свет, палитра, шрифты, подписи."""

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920

INK = (42, 26, 18)
DOUGH = (232, 170, 96)
DOUGH_HI = (255, 214, 150)
SEED = (246, 230, 196)
ICING = (255, 96, 156)
CARROT = (242, 122, 32)
LEAF = (58, 150, 62)
CREAM = (255, 228, 150)
PINK = (255, 146, 188)

FONT_BOLD = "/usr/share/fonts/truetype/macos/Inter-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/macos/Inter-Regular.ttf"
_fonts = {}


def font(size, bold=True):
    key = (size, bold)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)
    return _fonts[key]


def grad(size, top, bot):
    h = size[1]
    col = Image.new("RGB", (1, h))
    px = col.load()
    for y in range(h):
        t = y / (h - 1)
        px[0, y] = tuple(int(top[i] * (1 - t) + bot[i] * t) for i in range(3))
    return col.resize(size, Image.Resampling.NEAREST)


def paste(base, spr, x, y):
    """Вклеить RGBA-спрайт центром в (x, y)."""
    sw, sh = spr.size
    left, top = int(round(x - sw / 2)), int(round(y - sh / 2))
    if left >= base.width or top >= base.height or left + sw <= 0 or top + sh <= 0:
        return
    src = spr
    if left < 0 or top < 0 or left + sw > base.width or top + sh > base.height:
        cx0 = max(0, -left)
        cy0 = max(0, -top)
        cx1 = sw - max(0, left + sw - base.width)
        cy1 = sh - max(0, top + sh - base.height)
        src = spr.crop((cx0, cy0, cx1, cy1))
        left, top = max(0, left), max(0, top)
    base.alpha_composite(src, (left, top))


def fit_font(text, max_w, start, bold=True):
    size = start
    while size > 28:
        f = font(size, bold)
        if f.getlength(text) <= max_w:
            return f
        size -= 2
    return font(28, bold)


def draw_center(d, text, y, fnt, fill, stroke=INK, sw=8, x=W // 2):
    d.text((x, y), text, font=fnt, fill=fill, anchor="mt", stroke_width=sw, stroke_fill=stroke)


def wrap(text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = w if not cur else cur + " " + w
        if fnt.getlength(trial) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines or [text]


def _wrap_words(words, fnt, max_w):
    lines, cur, idx = [], [], []
    for i, w in enumerate(words):
        trial = " ".join(cur + [w])
        if cur and fnt.getlength(trial) > max_w:
            lines.append((cur, idx))
            cur, idx = [w], [i]
        else:
            cur.append(w)
            idx.append(i)
    if cur:
        lines.append((cur, idx))
    return lines


def caption_block(im, text, speaker, y=1600, active=None):
    """Чистые субтитры: обводка, цвет по говорящему, без плашки."""
    fill = CREAM if speaker == "bublik" else PINK
    hi = (255, 255, 255)
    fnt = font(58)
    words = text.split()
    lines = _wrap_words(words, fnt, 940)
    while len(lines) > 2 and fnt.size > 40:
        fnt = font(fnt.size - 4)
        lines = _wrap_words(words, fnt, 940)
    d = ImageDraw.Draw(im)
    lh = int(fnt.size * 1.16)
    block_h = lh * len(lines)
    top = y - block_h // 2
    gap = 14
    for li, (line_words, indexes) in enumerate(lines):
        widths = [fnt.getlength(w) for w in line_words]
        total = sum(widths) + gap * (len(line_words) - 1)
        x = (W - total) / 2
        yy = top + li * lh
        for w, wid, ii in zip(line_words, widths, indexes):
            d.text(
                (x, yy),
                w,
                font=fnt,
                fill=hi if active == ii else fill,
                anchor="lt",
                stroke_width=8,
                stroke_fill=(0, 0, 0),
            )
            x += wid + gap


def hook_block(im, text):
    d = ImageDraw.Draw(im)
    lines = text.split("\n")
    y = 168
    for line in lines:
        fnt = fit_font(line, 980, 86)
        d.text(
            (W // 2, y),
            line,
            font=fnt,
            fill=(255, 255, 255),
            anchor="mt",
            stroke_width=10,
            stroke_fill=(0, 0, 0),
        )
        y += int(fnt.size * 1.12)


def bottom_shade(im):
    shade = Image.new("RGBA", (W, 420), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    for y in range(420):
        a = int(155 * (y / 420) ** 1.35)
        sd.line([(0, y), (W, y)], fill=(0, 0, 0, a))
    im.alpha_composite(shade, (0, H - 420))


def stamp(text, angle=-14, fill=(220, 48, 48)):
    fnt = font(64)
    tmp = Image.new("RGBA", (640, 160), (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    d.text((20, 30), text, font=fnt, fill=fill, stroke_width=6, stroke_fill=(255, 255, 255))
    box = tmp.getbbox()
    tmp = tmp.crop(box)
    return tmp.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)
