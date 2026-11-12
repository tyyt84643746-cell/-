"""«Тридцать дней», серия 6 «Список». Сцена: frame(t) -> (RGBA, zoom, bright)."""
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

LIST = ["Громов А.", "Громова В.", "Савельев Н.", "Вершинина Н.", "Зуева М., врач", "Ершов П., механик"]


def paper(img, t, lines, title=None):
    notebook(img, t, lines, y0=520, title=title)


# ======================================================================= 1: нужен список
Y1 = None
def scene1(t):
    global Y1
    s = shelter(); dur = DUR[0]; tm = wt(0, "В убежище"); tw = wt(0, "Желающих"); tn = wt(0, "Нужен")
    if t < tm:
        img = darken(s.bg, 0.5); p = P(img, 1.0); stash(p, t); cage(P(img, 1.0), 60, 820, 1020, 1480)
        padlock(P(img, 1.0), 540, 1150, 1.3, False); glow(img, 540, 1150, 260, RED, 0.25 + 0.1 * math.sin(t * 5))
        return img, lerp(1.0, 1.08, ease(t / tm)), 1.0
    if Y1 is None:
        Y1 = Yard(0.3); Y1.snow = Snow(40, 81, (2, 4), (40, 100)); rnd = random.Random(31)
        Y1.crowd = [(40 + (i % 13) * 84 + rnd.uniform(-16, 16), 1300 + (i // 13) * 110 + rnd.uniform(-10, 10), rnd.uniform(0.75, 0.95),
                     mixc((56, 62, 84), (92, 80, 96), rnd.random()), mixc((90, 70, 60), (60, 80, 100), rnd.random()), rnd.uniform(0, 6)) for i in range(39)]
    img = Y1.bg.copy(); p = P(img, 1.0)
    n = int(len(Y1.crowd) * clamp((t - tm) / (tn - tm)))
    for (x, y, sc, c, h, ph) in sorted(Y1.crowd[: max(8, n)], key=lambda a: a[1]):
        silhouette(p, x + 4 * math.sin(t * 3 + ph), y + 3 * abs(math.sin(t * 4 + ph)), sc, c, hat=h)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); o = P(ov, 1.0)
    o.rr(120, 320, 960, 500, 30, (10, 14, 28, 235))
    ctext(ov, 330, 340, "МЕСТ", font(40), (200, 206, 224)); ctext(ov, 330, 390, "40", font(84), AMBER)
    if t > tw:
        ctext(ov, 750, 340, "ЖЕЛАЮЩИХ", font(40), (200, 206, 224)); ctext(ov, 750, 390, f"{int(lerp(60, 104, ease((t - tw) / 1.0)))}", font(84), RED)
    img.alpha_composite(ov)
    Y1.snow.draw(img, t, 200)
    return img, lerp(1.0, 1.06, ease(t / dur)), 1.0


# ======================================================================= 2: пишут список
def scene2(t):
    s = shelter(); dur = DUR[1]; ta, tb, tc, tm = wt(1, "Сначала"), wt(1, "Потом старики"), wt(1, "Потом те"), wt(1, "Мест остаётся")
    if t < ta:
        img = s.base(t, dark=0.45, lamps=0.5); p = P(img, 1.0)
        nina(img, 180, 1560, 1.0, t, look=0.6, dark=0.9); kolyan(img, 900, 1570, 1.05, t, phone_up=False, serious=True, look=-0.6, dark=0.9)
        hero(img, 540, 1575, 1.1, t, look=(0.0, 0.9), brows="worried", dark=0.95)
        p = P(img, 1.0); p.rr(120, 1380, 960, 1440, 12, (110, 80, 60)); p.rect(160, 1440, 190, 1700, (90, 66, 48)); p.rect(890, 1440, 920, 1700, (90, 66, 48))
        p.rr(360, 1340, 720, 1392, 4, PAPER); p.rr(820, 1270, 850, 1384, 6, (238, 232, 216)); glow(img, 835, 1250, 300, AMBER, 0.35 + 0.05 * math.sin(t * 13))
        return img, lerp(1.0, 1.08, ease(t / ta)), 1.0
    img = darken(s.bg, 0.4)
    left = 40 - (14 if t > ta + 0.9 else 0) - (11 if t > tb + 0.9 else 0) - (9 if t > tc + 1.2 else 0)
    paper(img, t, [(ta, lambda p, k: written(p, 200, 640, "1. Дети — 14", k * 1.3, 80)),
                   (tb, lambda p, k: written(p, 200, 790, "2. Старики — 11", k * 1.3, 80)),
                   (tc, lambda p, k: written(p, 200, 940, "3. Врач, механик,", k * 1.3, 72)),
                   (tc + 0.7, lambda p, k: written(p, 260, 1050, "электрик… — 9", k * 1.3, 72)),
                   (tm, lambda p, k: written(p, 200, 1250, f"Осталось мест: {left}", 1, 80, (170, 50, 50)))], title="список")
    return img, lerp(1.0, 1.05, ease((t - ta) / (dur - ta))), 1.0


