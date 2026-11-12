"""«Тридцать дней», серия 5 «Кто внутри». Сцена: frame(t) -> (RGBA, zoom, bright)."""
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


SH = None
def shelter():
    global SH
    if SH is None: SH = Shelter()
    return SH


def name_card(img, t, t0, txt):
    fact_card(img, t, t0, txt)


def cage(p, x0, y0, x1, y1, col=(120, 124, 136)):
    p.rr(x0, y0, x1, y1, 8, None, col, 12)
    for x in range(int(x0) + 50, int(x1), 50): p.line([(x, y0), (x, y1)], col, 5, round_caps=False)
    for y in range(int(y0) + 60, int(y1), 60): p.line([(x0, y), (x1, y)], col, 5, round_caps=False)


def stash(p, t=0.0):
    """Склад Кирилла: всё новое."""
    p.rr(110, 1180, 420, 1440, 16, (200, 150, 50)); p.rr(140, 1210, 390, 1300, 8, (40, 40, 46)); p.rr(200, 1130, 330, 1186, 14, None, (40, 40, 46), 12)
    p.circ(170, 1380, 22, (40, 40, 46)); p.circ(360, 1380, 22, (220, 60, 50))
    for k in range(3): box(p, 460 + k * 8, 1440 - k * 150, 250, 140, "ФИЛЬТР", (176, 180, 190))
    for k in range(4):
        p.rr(740 + k * 62, 1240, 792 + k * 62, 1440, 14, (80, 140, 200)); p.rr(752 + k * 62, 1222, 780 + k * 62, 1242, 5, (40, 80, 150))
    for r in range(3):
        for k in range(3): box(p, 730 + k * 96, 1220 - r * 110, 90, 100, None, (150, 116, 80))


# ======================================================================= 1: вход
def scene1(t):
    s = shelter(); dur = DUR[0]; ta = wt(0, "Артём входит"); tk = wt(0, "Кекс")
    if t < ta:
        img = vgrad(W, H, [(0, (20, 22, 30)), (1, (12, 12, 18))])
        iron_door(img, 540, 330, 800, 930, [True, True, True], names=False, t=t)
        k = ease(t / 1.2); p = P(img, 1.0); gx = 940 - lerp(110, 420, k)
        p.poly([(gx, 330), (940, 330), (940, 1260), (gx, 1260)], (10, 10, 14))
        p.poly([(gx, 330), (gx + 22, 350), (gx + 22, 1240), (gx, 1260)], IRON_D)
        glow(img, (gx + 940) / 2, 800, 420, AMBER, 0.3 * (0.8 + 0.2 * math.sin(t * 7)))
        p = P(img, 1.0); p.rect(0, 1320, W, H, (150, 160, 184))
        return img, lerp(1.0, 1.12, ease(t / ta)), 1.0
    tt = t - ta
    img = s.base(t, dark=0.35)
    glow(img, 900, 900, 460, AMBER, 0.2 + 0.05 * math.sin(t * 6), 1.4)
    k = ease(tt / 1.4)
    hiss = t > tk
    cat(img, lerp(-80, 330, k), 1570, 0.75, t, look=0.8, ears_back=hiss, yawn=hiss and (t * 3 % 1) < 0.6, dark=0.9)
    pts = hero(img, lerp(-240, 130, k), 1580, 1.1, t, walk=t * 5 if tt < 1.4 else None, look=(0.8, 0.0), lamp=True, brows="worried", dark=0.95)
    lamp_glow(img, pts["lamp"], True, size=1.1)
    return img, lerp(1.0, 1.06, ease(tt / (dur - ta))), 1.0


# ======================================================================= 2: зал
def scene2(t):
    s = shelter(); dur = DUR[1]; tb = wt(1, "Сорок"); tp = wt(1, "На стенах"); tn = wt(1, "Но на одной")
    img = s.base(t, dark=0.55)
    sweep = lerp(150, 930, ease(t / (tn - 0.4)))                                       # луч фонарика гуляет по залу
    glow(img, sweep, 760 if t > tp else 1150, 420, (255, 240, 200), 0.3, 1.4)
    if t > tn:
        k = ease((t - tn) / 0.6); p = P(img, 1.0)
        p.rr(660, 1010, 1060, 1066, 26, mixc((60, 110, 130), (80, 170, 190), k)); p.rr(660, 1010, 760, 1066, 26, (60, 110, 130))
        glow(img, 860, 1040, 300, (120, 220, 240), 0.35 * k)
    if tb < t < tp: fact_card(img, t, tb, "40 КОЕК")
    pts = hero(img, 170, 1580, 1.0, t, view="back", lamp=True, dark=0.8)
    return img, lerp(1.0, 1.1, ease(t / dur)), 1.0


