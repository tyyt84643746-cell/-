"""Общий мир сериала «Тридцать дней»: деревня, двор, дождь, телевизор, пузыри, сепия."""
import math, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
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


# ---- из серии 2: погреб, тетрадь, люк ----
FH = "/usr/share/fonts/truetype/freefont/FreeSerifBoldItalic.ttf"
_H = {}
def hand(sz):
    if sz not in _H: _H[sz] = ImageFont.truetype(FH if os.path.exists(FH) else FB, sz)
    return _H[sz]
PAPER = (226, 210, 176); INK = (52, 44, 78); RUST = (128, 78, 52)


def fact_card(img, t, t0, sub):
    if t < t0: return
    k = ease((t - t0) / 0.35); f = font(40)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    tw = od.textlength(sub, font=f); x0 = W / 2 - tw / 2 - 34; y0 = 330 - 20 * (1 - k)
    od.rounded_rectangle([x0, y0, x0 + tw + 68, y0 + 84], radius=20, fill=(10, 14, 28, int(220 * k)), outline=(255, 178, 64, int(255 * k)), width=3)
    od.text((x0 + 34, y0 + 18), sub, font=f, fill=(255, 226, 170, int(255 * k)))
    img.alpha_composite(ov)


def hatch(p, cx, cy, s=1.0, open_k=0.0):
    p.rr(cx - 190 * s, cy - 90 * s, cx + 190 * s, cy + 90 * s, 20 * s, (40, 34, 32))
    if open_k < 1:
        yy = cy - 90 * s - 150 * s * open_k
        p.rr(cx - 180 * s, yy + 10 * s, cx + 180 * s, yy + 170 * s * (1 - open_k * 0.6), 16 * s, (92, 96, 108))
        for dx, dy in ((-120, 40), (60, 110), (110, 50), (-40, 120)): p.circ(cx + dx * s, yy + dy * s * (1 - open_k * 0.6), 14 * s, RUST)
        p.el(cx - 36 * s, yy + 60 * s, cx + 36 * s, yy + 110 * s, None, (40, 42, 50), int(10 * s))
        for dx in (-150, 150): p.circ(cx + dx * s, yy + 30 * s, 8 * s, (50, 52, 60))


class Cellar:
    def __init__(s):
        s.bg = vgrad(W, H, [(0, (40, 30, 28)), (1, (24, 18, 20))])
        rnd = random.Random(17)
        def bricks(p):
            for row in range(0, 28):
                y = row * 62; off = 70 if row % 2 else 0
                for x in range(-140 + off, W + 140, 140):
                    c = mixc((98, 58, 46), (70, 44, 38), rnd.random())
                    p.rr(x + 4, y + 4, x + 136, y + 58, 6, c)
            p.rect(0, 1500, W, H, (44, 36, 34))
            for x in range(-200, W, 160): p.line([(x, 1500), (x + 240, H)], (36, 30, 28), 5, round_caps=False)
        s.bg.alpha_composite(layer(W, H, bricks))
        def shelf(p):
            for y in (700, 980, 1260):
                p.rr(560, y, 1060, y + 26, 6, (90, 66, 48))
            p.rect(566, 640, 584, 1500, (74, 54, 40)); p.rect(1036, 640, 1054, 1500, (74, 54, 40))
            cols = [(120, 140, 110), (140, 110, 80), (110, 124, 140), (150, 130, 96)]
            for y in (700, 980, 1260):
                for k in range(5):
                    x = 610 + k * 86; c = cols[(k + y) % 4]
                    p.rr(x, y - 150, x + 66, y, 14, mixc(c, (30, 26, 24), 0.35))
                    p.rr(x + 6, y - 172, x + 60, y - 146, 8, (120, 110, 100))
                    p.rr(x + 10, y - 110, x + 30, y - 30, 6, mixc(c, (255, 255, 255), 0.12))
            for (x, y) in ((560, 640), (1060, 640)):                                # паутина
                for a in range(0, 91, 30):
                    dx = math.cos(math.radians(a)) * 130 * (1 if x < 800 else -1); dy = math.sin(math.radians(a)) * 130
                    p.line([(x, y), (x + dx, y + dy)], (150, 150, 160), 2, round_caps=False)
        s.shelf = layer(W, H, shelf)
        def ladder(p):
            p.line([(170, 240), (130, 1520)], (110, 84, 60), 22, round_caps=False)
            p.line([(390, 240), (430, 1520)], (110, 84, 60), 22, round_caps=False)
            s.steps = []
            for k in range(8):
                y = 380 + k * 150; xl = 170 - 40 * (y - 240) / 1280; xr = 390 + 40 * (y - 240) / 1280
                p.rr(xl - 6, y, xr + 6, y + 24, 6, (128, 98, 70)); s.steps.append((xl, y, xr))
        s.ladder = layer(W, H, ladder)
        shaft = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(shaft).polygon([(140, 0), (420, 0), (620, 1520), (-60, 1520)], fill=(170, 200, 240, 46))
        s.shaft = shaft.filter(ImageFilter.GaussianBlur(30))
        s.motes = [(random.random(), random.random(), random.uniform(0, 6.28)) for _ in range(40)]

    def base(s, t, dark=0.55, shaft=True, shelf=True, ladder=True):
        img = darken(s.bg, dark)
        if shelf: img.alpha_composite(darken(s.shelf, dark + 0.15))
        if ladder: img.alpha_composite(darken(s.ladder, dark + 0.2))
        if shaft:
            img.alpha_composite(s.shaft)
            d = ImageDraw.Draw(img)
            for u, v, ph in s.motes:
                y = ((v + t * 0.03) % 1.0) * 1500; x = 280 + (u - 0.5) * (280 + y * 0.45) + 8 * math.sin(t + ph)
                d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(220, 230, 250, 130))
        return img