# ======================================================================= 3: сорок первая
def scene3(t):
    s = shelter(); dur = DUR[2]; ty = wt(2, "Ей шесть"); tm = wt(2, "Её мама")
    img = s.base(t, dark=0.5, lamps=0.6)
    mother(img, 700, 1570, 1.2, t, look=-0.5 if t < tm else 0.0, dark=0.95)
    girl(img, 400, 1575, 1.25, t, look=math.sin(t * 1.2) * 0.6, smile=t < ty)
    glow(img, 400, 1300, 420, WARM, 0.2, 1.4)
    fact_card(img, t, 0.4, "№ 41")
    if t > ty: bubble(img, 90, 760, "Соня, 6 лет", (t - ty) / 0.3)
    return img, lerp(1.0, 1.1, ease(t / dur)), 1.0


# ======================================================================= 4: зачёркнутая фамилия
def scene4(t):
    s = shelter(); dur = DUR[3]; tf = wt(3, "Находит"); tz = wt(3, "И зачёркивает"); tw = wt(3, "На это место")
    if t < tf:
        img = s.base(t, dark=0.5, lamps=0.6)
        pts = hero(img, 540, 1640, 1.45, t, look=(0.0, 0.8), arm="up" if t > 0.8 else None, brows="worried", mouth="flat")
        if t > 0.8:
            hx, hy = pts["hand"]; P(img, 1.0).line([(hx, hy), (hx + 16, hy - 150)], (214, 180, 96), 12); P(img, 1.0).poly([(hx + 10, hy - 150), (hx + 22, hy - 150), (hx + 18, hy - 176)], (60, 50, 40))
        return img, lerp(1.0, 1.08, ease(t / tf)), 1.0
    img = darken(s.bg, 0.4)
    def names(p, k):
        for j, nm in enumerate(LIST[:5]): p.text(200, 610 + j * 130, f"{36 + j}. {nm}" if j else f"36. {nm}", hand(76), INK)
    def mark(p, k):
        glow(img, 520, 660, 300, AMBER, 0.25)
        p.rr(180, 600, 900, 720, 14, None, (214, 150, 60), 6)
    def strike(p, k):
        p.line([(190, 668), (190 + 560 * k, 660)], (170, 50, 50), 12)
    def newname(p, k):
        written(p, 300, 1280, "Соня, 6 лет", k * 1.3, 96, (170, 50, 50))
    paper(img, t, [(-9, names), (tf, mark), (tz, strike), (tw, newname)], title="список")
    return img, lerp(1.0, 1.06, ease((t - tf) / (dur - tf))), 1.0


# ======================================================================= 5: Колян и Артём
def scene5(t):
    s = shelter(); dur = DUR[4]; ta = wt(4, "Артём отвечает"); t4 = wt(4, "Он на четверых")
    img = s.base(t, dark=0.5, lamps=0.6)
    hero(img, 300, 1590, 1.25, t, look=(0.8, 0.0), brows="calm", mouth="smile" if t > ta + 1.0 else "flat")
    shake = 6 * math.sin(t * 30) if t < 1.6 else 0
    kolyan(img, 800 + shake, 1600, 1.3, t, phone_up=False, serious=True, look=-0.8)
    if t < ta: bubble(img, 330, 470, "ты всё это нашёл!", (t - 0.5) / 0.25)
    else: bubble(img, 90, 470, "у меня есть погреб деда", (t - ta - 0.6) / 0.3)
    fact_card(img, t, t4, "ПОГРЕБ · 4 МЕСТА")
    return img, lerp(1.0, 1.06, ease(t / dur)), 1.0


