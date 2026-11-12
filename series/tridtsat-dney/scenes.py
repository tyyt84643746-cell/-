"""«Тридцать дней», серия 1. Сцена: frame(t) -> (RGBA, zoom, bright)."""
import json, math, os, random, re
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from chars import *
from script import SCENES, CAPTION_NUMS

D = os.path.dirname(os.path.abspath(__file__))
FPS = 30; LEAD = 0.4; TAIL = 1.0
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ALN = [json.load(open(f"{D}/v{i}.json")) for i in range(1, 10)]
NFR = [round((a["character_end_times_seconds"][-1] + LEAD + TAIL) * FPS) for a in ALN]
DUR = [n / FPS for n in NFR]
STARTS = [sum(DUR[:i]) for i in range(9)]
_F = {}
def font(sz):
    if sz not in _F: _F[sz] = ImageFont.truetype(FB, sz)
    return _F[sz]


def wt(i, sub, end=False):
    text = SCENES[i]["text"]; k = text.find(sub); assert k >= 0, (i, sub)
    a = ALN[i]
    return (a["character_end_times_seconds"][k + len(sub) - 1] if end else a["character_start_times_seconds"][k]) + LEAD


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


# ======================================================================= квартира (сцены 1–3)
class Flat:
    def __init__(s):
        s.bg = vgrad(W, H, [(0, (26, 30, 52)), (0.6, (34, 38, 62)), (1, (24, 24, 38))])
        def deco(p):
            p.rect(0, 1480, W, H, (40, 36, 48))
            for x in range(-200, W, 120): p.line([(x, 1480), (x + 240, H)], (48, 42, 54), 4, round_caps=False)
            p.rr(700, 320, 1000, 700, 10, (8, 12, 26)); p.rr(690, 310, 1010, 710, 12, None, (90, 98, 126), 12)  # окно
            p.line([(850, 320), (850, 700)], (90, 98, 126), 8)
            for k in range(14): p.circ(720 + (k * 53) % 270, 340 + (k * 97) % 340, 2, (200, 180, 120))   # огни города
        s.bg.alpha_composite(layer(W, H, deco))
        def sofa(p):
            p.rr(40, 1110, 1040, 1330, 60, (70, 76, 110))                                 # спинка
        s.sofa_back = layer(W, H, sofa)
        def sofa_f(p):
            p.rr(40, 1320, 1040, 1530, 50, (82, 88, 126))
            p.rr(0, 1180, 140, 1540, 50, (76, 82, 118)); p.rr(940, 1180, 1080, 1540, 50, (76, 82, 118))
            p.rr(60, 1520, 100, 1580, 10, (40, 36, 48)); p.rr(980, 1520, 1020, 1580, 10, (40, 36, 48))
        s.sofa_front = layer(W, H, sofa_f)
        s.dark = darken(s.bg, 0.35)

FLAT = None
def flat():
    global FLAT
    if FLAT is None: FLAT = Flat()
    return FLAT


def scene1(t):
    dur = DUR[0]; tp = wt(0, "Поверил")
    if t < tp:
        img = Image.new("RGBA", (W, H), (4, 6, 12, 255))
        k = ease(t / 0.5); f = font(int(lerp(300, 520, k)))
        ctext(img, W / 2, 760 - lerp(150, 260, k), "30", f, (255, 255, 255))
        glow(img, W / 2, 900, 600, (255, 200, 120), 0.10 * k, 1.5)
        return img, lerp(1.0, 1.06, t / tp), 1.0
    tt = t - tp; fl = 0.8 + 0.2 * math.sin(t * 17) * math.sin(t * 5)
    img = Image.new("RGBA", (W, H), (4, 6, 12, 255))
    glow(img, 540, 900, 760, (90, 130, 220), 0.45 * fl, 1.4)
    hero(img, 540, 1560, 1.35, t, look=(0.0, 0.0), brows="worried", dark=0.55 * fl + 0.15)
    return img, lerp(1.12, 1.0, ease(tt / (dur - tp))), 1.0


