"""«Тридцать дней», серия 2 «Секрет деда». Сцена: frame(t) -> (RGBA, zoom, bright)."""
import json, math, os, random, re, sys
D = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(D, "..", "tridtsat-dney"))
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from chars import *
from world import *
from script import SCENES, CAPTION_NUMS

FPS = 30; LEAD = 0.4; TAIL = 1.0
N = len(SCENES)
ALN = [json.load(open(f"{D}/v{i}.json")) for i in range(1, N + 1)]
NFR = [round((a["character_end_times_seconds"][-1] + LEAD + TAIL) * FPS) for a in ALN]
DUR = [n / FPS for n in NFR]
STARTS = [sum(DUR[:i]) for i in range(N)]
FH = "/usr/share/fonts/truetype/freefont/FreeSerifBoldItalic.ttf"
_H = {}
def hand(sz):
    if sz not in _H: _H[sz] = ImageFont.truetype(FH if os.path.exists(FH) else FB, sz)
    return _H[sz]
PAPER = (226, 210, 176); INK = (52, 44, 78); RUST = (128, 78, 52)


def wt(i, sub, end=False):
    text = SCENES[i]["text"]; k = text.find(sub); assert k >= 0, (i, sub)
    a = ALN[i]
    return (a["character_end_times_seconds"][k + len(sub) - 1] if end else a["character_start_times_seconds"][k]) + LEAD


def fact_card(img, t, t0, sub):
    if t < t0: return
    k = ease((t - t0) / 0.35); f = font(40)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    tw = od.textlength(sub, font=f); x0 = W / 2 - tw / 2 - 34; y0 = 330 - 20 * (1 - k)
    od.rounded_rectangle([x0, y0, x0 + tw + 68, y0 + 84], radius=20, fill=(10, 14, 28, int(220 * k)), outline=(255, 178, 64, int(255 * k)), width=3)
    od.text((x0 + 34, y0 + 18), sub, font=f, fill=(255, 226, 170, int(255 * k)))
    img.alpha_composite(ov)


# ======================================================================= сцена 1: где мы остановились
Y1 = R1 = None
def scene1(t):
    global Y1, R1
    dur = DUR[0]
    ta, tb, tc, td = wt(0, "Яма"), wt(0, "Деньги"), wt(0, "Деревня"), wt(0, "И тут")
    if t < ta:
        img = Image.new("RGBA", (W, H), (4, 6, 12, 255))
        k = ease(t / 0.5); ctext(img, W / 2, 620, "18", font(int(lerp(300, 500, k))), (255, 255, 255))
        return img, lerp(1.0, 1.05, t / ta), 1.0
    if t < tb:
        if Y1 is None:
            Y1 = Yard(0.75); Y1.bg = darken(Y1.bg, 0.6); R1 = Rain()
        img = Y1.bg.copy(); Y1.pit(img, 1.0, t)
        hero(img, 420, 1600, 1.0, t, look=(0.4, 0.9), brows="worried", mouth="flat", dark=0.75)
        P(img, 1.0).el(180, 1520, 640, 1720, (66, 50, 42)); R1.draw(img, t)
        return img, 1.06, 0.85
    if t < tc:
        img = Image.new("RGBA", (W, H), (10, 12, 22, 255))
        money = int(lerp(1_240_000, 610_000, ease((t - tb) / (tc - tb))))
        P(img, 1.0).rr(150, 640, 930, 800, 36, (20, 24, 40))
        ctext(img, W / 2, 668, f"{money:,} ₽".replace(",", " "), font(84), (255, 120, 110))
        hero(img, 540, 1560, 1.15, t, look=(0.0, -0.8), brows="worried")
        return img, 1.03, 1.0
    if t < td:
        if Y1 is None:
            Y1 = Yard(0.75); Y1.bg = darken(Y1.bg, 0.6); R1 = Rain()
        img = darken(Yard(0.25).bg, 1.0) if False else Y1.bg.copy()
        kolyan(img, 560, 1580, 1.3, t)
        p = P(img, 1.0)
        for j, (x, y) in enumerate(((200, 620), (820, 560), (330, 900), (860, 980))):
            k = ease((t - tc - j * 0.15) / 0.2)
            if k > 0: laugh_face(p, x, y - 20 * k, 50 * k)
        return img, 1.04, 0.95
    tt = t - td
    img = Image.new("RGBA", (W, H), (14, 16, 26, 255))
    glow(img, 540, 1000, 700, AMBER, 0.2, 1.5)
    granny(img, 420, 1620, 1.5, t, look=0.6)
    k = ease((tt - 0.6) / 0.5)
    kx, ky = lerp(560, 760, k), lerp(1300, 1000, k)
    p = P(img, 1.0); p.line([(520, 1280), (kx, ky + 60)], (52, 80, 64), 44); p.circ(kx, ky + 60, 22, SKIN)
    if k > 0.3:
        glow(img, kx, ky - 40, 160, AMBER, 0.5 * k)
        p = P(img, 1.0)
        p.el(kx - 34, ky - 110, kx + 34, ky - 42, None, (200, 170, 90), 12)
        p.line([(kx, ky - 42), (kx, ky + 50)], (200, 170, 90), 12)
        p.line([(kx, ky + 20), (kx + 26, ky + 20)], (200, 170, 90), 10); p.line([(kx, ky + 44), (kx + 20, ky + 44)], (200, 170, 90), 10)
    return img, lerp(1.0, 1.08, ease(tt / (dur - td))), 1.0


