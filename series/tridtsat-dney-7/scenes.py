"""«Тридцать дней», серия 7 «День ноль». Сцена: frame(t) -> (RGBA, zoom, bright)."""
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


SH = CEL = None
def shelter():
    global SH
    if SH is None: SH = Shelter()
    return SH

def cellar():
    global CEL
    if CEL is None: CEL = Cellar()
    return CEL


def clock(img, cx, cy, r, hh, mm, ss=None):
    p = P(img, 1.0)
    p.circ(cx, cy, r + 14, (60, 50, 44)); p.circ(cx, cy, r, (226, 216, 196))
    for k in range(12):
        a = math.radians(k * 30 - 90); r0 = r * (0.8 if k % 3 else 0.72)
        p.line([(cx + r0 * math.cos(a), cy + r0 * math.sin(a)), (cx + r * 0.9 * math.cos(a), cy + r * 0.9 * math.sin(a))], (60, 50, 44), 6 if k % 3 else 10, round_caps=False)
    def hand(ang, ln, wd, col):
        a = math.radians(ang - 90); p.line([(cx, cy), (cx + ln * math.cos(a), cy + ln * math.sin(a))], col, wd)
    hand((hh % 12 + mm / 60) * 30, r * 0.5, 14, (40, 34, 30)); hand(mm * 6, r * 0.75, 9, (40, 34, 30))
    if ss is not None: hand(ss * 6, r * 0.82, 4, (190, 50, 40))
    p.circ(cx, cy, 12, (40, 34, 30))


def checkers(p, x, y, s):
    for i in range(4):
        for j in range(4):
            p.rect(x + i * 40 * s, y + j * 40 * s, x + (i + 1) * 40 * s, y + (j + 1) * 40 * s, (220, 200, 160) if (i + j) % 2 else (90, 66, 48))
    for (i, j, c) in ((0, 1, (240, 240, 236)), (2, 1, (240, 240, 236)), (1, 2, (30, 30, 34)), (3, 2, (30, 30, 34))):
        p.circ(x + (i + 0.5) * 40 * s, y + (j + 0.5) * 40 * s, 15 * s, c)


# ======================================================================= 1: работают вместе
def scene1(t):
    s = shelter(); dur = DUR[0]; tg = wt(0, "Генератор"); tk = wt(0, "Колян"); tn = wt(0, "Нина")
    lamps = clamp((t - tg) / 0.4) if t > tg else 0.3
    img = s.base(t, dark=0.45, lamps=lamps)
    if t < tk:
        p = P(img, 1.0); stash(p, t)
        for x in (270, 810): glow(img, x, 430, 300, WARM, 0.4 * lamps)
        kirill(img, 880, 1580, 1.1, t, look=-0.6, lantern=False)
        return img, lerp(1.0, 1.06, ease(t / tk)), 1.0
    if t < tn:
        p = P(img, 1.0); p.rr(-20, 300, W + 20, 380, 30, (120, 124, 136)); p.rr(420, 290, 620, 390, 14, (168, 172, 184))
        pts = kolyan(img, 520, 1580, 1.3, t, phone_up=False, serious=False, look=0.0)
        p = P(img, 1.0); sp = math.sin(t * 9) * 20
        p.line([(620, 700 + sp), (560, 420)], (150, 156, 172), 14); p.rr(540, 390, 590, 440, 8, (150, 156, 172))
        if (t * 3) % 1 < 0.3: glow(img, 560, 420, 60, (255, 240, 180), 0.8)
        return img, 1.04, 1.0
    p = P(img, 1.0)
    p.rr(260, 1400, 820, 1440, 10, (110, 80, 60)); p.rect(300, 1440, 330, 1640, (90, 66, 48)); p.rect(750, 1440, 780, 1640, (90, 66, 48))
    checkers(p, 460, 1250, 1.0)
    nina(img, 200, 1600, 1.0, t, look=0.7)
    girl(img, 720, 1560, 0.95, t, look=-0.7, smile=True)
    girl(img, 900, 1570, 0.85, t + 1.3, look=-0.6, smile=True)
    p = P(img, 1.0); p.rr(260, 1400, 820, 1440, 10, (110, 80, 60)); checkers(p, 460, 1250, 1.0)
    return img, lerp(1.0, 1.05, ease((t - tn) / (dur - tn))), 1.0