def scene2(t):
    s = flat(); dur = DUR[1]; tf = wt(1, "Друзья")
    if t < wt(1, "Ведущий") + 2.6:
        img = darken(s.bg, 0.45)
        tv(img, 90, 520, 990, 1030, t, "УЛЬТИМАТУМ", sub="Срок — 30 дней")
        P(img, 1.0).rr(380, 1050, 700, 1080, 10, (20, 22, 30))
        cat(img, 860, 1560, 1.05, t, pose="lie", look=-0.6, dark=0.7)
        return img, lerp(1.0, 1.1, ease(t / (tf))), 1.0
    img = darken(s.bg, 0.5); img.alpha_composite(darken(s.sofa_back, 0.6))
    fl = 0.85 + 0.15 * math.sin(t * 13)
    glow(img, 540, 900, 700, (100, 140, 230), 0.3 * fl, 1.5)
    hero(img, 420, 1660, 1.3, t, look=(0.1, -0.2), brows="worried", dark=0.82, mouth="flat" if t > wt(1, "Артём не") else None)
    cat(img, 760, 1400, 1.0, t, look=-0.7)
    img.alpha_composite(darken(s.sofa_front, 0.6))
    bubble(img, 90, 420, "опять пугают", (t - tf) / 0.3, face=True)
    bubble(img, 420, 560, "ха-ха, бункер копай", (t - tf - 0.9) / 0.3, face=True)
    bubble(img, 160, 700, "спать иди", (t - tf - 1.8) / 0.3)
    return img, 1.03, 1.0


def scene3(t):
    s = flat(); dur = DUR[2]; tm = wt(2, "Утром")
    if t < tm:
        img = darken(s.bg, 0.3)
        hero(img, 540, 1720, 1.3, t, look=(0.0, 0.7), brows="worried", dark=0.5)
        p = P(img, 1.0)
        p.rr(-20, 1380, W + 20, H, 20, (52, 40, 40))                                     # стол
        p.poly([(330, 1380), (750, 1380), (720, 1180), (360, 1180)], (60, 66, 84))       # ноутбук
        p.poly([(345, 1372), (735, 1372), (710, 1196), (370, 1196)], (180, 210, 250))
        for k in range(6): p.rect(400, 1220 + k * 24, 400 + (k * 47) % 260 + 60, 1230 + k * 24, (120, 150, 200))
        p.rr(300, 1380, 780, 1400, 6, (80, 86, 104))
        glow(img, 540, 1250, 520, (170, 200, 250), 0.35, 1.5)
        cat(img, 880, 1440, 0.95, t, yawn=(t % 5.0) > 3.6, look=-0.8, dark=0.75)
        return img, lerp(1.0, 1.08, ease(t / tm)), 1.0
    tt = t - tm
    img = vgrad(W, H, [(0, (196, 206, 224)), (1, (150, 160, 184))])
    p = P(img, 1.0)
    p.rr(250, 330, 830, 1500, 70, (18, 20, 28)); p.rr(272, 352, 808, 1478, 54, (246, 247, 250))
    p.rr(300, 420, 780, 800, 24, (200, 210, 226))
    for k in range(3): p.rr(300 + k * 0, 480 + k * 90, 780, 520 + k * 90, 0, (200, 210, 226))
    p.poly([(380, 760), (540, 560), (700, 760)], (170, 184, 206)); p.rect(420, 680, 660, 780, (184, 196, 216))
    p.text(300, 830, "ПРОДАЮ КВАРТИРУ", font(44), (20, 24, 36))
    p.text(300, 900, "1-комн., 14 этаж", font(34), (90, 96, 116))
    k = ease((tt - 1.2) / 0.4)
    p.text(300, 980, "12 500 000 ₽", font(46), (120, 126, 146))
    if k > 0:
        p.line([(296, 1006), (296 + 330 * k, 1006)], RED, 6, round_caps=False)
        if k > 0.9: p.text(300, 1050, "9 900 000 ₽", font(58), (200, 40, 40))
    p.rr(300, 1180, 780, 1270, 40, (60, 120, 230)); ctext(img, 540, 1200, "Опубликовать", font(40), (255, 255, 255))
    if tt > 0.6:
        hx = lerp(700, 560, ease((tt - 0.6) / 0.5)); hy = lerp(1500, 1250, ease((tt - 0.6) / 0.5))
        P(img, 1.0).el(hx - 50, hy - 40, hx + 50, hy + 80, SKIN)
    return img, lerp(1.0, 1.05, ease(tt / (dur - tm))), 1.0