# ======================================================================= сцена 2: люк за сараем
Y2 = None
def hatch(p, cx, cy, s=1.0, open_k=0.0):
    p.rr(cx - 190 * s, cy - 90 * s, cx + 190 * s, cy + 90 * s, 20 * s, (40, 34, 32))
    if open_k < 1:
        yy = cy - 90 * s - 150 * s * open_k
        p.rr(cx - 180 * s, yy + 10 * s, cx + 180 * s, yy + 170 * s * (1 - open_k * 0.6), 16 * s, (92, 96, 108))
        for dx, dy in ((-120, 40), (60, 110), (110, 50), (-40, 120)): p.circ(cx + dx * s, yy + dy * s * (1 - open_k * 0.6), 14 * s, RUST)
        p.el(cx - 36 * s, yy + 60 * s, cx + 36 * s, yy + 110 * s, None, (40, 42, 50), int(10 * s))
        for dx in (-150, 150): p.circ(cx + dx * s, yy + 30 * s, 8 * s, (50, 52, 60))

def scene2(t):
    global Y2
    if Y2 is None:
        Y2 = Yard(0.1); Y2.snow = Snow(40, 15, (2, 4), (40, 100))
    dur = DUR[1]; tl = wt(1, "Под снегом"); td = wt(1, "Твой дед"); tf = wt(1, "В шестьдесят")
    img = Y2.bg.copy(); p = P(img, 1.0)
    cx, cy = 540, 1400
    kb = ease((t - tl) / 1.2)
    hatch(p, cx, cy, 1.0)
    for j, dx in enumerate((-150, -50, 50, 150)):                                   # доски разъезжаются
        off = (-1 if j < 2 else 1) * 330 * kb
        p.rr(cx + dx - 46 + off, cy - 120, cx + dx + 46 + off, cy + 120, 8, (124, 98, 72))
        p.rr(cx + dx - 46 + off, cy - 120, cx + dx + 46 + off, cy - 80 + 20 * (1 - kb), 12, SNOW)
    if kb > 0.6: glow(img, cx, cy, 240, AMBER, 0.12)
    walking = t < tl
    gx = lerp(1200, 890, ease(t / tl)) if walking else 890
    hx = lerp(-100, 190, ease(t / tl)) if walking else 190
    granny(img, gx, 1500, 1.0, t, look=-0.7)
    hero(img, hx, 1500, 1.05, t, walk=t * 5 if walking else None, look=(0.6, 0.7) if t > tl else (0.7, 0.0),
         mouth="o" if tl + 0.8 < t < td + 1.5 else None, brows="worried" if t > tl else "calm")
    if td < t < tf: bubble(img, 520, 800, "он построил погреб", (t - td - 1.2) / 0.3)
    Y2.snow.draw(img, t, 200)
    fact_card(img, t, tf, "ОКТЯБРЬ 1962 · 13 ДНЕЙ")
    return img, lerp(1.0, 1.08, ease(t / dur)), 1.0