def notebook(img, t, lines, y0=520, title=None):
    """Разворот тетради крупным планом. lines: [(t0, рисующая функция p, k)]."""
    p = P(img, 1.0)
    p.rr(70, y0 - 60, 1010, y0 + 1000, 18, (70, 52, 40))
    p.rr(90, y0 - 40, 990, y0 + 980, 10, PAPER)
    for y in range(y0 + 30, y0 + 960, 62): p.line([(110, y), (970, y)], (190, 180, 160), 2, round_caps=False)
    p.line([(170, y0 - 40), (170, y0 + 980)], (200, 120, 110), 3, round_caps=False)
    if title: p.text(200, y0 - 20, title, hand(44), (120, 100, 90))
    for t0, fn in lines:
        k = clamp((t - t0) / 0.8)
        if k > 0: fn(p, k)
    glow(img, 540, y0 + 400, 700, (255, 236, 196), 0.16, 1.5)


def written(p, x, y, text, k, size=54, col=INK):
    n = int(len(text) * clamp(k)); p.text(x, y, text[:n], hand(size), col)


# ---- из серии 3: ключи, замки, дверь убежища, поле со складом, фургон, изба ----
KEYC = (214, 180, 96); IRON = (86, 90, 102); IRON_D = (58, 60, 70)
NAMES = ["Громов", "Савельев", "Вершинин"]


def key(p, x, y, s=1.0, col=KEYC):
    p.el(x - 34 * s, y - 110 * s, x + 34 * s, y - 42 * s, None, col, max(1, int(12 * s)))
    p.line([(x, y - 42 * s), (x, y + 50 * s)], col, 12 * s)
    p.line([(x, y + 20 * s), (x + 26 * s, y + 20 * s)], col, 10 * s); p.line([(x, y + 44 * s), (x + 20 * s, y + 44 * s)], col, 10 * s)


def padlock(p, x, y, s, opened, name=None):
    col = (150, 140, 110) if opened else (110, 96, 78)
    if opened: p.arc(x - 40 * s, y - 150 * s, x + 40 * s, y - 50 * s, 150, 330, (150, 156, 172), 14 * s)
    else: p.arc(x - 40 * s, y - 110 * s, x + 40 * s, y - 10 * s, 180, 360, (150, 156, 172), 14 * s)
    p.rr(x - 62 * s, y - 60 * s, x + 62 * s, y + 60 * s, 14 * s, col)
    p.circ(x, y - 8 * s, 14 * s, (30, 26, 26)); p.rr(x - 6 * s, y - 6 * s, x + 6 * s, y + 30 * s, 3 * s, (30, 26, 26))
    for dx, dy in ((-40, -40), (40, 36)): p.circ(x + dx * s, y + dy * s, 8 * s, RUST)
    if name: 
        f = hand(int(44 * s)); tw = p.d.textlength(name, font=f) / p.k
        p.text(x - tw / 2, y + 76 * s, name, f, (200, 190, 170))