# ======================================================================= деревня
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


VIL = None
def scene4(t):
    global VIL
    if VIL is None:
        VIL = Village(0.35)
        bg = VIL.sky.copy()
        def l(p):
            s.chim = VIL.house(p, 420, 1300, 1.2, lit=True)
            VIL.fence(p, 1430, -40, 360)
            p.rr(60, 1080, 300, 1300, 8, (90, 66, 50)); p.poly([(40, 1080), (320, 1080), (180, 980)], (70, 74, 90))   # баня
            p.poly([(40, 1080), (320, 1080), (300, 1066), (60, 1066)], SNOW)
        class _: pass
        s = _(); VIL.house_layer = layer(W, H, l); VIL.chim = s.chim; VIL.snow = Snow(70, 2, (2, 4.5), (50, 120))
    v = VIL; dur = DUR[3]
    img = v.sky.copy(); img.alpha_composite(v.house_layer); smoke(img, *v.chim, t)
    for wx in (420 + 70 * 1.2 + 66, 420 + 330 * 1.2 + 66): glow(img, wx, 1300 - 330 * 1.2 + 186, 150, AMBER, 0.25)
    tq = wt(3, "Потом говорит")
    granny(img, 760, 1410, 1.0, t, look=-0.7)
    tw = min(t, 3.6)
    hx = lerp(-100, 330, ease(tw / 3.6))
    walking = t < 3.6
    pts = hero(img, hx, 1580, 1.18, t, walk=t * 5 if walking else None, arm="reach", look=(0.7, 0.0),
               mouth="o" if t > tq else None, brows="worried" if wt(3, "Бабушка") < t < tq else "calm")
    p = P(img, 1.0); hxh, hyh = pts["hand"]
    carrier(p, hxh, hyh + 150, 1.0)
    cat(img, hxh, hyh + 120, 0.45, t, look=0.6, head_only=True)
    shovel(p, hx - 90, 1500 - 360, hx - 160, 1560)
    v.snow.draw(img, t, 220)
    if t > tq:
        bubble(img, 560, 760, "копай за баней", (t - tq) / 0.3)
    return img, lerp(1.04, 1.0, ease(t / dur)), 1.0


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