# ======================================================================= погреб
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

CEL = None
def cellar():
    global CEL
    if CEL is None: CEL = Cellar()
    return CEL


def scene3(t):
    c = cellar(); dur = DUR[2]; tk = wt(2, "Кекс"); ts = wt(2, "чихает"); tw = wt(2, "Кирпичные")
    if t < tk:
        img = Image.new("RGBA", (W, H), (150, 170, 200, 255))                       # вид сверху в люк
        p = P(img, 1.0); p.rr(120, 420, 960, 1500, 40, (16, 12, 14)); p.rr(90, 390, 990, 1530, 50, None, (92, 96, 108), 30)
        for k in range(5): p.rr(300, 560 + k * 170, 780, 590 + k * 170, 8, mixc((128, 98, 70), (20, 16, 16), k / 5))
        on = t > 0.9
        pts = hero(img, 540, 1900, 1.35, t, look=(0.0, 0.9), lamp=True, brows="worried")
        lamp_glow(img, pts["lamp"], on, size=1.35)
        if on: glow(img, 540, 1000, 420, (255, 240, 200), 0.25, 1.4)
        return img, lerp(1.0, 1.08, t / tk), 1.0
    img = c.base(t)
    glow(img, 760, 1000, 620, (255, 236, 196), 0.2, 1.5)
    sneeze = ts < t < ts + 0.5
    cy = lerp(900, 1480, ease((t - tk) / 1.2))
    cat(img, 300, cy, 0.95, t, ears_back=sneeze, yawn=sneeze, look=0.6, dark=0.9)
    if ts < t < ts + 1.2:
        k = (t - ts) / 1.2
        for j in range(7):
            a = j * 0.9; r = 60 + 180 * k
            glow(img, 330 + r * math.cos(a), cy - 200 - r * abs(math.sin(a)) * 0.6, 40 + 40 * k, (200, 190, 180), 0.5 * (1 - k), 1.3)
    if t > tw - 0.6:
        hy = lerp(600, 1560, ease((t - tw + 0.6) / 1.2))
        pts = hero(img, 760, hy, 1.1, t, look=(0.6, -0.2), lamp=True, brows="worried", mouth="o" if t > tw + 1.0 else None, dark=0.95)
        lamp_glow(img, pts["lamp"], True, size=1.1)
    return img, lerp(1.0, 1.08, ease(t / dur)), 1.0


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


