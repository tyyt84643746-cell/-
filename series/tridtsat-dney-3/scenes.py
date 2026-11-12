"""«Тридцать дней», серия 3 «Три замка». Сцена: frame(t) -> (RGBA, zoom, bright)."""
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
KEYC = (214, 180, 96); IRON = (86, 90, 102); IRON_D = (58, 60, 70)
NAMES = ["Громов", "Савельев", "Вершинин"]


def wt(i, sub, end=False):
    text = SCENES[i]["text"]; k = text.find(sub); assert k >= 0, (i, sub)
    a = ALN[i]
    return (a["character_end_times_seconds"][k + len(sub) - 1] if end else a["character_start_times_seconds"][k]) + LEAD


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


def letter(img, t, lines, y0=520):
    notebook(img, t, lines, y0=y0)


CEL = None
def cellar():
    global CEL
    if CEL is None: CEL = Cellar()
    return CEL


# ======================================================================= 1: коробка под ступенью
def scene1(t):
    c = cellar(); dur = DUR[0]; tb = wt(0, "В ней"); tl = wt(0, "Если ты")
    if t < tl:
        img = c.base(t, dark=0.3, shaft=False, shelf=False)
        xl, y, xr = c.steps[5]
        p = P(img, 1.0); p.rr(xl + 10, y + 2, xr - 10, y + 40, 6, (8, 6, 8))
        p.rr(xl - 10, y - 64, xr + 10, y - 30, 8, (150, 118, 84))
        k = ease(t / 1.2); bx = lerp((xl + xr) / 2, 560, k); by = lerp(y + 20, 1150, k)
        glow(img, bx, by, 260, AMBER, 0.35)
        p = P(img, 1.0); ko = ease((t - tb) / 0.6)
        p.rr(bx - 150, by - 70, bx + 150, by + 70, 14, (120, 136, 128)); p.rr(bx - 150, by - 70, bx + 150, by - 40, 8, (96, 110, 104))
        for dx in (-100, 0, 100): p.el(bx + dx - 24, by - 14, bx + dx + 24, by + 34, None, (168, 150, 110), 5)
        if ko > 0:
            p.poly([(bx - 150, by - 70), (bx + 150, by - 70), (bx + 140, by - 70 - 150 * ko), (bx - 140, by - 70 - 150 * ko)], (138, 152, 144))
            p.rr(bx - 110, by - 110 * ko - 40, bx - 10, by - 30, 6, PAPER); p.rr(bx + 10, by - 130 * ko - 40, bx + 120, by - 30, 6, (214, 196, 160))
        pts = hero(img, 820, 1600, 1.15, t, look=(-0.8, 0.3), lamp=True, brows="worried", mouth="o" if ko > 0.3 else None)
        lamp_glow(img, pts["lamp"], True, size=1.15)
        cat(img, 240, 1600, 0.8, t, look=0.7, ears_back=t < 1.0)
        return img, lerp(1.0, 1.1, ease(t / tl)), 1.0
    img = darken(c.bg, 0.35)
    letter(img, t, [(tl, lambda p, k: written(p, 200, 700, "Если ты это читаешь —", k * 1.2, 68)),
                    (wt(0, "значит"), lambda p, k: written(p, 200, 840, "значит, опять началось.", k * 1.2, 68, (150, 40, 40)))])
    return img, lerp(1.0, 1.05, (t - tl) / (dur - tl)), 1.0


# ======================================================================= 2: письмо и карта
def village_map(img, t, t0, tx):
    p = P(img, 1.0)
    p.rr(70, 460, 1010, 1520, 18, (70, 52, 40)); p.rr(90, 480, 990, 1500, 10, (214, 196, 160))
    k = clamp((t - t0) / 1.0)
    pts = [(120 + i * 30, 1260 + 40 * math.sin(i * 0.5)) for i in range(29)]                    # речка
    p.line(pts[: max(2, int(len(pts) * k))], (90, 120, 160), 10)
    if k > 0.3:
        p.line([(160, 760), (900, 900)], (120, 100, 80), 8)                                     # дорога
        for (x, y) in ((220, 680), (360, 700), (520, 740), (240, 860), (420, 880), (620, 900)):
            p.rr(x, y, x + 70, y + 56, 4, None, INK, 5); p.poly([(x - 8, y), (x + 78, y), (x + 35, y - 36)], INK)
        p.text(210, 600, "деревня", hand(52), INK)
        p.rr(232, 852, 318, 924, 6, None, (150, 40, 40), 6); p.text(150, 930, "наш дом", hand(44), (150, 40, 40))
    kx = clamp((t - tx) / 0.9)
    if kx > 0:
        a, b = (275, 890), (780, 1080)
        n = int(12 * kx)
        for j in range(n):
            u0, u1 = j / 12, (j + 0.55) / 12
            p.line([(lerp(a[0], b[0], u0), lerp(a[1], b[1], u0)), (lerp(a[0], b[0], u1), lerp(a[1], b[1], u1))], (150, 40, 40), 7)
        if kx >= 1:
            p.line([(740, 1040), (820, 1120)], (150, 40, 40), 14); p.line([(820, 1040), (740, 1120)], (150, 40, 40), 14)
            p.rr(700, 1000, 860, 1160, 8, None, INK, 5); p.text(650, 1170, "зерносклад", hand(50), INK)
            glow(img, 780, 1080, 200, AMBER, 0.3 + 0.1 * math.sin(t * 5))
    glow(img, 540, 980, 700, (255, 236, 196), 0.14, 1.5)


