"""Выпуск 15. Кадр = реплика, ключевое слово = действие."""

import math

from PIL import Image, ImageDraw

from chars2 import hand_world, sprite
from hd_room import PAINT, carrot_sprite, draw_table
from look import H, INK, W, font, grad, paste, stamp

# b / p: кто где стоит. table — стол поверх ног. carrot — морковь на столе.
BASE = {
    "shock": dict(b=dict(x=250, y=1360, sc=0.95, pose="shock", expr="shock"),
                  p=dict(x=820, y=1410, sc=0.78, pose="hold", expr="wow")),
    "radar_reveal": dict(b=dict(x=200, y=1500, sc=0.48, pose="point", expr="shock"),
                         p=dict(x=880, y=1520, sc=0.42, pose="idle", expr="wow")),
    "grandma": dict(table=True, carrot=True,
                    b=dict(x=330, y=1100, sc=0.92, pose="talk", expr="normal"),
                    p=dict(x=770, y=1130, sc=0.82, pose="talk", expr="happy")),
    "dark_bite": dict(b=dict(x=240, y=1380, sc=0.72, pose="idle", expr="worry"),
                      p=dict(x=640, y=1320, sc=1.0, pose="hold", expr="squint")),
    "raid": dict(b=dict(x=170, y=1460, sc=0.4, pose="shock", expr="shock"),
                 p=dict(x=910, y=1480, sc=0.36, pose="idle", expr="wow")),
    "lock": dict(b=dict(x=170, y=1460, sc=0.4, pose="point", expr="shock"),
                 p=dict(x=910, y=1480, sc=0.36, pose="idle", expr="wow")),
    "scope": dict(b=dict(x=180, y=1500, sc=0.42, pose="point", expr="normal"),
                  p=dict(x=900, y=1520, sc=0.38, pose="idle", expr="wow")),
    "catseyes": dict(b=dict(x=180, y=1500, sc=0.42, pose="talk", expr="normal"),
                     p=dict(x=900, y=1520, sc=0.38, pose="shock", expr="wow")),
    "papers": dict(b=dict(x=180, y=1520, sc=0.4, pose="talk", expr="normal"),
                   p=dict(x=900, y=1540, sc=0.36, pose="idle", expr="wow")),
    "pile": dict(b=dict(x=200, y=1500, sc=0.42, pose="point", expr="normal"),
                 p=dict(x=880, y=1520, sc=0.4, pose="shock", expr="wow")),
    "pilot": dict(b=dict(x=180, y=1480, sc=0.44, pose="talk", expr="normal"),
                  p=dict(x=900, y=1500, sc=0.38, pose="idle", expr="wow")),
    "garden": dict(b=dict(x=200, y=1080, sc=0.5, pose="point", expr="happy"),
                   p=dict(x=520, y=1120, sc=0.72, pose="talk", expr="happy")),
    "poster": dict(b=dict(x=200, y=1480, sc=0.42, pose="point", expr="normal"),
                   p=dict(x=900, y=1500, sc=0.38, pose="idle", expr="wow")),
    "shelves": dict(b=dict(x=200, y=1420, sc=0.48, pose="talk", expr="worry"),
                    p=dict(x=860, y=1460, sc=0.42, pose="idle", expr="worry")),
    "curtain": dict(b=dict(x=200, y=1420, sc=0.48, pose="point", expr="shock"),
                    p=dict(x=520, y=1460, sc=0.42, pose="shock", expr="shock")),
    "beta": dict(b=dict(x=180, y=1500, sc=0.4, pose="point", expr="normal"),
                 p=dict(x=900, y=1520, sc=0.36, pose="idle", expr="wow")),
    "vitamin": dict(b=dict(x=180, y=1480, sc=0.4, pose="talk", expr="normal"),
                    p=dict(x=900, y=1500, sc=0.36, pose="idle", expr="happy")),
    "retina": dict(b=dict(x=180, y=1500, sc=0.4, pose="point", expr="normal"),
                   p=dict(x=900, y=1520, sc=0.36, pose="idle", expr="wow")),
    "dim": dict(b=dict(x=180, y=1500, sc=0.4, pose="talk", expr="worry"),
                p=dict(x=900, y=1520, sc=0.36, pose="idle", expr="worry")),
    "nosuper": dict(b=dict(x=180, y=1480, sc=0.42, pose="talk", expr="normal"),
                    p=dict(x=900, y=1500, sc=0.38, pose="idle", expr="worry")),
    "palms": dict(b=dict(x=260, y=1280, sc=0.7, pose="shock", expr="wow"),
                  p=dict(x=680, y=1240, sc=1.05, pose="orange", expr="wow")),
    "skin": dict(b=dict(x=180, y=1500, sc=0.4, pose="talk", expr="normal"),
                 p=dict(x=900, y=1520, sc=0.36, pose="orange", expr="worry")),
    "label": dict(b=dict(x=180, y=1500, sc=0.4, pose="point", expr="normal"),
                  p=dict(x=900, y=1520, sc=0.36, pose="orange", expr="worry")),
    "eyesame": dict(table=True, carrot=True,
                    b=dict(x=320, y=1100, sc=0.9, pose="talk", expr="normal"),
                    p=dict(x=780, y=1130, sc=0.8, pose="idle", expr="worry")),
    "switch": dict(b=dict(x=520, y=1320, sc=0.95, pose="point", expr="normal"),
                   p=dict(x=250, y=1380, sc=0.75, pose="hold", expr="wow")),
    "dark": dict(b=dict(x=380, y=1360, sc=0.85, pose="idle", expr="squint"),
                 p=dict(x=720, y=1400, sc=0.75, pose="idle", expr="shut")),
    "send": dict(b=dict(x=420, y=1180, sc=1.05, pose="point", expr="happy"),
                 p=dict(x=860, y=1320, sc=0.62, pose="talk", expr="happy")),
    "car": dict(b=dict(x=160, y=720, sc=0.42, pose="point", expr="normal"),
                p=dict(x=940, y=760, sc=0.36, pose="shock", expr="wow")),
}