def scene4(t):
    c = cellar(); dur = DUR[3]; tn = wt(3, "Чертежи"); 
    if t < tn:
        img = c.base(t, shaft=False, ladder=False)
        p = P(img, 1.0); p.rr(-20, 1380, W + 20, H, 10, (80, 60, 46))
        ko = ease((t - 1.0) / 0.7)
        p.rr(300, 1180, 780, 1400, 14, (96, 104, 112)); p.rr(300, 1180, 780, 1210, 8, (70, 76, 84))
        p.poly([(300, 1180), (780, 1180), (780 - 30 * ko, 1180 - 200 * ko - 30 * (1 - ko)), (300 - 30 * ko, 1180 - 200 * ko - 30 * (1 - ko))], (110, 118, 126))
        for dx in (340, 700): p.circ(dx, 1300, 10, RUST)
        if ko > 0.5:
            p.rr(380, 1130 - 40 * ko, 700, 1200, 8, (60, 80, 110)); p.rr(396, 1146 - 40 * ko, 684, 1160 - 40 * ko, 4, PAPER)
            glow(img, 540, 1150, 260, AMBER, 0.3 * ko)
        pts = hero(img, 220, 1900, 1.3, t, look=(0.8, 0.8), lamp=True, brows="calm", mouth="o" if ko > 0.5 else None)
        lamp_glow(img, pts["lamp"], True, size=1.3)
        cat(img, 900, 1380, 0.8, t, look=-0.7)
        return img, lerp(1.0, 1.1, ease(t / tn)), 1.0
    img = darken(c.bg, 0.4)
    ta, tb, tc_, td = wt(3, "Воздух"), wt(3, "вода"), wt(3, "еда"), wt(3, "На четверых")
    def plan(p, k):                                                                # разрез погреба
        pts = [(230, 1180), (230, 760), (860, 760), (860, 1180), (230, 1180)]
        n = int(k * 4); p.line(pts[: n + 2], INK, 6)
        if k >= 1: p.line([(300, 760), (300, 640), (420, 640), (420, 760)], INK, 6)
    def air(p, k):
        p.line([(760, 760), (760, 760 - 170 * k)], INK, 8)
        if k >= 1:
            p.line([(730, 590), (790, 590)], INK, 8)
            for j in range(3): p.arc(690 + j * 34, 610 + j * 40, 730 + j * 34, 650 + j * 40, 200, 340, INK, 4)
            p.text(790, 606, "воздух", hand(54), INK)
    def water(p, k):
        p.rr(280, 1180 - 190 * k, 400, 1180, 14, None, INK, 6)
        if k >= 1:
            for y in (1030, 1080, 1130): p.line([(290, y), (390, y)], INK, 4)
            p.text(264, 1196, "вода", hand(54), INK)
    def food(p, k):
        for j in range(int(k * 5)): p.rr(470 + j * 46, 1110, 508 + j * 46, 1180, 6, None, INK, 5)
        if k >= 1: p.text(520, 1196, "еда", hand(54), INK)
    def four(p, k):
        for j in range(int(k * 4 + 0.01)):
            x = 470 + j * 90
            p.circ(x, 880, 22, INK); p.line([(x, 902), (x, 990)], INK, 8); p.line([(x - 26, 940), (x + 26, 940)], INK, 6)
        if k >= 1: p.text(820, 880, "×4", hand(70), (170, 50, 50))
    notebook(img, t, [(tn, plan), (ta, air), (tb, water), (tc_, food), (td, four)], title="погреб. план")
    return img, lerp(1.0, 1.06, ease((t - tn) / (dur - tn))), 1.0


# ======================================================================= сцена 5: стройка и Колян
Y5 = None
def scene5(t):
    global Y5
    if Y5 is None:
        Y5 = Yard(0.15); Y5.snow = Snow(40, 25, (2, 4), (40, 100))
    dur = DUR[4]; tk = wt(4, "Колян"); tv_ = wt(4, "Теперь"); tc = wt(4, "В комментариях")
    img = Y5.bg.copy(); p = P(img, 1.0)
    hatch(p, 300, 1440, 0.95, open_k=1.0)
    carry = (t * 0.45) % 1.0
    hx = lerp(900, 420, ease(carry / 0.7)) if t < tk else 620
    pts = hero(img, hx, 1500, 1.0, t, walk=t * 5 if t < tk else None, arm="reach", look=(-0.6, 0.2) if t < tk else (0.7, 0.0))
    hxh, hyh = pts["hand"]
    P(img, 1.0).rr(hxh - 150, hyh - 16, hxh + 110, hyh + 16, 6, (150, 116, 80))
    if t > tk - 0.3:
        kolyan(img, 920, 1560, 1.1, t)
    if t > tv_ - 0.2:
        views = int(lerp(1200, 40000, ease((t - tv_) / 2.0)))
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); o = P(ov, 1.0)
        o.rr(80, 330, 1000, 520, 30, (10, 14, 28, 230))
        o.text(120, 352, "«Внук копает бункер. Часть 2»", font(38), (244, 246, 250))
        o.text(120, 420, f"просмотры: {views:,}".replace(",", " "), font(42), AMBER); o.circ(940, 444, 14, RED)
        img.alpha_composite(ov)
    bubble(img, 60, 600, "а вдруг он прав?", (t - tc) / 0.3)
    bubble(img, 420, 740, "где взять фильтр?", (t - tc - 0.7) / 0.3)
    Y5.snow.draw(img, t, 200)
    return img, lerp(1.0, 1.06, ease(t / dur)), 1.0