# ======================================================================= 3: Кирилл
def scene3(t):
    s = shelter(); dur = DUR[2]; tk = wt(2, "Это Кирилл")
    img = s.base(t, dark=0.45)
    k = ease(t / 1.6)
    nina(img, 120, 1560, 0.95, t, look=0.8, dark=0.85)
    kolyan(img, 300, 1570, 1.0, t, phone_up=False, serious=True, look=0.8, dark=0.85)
    pts = hero(img, 480, 1575, 1.05, t, look=(0.9, 0.0), lamp=True, brows="worried", mouth="o" if t < 2.0 else None, dark=0.95)
    lamp_glow(img, pts["lamp"], True, size=1.05)
    kx = lerp(1300, 860, k)
    pk = kirill(img, kx, 1580, 1.1, t, look=-0.8, dark=lerp(0.3, 1.0, k))
    glow(img, pk["lantern"][0], pk["lantern"][1], 300, AMBER, 0.4 * k)
    name_card(img, t, tk, "КИРИЛЛ ВЕРШИНИН · ВНУК")
    return img, lerp(1.0, 1.08, ease(t / dur)), 1.0


# ======================================================================= 4: разговор
def scene4(t):
    s = shelter(); dur = DUR[3]; tq = wt(3, "Ты хотел"); ta = wt(3, "всех всё")
    img = s.base(t, dark=0.45)
    nina(img, 280, 1640, 1.45, t, look=0.8)
    pk = kirill(img, 820, 1650, 1.35, t, look=-0.8 if t < wt(3, "Кирилл молчит") else -0.2, mouth="flat")
    glow(img, pk["lantern"][0], pk["lantern"][1], 320, AMBER, 0.4)
    if t < ta: bubble(img, 70, 480, "ты хотел закрыться один?", (t - tq) / 0.3)
    bubble(img, 330, 500, "всех всё равно не спасти", (t - ta) / 0.3)
    return img, lerp(1.0, 1.08, ease(t / dur)), 1.0


# ======================================================================= 5: старые запасы
def scene5(t):
    s = shelter(); dur = DUR[4]; tc = wt(4, "Консервы"); tb = wt(4, "Бочки"); tf = wt(4, "Старые фильтры"); tu = wt(4, "Убежище есть")
    img = darken(s.bg, 0.5); p = P(img, 1.0)
    if t < tb:
        p.rr(80, 1100, 1000, 1130, 8, (96, 84, 70)); p.rr(80, 1420, 1000, 1450, 8, (96, 84, 70))
        k = ease((t - tc) / 0.8)
        for row, y in enumerate((1100, 1420)):
            for j in range(6):
                x = 130 + j * 140; bulge = 16 * k * (1 if (j + row) % 2 == 0 else 0.5)
                p.rr(x - bulge, y - 190, x + 100 + bulge, y, 18 + bulge, mixc((150, 156, 170), RUST, 0.3 + 0.4 * k))
                p.rr(x + 10, y - 140, x + 90, y - 70, 6, (196, 176, 140))
                if k > 0.5: p.circ(x + 30, y - 40, 14, RUST)
        glow(img, 540, 1150, 620, (255, 240, 200), 0.25, 1.4)
    elif t < tf:
        for j, x in enumerate((240, 540, 840)):
            tilt = (0, 14, -10)[j]
            p.rr(x - 120 + tilt, 1020, x + 120 + tilt, 1460, 40, (72, 96, 120)); p.rr(x - 126 + tilt, 1120, x + 126 + tilt, 1150, 10, (50, 60, 76)); p.rr(x - 126 + tilt, 1320, x + 126 + tilt, 1350, 10, (50, 60, 76))
            p.el(x - 100 + tilt, 1000, x + 100 + tilt, 1060, (16, 16, 22))
        for a in range(0, 91, 30): p.line([(120, 1000), (120 + 150 * math.cos(math.radians(a)), 1000 + 150 * math.sin(math.radians(a)))], (150, 150, 160), 2, round_caps=False)
        glow(img, 540, 1150, 620, (255, 240, 200), 0.22, 1.4)
    elif t < tu:
        k = clamp((t - tf - 0.6) / 1.2)
        pts = hero(img, 540, 1960, 1.5, t, look=(0.0, 0.9), lamp=True, brows="worried", mouth="flat")
        lamp_glow(img, pts["lamp"], True, size=1.5)
        p = P(img, 1.0); cx, cy = 540, 1440
        if k < 1: p.rr(cx - 150 + 60 * k, cy - 90 + 40 * k, cx + 150 - 60 * k, cy + 90, 12, mixc((150, 156, 170), (110, 100, 90), k))
        rnd = random.Random(4)
        for j in range(60):
            u, v = rnd.uniform(-1, 1), rnd.random()
            if v < k: p.circ(cx + u * 190, cy + 60 + (k - v) * 300 * (0.5 + rnd.random()), rnd.uniform(4, 10), (120, 110, 100))
        p.circ(cx - 190, cy + 60, 34, SKIN); p.circ(cx + 190, cy + 60, 34, SKIN)
    else:
        img = s.base(t, dark=0.3)
        fact_card(img, t, tu, "40 МЕСТ · 0 ЗАПАСОВ")
        hero(img, 540, 1580, 1.15, t, look=(0.0, 0.5), brows="worried", mouth="flat", dark=0.8)
        cat(img, 780, 1575, 0.7, t, look=-0.6, dark=0.8)
    return img, lerp(1.0, 1.06, ease(t / dur)), 1.0


