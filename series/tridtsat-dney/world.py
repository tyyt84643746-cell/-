"""Общий мир сериала «Тридцать дней»: деревня, двор, дождь, телевизор, пузыри, сепия."""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from chars import *

FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
_F = {}
def font(sz):
    if sz not in _F: _F[sz] = ImageFont.truetype(FB, sz)
    return _F[sz]


def darken(img, k):
    a = np.asarray(img).astype(np.float32); a[..., :3] *= k
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def ctext(img, cx, y, s, f, fill):
    d = ImageDraw.Draw(img); w = d.textlength(s, font=f); d.text((cx - w / 2, y), s, font=f, fill=fill)


def tv(img, x0, y0, x1, y1, t, plate, plate_col=(240, 240, 244), plate_txt=(20, 24, 36), sub=None):
    """Телевизор с ведущим и плашкой."""
    p = P(img, 1.0)
    p.rr(x0 - 18, y0 - 18, x1 + 18, y1 + 18, 22, (12, 14, 20))
    scr = vgrad(x1 - x0, y1 - y0, [(0, (40, 70, 130)), (1, (20, 36, 76))])
    sp = P(scr, 1.0); w, h = x1 - x0, y1 - y0
    for k in range(6): sp.rect(0, h * 0.2 + k * 30, w, h * 0.2 + k * 30 + 2, (60, 90, 150))
    cx = w / 2; hb = h * 0.84
    sp.rr(cx - w * 0.2, hb - h * 0.36, cx + w * 0.2, hb + 30, 40, (22, 28, 46))     # ведущий
    sp.el(cx - w * 0.09, hb - h * 0.62, cx + w * 0.09, hb - h * 0.34, (210, 176, 150))
    sp.chord(cx - w * 0.095, hb - h * 0.64, cx + w * 0.095, hb - h * 0.46, 180, 360, (50, 40, 34))
    sp.rr(cx - 10, hb - h * 0.34, cx + 10, hb - h * 0.16, 4, (150, 40, 50))
    mouth = abs(math.sin(t * 11)) * 6
    sp.el(cx - 10, hb - h * 0.42, cx + 10, hb - h * 0.42 + 4 + mouth, (90, 40, 40))
    fs = int(h * 0.11)
    tw = ImageDraw.Draw(scr).textlength(plate, font=font(fs))
    sp.rr(w * 0.06, h * 0.72, w * 0.06 + tw + 50, h * 0.72 + fs * 1.5, 6, plate_col)
    sp.text(w * 0.06 + 25, h * 0.72 + fs * 0.2, plate, font(fs), plate_txt)
    if sub:
        sp.rect(0, h * 0.72 + fs * 1.5, w, h * 0.72 + fs * 2.4, (14, 18, 30))
        sp.text(w * 0.06 + 25, h * 0.72 + fs * 1.58, sub, font(int(fs * 0.62)), (220, 224, 236))
    if (t * 30) % 7 < 1: sp.rect(0, 0, w, h, (255, 255, 255, 0))
    comp(img, scr, x0, y0)
    glow(img, (x0 + x1) / 2, (y0 + y1) / 2, max(w, h) * 0.9, (110, 150, 230), 0.25, 1.6)


def laugh_face(p, x, y, r):
    p.circ(x, y, r, (246, 200, 60))
    p.arc(x - r * 0.55, y - r * 0.45, x - r * 0.1, y - r * 0.05, 200, 340, EYE, 4)
    p.arc(x + r * 0.1, y - r * 0.45, x + r * 0.55, y - r * 0.05, 200, 340, EYE, 4)
    p.chord(x - r * 0.55, y - r * 0.2, x + r * 0.55, y + r * 0.65, 0, 180, (110, 40, 40))
    p.circ(x - r * 0.75, y - r * 0.05, r * 0.16, (120, 190, 240)); p.circ(x + r * 0.75, y - r * 0.05, r * 0.16, (120, 190, 240))


def bubble(img, x, y, txt, k, face=False):
    if k <= 0: return
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); p = P(ov, 1.0); f = font(40)
    tw = ImageDraw.Draw(ov).textlength(txt, font=f)
    wbox = tw + 60 + (70 if face else 0)
    sc = ease(k); yy = y + 20 * (1 - sc)
    p.rr(x, yy, x + wbox, yy + 84, 30, (238, 242, 250, int(240 * sc)))
    p.poly([(x + 30, yy + 80), (x + 60, yy + 80), (x + 26, yy + 110)], (238, 242, 250, int(240 * sc)))
    p.text(x + 30, yy + 18, txt, f, (30, 36, 52, int(255 * sc)))
    if face: laugh_face(p, x + tw + 70, yy + 42, 26)
    img.alpha_composite(ov)