# ======================================================================= 2: последняя дверь
def scene2(t):
    s = shelter(); dur = DUR[1]; ts = wt(1, "Соня"); tc = wt(1, "Он закрывает"); tk = wt(1, "Все три")
    if t < tc:
        img = s.base(t, dark=0.45, lamps=1.0)
        girl(img, 600, 1580, 1.35, t, look=-0.7, smile=True)
        if t > ts:
            k = abs(math.sin((t - ts) * 6)); p = P(img, 1.0)
            p.el(700, 1180 - 40 * k, 760, 1300 - 40 * k, (214, 208, 200)); p.el(690, 1120 - 40 * k, 720, 1200 - 40 * k, (214, 208, 200)); p.el(740, 1120 - 40 * k, 770, 1200 - 40 * k, (214, 208, 200))
        mother(img, 860, 1580, 1.15, t, look=-0.6)
        hero(img, 180, 1900, 1.3, t, view="back", dark=0.9)
        return img, lerp(1.0, 1.06, ease(t / tc)), 1.0
    tt = t - tc
    img = vgrad(W, H, [(0, (20, 22, 30)), (1, (12, 12, 18))])
    iron_door(img, 540, 330, 800, 930, [True, True, True], names=True, t=t)
    k = ease(tt / 1.2); p = P(img, 1.0); gx = 940 - 260 * (1 - k)
    if k < 1:
        p.poly([(gx, 330), (940, 330), (940, 1260), (gx, 1260)], (8, 8, 12)); glow(img, (gx + 940) / 2, 800, 260 * (1 - k) + 1, AMBER, 0.35 * (1 - k))
    p = P(img, 1.0); p.rect(0, 1320, W, H, (150, 160, 184))
    if t > tk: fact_card(img, t, tk, "3 КЛЮЧА · 40 ЧЕЛОВЕК")
    return img, lerp(1.0, 1.06, ease(tt / (dur - tc))), 1.0


# ======================================================================= 3: погреб
def scene3(t):
    c = cellar(); dur = DUR[2]; te = wt(2, "Четвёртая")
    img = c.base(t, dark=0.35, shaft=False)
    glow(img, 640, 1100, 640, AMBER, 0.3 + 0.03 * math.sin(t * 11), 1.4)
    p = P(img, 1.0)
    p.rr(600, 1330, 1060, 1380, 10, (110, 80, 60)); p.rect(640, 1380, 670, 1560, (90, 66, 48)); p.rect(990, 1380, 1020, 1560, (90, 66, 48))
    p.rr(860, 1250, 900, 1330, 6, (238, 232, 216)); glow(img, 880, 1230, 200, AMBER, 0.45 + 0.05 * math.sin(t * 13))
    pt = granny(img, 360, 1580, 1.05, t, mug=True, look=0.6)
    steam(img, pt["mug"][0], pt["mug"][1] - 20, t, period=1.6, scale=0.6)
    nina(img, 760, 1580, 1.0, t, look=-0.5)
    cat(img, 760, 1350, 0.6, t, pose="lie", look=0.0)
    if t > te:
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); o = P(ov, 1.0); k = ease((t - te) / 0.3)
        o.rr(150, 320, 930, 470, 30, (10, 14, 28, int(235 * k)))
        for j in range(4):
            cx = 290 + j * 166; a = int(255 * k)
            if j < 3: o.circ(cx, 372, 26, (255, 178, 64, a)); o.rr(cx - 30, 400, cx + 30, 450, 18, (255, 178, 64, a))
            else: o.el(cx - 26, 346, cx + 26, 398, None, (200, 206, 224, a), 5); o.rr(cx - 30, 400, cx + 30, 450, 18, None, (200, 206, 224, a), 5)
        img.alpha_composite(ov)
    return img, lerp(1.0, 1.06, ease(t / dur)), 1.0


# ======================================================================= 4: полночь
def scene4(t):
    c = cellar(); dur = DUR[3]; tr = wt(3, "Радио"); tc = wt(3, "Артём смотрит")
    img = c.base(t, dark=0.25, shaft=False)
    glow(img, 540, 1100, 520, AMBER, 0.18, 1.4)
    if t < tc:
        radio(img, 540, 900, 1.0, t, on=True)
        st = Image.effect_noise((260, 110), 60).convert("RGBA"); st.putalpha(70); comp(img, st, 540 + 60, 900 - 140)
        hero(img, 300, 1620, 1.1, t, look=(0.6, -0.5), brows="worried", dark=0.8)
        granny(img, 800, 1600, 0.95, t, look=-0.4, dark=0.7)
        return img, lerp(1.0, 1.06, ease(t / tc)), 1.0
    tt = t - tc
    clock(img, 540, 900, 330, 0, 0, ss=(tt * 3) % 60)
    return img, lerp(1.0, 1.12, ease(tt / (dur - tc))), 1.0