# ======================================================================= 6: уходят в погреб
Y6 = None
def scene6(t):
    global Y6
    if Y6 is None:
        Y6 = Yard(0.75); Y6.bg = darken(Y6.bg, 0.7); Y6.snow = Snow(60, 91, (2, 4), (40, 110))
    dur = DUR[5]; te = wt(5, "Четвёртое")
    img = Y6.bg.copy(); p = P(img, 1.0)
    hatch(p, 820, 1420, 0.9, open_k=1.0); glow(img, 820, 1420, 320, AMBER, 0.4 + 0.05 * math.sin(t * 6))
    k = ease(t / (te - 0.2))
    granny(img, lerp(-420, 130, k), 1500, 0.95, t, look=0.7, dark=0.85)
    nina(img, lerp(-240, 330, k), 1505, 0.95, t, look=0.7, dark=0.85)
    pts = hero(img, lerp(-60, 540, k), 1510, 1.0, t, walk=t * 5 if k < 1 else None, look=(0.8, 0.2), lamp=True, dark=0.9)
    lamp_glow(img, pts["lamp"], True, size=1.0)
    cat(img, lerp(120, 690, k), 1505, 0.55, t, look=0.7, dark=0.85)
    if t > te:
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); o = P(ov, 1.0); kk = ease((t - te) / 0.3)
        o.rr(150, 320, 930, 470, 30, (10, 14, 28, int(235 * kk)))
        for j in range(4):
            cx = 290 + j * 166
            if j < 3: o.circ(cx, 372, 26, (255, 178, 64, int(255 * kk))); o.rr(cx - 30, 400, cx + 30, 450, 18, (255, 178, 64, int(255 * kk)))
            else: o.el(cx - 26, 346, cx + 26, 398, None, (200, 206, 224, int(255 * kk)), 5); o.rr(cx - 30, 400, cx + 30, 450, 18, None, (200, 206, 224, int(255 * kk)), 5)
        img.alpha_composite(ov)
    Y6.snow.draw(img, t, 190)
    return img, lerp(1.0, 1.06, ease(t / dur)), 0.95


# ======================================================================= 7: Кирилл открывает склад
def scene7(t):
    s = shelter(); dur = DUR[6]; tk = wt(6, "Потом берёт"); to = wt(6, "И открывает")
    if t < tk:
        img = s.base(t, dark=0.5, lamps=0.5)
        kirill(img, 540, 1640, 1.5, t, look=-0.8, lantern=False)
        return img, lerp(1.0, 1.1, ease(t / tk)), 1.0
    img = darken(s.bg, 0.5 + 0.25 * ease((t - to) / 0.8)); p = P(img, 1.0)
    stash(p, t)
    opened = t > to + 0.5
    k = ease((t - to - 0.5) / 0.9)
    if not opened: cage(P(img, 1.0), 60, 820, 1020, 1480)
    else:
        cage(P(img, 1.0), 60 - 900 * k, 820, 1020 - 900 * k, 1480)
        glow(img, 540, 1200, 760, AMBER, 0.3 * k, 1.4)
    if t < to + 0.5:
        kx = ease((t - tk) / 0.8); key(P(img, 1.0), lerp(980, 560, kx), 1180, 1.1); glow(img, lerp(980, 560, kx), 1150, 140, AMBER, 0.4)
    padlock(P(img, 1.0), 540 - 900 * k, 1150, 1.3, t > to)
    if opened and k > 0.5: fact_card(img, t, to + 1.0, "СКЛАД ОТКРЫТ ДЛЯ ВСЕХ")
    return img, lerp(1.0, 1.08, ease((t - tk) / (dur - tk))), 1.0


# ======================================================================= 8: радио
def scene8(t):
    dur = DUR[7]; tp = wt(7, "Переговоры"); td = wt(7, "Осталось"); tq = wt(7, "А кого")
    img = vgrad(W, H, [(0, (26, 22, 26)), (1, (14, 12, 16))]); p = P(img, 1.0)
    p.rr(-20, 1180, W + 20, 1220, 8, (90, 66, 48)); p.rect(0, 1220, W, H, (30, 26, 28))
    on = t > 0.6 and not (0.75 < t < 0.85)
    radio(img, 540, 980, 1.25, t, on=on)
    if t > tp:
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); o = P(ov, 1.0); k = ease((t - tp) / 0.3)
        o.rr(120, 420, 960, 560, 26, (200, 40, 40, int(240 * k))); ctext(ov, 540, 452, "ПЕРЕГОВОРЫ СОРВАНЫ", font(58), (255, 255, 255, int(255 * k)))
        img.alpha_composite(ov)
    if t > td:
        kk = clamp((t - td) / 0.6)
        ctext(img, 540, 1290, "2", font(int(lerp(160, 240, ease(kk)))), mixc((255, 255, 255), RED, kk))
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