def scene2(t):
    c = cellar(); dur = DUR[1]; ta, tb, tm, tp = wt(1, "погреб был"), wt(1, "Настоящее"), wt(1, "Оно под"), wt(1, "Места")
    img = darken(c.bg, 0.35)
    if t < tm:
        letter(img, t, [(ta, lambda p, k: written(p, 200, 640, "Погреб — запасной.", k * 1.2, 76)),
                        (tb, lambda p, k: written(p, 200, 800, "Настоящее убежище", k * 1.2, 76)),
                        (tb + 0.9, lambda p, k: written(p, 200, 920, "строили всей деревней.", k * 1.2, 76))])
        return img, lerp(1.0, 1.05, t / tm), 1.0
    village_map(img, t, tm - 0.3, tm + 0.6)
    fact_card(img, t, tp, "МЕСТ: 40")
    return img, lerp(1.0, 1.06, ease((t - tm) / (dur - tm))), 1.0


# ======================================================================= 3: ночь, склад
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

FLD = None
def scene3(t):
    global FLD
    if FLD is None: FLD = Field()
    f = FLD; dur = DUR[2]; ts = wt(2, "Склад"); tu = wt(2, "Под досками"); td = wt(2, "И железную")
    img = f.sky.copy(); img.alpha_composite(f.barn)
    kd = ease((t - tu) / 1.4)
    if kd > 0:
        p = P(img, 1.0)
        p.poly([(420, 1500), (880, 1500), (840, 1330), (460, 1330)], (112, 114, 120))               # плита
        kk = ease((t - td) / 0.6)
        if kk > 0:
            p.poly([(520, 1480), (780, 1480), (760, 1350), (540, 1350)], mixc((112, 114, 120), IRON, kk))
            p.el(620, 1390, 680, 1440, None, IRON_D, 8); glow(img, 650, 1415, 220, AMBER, 0.25 * kk)
        p = P(img, 1.0)
        for j, dx in enumerate((-170, -60, 60, 170)):
            off = (-1 if j < 2 else 1) * 300 * kd
            p.poly([(650 + dx - 50 + off, 1510), (650 + dx + 50 + off, 1510), (650 + dx + 42 + off, 1320), (650 + dx - 42 + off, 1320)], (74, 58, 50))
    walking = t < tu
    hx = lerp(-80, 220, ease(t / tu)) if walking else 220
    cat(img, hx + 190, 1560, 0.6, t, look=0.7, dark=0.8)
    pts = hero(img, hx, 1570, 1.05, t, walk=t * 5 if walking else None, look=(0.8, 0.4), lamp=True,
               mouth="o" if t > td else None, brows="worried", dark=0.85)
    lamp_glow(img, pts["lamp"], True, size=1.05)
    glow(img, pts["lamp"][0] + 330, pts["lamp"][1] + 380, 380, (255, 240, 200), 0.22, 1.4)
    steam(img, *pts["mouth"], t, scale=1.0)
    f.snow.draw(img, t, 190)
    return img, lerp(1.0, 1.1, ease(t / dur)), 0.92


# ======================================================================= 4: три замка
def scene4(t):
    dur = DUR[3]; tk = wt(3, "Ключ бабушки"); tn = wt(3, "В письме")
    img = vgrad(W, H, [(0, (20, 22, 30)), (1, (12, 12, 18))])
    opened = t > tk + 1.3
    iron_door(img, 540, 430, 800, 1050, [opened, False, False], names=t > tn, t=t)
    if tk < t < tk + 1.6:
        k = ease((t - tk) / 1.0); x = 540 - 240; ly = 430 + 1050 * 0.72
        p = P(img, 1.0); key(p, lerp(x - 260, x - 4, k), ly + 30, 1.1)
        glow(img, lerp(x - 260, x, k), ly, 120, AMBER, 0.4)
    glow(img, 540, 900, 760, (255, 240, 200), 0.12, 1.5)
    if t > tn: fact_card(img, t, wt(3, "У каждой"), "3 СЕМЬИ · 3 КЛЮЧА")
    return img, lerp(1.0, 1.08, ease(t / dur)), 1.0