# ======================================================================= 5: шесть утра, тишина
def scene5(t):
    c = cellar(); dur = DUR[4]
    img = c.base(t, dark=0.2, shaft=False)
    clock(img, 540, 620, 210, 6, 0, ss=(t * 1.0) % 60)
    glow(img, 540, 620, 400, (200, 210, 240), 0.1, 1.4)
    hero(img, 540, 1660, 1.05, t, look=(0.0, -0.7), brows="worried", mouth="flat", dark=0.7)
    cat(img, 820, 1640, 0.65, t, look=-0.4, ears_back=True, dark=0.7)
    return img, lerp(1.0, 1.08, ease(t / dur)), 1.0


# ======================================================================= 6: на лестнице
def scene6(t):
    c = cellar(); dur = DUR[5]; tu = wt(5, "Поднимается"); th = wt(5, "Кладёт руку")
    img = c.base(t, dark=0.25, shaft=False, shelf=False)
    p = P(img, 1.0); p.rr(120, 120, 440, 220, 14, (92, 96, 108))
    for dx in (160, 400): p.circ(dx, 170, 12, RUST)
    on = t > 0.5
    k = ease((t - tu) / 1.4)
    pts = hero(img, 280, lerp(1600, 820, k), 1.05, t, look=(0.0, -0.9), lamp=on, arm="up" if t > th - 0.3 else None, brows="worried")
    lamp_glow(img, pts["lamp"], on, size=1.05)
    if on: glow(img, 280, 260, 300, (255, 240, 200), 0.35 * k + 0.1)
    if t > th:
        line = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(line)
        d.line([(130, 222), (430, 222)], fill=(255, 250, 230, int(200 * (0.6 + 0.4 * math.sin(t * 3)))), width=4); img.alpha_composite(line)
    return img, lerp(1.0, 1.1, ease(t / dur)), 1.0


# ======================================================================= 7: запись в тетради
def scene7(t):
    c = cellar(); dur = DUR[6]; tw = wt(6, "Тридцатый"); tv = wt(6, "Мы были")
    img = darken(c.bg, 0.35)
    notebook(img, t, [(-9, lambda p, k: written(p, 200, 600, "28 октября 1962", 1, 70, (120, 60, 50))),
                      (-9, lambda p, k: written(p, 200, 700, "Договорились. Больше не копаю.", 1, 54)),
                      (-9, lambda p, k: written(p, 200, 780, "Но люк не засыпаю.", 1, 54)),
                      (-9, lambda p, k: p.line([(200, 900), (880, 900)], (150, 140, 120), 4, round_caps=False)),
                      (tw, lambda p, k: written(p, 200, 980, "День 30.", k * 1.3, 96, (40, 60, 120))),
                      (tv, lambda p, k: written(p, 200, 1130, "Мы были вместе.", k * 1.3, 96, (40, 60, 120)))])
    return img, lerp(1.0, 1.08, ease(t / dur)), 1.0


# ======================================================================= 8: свет
def scene8(t):
    c = cellar(); dur = DUR[7]; tl = wt(7, "В лицо"); tq = wt(7, "А как думаешь")
    k = ease(t / 1.6)
    img = c.base(t, dark=0.25, shaft=False, shelf=False)
    if k > 0:
        shaft = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(shaft)
        d.polygon([(120, 0), (440, 0), (740, 1700), (-180, 1700)], fill=(255, 250, 235, int(170 * k)))
        img.alpha_composite(shaft.filter(ImageFilter.GaussianBlur(40)))
        glow(img, 280, 120, 700, (255, 252, 240), 0.9 * k, 1.2)
    pts = hero(img, 360, 1700, 1.6, t, look=(-0.2, -0.9), brows="calm", mouth="o" if t > tl else None, dark=lerp(0.4, 1.0, k))
    if t > tl:
        w = ease((t - tl) / 1.0)
        img.alpha_composite(Image.new("RGBA", (W, H), (255, 252, 244, int(200 * w))))
    if t > tq:
        kk = clamp((t - tq) / 0.6)
        ctext(img, 540, 860, "0", font(int(lerp(180, 300, ease(kk)))), mixc((40, 40, 50), RED, kk))
    return img, lerp(1.0, 1.12, ease(t / dur)), 1.0


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