def iron_door(img, cx, top, w, h, locks, names=False, t=0.0):
    p = P(img, 1.0)
    p.rr(cx - w / 2 - 40, top - 40, cx + w / 2 + 40, top + h + 40, 16, (96, 98, 104))        # бетон
    p.rr(cx - w / 2, top, cx + w / 2, top + h, 12, IRON)
    p.rr(cx - w / 2 + 24, top + 24, cx + w / 2 - 24, top + h - 24, 8, None, IRON_D, 8)
    for yy in (top + 60, top + h - 60):
        for k in range(7): p.circ(cx - w / 2 + 60 + k * (w - 120) / 6, yy, 10, IRON_D)
    for (x, y, r) in ((cx - w * 0.3, top + h * 0.3, 40), (cx + w * 0.25, top + h * 0.75, 54), (cx + w * 0.1, top + h * 0.2, 30)): p.circ(x, y, r, mixc(IRON, RUST, 0.55))
    p.el(cx - 90, top + h * 0.38 - 90, cx + 90, top + h * 0.38 + 90, None, IRON_D, 18)          # штурвал
    for a in range(0, 180, 45):
        dx, dy = 84 * math.cos(math.radians(a)), 84 * math.sin(math.radians(a))
        p.line([(cx - dx, top + h * 0.38 - dy), (cx + dx, top + h * 0.38 + dy)], IRON_D, 12)
    ly = top + h * 0.72
    for j, op in enumerate(locks):
        x = cx + (j - 1) * w * 0.3
        if op: glow(img, x, ly, 150, AMBER, 0.35)
        elif op is False and locks.count(True) == 2: glow(img, x, ly, 150, RED, 0.3 + 0.2 * math.sin(t * 4))
        padlock(P(img, 1.0), x, ly, 1.0, bool(op), NAMES[j] if names else None)


class Field:
    def __init__(s):
        s.sky = vgrad(W, H, [(0, (6, 10, 26)), (0.5, (18, 26, 54)), (0.62, (40, 48, 80)), (1, (150, 160, 184))])
        rnd = random.Random(7)
        def bg(p):
            for _ in range(70): p.circ(rnd.uniform(0, W), rnd.uniform(40, 900), rnd.uniform(1, 2.6), (170, 180, 210))
            p.circ(840, 380, 70, (226, 230, 240)); p.circ(868, 366, 62, (10, 16, 36))
            for k in range(36):
                x = k * 34 + rnd.uniform(-10, 10); h = rnd.uniform(140, 260)
                p.poly([(x - 56, 1150), (x + 56, 1150), (x, 1150 - h)], (14, 22, 40))
            p.rect(0, 1140, W, H, (120, 132, 160))
        s.sky.alpha_composite(layer(W, H, bg))
        def barn(p):
            p.poly([(180, 1320), (220, 980), (420, 1010), (400, 1320)], (60, 48, 44))               # уцелевшая стена
            for y in range(1010, 1320, 50): p.line([(196, y), (410, y + 8)], (46, 36, 34), 5, round_caps=False)
            for (a, b) in (((240, 990), (760, 1250)), ((300, 960), (640, 1300)), ((560, 1060), (900, 1290)), ((420, 1010), (980, 1180))):
                p.line([a, b], (74, 58, 50), 26)
                p.line([(a[0], a[1] - 12), (b[0], b[1] - 12)], SNOW, 8)
            p.el(380, 1260, 1000, 1380, (150, 160, 184))
        s.barn = layer(W, H, barn)
        s.snow = Snow(60, 33, (2, 4), (40, 100))


def van(p, x, y, s=1.0):
    p.rr(x - 220 * s, y - 190 * s, x + 200 * s, y - 20 * s, 30 * s, (70, 80, 110))
    p.rr(x + 60 * s, y - 170 * s, x + 180 * s, y - 100 * s, 14 * s, (150, 176, 210))
    p.rr(x - 190 * s, y - 160 * s, x + 20 * s, y - 80 * s, 12 * s, (54, 62, 90))
    p.circ(x - 130 * s, y - 20 * s, 40 * s, (18, 18, 24)); p.circ(x + 120 * s, y - 20 * s, 40 * s, (18, 18, 24))
    p.line([(x - 100 * s, y - 190 * s), (x - 100 * s, y - 260 * s)], (150, 156, 172), 6 * s); p.chord(x - 150 * s, y - 300 * s, x - 50 * s, y - 230 * s, 0, 180, (150, 156, 172))


class Room:
    def __init__(s):
        s.bg = vgrad(W, H, [(0, (44, 38, 44)), (1, (26, 22, 28))])
        def deco(p):
            for x in range(-40, W, 100): p.rect(x, 0, x + 94, 1480, (62, 50, 46))
            p.rect(0, 1480, W, H, (40, 32, 32))
            p.rr(120, 360, 420, 700, 8, (30, 30, 40)); p.rr(110, 350, 430, 710, 10, None, (110, 90, 70), 12)       # рамка с фото
            p.el(220, 440, 320, 560, (90, 84, 80)); p.rr(190, 560, 350, 690, 30, (70, 66, 64))
        s.bg.alpha_composite(layer(W, H, deco))