def layout(scene, t, dur):
    src = BASE[scene]
    b = dict(src["b"])
    p = dict(src["p"])
    if scene == "garden":
        p["x"] = int(260 + 640 * min(1, t / max(dur, 0.01)))
    if scene == "raid":
        b["x"] = int(150 + 30 * math.sin(t * 3))
    return {
        "b": b,
        "p": p,
        "table": bool(src.get("table")),
        "carrot": bool(src.get("carrot")),
    }


def _punch(im, t):
    if t > 0.35:
        return im
    z = 1.07 - 0.07 * (t / 0.35)
    nw, nh = int(W * z), int(H * z)
    big = im.resize((nw, nh), Image.Resampling.BILINEAR)
    left, top = (nw - W) // 2, (nh - H) // 2
    return big.crop((left, top, left + W, top + H))


def render_frame(scene, t, dur, speaker, mouth_b, mouth_p, blink_b, blink_p, global_t=0):
    painter = PAINT[scene]
    im = painter(t, dur).convert("RGBA")
    lay = layout(scene, t, dur)
    fx = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fx)
    for who, spec, mouth, blink in (
        ("bublik", lay["b"], mouth_b, blink_b),
        ("ponchik", lay["p"], mouth_p, blink_p),
    ):
        sc = spec["sc"] * (1.05 if speaker == who else 0.96)
        bob = math.sin(t * 3.1 + (0 if who == "bublik" else 1.3)) * 6
        if speaker == who:
            bob += math.sin(t * 11) * 3
            col = (255, 200, 90, 46) if who == "bublik" else (255, 120, 170, 46)
            x, y = spec["x"], spec["y"] + bob
            fd.ellipse([x - 190 * sc, y - 180 * sc, x + 190 * sc, y + 200 * sc], fill=col)
        else:
            x, y = spec["x"], spec["y"] + bob
        fd.ellipse([x - 80 * sc, y + 150 * sc, x + 90 * sc, y + 190 * sc], fill=(0, 0, 0, 45))
    im = Image.alpha_composite(im, fx)

    for who, spec, mouth, blink in (
        ("bublik", lay["b"], mouth_b, blink_b),
        ("ponchik", lay["p"], mouth_p, blink_p),
    ):
        sc = spec["sc"] * (1.05 if speaker == who else 0.96)
        bob = math.sin(t * 3.1 + (0 if who == "bublik" else 1.3)) * 6
        if speaker == who:
            bob += math.sin(t * 11) * 3
        img, hands = sprite(who, spec["pose"], spec["expr"], mouth, blink, sc)
        x, y = spec["x"], spec["y"] + bob
        paste(im, img, x, y)
        if spec["pose"] == "hold" and hands and not lay["table"]:
            hx, hy = hand_world(hands[0], x, y, sc)
            veg = carrot_sprite(max(90, int(120 * sc)))
            paste(im, veg, hx - 6, hy - veg.size[1] * 0.28)

    if lay["table"]:
        draw_table(im)
        if lay["carrot"]:
            paste(im, carrot_sprite(150), 540, 1228)
    if scene == "shock":
        paste(im, stamp("МИФ"), 860, 430)
    if scene == "shock" and global_t < 0.4:
        im = _punch(im, global_t)
    return im


def cover():
    im = grad((W, H), (14, 18, 42), (32, 18, 28)).convert("RGBA")
    d = ImageDraw.Draw(im)
    d.ellipse([760, 80, 980, 300], fill=(255, 236, 186))
    paste(im, carrot_sprite(640), 300, 1120)
    from hd_room import ban, eye_icon

    eye_icon(d, 760, 1040, 150)
    ban(d, 760, 1040, 190)
    # Заголовок строго в зоне y 300–680 (сетка 3:4).
    lines = [("МОРКОВЬ", 78, (255, 255, 255)), ("НЕ ВКЛЮЧАЕТ", 64, (255, 214, 90)), ("НОЧНОЕ ЗРЕНИЕ", 60, (255, 255, 255))]
    y = 330
    for text, size, col in lines:
        d.text((W // 2, y), text, font=font(size), fill=col, anchor="mt", stroke_width=8, stroke_fill=(0, 0, 0))
        y += size + 12
    d.text((W // 2, 760), "Зачем британцы кормили", font=font(40), fill=(255, 255, 255), anchor="mt", stroke_width=5, stroke_fill=(0, 0, 0))
    d.text((W // 2, 816), "ею пилотов?", font=font(40), fill=(255, 255, 255), anchor="mt", stroke_width=5, stroke_fill=(0, 0, 0))
    # Герои выглядывают снизу, лента поверх.
    img, _ = sprite("bublik", "shock", "shock", 3, False, 0.7)
    paste(im, img, 260, 1620)
    img, _ = sprite("ponchik", "idle", "wow", 0, False, 0.58)
    paste(im, img, 820, 1660)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 1768, W, 1888], fill=(196, 40, 48))
    d.text((W // 2, 1804), "БУБЛИК ЗНАЕТ  ·  ПРОВЕРЬ ДОМА", font=font(36), fill=(255, 255, 255), anchor="mt")
    return im.convert("RGB")