YARD = None
def scene5(t):
    global YARD
    if YARD is None: YARD = Yard(0.25); YARD.snow = Snow(50, 5, (2, 4), (40, 100))
    y = YARD; dur = DUR[4]
    img = y.bg.copy(); p = P(img, 1.0)
    rnd = random.Random(9)
    for x in (120, 250, 420, 560):
        silhouette(p, x, 1150, 0.95, mixc((56, 62, 84), (80, 76, 96), rnd.random()), hat=mixc((90, 70, 60), (60, 70, 90), rnd.random()))
    y.pit(img)
    dig = math.sin(t * 4.5)
    pts = hero(img, 560, 1720, 1.05, t, arm="reach", look=(0.3, 0.8), brows="calm")
    P(img, 1.0).el(190, 1640, 930, 1760, (66, 50, 42))
    hx, hy = pts["hand"]; shovel(P(img, 1.0), hx, hy + 10 * dig, hx + 40, hy + 250 + 30 * dig)
    if dig > 0.9:
        glow(img, 900, 1430, 40, (110, 88, 70), 0.9, 1.0)
    pk = kolyan(img, 900, 1600, 1.15, t)
    tv_ = wt(4, "Видео")
    if t > tv_ - 0.3:
        views = int(lerp(12, 1200, ease((t - tv_) / (dur - tv_ - 0.8)))) if t > tv_ else 12
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); o = P(ov, 1.0)
        o.rr(80, 330, 1000, 520, 30, (10, 14, 28, 230))
        o.text(120, 352, "«Внук копает себе могилу»", font(40), (244, 246, 250))
        o.text(120, 420, f"просмотры: {views:,}".replace(",", " "), font(42), AMBER)
        o.circ(940, 444, 14, RED)
        img.alpha_composite(ov)
    y.snow.draw(img, t, 200)
    return img, lerp(1.0, 1.06, ease(t / dur)), 1.0


# ======================================================================= покупки (сцена 6)
class Shed:
    def __init__(s):
        s.bg = vgrad(W, H, [(0, (40, 34, 36)), (1, (26, 24, 30))])
        def l(p):
            for x in range(-40, W, 90): p.rect(x, 0, x + 84, 1500, (58, 46, 40))
            p.rect(0, 1500, W, H, (44, 38, 36))
        s.bg.alpha_composite(layer(W, H, l))
        s.bulb = (540, 120)

def box(p, x, y, w, h, label, col=(150, 116, 80)):
    p.rr(x, y - h, x + w, y, 8, col); p.rect(x, y - h, x + w, y - h + 16, mixc(col, (0, 0, 0), 0.2))
    p.rr(x + w / 2 - 14, y - h, x + w / 2 + 14, y - h * 0.4, 2, mixc(col, (255, 255, 255), 0.2))
    if label: p.text(x + 18, y - h / 2, label, font(30), (40, 30, 24))

SHED = None
def scene6(t):
    global SHED
    if SHED is None: SHED = Shed()
    s = SHED; dur = DUR[5]
    img = s.bg.copy()
    glow(img, 540, 140, 900, WARM, 0.28, 1.5); glow(img, 540, 140, 40, (255, 250, 230), 1.0, 1.2)
    P(img, 1.0).line([(540, 0), (540, 110)], (30, 30, 34), 4)
    tf, tw_, tc, tk = wt(5, "Фильтры"), wt(5, "Вода"), wt(5, "Консервы"), wt(5, "корма")
    p = P(img, 1.0)
    def pop(t0): return clamp((t - t0) / 0.25)
    p.rect(420, 1180, 790, 1196, (90, 70, 56)); p.rect(420, 940, 790, 956, (90, 70, 56))
    p.rect(426, 940, 440, 1540, (80, 62, 50)); p.rect(770, 940, 784, 1540, (80, 62, 50))
    if pop(tf) > 0:
        box(p, 40, 1540, 360, 250, "ФИЛЬТР"); box(p, 70, 1290, 300, 180, "ФИЛЬТР")
    if pop(tw_) > 0:
        for k in range(4): p.rr(450 + k * 80, 1000, 515 + k * 80, 1180, 14, (70, 120, 180)); p.rr(466 + k * 80, 984, 500 + k * 80, 1002, 6, (50, 90, 150))
    if pop(tc) > 0:
        for r in range(3):
            for k in range(6 - r): p.rr(450 + k * 54 + r * 27, 940 - 66 * (r + 1), 498 + k * 54 + r * 27, 940 - 66 * r - 4, 8, (160, 166, 180))
    hero(img, 900, 1540, 1.0, t, look=(-0.6, 0.3), brows="worried", dark=0.9)
    if pop(tk) > 0:
        p.rr(450, 1310, 760, 1540, 30, (120, 140, 90)); p.text(486, 1440, "КОРМ 30 КГ", font(34), (240, 240, 230))
        cat(img, 600, 1330, 0.8, t, look=0.4)
    money = int(lerp(9_900_000, 1_240_000, ease(t / (dur - 0.8))))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); o = P(ov, 1.0)
    txt = f"{money:,} ₽".replace(",", " ")
    o.rr(190, 320, 890, 430, 30, (10, 14, 28, 230)); ctext(ov, 540, 336, txt, font(64), (255, 120, 110) if money < 3_000_000 else AMBER)
    img.alpha_composite(ov)
    return img, lerp(1.06, 1.0, ease(t / dur)), 1.0


