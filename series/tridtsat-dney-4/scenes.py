"""«Тридцать дней», серия 4 «Третий ключ». Сцена: frame(t) -> (RGBA, zoom, bright)."""
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


def wt(i, sub, end=False):
    text = SCENES[i]["text"]; k = text.find(sub); assert k >= 0, (i, sub)
    a = ALN[i]
    return (a["character_end_times_seconds"][k + len(sub) - 1] if end else a["character_start_times_seconds"][k]) + LEAD


def photo(p, x, y, w, h):
    """Старая фотография: трое у железной двери."""
    p.rr(x - 16, y - 16, x + w + 16, y + h + 16, 8, (110, 86, 62))
    p.rect(x, y, x + w, y + h, (196, 176, 140))
    dw = w * 0.34; dx = x + w / 2 - dw / 2
    p.rr(dx, y + h * 0.12, dx + dw, y + h * 0.8, 6, (120, 106, 86)); p.el(dx + dw / 2 - dw * 0.16, y + h * 0.36, dx + dw / 2 + dw * 0.16, y + h * 0.36 + dw * 0.32, None, (90, 78, 62), max(2, int(w * 0.012)))
    for j, u in enumerate((0.2, 0.5, 0.8)):
        cx = x + w * u; s = w / 700
        col = (70, 60, 48)
        p.rr(cx - 46 * s, y + h * 0.5, cx + 46 * s, y + h * 0.96, 30 * s, col)
        p.el(cx - 36 * s, y + h * 0.5 - 84 * s, cx + 36 * s, y + h * 0.5, mixc(col, (255, 255, 255), 0.15))
        p.chord(cx - 40 * s, y + h * 0.5 - 100 * s, cx + 40 * s, y + h * 0.5 - 40 * s, 180, 360, (50, 42, 34))
    p.rect(x, y + h * 0.96, x + w, y + h, (170, 150, 116))


# ======================================================================= 1: заколоченный дом
V1 = None
def scene1(t):
    global V1
    dur = DUR[0]; th = wt(0, "На краю")
    if t < th:
        img = vgrad(W, H, [(0, (20, 22, 30)), (1, (12, 12, 18))])
        iron_door(img, 540, 430, 800, 1050, [True, True, False], names=True, t=t)
        return img, lerp(1.0, 1.08, ease(t / th)), 1.0
    if V1 is None:
        V1 = Village(0.6); V1.snow = Snow(60, 61, (2, 4), (40, 110))
        def l(p):
            V1.house(p, 250, 1320, 1.15, lit=False)
            hh = 330 * 1.15
            for wx in (250 + 70 * 1.15, 250 + 330 * 1.15):                         # доски крест-накрест
                y0 = 1320 - hh + 90 * 1.15
                p.line([(wx - 10, y0 - 6), (wx + 136, y0 + 156)], (124, 98, 72), 16, round_caps=False)
                p.line([(wx + 136, y0 - 6), (wx - 10, y0 + 156)], (124, 98, 72), 16, round_caps=False)
            p.line([(480, 1150), (640, 1150)], (124, 98, 72), 18, round_caps=False)
            V1.fence(p, 1440, 600, W + 40)
        V1.l = layer(W, H, l)
    img = V1.sky.copy(); img.alpha_composite(V1.l)
    tt = t - th
    hx = lerp(-100, 150, ease(tt / 1.6)); walking = tt < 1.6
    pts = hero(img, hx, 1580, 1.0, t, walk=t * 5 if walking else None, look=(0.8, -0.3), lamp=True, brows="worried", dark=0.9)
    lamp_glow(img, pts["lamp"], True, size=1.0)
    cat(img, hx + 190, 1570, 0.6, t, look=0.7, dark=0.85)
    V1.snow.draw(img, t, 190)
    return img, lerp(1.0, 1.08, ease(tt / (dur - th))), 0.9


# ======================================================================= 2–3: внутри, фотография, записка
RM = None
def room():
    global RM
    if RM is None:
        RM = Room(); RM.motes = [(random.random(), random.random(), random.uniform(0, 6.28)) for _ in range(50)]
    return RM