# ======================================================================= 5: миллион
def van(p, x, y, s=1.0):
    p.rr(x - 220 * s, y - 190 * s, x + 200 * s, y - 20 * s, 30 * s, (70, 80, 110))
    p.rr(x + 60 * s, y - 170 * s, x + 180 * s, y - 100 * s, 14 * s, (150, 176, 210))
    p.rr(x - 190 * s, y - 160 * s, x + 20 * s, y - 80 * s, 12 * s, (54, 62, 90))
    p.circ(x - 130 * s, y - 20 * s, 40 * s, (18, 18, 24)); p.circ(x + 120 * s, y - 20 * s, 40 * s, (18, 18, 24))
    p.line([(x - 100 * s, y - 190 * s), (x - 100 * s, y - 260 * s)], (150, 156, 172), 6 * s); p.chord(x - 150 * s, y - 300 * s, x - 50 * s, y - 230 * s, 0, 180, (150, 156, 172))

Y5 = None
def scene5(t):
    global Y5
    dur = DUR[4]; tb = wt(4, "В деревню"); tm = wt(4, "Незнакомые")
    if t < tb:
        img = Image.new("RGBA", (W, H), (10, 12, 22, 255)); p = P(img, 1.0)
        p.rr(160, 360, 920, 1560, 60, (18, 20, 28)); p.rr(186, 386, 894, 1534, 44, (30, 36, 60))
        p.rr(220, 440, 860, 900, 20, (60, 72, 100)); p.poly([(480, 600), (480, 760), (620, 680)], (240, 244, 250))
        p.text(220, 930, "Внук копает бункер", font(46), (244, 246, 250)); p.text(220, 990, "Часть 2", font(38), (150, 160, 190))
        views = int(lerp(40_000, 1_000_000, ease(t / (tb - 0.3))))
        ctext(img, 540, 1110, f"{views:,}".replace(",", " "), font(104), AMBER); ctext(img, 540, 1240, "просмотров", font(44), (200, 206, 224))
        if views >= 1_000_000: glow(img, 540, 1160, 420, AMBER, 0.2)
        return img, lerp(1.0, 1.08, ease(t / tb)), 1.0
    if Y5 is None:
        Y5 = Yard(0.2); Y5.snow = Snow(40, 44, (2, 4), (40, 100))
    img = Y5.bg.copy(); p = P(img, 1.0)
    vx = lerp(1400, 760, ease((t - tb) / 1.4)); van(p, vx, 1470, 1.0)
    if t > tb + 1.2:
        for j, x in enumerate((420, 560)):
            silhouette(p, x, 1500, 0.9, (60, 66, 92), hat=(110, 70, 70) if j else (70, 90, 110))
            p.line([(x + 40, 1300), (x + 90, 1150)], (40, 44, 60), 8); p.rr(x + 70, 1090, x + 116, 1160, 6, (205, 228, 255))
    hero(img, 170, 1560, 1.05, t, look=(0.8, 0.0), brows="worried", arm="phone" if t > tm - 0.3 else None, phone_on=True)
    bubble(img, 330, 520, "возьми нас к себе", (t - tm - 0.2) / 0.3)
    bubble(img, 420, 650, "сколько стоит место?", (t - tm - 0.8) / 0.3)
    bubble(img, 360, 780, "я с детьми", (t - tm - 1.4) / 0.3)
    Y5.snow.draw(img, t, 200)
    return img, 1.04, 1.0