# ======================================================================= дождь и бабушка (сцены 7–8)
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

YARD2 = RAIN = None
def pit_scene(t, water):
    global YARD2, RAIN
    if YARD2 is None:
        YARD2 = Yard(0.75); RAIN = Rain()
        YARD2.bg = darken(YARD2.bg, 0.6)
    img = YARD2.bg.copy()
    glow(img, 620 + 0.75 * 70 + 40, 1050 - 0.75 * 330 + 150, 70, AMBER, 0.6)     # окно, в окне Кекс
    cat(img, 620 + 0.75 * 70 + 42, 1050 - 0.75 * 330 + 236, 0.32, t, head_only=True, look=0.3, dark=0.7)
    YARD2.pit(img, water, t)
    return img


def scene7(t):
    dur = DUR[6]; tm = wt(6, "Утром")
    water = 0.0 if t < tm else ease((t - tm) / 1.0)
    img = pit_scene(t, water)
    if t > wt(6, "Артём сидит") - 0.5:
        pts = hero(img, 420, 1600, 1.0, t, look=(0.4, 0.9), brows="worried", mouth="flat", dark=0.75)
        P(img, 1.0).el(180, 1520, 640, 1720, (66, 50, 42))
    RAIN.draw(img, t)
    return img, lerp(1.0, 1.1, ease(t / dur)), 0.85


def sepia(img, amt):
    a = np.asarray(img.convert("RGB")).astype(np.float32)
    g = a @ np.array([0.3, 0.59, 0.11], np.float32)
    s = np.stack([g * 1.08 + 18, g * 0.9 + 8, g * 0.68], -1)
    out = a * (1 - amt) + s * amt
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).convert("RGBA")


def scene8(t):
    dur = DUR[7]; td = wt(7, "Твой дед")
    if t < td:
        img = pit_scene(t + 20, 1.0)
        hero(img, 420, 1600, 1.0, t, look=(0.7, 0.0) if t > 1.0 else (0.4, 0.9), brows="worried", dark=0.78,
             mouth="o" if t > wt(7, "И говорит") else None)
        P(img, 1.0).el(180, 1520, 640, 1720, (66, 50, 42))
        gx = lerp(1200, 700, ease(t / 1.4))
        pt = granny(img, gx, 1600, 1.0, t, mug=True, look=-0.6, dark=0.85)
        steam(img, pt["mug"][0], pt["mug"][1] - 20, t, period=1.6, scale=0.6)
        RAIN.draw(img, t + 3, 90)
        return img, 1.04, 0.9
    tt = t - td
    img = vgrad(W, H, [(0, (150, 150, 150)), (0.55, (190, 190, 190)), (1, (220, 220, 220))])
    p = P(img, 1.0)
    for k in range(12): p.poly([(k * 100 - 40, 1000), (k * 100 + 60, 1000), (k * 100 + 10, 760 - (k % 3) * 50)], (110, 110, 110))
    p.rect(0, 1000, W, H, (200, 200, 200))
    p.el(200, 1380, 900, 1640, (90, 90, 90)); p.el(240, 1400, 860, 1610, (50, 50, 50))
    dig = math.sin(tt * 4)
    x = 640; yb = 1480
    p.rr(x - 50, yb - 330, x + 50, yb, 34, (40, 40, 40)); p.el(x - 40, yb - 420, x + 40, yb - 330, (40, 40, 40))
    p.chord(x - 46, yb - 440, x + 46, yb - 370, 180, 360, (40, 40, 40)); p.rr(x - 60, yb - 400, x + 60, yb - 388, 4, (40, 40, 40))
    p.line([(x - 30, yb - 240), (x - 140, yb - 120 + 20 * dig)], (40, 40, 40), 30)
    shovel(p, x - 140, yb - 120 + 20 * dig, x - 230, yb + 40 + 30 * dig)
    ctext(img, W / 2, 1220, "1962", font(110), (70, 60, 50))
    img = sepia(img, 1.0)
    a = np.asarray(img).astype(np.float32)
    a[..., :3] += np.random.default_rng(int(t * 30)).normal(0, 14, (H, W, 1))
    if int(t * 30) % 9 == 0: a[:, int((t * 997) % W):int((t * 997) % W) + 3, :3] *= 0.6
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA"), lerp(1.0, 1.06, tt / (dur - td)), 1.0