class Village:
    def __init__(s, dusk=0.0):
        s.sky = vgrad(W, H, [(0, mixc((64, 80, 112), (16, 22, 44), dusk)), (0.55, mixc((120, 132, 160), (40, 46, 74), dusk)), (1, (200, 208, 224))])
        rnd = random.Random(41)
        def forest(p):
            for k in range(36):
                x = k * 34 + rnd.uniform(-10, 10); h = rnd.uniform(180, 320); base = 1000
                p.poly([(x - 60, base), (x + 60, base), (x, base - h)], mixc((40, 56, 70), (20, 28, 44), dusk))
            p.rect(0, 990, W, H, (214, 222, 236))
        s.sky.alpha_composite(layer(W, H, forest))
        s.dusk = dusk

    def house(s, p, x, y, sc=1.0, lit=True):
        """Бревенчатый дом: x — левый край, y — земля."""
        w, h = 520 * sc, 330 * sc
        p.rect(x, y - h, x + w, y, (104, 74, 54))
        for k in range(1, 9): p.line([(x, y - h + k * h / 9), (x + w, y - h + k * h / 9)], (84, 58, 42), 5 * sc, round_caps=False)
        p.poly([(x - 30 * sc, y - h), (x + w + 30 * sc, y - h), (x + w / 2, y - h - 220 * sc)], (70, 74, 90))
        p.poly([(x - 30 * sc, y - h), (x + w + 30 * sc, y - h), (x + w + 22 * sc, y - h - 12 * sc), (x - 22 * sc, y - h - 12 * sc)], SNOW)
        p.poly([(x - 10 * sc, y - h - 6 * sc), (x + w / 2, y - h - 210 * sc), (x + w / 2 - 40 * sc, y - h - 190 * sc)], SNOW)
        p.rect(x + w * 0.7, y - h - 200 * sc, x + w * 0.7 + 40 * sc, y - h - 60 * sc, (90, 66, 56))
        for wx in (x + 70 * sc, x + 330 * sc):
            p.rr(wx, y - h + 90 * sc, wx + 110 * sc, y - h + 220 * sc, 6, (255, 196, 110) if lit else (30, 34, 50))
            p.rr(wx - 10 * sc, y - h + 80 * sc, wx + 120 * sc, y - h + 230 * sc, 8, None, (236, 232, 220), 8 * sc)
        p.rr(x + w * 0.42, y - h + 60 * sc, x + w * 0.58, y, 6, (70, 50, 40))
        p.rect(x + w * 0.36, y - 30 * sc, x + w * 0.64, y, (96, 80, 70))
        return (x + w * 0.7 + 20 * sc, y - h - 200 * sc)

    def fence(s, p, y, x0=0, x1=W):
        p.rect(x0, y - 120, x1, y - 106, (110, 86, 64)); p.rect(x0, y - 60, x1, y - 46, (110, 86, 64))
        rnd = random.Random(3)
        for x in range(int(x0) + 10, int(x1), 46):
            tilt = rnd.uniform(-8, 8)
            p.poly([(x, y), (x + 30, y), (x + 30 + tilt, y - 170), (x + 15 + tilt, y - 190), (x + tilt, y - 170)], (124, 98, 72))
            p.circ(x + 15 + tilt, y - 186, 12, SNOW)


def smoke(img, x, y, t):
    for k in range(6):
        u = ((t * 0.25 + k / 6) % 1.0)
        glow(img, x + 40 * u + 10 * math.sin(t + k), y - 280 * u, 30 + 70 * u, (220, 226, 236), 0.35 * (1 - u), 1.3)


class Yard:
    def __init__(s, dusk=0.2):
        v = Village(dusk); s.v = v
        s.bg = v.sky.copy()
        def l(p):
            p.rect(0, 1150, W, H, (214, 222, 236))
            v.house(p, 620, 1050, 0.75, lit=True)
            v.fence(p, 1160, -40, W + 40)
            p.rr(-60, 840, 360, 1210, 8, (90, 66, 50))                                       # стена бани
            for k in range(1, 6): p.line([(-60, 840 + k * 62), (360, 840 + k * 62)], (74, 54, 40), 5, round_caps=False)
        s.bg.alpha_composite(layer(W, H, l))

    def pit(s, img, water=0.0, t=0.0):
        p = P(img, 1.0)
        p.el(160, 1440, 960, 1720, (66, 50, 42))
        p.el(190, 1460, 930, 1700, (36, 28, 26))
        if water > 0:
            p.el(200 + 20 * (1 - water), 1480, 920 - 20 * (1 - water), 1690, (60, 76, 96))
            for k in range(5):
                u = ((t * 0.7 + k / 5) % 1.0); cx = 300 + (k * 137) % 500; cy = 1560 + (k * 41) % 90
                p.el(cx - 60 * u, cy - 14 * u, cx + 60 * u, cy + 14 * u, None, (120, 140, 166, int(200 * (1 - u))), 3)
        p.el(840, 1360, 1120, 1560, (92, 72, 58)); p.el(880, 1380, 1080, 1480, (110, 88, 70))      # куча земли


def box(p, x, y, w, h, label, col=(150, 116, 80)):
    p.rr(x, y - h, x + w, y, 8, col); p.rect(x, y - h, x + w, y - h + 16, mixc(col, (0, 0, 0), 0.2))
    p.rr(x + w / 2 - 14, y - h, x + w / 2 + 14, y - h * 0.4, 2, mixc(col, (255, 255, 255), 0.2))
    if label: p.text(x + 18, y - h / 2, label, font(30), (40, 30, 24))


class Rain:
    def __init__(s):
        rnd = random.Random(13)
        s.drops = [(rnd.uniform(0, W + 300), rnd.uniform(0, H), rnd.uniform(1400, 2100), rnd.uniform(40, 90)) for _ in range(220)]
    def draw(s, img, t, a=150):
        d = ImageDraw.Draw(img)
        for x, y, v, l in s.drops:
            yy = (y + v * t) % (H + 100) - 50; xx = x - 0.25 * (yy - y) % (W + 300) - 150
            xx = (x - (v * t) * 0.25) % (W + 300) - 150
            d.line([(xx, yy), (xx - l * 0.25, yy + l)], fill=(170, 190, 220, a), width=3)


def sepia(img, amt):
    a = np.asarray(img.convert("RGB")).astype(np.float32)
    g = a @ np.array([0.3, 0.59, 0.11], np.float32)
    s = np.stack([g * 1.08 + 18, g * 0.9 + 8, g * 0.68], -1)
    out = a * (1 - amt) + s * amt
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).convert("RGBA")