# ======================================================================= 6–7: Колян
Y6 = None
def scene6(t):
    global Y6
    if Y6 is None:
        Y6 = Yard(0.15); Y6.snow = Snow(40, 55, (2, 4), (40, 100))
    c = cellar(); dur = DUR[5]; ta = wt(5, "Артём молча"); tl = wt(5, "Вторая"); tk = wt(5, "Это фамилия")
    if t < tl:
        img = Y6.bg.copy()
        show = t > ta
        pts = hero(img, 330, 1560, 1.1, t, look=(0.8, 0.0), arm="reach" if show else None, brows="calm", mouth="flat")
        if show:
            hx, hy = pts["hand"]; p = P(img, 1.0); p.rr(hx - 30, hy - 90, hx + 90, hy + 50, 6, PAPER)
            for yy in range(-60, 40, 26): p.line([(hx - 14, hy + yy), (hx + 74, hy + yy)], INK, 4, round_caps=False)
        kolyan(img, 800, 1570, 1.15, t, serious=show and t > ta + 1.0, look=-0.7 if show else 0.0)
        Y6.snow.draw(img, t, 200)
        return img, lerp(1.0, 1.06, ease(t / tl)), 1.0
    img = darken(c.bg, 0.35)
    def names(p, k):
        p.text(200, 600, "Ключи у трёх семей:", hand(70), INK)
        for j, nm in enumerate(NAMES):
            p.text(260, 770 + j * 150, f"{j + 1}. {nm}", hand(96), INK)
    def mark(p, k):
        p.line([(250, 1040), (250 + 560 * k, 1040)], (190, 60, 50), 12)
        if k >= 1: p.rr(220, 900, 840, 1060, 16, None, (190, 60, 50), 8)
    letter(img, t, [(-9, names), (tk - 0.2, mark)])
    return img, lerp(1.0, 1.08, ease((t - tl) / (dur - tl))), 1.0


class Room:
    def __init__(s):
        s.bg = vgrad(W, H, [(0, (44, 38, 44)), (1, (26, 22, 28))])
        def deco(p):
            for x in range(-40, W, 100): p.rect(x, 0, x + 94, 1480, (62, 50, 46))
            p.rect(0, 1480, W, H, (40, 32, 32))
            p.rr(120, 360, 420, 700, 8, (30, 30, 40)); p.rr(110, 350, 430, 710, 10, None, (110, 90, 70), 12)       # рамка с фото
            p.el(220, 440, 320, 560, (90, 84, 80)); p.rr(190, 560, 350, 690, 30, (70, 66, 64))
        s.bg.alpha_composite(layer(W, H, deco))

ROOM = None
def scene7(t):
    global ROOM, Y6
    dur = DUR[6]; th = wt(6, "Дома"); tk = wt(6, "На дне")
    if t < th:
        if Y6 is None:
            Y6 = Yard(0.15); Y6.snow = Snow(40, 55, (2, 4), (40, 100))
        img = Y6.bg.copy()
        down = t > 0.9
        kolyan(img, 540, 1580, 1.5, t, phone_up=not down, serious=down, rec=not down, look=-0.3 if down else 0.0)
        Y6.snow.draw(img, t, 200)
        return img, lerp(1.0, 1.1, ease(t / th)), 1.0
    if ROOM is None: ROOM = Room()
    tt = t - th; img = ROOM.bg.copy(); p = P(img, 1.0)
    ko = ease((tt - 0.5) / 0.8)
    p.rr(250, 1180, 830, 1500, 18, (96, 66, 46))
    for x in (300, 540, 780): p.rect(x - 14, 1180, x + 14, 1500, (60, 62, 70))
    p.poly([(250, 1180), (830, 1180), (850 - 20 * ko, 1180 - 240 * ko - 40 * (1 - ko)), (230 + 20 * ko, 1180 - 240 * ko - 40 * (1 - ko))], (110, 78, 54))
    if ko > 0.6: p.rr(270, 1190, 810, 1260, 8, (24, 18, 18))
    kk = ease((t - tk) / 0.7)
    if kk > 0:
        ky = lerp(1240, 900, kk); glow(img, 540, ky - 30, 260, AMBER, 0.45 * kk); key(P(img, 1.0), 540, ky, 1.3)
    kolyan(img, 860, 1900, 1.35, t, phone_up=False, serious=True, look=-0.8)
    return img, lerp(1.0, 1.08, ease(tt / (dur - th))), 1.0


# ======================================================================= 8: третий замок
def scene8(t):
    dur = DUR[7]; tt3 = wt(7, "Третий"); tq = wt(7, "Как думаешь")
    img = vgrad(W, H, [(0, (20, 22, 30)), (1, (12, 12, 18))])
    second = t > 0.9
    iron_door(img, 540, 430, 800, 1050, [True, True if second else False, False], names=True, t=t)
    if t < 1.2:
        k = ease(t / 0.8); ly = 430 + 1050 * 0.72; key(P(img, 1.0), lerp(900, 536, k), ly + 30, 1.1)
    if t > tt3:
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); o = P(ov, 1.0)
        k = ease((t - tt3) / 0.4); x = 780; y = 880
        o.el(x - 70, y - 150, x + 70, y - 10, None, (230, 58, 58, int(255 * k)), 10); ctext(ov, x, y - 138, "?", font(110), (230, 58, 58, int(255 * k)))
        img.alpha_composite(ov)
    if t > tq:
        kk = clamp((t - tq) / 0.6)
        ctext(img, 540, 500, "10", font(int(lerp(130, 190, ease(kk)))), mixc((255, 255, 255), RED, kk))
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