# ======================================================================= финал (сцена 9)
def scene9(t):
    dur = DUR[8]
    img = Image.new("RGBA", (W, H), (8, 10, 18, 255))
    p = P(img, 1.0); p.rect(0, 1500, W, H, (20, 18, 24))
    tv(img, 190, 380, 890, 780, t, "ПЕРЕГОВОРЫ ПРЕРВАНЫ", plate_col=(200, 40, 40), plate_txt=(255, 255, 255))
    P(img, 1.0).rr(400, 800, 680, 830, 10, (20, 22, 30))
    hero(img, 420, 1700, 1.2, t, view="back", dark=0.55)
    granny(img, 820, 1700, 1.05, t, dark=0.45)
    cat(img, 600, 1720, 0.7, t, pose="lie", ears_back=True, dark=0.55)
    k = clamp((t - 1.2) / 0.6)
    ctext(img, W / 2, 850, "18", font(int(lerp(120, 170, ease(k)))), mixc((255, 255, 255), RED, k))
    return img, lerp(1.0, 1.08, ease(t / dur)), 1.0


SCENE_FUNCS = [scene1, scene2, scene3, scene4, scene5, scene6, scene7, scene8, scene9]


def captions(i):
    text = SCENES[i]["text"]; a = ALN[i]
    st = a["character_start_times_seconds"]; en = a["character_end_times_seconds"]
    words = [(m.start(), m.group()) for m in re.finditer(r"\S+", text)]
    for k_ in CAPTION_NUMS:
        p0 = text.find(k_)
        if p0 < 0: continue
        p1 = p0 + len(k_)
        tail = text[p1:].split(" ")[0] if not text[p1:].startswith(" ") else ""
        words = [w for w in words if not (p0 <= w[0] < p1)] + [(p0, text[p0:p1] + tail)]; words.sort()
    sents, cur = [], []
    for w in words:
        cur.append(w)
        if w[1][-1] in ".?!": sents.append(cur); cur = []
    if cur: sents.append(cur)
    chunks = []
    for sent in sents:
        n = math.ceil(len(sent) / 6); per = math.ceil(len(sent) / n)
        for j in range(0, len(sent), per): chunks.append(sent[j:j + per])
    out = []
    for j, c in enumerate(chunks):
        a0 = st[c[0][0]] + LEAD; last = c[-1]; b0 = en[last[0] + len(last[1]) - 1] + LEAD + 0.25
        if j + 1 < len(chunks): b0 = min(b0 + 0.4, st[chunks[j + 1][0][0]] + LEAD)
        s_ = text[c[0][0]: last[0] + len(last[1])]
        for k_, v_ in CAPTION_NUMS.items(): s_ = s_.replace(k_, v_)
        out.append((a0, b0, s_))
    return out