# ======================================================================= сцена 6: вентиляция
def scene6(t):
    c = cellar(); dur = DUR[5]; tf = wt(5, "Новый фильтр"); tl = wt(5, "Без воздуха"); td = wt(5, "Два дня")
    img = c.base(t, shaft=False, shelf=False, ladder=False)
    p = P(img, 1.0)
    p.rr(200, -20, 320, 700, 20, (110, 84, 66)); p.rr(214, -20, 240, 700, 10, (140, 110, 86))        # ржавая труба
    for (x, y, r) in ((260, 300, 30), (230, 480, 24), (290, 560, 36), (250, 640, 28)): p.circ(x, y, r, (40, 28, 26))
    p.poly([(200, 700), (320, 700), (300, 760), (270, 730), (240, 770), (215, 740)], (110, 84, 66))
    fixed = t > td + 2.2
    fx = 560 if t < tf else lerp(560, 300, ease((t - tf) / 0.8))
    if fixed: fx = 300
    box(p, fx, 1120, 300, 240, "ФИЛЬТР", (150, 116, 80))
    p.rr(fx + 110, 800, fx + 190, 882, 10, (150, 156, 172))                              # патрубок фильтра (уже трубы)
    if fixed:
        p.poly([(200, 700), (320, 700), (fx + 190, 800), (fx + 110, 800)], (168, 172, 184))
        for y in (720, 750, 780): p.line([(206 + (y - 700) * 3.1, y), (318 + (y - 700) * 1.7, y)], (120, 124, 136), 5, round_caps=False)
        glow(img, 330, 760, 200, AMBER, 0.25)
    elif t > tf + 1.0 and t < td:
        glow(img, 330, 790, 120, RED, 0.5 if (t % 0.8) < 0.4 else 0.2)
        p = P(img, 1.0); p.line([(290, 750), (370, 830)], RED, 12); p.line([(370, 750), (290, 830)], RED, 12)
    if td < t <= td + 2.2:
        fact_card(img, t, td, "ДЕНЬ 1 … ДЕНЬ 2")
    pts = hero(img, 880, 1560, 1.15, t, look=(-0.8, -0.3), lamp=True, arm=None,
               brows="worried" if not fixed else "calm", mouth="smile" if fixed else ("flat" if t > tl else None))
    lamp_glow(img, pts["lamp"], True, size=1.15)
    cat(img, 600, 1560, 0.7, t, look=-0.6, ears_back=(tl < t < td))
    if tl < t < td: darkk = 0.8
    return img, lerp(1.0, 1.08, ease(t / dur)), 0.85 if tl < t < td else 1.0


# ======================================================================= сцены 7–8: последняя запись
def written(p, x, y, text, k, size=54, col=INK):
    n = int(len(text) * clamp(k)); p.text(x, y, text[:n], hand(size), col)