def scene2(t):
    r = room(); dur = DUR[1]; tp = wt(1, "На стене"); tm = wt(1, "Трое")
    if t < tp:
        img = darken(r.bg, 0.45)
        d = ImageDraw.Draw(img)
        for u, v, ph in r.motes:
            x = u * W + 20 * math.sin(t * 0.5 + ph); y = (v + t * 0.02) % 1.0 * 1500
            d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(220, 220, 210, 120))
        k = ease(t / 1.5)
        cat(img, lerp(-80, 240, k), 1570, 0.75, t, look=0.6, dark=0.85)
        pts = hero(img, lerp(-200, 480, k), 1580, 1.1, t, walk=t * 5 if t < 1.5 else None, look=(0.6, -0.4), lamp=True, brows="worried", dark=0.95)
        lamp_glow(img, pts["lamp"], True, size=1.1)
        kolyan(img, lerp(-500, 860, ease((t - 0.3) / 1.6)), 1590, 1.1, t, rec=False, serious=True, look=-0.4, dark=0.85)
        glow(img, 270, 520, 420, (255, 240, 200), 0.22, 1.4)
        return img, lerp(1.0, 1.08, ease(t / tp)), 1.0
    img = darken(r.bg, 0.3); p = P(img, 1.0)
    photo(p, 170, 560, 740, 700)
    img = sepia(img, 0.25)
    glow(img, 540, 900, 760, (255, 236, 196), 0.2, 1.5)
    fact_card(img, t, wt(1, "Шестьдесят"), "1962 ГОД")
    return img, lerp(1.0, 1.1, ease((t - tp) / (dur - tp))), 1.0


def scene3(t):
    r = room(); dur = DUR[2]; tz = wt(2, "Но за"); tk = wt(2, "Ключ у"); ta = wt(2, "И городской")
    img = darken(r.bg, 0.3); p = P(img, 1.0)
    k = ease((t - tz) / 0.9)
    if k > 0:                                                                   # записка за рамкой
        p.rr(300, 760, 780, 1100, 8, PAPER)
        for yy in range(820, 1080, 52): p.line([(340, yy), (740, yy)], INK, 5, round_caps=False)
        glow(img, 540, 930, 300, AMBER, 0.25 * k)
    if k < 1:
        off = 760 * k
        photo(P(img, 1.0, ox=off * 0.9, oy=-off * 0.25), 170, 560, 740, 700)
    if t > tk - 0.2:
        img = darken(cellar_bg(), 0.35)
        notebook(img, t, [(tk, lambda p, k: written(p, 200, 640, "Ключ у дочери.", k * 1.2, 84)),
                          (tk + 0.9, lambda p, k: written(p, 200, 790, "Нина Вершинина", k * 1.2, 84, (150, 40, 40))),
                          (ta, lambda p, k: written(p, 200, 980, "г. Заречный,", k * 1.3, 70)),
                          (ta + 0.6, lambda p, k: written(p, 200, 1090, "ул. Садовая, 14, кв. 7", k * 1.3, 70))])
    else:
        glow(img, 540, 900, 760, (255, 236, 196), 0.2, 1.5)
    return img, lerp(1.0, 1.06, ease(t / dur)), 1.0

_CB = None
def cellar_bg():
    global _CB
    if _CB is None: _CB = room().bg
    return _CB


# ======================================================================= 4: деревня спорит
Y4 = None
def scene4(t):
    global Y4
    if Y4 is None:
        Y4 = Yard(0.2); Y4.snow = Snow(40, 71, (2, 4), (40, 100))
        rnd = random.Random(12)
        Y4.crowd = [(60 + i * 86 + rnd.uniform(-16, 16), 1330 + (i % 3) * 60, rnd.uniform(0.8, 1.0),
                     mixc((56, 62, 84), (92, 80, 96), rnd.random()), mixc((90, 70, 60), (60, 80, 100), rnd.random()), rnd.uniform(0, 6)) for i in range(12)]
    dur = DUR[3]; tm = wt(3, "Мест"); tj = wt(3, "Жителей"); tn = wt(3, "И каждый"); tv = wt(3, "Вчера"); ts = wt(3, "Сегодня")
    img = Y4.bg.copy(); p = P(img, 1.0)
    if t > tn:
        van(p, lerp(1500, 860, ease((t - tn) / 1.2)), 1300, 0.8)
    solo = t > tv
    for (x, y, s, c, h, ph) in sorted(Y4.crowd, key=lambda a: a[1]):
        dx = 0 if not solo else (x - 540) * 0.25 * ease((t - tv) / 0.8)
        silhouette(p, x + dx + 4 * math.sin(t * 3 + ph), y + (60 if solo else 0) * 0 + 3 * abs(math.sin(t * 4 + ph)), s, c, hat=h)
    if solo:
        hero(img, 540, 1570, 1.1, t, look=(math.sin(t * 2) * 0.8, 0.0), brows="worried", mouth="flat")
        if t > ts:
            bubble(img, 70, 560, "возьми меня", (t - ts) / 0.25); bubble(img, 620, 640, "и меня!", (t - ts - 0.4) / 0.25)
            bubble(img, 240, 760, "у меня дети", (t - ts - 0.8) / 0.25)
    else:
        bubble(img, 80, 560, "я первый записался", (t - 0.6) / 0.3); bubble(img, 520, 690, "а мы тут родились!", (t - 1.3) / 0.3)
    if tm - 0.2 < t < tv:
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); o = P(ov, 1.0)
        o.rr(120, 320, 960, 500, 30, (10, 14, 28, 235))
        ctext(ov, 330, 340, "МЕСТ", font(40), (200, 206, 224)); ctext(ov, 330, 390, "40", font(84), AMBER)
        if t > tj:
            ctext(ov, 750, 340, "ЖИТЕЛЕЙ", font(40), (200, 206, 224)); ctext(ov, 750, 390, "60", font(84), RED)
        img.alpha_composite(ov)
    Y4.snow.draw(img, t, 200)
    return img, lerp(1.0, 1.06, ease(t / dur)), 1.0