# ======================================================================= 6: склад Кирилла
def scene6(t):
    s = shelter(); dur = DUR[5]; tn = wt(5, "Но только")
    img = darken(s.bg, 0.6); p = P(img, 1.0)
    stash(p, t)
    glow(img, 540, 1250, 700, WARM, 0.3, 1.4)
    for j, (w_, x, y) in enumerate((("Генератор", 265, 1150), ("Фильтры", 590, 1000), ("Вода", 860, 1200), ("Еды на целый", 870, 900))):
        t0 = wt(5, w_)
        if t0 < t < t0 + 1.0: glow(img, x, y, 260, AMBER, 0.45 * math.sin(math.pi * (t - t0)))
    if t > wt(5, "Еды на целый"): fact_card(img, t, wt(5, "Еды на целый"), "ЕДЫ НА 1 ГОД" if t < tn else "НО НА ОДНОГО")
    return img, lerp(1.0, 1.08, ease(t / dur)), 1.0


# ======================================================================= 7: деревня несёт
def scene7(t):
    s = shelter(); dur = DUR[6]; ta = wt(6, "Артём отдаёт"); th = wt(6, "Этого хватит")
    img = s.base(t, dark=0.6, lamps=0.8); p = P(img, 1.0)
    rnd = random.Random(8)
    n = int(clamp(t / (ta + 1.5)) * 9)
    for j in range(n):                                                                    # растёт общая куча
        box(p, 380 + (j % 3) * 120 + rnd.uniform(-10, 10), 1500 - (j // 3) * 96, 110, 90, None, mixc((150, 116, 80), (110, 124, 110), rnd.random()))
    for j in range(4):                                                                    # люди идут с коробками
        u = (t * 0.22 + j * 0.25) % 1.0; x = lerp(-120, 420, u)
        if u < 0.9:
            silhouette(p, x, 1560 + (j % 2) * 20, 0.85, mixc((56, 62, 84), (92, 80, 96), j / 4), hat=(90, 70, 60))
            box(p, x + 10, 1330 + (j % 2) * 20, 80, 70, None, (150, 116, 80))
    if t > ta:
        pts = hero(img, 840, 1580, 1.1, t, look=(-0.7, 0.3), arm=None, brows="calm", mouth="flat")
        p = P(img, 1.0); box(p, 660, 1560, 150, 120, "ФИЛЬТР", (150, 116, 80))
        k = ease((t - ta - 1.0) / 0.5)
        if k > 0:
            p.rr(690, 1410 + 20 * (1 - k), 790, 1440 + 20 * (1 - k), 6, (120, 150, 110)); p.rr(700, 1396 + 20 * (1 - k), 800, 1426 + 20 * (1 - k), 6, (130, 160, 120))
    cat(img, 980, 1580, 0.6, t, look=-0.7)
    if t > th:
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); o = P(ov, 1.0); k = ease((t - th) / 0.3)
        o.rr(170, 320, 910, 440, 30, (10, 14, 28, int(235 * k))); ctext(ov, 540, 344, "ХВАТИТ НА 3 ДНЯ", font(60), (230, 58, 58, int(255 * k)))
        img.alpha_composite(ov)
    return img, lerp(1.0, 1.06, ease(t / dur)), 1.0


# ======================================================================= 8: замок на складе
def scene8(t):
    s = shelter(); dur = DUR[7]; tl = wt(7, "И молча"); tq = wt(7, "А ты бы")
    if t < tl:
        img = s.base(t, dark=0.6, lamps=0.6)
        pk = kirill(img, 540, 1640, 1.5, t, look=-0.7 * math.sin(t * 1.5), lantern=False)
        return img, lerp(1.0, 1.1, ease(t / tl)), 1.0
    tt = t - tl
    img = darken(s.bg, 0.5); p = P(img, 1.0)
    stash(p, t); glow(img, 540, 1250, 620, WARM, 0.2, 1.4)
    k = ease(tt / 0.7)
    cage(P(img, 1.0), 60, 820, 1020 - 0, 1480)
    lock_closed = tt > 1.2
    ly = lerp(700, 1150, k)
    padlock(P(img, 1.0), 540, ly, 1.3, not lock_closed)
    if lock_closed and tt < 1.5: glow(img, 540, 1150, 240, RED, 0.5)
    if t > tq:
        kk = clamp((t - tq) / 0.6)
        ctext(img, 540, 480, "5", font(int(lerp(140, 220, ease(kk)))), mixc((255, 255, 255), RED, kk))
    return img, lerp(1.0, 1.08, ease(tt / (dur - tl))), 1.0


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