def scene7(t):
    c = cellar(); dur = DUR[6]; tl = wt(6, "Последняя"); td = wt(6, "Двадцать"); a, b, d_ = wt(6, "Договорились"), wt(6, "Больше"), wt(6, "Но люк")
    if t < tl:
        img = c.base(t, dark=0.3, shaft=False)
        p = P(img, 1.0)
        pts = hero(img, 460, 1640, 1.2, t, look=(0.3, 0.9), lamp=True, brows="calm", arm="reach")
        lamp_glow(img, pts["lamp"], True, size=1.2)
        hx, hy = pts["hand"]; p = P(img, 1.0)
        p.rr(hx - 70, hy - 60, hx + 90, hy + 50, 8, (60, 80, 110)); p.rr(hx - 58, hy - 50, hx + 78, hy + 40, 4, PAPER)
        glow(img, hx, hy, 220, (255, 236, 196), 0.35)
        p = P(img, 1.0); p.rr(200, 1500, 720, 1700, 16, (90, 66, 48))
        cat(img, 840, 1560, 0.85, t, pose="lie", look=-0.5, dark=0.8)
        return img, lerp(1.0, 1.1, ease(t / tl)), 1.0
    img = darken(c.bg, 0.35)
    lines = [(td, lambda p, k: written(p, 200, 640, "28 октября 1962", k, 86, (120, 60, 50))),
             (a, lambda p, k: written(p, 200, 800, "Договорились.", k, 80)),
             (b, lambda p, k: written(p, 200, 925, "Больше не копаю.", k, 80)),
             (d_, lambda p, k: written(p, 200, 1050, "Но люк не засыпаю.", k, 80))]
    notebook(img, t, lines)
    return img, lerp(1.0, 1.05, ease((t - tl) / (dur - tl))), 1.0


def scene8(t):
    c = cellar(); dur = DUR[7]; ti = wt(7, "Если"); th = wt(7, "Артём берёт"); tq = wt(7, "Как думаешь")
    if t < th:
        img = darken(c.bg, 0.35)
        lines = [(-9, lambda p, k: written(p, 200, 640, "28 октября 1962", 1, 86, (120, 60, 50))),
                 (-9, lambda p, k: written(p, 200, 800, "Договорились.", 1, 80)),
                 (-9, lambda p, k: written(p, 200, 925, "Больше не копаю.", 1, 80)),
                 (-9, lambda p, k: written(p, 200, 1050, "Но люк не засыпаю.", 1, 80)),
                 (ti, lambda p, k: written(p, 200, 1220, "Если начнётся снова —", k * 1.3, 62, (150, 40, 40))),
                 (ti + 1.3, lambda p, k: written(p, 200, 1340, "смотри под 3-й ступенью.", k * 1.3, 62, (150, 40, 40)))]
        notebook(img, t, lines)
        return img, lerp(1.0, 1.08, ease(t / th)), 1.0
    tt = t - th
    img = c.base(t, dark=0.3, shaft=False, shelf=False)
    xl, y, xr = c.steps[5]                                                           # третья ступень снизу
    k = ease(tt / 1.0)
    glow(img, (xl + xr) / 2, y + 10, 260, (255, 240, 200), 0.5 * k, 1.3)
    p = P(img, 1.0); p.rr(xl - 10, y - 4, xr + 10, y + 30, 8, mixc((128, 98, 70), (255, 214, 140), 0.5 * k))
    if tt > 1.6:
        lift = ease((tt - 1.6) / 0.8)
        p.rr(xl - 10, y - 4 - 60 * lift, xr + 10, y + 30 - 60 * lift, 8, (150, 118, 84))
        p.rr(xl + 10, y + 2, xr - 10, y + 40, 6, (8, 6, 8)); glow(img, (xl + xr) / 2, y + 20, 120, AMBER, 0.5 * lift)
    pts = hero(img, 720, 1620, 1.2, t, look=(-0.9, -0.2), lamp=True, arm=None, brows="worried", mouth="o" if tt > 1.6 else None)
    lamp_glow(img, pts["lamp"], True, size=1.2)
    cat(img, 500, 1620, 0.8, t, look=-0.8, ears_back=tt > 1.6)
    if t > tq:
        kk = clamp((t - tq) / 0.6)
        ctext(img, 760, 560, "13", font(int(lerp(140, 200, ease(kk)))), mixc((255, 255, 255), RED, kk))
    return img, lerp(1.0, 1.1, ease(tt / (dur - th))), 1.0


SCENE_FUNCS = [scene1, scene2, scene3, scene4, scene5, scene6, scene7, scene8]


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