# ======================================================================= 5–6: город, Нина
class City:
    def __init__(s):
        s.sky = vgrad(W, H, [(0, (70, 86, 120)), (0.6, (150, 160, 184)), (1, (190, 196, 210))])
        rnd = random.Random(23)
        def b(p):
            x = -40
            while x < W + 400:
                w = rnd.randint(150, 260); h = rnd.randint(380, 820)
                p.rect(x, 1300 - h, x + w, 1320, mixc((84, 94, 122), (110, 116, 140), rnd.random()))
                for wy in range(1300 - h + 30, 1280, 56):
                    for wx in range(x + 18, x + w - 30, 44): p.rr(wx, wy, wx + 22, wy + 32, 3, (255, 214, 140) if rnd.random() < 0.3 else (60, 70, 98))
                x += w + rnd.randint(10, 30)
            p.rect(-40, 1310, W + 440, H, (96, 100, 116)); p.rect(-40, 1420, W + 440, 1600, (60, 62, 74))
            for xx in range(0, W + 400, 150): p.rr(xx, 1504, xx + 80, 1514, 4, (150, 150, 160))
        s.b = layer(W + 400, H, b)

def bus(p, x, y):
    p.rr(x - 300, y - 260, x + 300, y - 20, 30, (200, 170, 70))
    for k in range(5): p.rr(x - 270 + k * 108, y - 230, x - 180 + k * 108, y - 140, 10, (150, 176, 210))
    p.rect(x - 300, y - 110, x + 300, y - 96, (150, 120, 40))
    p.circ(x - 180, y - 20, 44, (18, 18, 24)); p.circ(x + 180, y - 20, 44, (18, 18, 24))

CITY = None
def hall(img):
    p = P(img, 1.0)
    p.rect(0, 0, W, H, (72, 78, 70)); p.rect(0, 1100, W, H, (58, 64, 60)); p.rect(0, 1090, W, 1104, (96, 100, 90))
    p.rect(0, 1560, W, H, (52, 46, 44))
    p.rr(520, 380, 960, 1570, 10, (52, 42, 40)); p.rr(546, 406, 934, 1570, 8, (26, 22, 26))
    p.poly([(934, 406), (1040, 350), (1040, 1640), (934, 1570)], (110, 80, 60))
    p.rr(700, 300, 780, 350, 8, (200, 200, 190)); p.text(722, 304, "7", font(36), (40, 40, 40))

def scene5(t):
    global CITY
    if CITY is None: CITY = City()
    dur = DUR[4]; td = wt(4, "Дверь"); tf = wt(4, "Она долго"); tb = wt(4, "И молча")
    if t < td:
        img = CITY.sky.copy(); comp(img, CITY.b, -t * 120, 0)
        by_ = 1530 + 3 * math.sin(t * 9)
        p = P(img, 1.0); bus(p, 540, by_)
        hero(img, 420, by_ - 30, 0.42, t, look=(0.6, 0.0)); cat(img, 530, by_ - 150, 0.22, t, head_only=True)
        p = P(img, 1.0); p.rect(240, by_ - 140, 840, by_ - 20, (200, 170, 70)); p.rect(240, by_ - 110, 840, by_ - 96, (150, 120, 40))
        p.rr(240, by_ - 60, 840, by_ - 20, 20, (200, 170, 70)); p.circ(360, by_ - 20, 44, (18, 18, 24)); p.circ(720, by_ - 20, 44, (18, 18, 24))
        return img, 1.05, 1.0
    img = Image.new("RGBA", (W, H)); hall(img)
    glow(img, 740, 900, 520, WARM, 0.25, 1.4)
    nina(img, 740, 1560, 1.25, t, look=-0.7)
    pts = hero(img, 260, 1580, 1.15, t, look=(0.8, 0.0), arm="reach" if t > tf - 0.8 else None, brows="calm")
    if t > tf - 0.8 and t < tb:
        hx, hy = pts["hand"]; photo(P(img, 1.0), hx - 20, hy - 130, 150, 140)
    if t > tb:
        k = ease((t - tb) / 0.8); p = P(img, 1.0)
        bx, by = 720, lerp(1500, 1180, k)
        p.rr(bx - 80, by - 50, bx + 80, by + 50, 10, (120, 70, 60)); p.rr(bx - 80, by - 50, bx + 80, by - 24, 6, (150, 96, 80))
        p.circ(bx, by, 10, KEYC); glow(img, bx, by, 160, AMBER, 0.3 * k)
    return img, lerp(1.0, 1.08, ease((t - td) / (dur - td))), 1.0


def scene6(t):
    dur = DUR[5]; tk = wt(5, "Она отдаёт"); tq = wt(5, "Возьмите")
    img = Image.new("RGBA", (W, H)); hall(img)
    glow(img, 600, 900, 700, WARM, 0.25, 1.4)
    ku = ease((t - tk) / 0.8)
    pt = nina(img, 600, 1680, 1.6, t, look=-0.3, key_up=ku)
    if ku > 0.2:
        hx, hy = pt["hand"]; glow(img, hx, hy - 90, 180, AMBER, 0.5 * ku); key(P(img, 1.0), hx, hy - 70, 1.2)
    if t < tk: bubble(img, 90, 520, "только всем вместе", (t - 0.5) / 0.3)
    bubble(img, 120, 520, "возьмите меня с собой", (t - tq) / 0.3)
    return img, lerp(1.0, 1.08, ease(t / dur)), 1.0


# ======================================================================= 7–8: возвращение
FLD = None
def scene7(t):
    global FLD
    if FLD is None: FLD = Field()
    f = FLD; dur = DUR[6]; tk = wt(6, "Артём достаёт"); tn = wt(6, "Но он")
    img = f.sky.copy(); img.alpha_composite(f.barn)
    p = P(img, 1.0)
    p.poly([(640, 1480), (1060, 1480), (1020, 1310), (680, 1310)], (112, 114, 120)); p.poly([(730, 1460), (970, 1460), (950, 1330), (750, 1330)], IRON)
    walking = t < tk
    k = ease(t / tk) if walking else 1.0
    nina(img, lerp(-520, 90, k), 1560, 0.9, t, look=0.7, dark=0.85)
    kolyan(img, lerp(-360, 290, k), 1570, 0.98, t, phone_up=False, serious=True, look=0.6, dark=0.85)
    cat(img, lerp(40, 680, k), 1570, 0.55, t, look=0.7, dark=0.8, ears_back=t > tn)
    pts = hero(img, lerp(-160, 510, k), 1575, 1.0, t, walk=t * 5 if walking else None, look=(0.8, 0.3), lamp=True,
               arm="up" if tk < t < tn + 0.3 else None, brows="worried", mouth="o" if t > tn else None, dark=0.9)
    lamp_glow(img, pts["lamp"], True, size=1.0)
    if tk < t < tn + 0.3:
        hx, hy = pts["hand"]; glow(img, hx, hy - 60, 140, AMBER, 0.5); key(P(img, 1.0), hx, hy - 40, 0.8)
    if t > tn: glow(img, 850, 1395, 260, AMBER, 0.35 + 0.1 * math.sin(t * 6))
    f.snow.draw(img, t, 190)
    return img, lerp(1.0, 1.1, ease(t / dur)), 0.92


def scene8(t):
    dur = DUR[7]; td = wt(7, "Дверь"); ts = wt(7, "На снегу"); tq = wt(7, "Как думаешь")
    img = vgrad(W, H, [(0, (20, 22, 30)), (1, (12, 12, 18))])
    iron_door(img, 540, 330, 800, 930, [True, True, True], names=True, t=t)
    if t > td:
        k = ease((t - td) / 0.8); p = P(img, 1.0)
        gx = 940 - 110 * k
        p.poly([(gx, 330), (940, 330), (940, 1260), (gx, 1260)], (6, 6, 10))
        p.poly([(gx, 330), (gx + 22, 350), (gx + 22, 1240), (gx, 1260)], IRON_D)
        glow(img, (gx + 940) / 2, 800, 240, AMBER, 0.22 * k * (0.8 + 0.2 * math.sin(t * 7)))
    p = P(img, 1.0); p.rect(0, 1320, W, H, (150, 160, 184)); p.rr(-20, 1300, W + 20, 1350, 24, (176, 186, 208))
    if t > ts:
        n = int(8 * clamp((t - ts) / 1.4))
        for j in range(n):
            x = 120 + j * 100; y = 1540 - j * 22 + (16 if j % 2 else -16)
            p.el(x - 20, y - 34, x + 20, y + 20, (96, 106, 134)); p.el(x - 14, y + 22, x + 14, y + 44, (96, 106, 134))
    if t > tq:
        kk = clamp((t - tq) / 0.6)
        ctext(img, 340, 470, "7", font(int(lerp(130, 200, ease(kk)))), mixc((255, 255, 255), RED, kk))
    return img, lerp(1.0, 1.08, ease(t / dur)), 1.0


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
