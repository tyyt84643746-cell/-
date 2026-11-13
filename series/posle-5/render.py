"""«После», серия 5 «Автобус» (сезон 2, 3D). Запуск: LIBGL_ALWAYS_SOFTWARE=1 xvfb-run -a python3 render.py [preview | sheet N K | at N T]"""
import math, os, random, sys
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(D, "..", "engine3d")); sys.path.insert(0, D)
import numpy as np
from village import *
from show import *
from script import SCENES, CAPTION_NUMS

LEADS = [0.3] * 6
TAILS = [0.6, 0.7, 0.8, 0.9, 1.1, 2.8]
KEY = {"сигнал", "свет", "пойдёшь", "2", "ближе", "кекс", "автобус", "12", "5", "детей", "север", "убежищу", "пустили", "9", "7", "взять", "нет", "комментариях"}
NIGHT = dict(sun_dir=(0.4, -0.7, -0.5), sun_col=(0.16, 0.2, 0.34), amb_top=(0.05, 0.07, 0.15), amb_bot=(0.02, 0.03, 0.06), fog=0.014, fog_col=(0.025, 0.035, 0.08),
             sky=((0.004, 0.008, 0.03), (0.03, 0.045, 0.1), (0.025, 0.035, 0.08)), shadow_center=(0, 0, 0), shadow_size=24)
WARM = (1.0, 0.9, 0.7)

def forest(z0, z1, seed=7, gap=3.2, n=46):
    rnd = random.Random(seed); it = []
    for _ in range(n):
        x = rnd.uniform(gap, 30) * rnd.choice((-1, 1)); it += pine(T(x, 0, rnd.uniform(z1, z0)), rnd.uniform(4.5, 7.5))
    return it
def tracks(z0, z1):
    it = []; k = 0; z = z0
    while z > z1:
        for lane, ph in ((-1.7, 0.0), (-0.9, 1.3), (0.0, 2.1), (0.8, 0.6), (1.6, 1.9)):
            x = lane + 0.35 * math.sin(k * 0.21 + ph) + (0.15 if k % 2 else -0.15)
            it.append(box(T(x, 0.025, z - ph * 0.3) @ S(0.18, 0.02, 0.36), rgb((150, 158, 182)), cast=False))
        z -= 0.75; k += 1
    return it
FIELD = [box(T(0, -0.25, -20) @ S(240, 0.5, 240), C["snow"])] + forest(2, -75, 9, 3.6, 60) + tracks(9, -62)


BUS_M = T(1.2, 0, -4.5) @ Ry(-0.95) @ Rz(0.07)
def bus(m, t):
    BODY = rgb((214, 220, 230)); STR = rgb((60, 110, 170)); it = []
    it.append(box(m @ T(0, 1.55, 0) @ S(7.6, 2.3, 2.4), BODY)); it.append(box(m @ T(0, 0.85, 0) @ S(7.64, 0.5, 2.44), STR))
    it.append(box(m @ T(0, 2.78, 0) @ S(7.7, 0.22, 2.5), C["snow"])); it.append(ball(m @ T(-1, 2.9, 0) @ S(5, 0.5, 2.2), C["snow"]))
    for k in range(6):
        for sz in (-1.21, 1.21):
            it.append(box(m @ T(-3.0 + k * 1.15, 1.95, sz) @ S(0.95, 0.9, 0.04), rgb((255, 200, 120)), emit=0.55 + 0.1 * math.sin(t * 2 + k), cast=False))
        if k % 2 == 0: it.append(ball(m @ T(-3.0 + k * 1.15, 1.8, 1.24) @ S(0.42, 0.42, 0.06), rgb((60, 44, 36)), cast=False))   # силуэты в окнах
        else: it.append(ball(m @ T(-3.0 + k * 1.15 + 0.1, 1.68, 1.24) @ S(0.3, 0.3, 0.06), rgb((60, 44, 36)), cast=False))
    it.append(box(m @ T(3.81, 1.9, 0) @ S(0.04, 1.1, 2.1), rgb((30, 40, 60)), cast=False))                       # лобовое
    it.append(box(m @ T(2.9, 1.3, 1.22) @ S(0.9, 1.9, 0.05), rgb((40, 50, 70)), cast=False))                    # дверь
    for sx in (-2.6, 2.4):
        for sz in (-1.1, 1.1): it.append(cyl(m @ T(sx, 0.45, sz) @ Rx(PI / 2) @ S(0.95, 0.4, 0.95), C["dark"]))
    for sz in (-0.8, 0.8): it.append(ball(m @ T(3.82, 0.95, sz) @ S(0.12, 0.34, 0.34), rgb((255, 244, 210)), emit=8.0, cast=False))
    for (x, z, s_) in ((3.6, 1.6, 2.2), (-3.4, 1.5, 2.6), (0.5, 1.7, 1.8), (4.3, -0.6, 2.0)): it.append(ball(m @ T(x, 0.1, z) @ S(s_, 0.9, s_ * 0.7), C["snow"]))
    return it
def bus_pt(x, y, z): return tuple((BUS_M @ np.array([x, y, z, 1], "f4"))[:3])
HEAD = [bus_pt(3.9, 0.95, -0.8), bus_pt(3.9, 0.95, 0.8)]
BUS_L = [(bus_pt(5.5, 1.2, 0), WARM, 11.0), (bus_pt(2.5, 1.8, 3.0), (1.0, 0.75, 0.45), 6.5)]
def bus_glow(k=1.0): return [(p, (255, 240, 200), 120, 0.7 * k) for p in HEAD]

KID = [dict(body=rgb(c), body_d=rgb(tuple(int(v * 0.7) for v in c)), hat=rgb(h), hat_b=rgb(tuple(min(255, int(v * 1.3)) for v in h)), legs=rgb((60, 60, 80)), pack=None)
       for c, h in (((232, 140, 170), (240, 240, 244)), ((90, 150, 200), (220, 90, 70)), ((110, 180, 120), (60, 70, 120)))]
def driver(root, t, **kw):
    return person(root, t, colors=dict(body=rgb((120, 84, 56)), body_d=rgb((90, 62, 42)), hat=rgb((50, 54, 66)), hat_b=rgb((70, 76, 90)), legs=rgb((44, 46, 54)), pack=None),
                  beard=rgb((90, 70, 56)), **kw)
def passengers(t, n=5):
    it = []
    spots = [(3.6, -0.2, 0), (4.4, 0.6, 1), (2.6, 0.2, 2), (5.3, -0.4, None), (1.8, -0.8, None)]
    for j, (x, z, kid) in enumerate(spots[:n]):
        root = T(x, 0, z) @ Ry(-0.25)
        if kid is None: p, _ = villager(j + 3, root, t, blink_seed=j * 0.5, look=0.2 * math.sin(t + j))
        else: p, _ = person(root, t, colors=KID[kid], scale=0.56 + 0.05 * kid, blink_seed=j * 0.5, look=0.3 * math.sin(t * 1.3 + j))
        it += p
    return it

def trio_back(t, z0=7.0, walk=None, lamp=True):
    it = []
    p, _ = artyom(T(-0.6, 0, z0) @ Ry(PI), t, blink_seed=0.7, lamp=lamp, walk=walk); it += p
    p, _ = kolyan(T(0.9, 0, z0 + 0.5) @ Ry(PI), t, blink_seed=0.2, walk=walk + 1.5 if walk is not None else None); it += p
    p, _ = guest(T(0.2, 0, z0 - 1.3) @ Ry(PI), t, blink_seed=1.1, walk=walk + 3 if walk is not None else None); it += p
    return it, [((-0.6, 2.1, z0 - 1.0), WARM, 5.0)]

def scene_3d(si, t):
    wt = SH.wt
    if si == 0:                                                                 # сигнал в лесу
        on = (t % 1.2) < 0.16; SRC = (1.5, 3.0, -58)
        it = list(FIELD); tr, l = trio_back(t, 6.6); it += tr
        it += cat2(T(-1.7, 0, 7.2) @ Ry(PI), t, look=0.3 * math.sin(t * 1.4))
        gl = [(SRC, (255, 235, 190), 330, 1.0), (SRC, (255, 250, 230), 90, 1.3)] if on else []
        if on: it.append(ball(T(*SRC) @ S(1.6), rgb((255, 240, 200)), emit=30.0, cast=False))
        k = ease(t / SH.DUR[0])
        return dict(items=it, eye=(0.2, lerp(3.2, 3.0, k), lerp(13.6, 12.6, k)), tgt=(0.4, 1.4, -20), fov=44, glows=gl, env=NIGHT, lights=l)
    if si == 1:                                                                 # идут
        zc = 6.0 - 1.7 * t; on = (t % 1.0) < 0.16; SRC = (1.5, 3.0, -58)
        it = list(FIELD); tr, l = trio_back(t, zc, walk=t * 6.5); it += tr
        it += cat2(T(-0.3, 0.06 * abs(math.sin(t * 9)), zc - 4.6) @ Ry(PI) @ S(1.3), t)
        kk = t / SH.DUR[1]
        if t > wt(1, "Кекс") - 0.15:                                             # вид спереди: кот ведёт
            return dict(items=it, eye=(-1.0, 0.75, zc - 8.6), tgt=(-0.2, 1.25, zc), fov=44, env=dict(NIGHT, shadow_center=(0, 0, zc - 2)),
                        lights=[((-0.6, 2.1, zc - 1.0), WARM, 5.0), ((-0.6, 1.2, zc - 6.2), WARM, 5.0)])
        gl = [(SRC, (255, 235, 190), lerp(300, 520, kk), 1.0), (SRC, (255, 250, 230), lerp(90, 170, kk), 1.3)] if on else []
        if on: it.append(ball(T(*SRC) @ S(1.6), rgb((255, 240, 200)), emit=30.0, cast=False))
        return dict(items=it, eye=(lerp(1.2, 0.2, kk), 3.6, zc + 7.5), tgt=(0.1, 0.9, zc - 14), fov=46, glows=gl, lights=[((-0.6, 2.1, zc - 1.0), WARM, 5.0)],
                    env=dict(NIGHT, shadow_center=(0, 0, zc - 2)))
    it = [x for x in FIELD if not (abs(x[1][0, 3]) < 9 and -12 < x[1][2, 3] < 3 and x[1][1, 3] > 0.1)] + bus(BUS_M, t)   # поляна вокруг автобуса
    if si == 2:                                                                 # автобус
        tr, l = trio_back(t, 7.2); it += tr
        it += cat2(T(-1.8, 0, 6.4) @ Ry(PI + 0.3), t)
        k = ease(t / SH.DUR[2])
        return dict(items=it, eye=(lerp(-1.6, 0.4, k), lerp(2.3, 2.9, k), lerp(13.2, 14.0, k)), tgt=(1.4, 1.5, -4), fov=46, env=NIGHT, lights=l + BUS_L)
    if si == 3:                                                                 # водитель
        tn = wt(3, "Нас туда")
        p, _ = driver(T(3.4, 0, 0.6) @ Ry(-0.15), t, blink_seed=0.5, mouth="o" if t > tn else None, look=0.1 * math.sin(t)); it += p
        it += passengers(t, 3)[len(person(T(0, 0, 0), 0)[0]):]                  # без первого места (там водитель)
        k = ease(t / SH.DUR[3])
        return dict(items=it, eye=(3.0, 1.9, lerp(6.6, 5.6, k)), tgt=(3.4, 1.9, 0.6), fov=40, env=NIGHT, lights=BUS_L + [((2.6, 2.2, 3.6), WARM, 6.5)], glows=bus_glow(0.6))
    if si == 4:                                                                 # Артём считает
        p, _ = artyom(T(0.4, 0, 3.4) @ Ry(0.5), t, blink_seed=0.7, lamp=True, look=0.5 + 0.2 * math.sin(t), mouth="o" if t > wt(4, "С ними") else None); it += p
        it += cat2(T(-0.6, 0, 4.2) @ Ry(0.6), t, look=0.4)
        it += passengers(t, 5)
        k = ease(t / SH.DUR[4])
        return dict(items=it, eye=(lerp(-0.8, -0.4, k), 2.0, lerp(8.8, 8.0, k)), tgt=(1.2, 1.75, 2.4), fov=42, env=NIGHT, lights=BUS_L + [((0.2, 2.2, 5.0), WARM, 6.0)], glows=bus_glow(0.5))
    tr, l = trio_back(t, 7.4); it += tr                                         # 5: решение
    it += cat2(T(-1.8, 0, 6.6) @ Ry(PI + 0.3), t)
    p, _ = driver(T(1.2, 0, 1.2), t, blink_seed=0.5); it += p
    it += passengers(t, 5)
    k = ease(t / SH.DUR[5])
    return dict(items=it, eye=(0.6, lerp(3.2, 3.5, k), lerp(14.6, 13.8, k)), tgt=(1.4, 1.3, -4), fov=46, env=NIGHT, lights=l + BUS_L)

def panel(d, x0, y0, x1, y1, k=1.0): d.rounded_rectangle([x0, y0, x1, y1], radius=28, fill=PANEL + (int(215 * k),))

def overlay(sh, si, t, d):
    wt = sh.wt
    stroke_text(d, (W / 2, 250), "ПОСЛЕ УЛЬТИМАТУМА", font(60), WHITE, 6)
    stroke_text(d, (W / 2, 350), "НОЧЬ 31", font(122), YEL, 9)
    def tiles(tq, a, b, y=1340):
        for j, (x, lab, c, dl) in enumerate(((290, a, GREEN, 0.0), (790, b, RED, 0.3))):
            k = ease((t - tq - dl) / 0.25)
            if k <= 0: continue
            A = int(255 * k); yy = y + 30 * (1 - k)
            d.rounded_rectangle([x - 225, yy, x + 225, yy + 170], radius=36, fill=PANEL + (int(230 * k),), outline=c + (A,), width=6)
            d.text((x, yy + 85), lab, font=font(56), fill=c + (A,), anchor="mm")
    if si == 0:
        panel(d, 150, 460, 930, 640); x = 215
        for j, ch in enumerate("···———···"):
            col = YEL if (t * 2.2) % 11 > j else (70, 76, 96)
            if ch == "·": d.ellipse([x, 530, x + 34, 564], fill=col); x += 54
            else: d.rounded_rectangle([x, 532, x + 70, 562], radius=12, fill=col); x += 94
            if j in (2, 5): x += 26
        stroke_text(d, (W / 2, 740), "S O S", font(110), RED, 9)
        tiles(wt(0, "Ты пойдёшь") - 0.05, "ИДТИ?", "НЕТ?")
    if si == 1:
        t2 = wt(1, "два"); k = ease((t - t2 + 0.2) / 0.25)
        if k > 0:
            A = int(255 * k); panel(d, 60, 450, 520, 690, k); mins = int(lerp(0, 120, ease((t - t2) / 1.2)))
            d.text((290, 500), "В ПУТИ", font=font(38), fill=(190, 196, 214, A), anchor="mm")
            d.text((290, 600), f"{mins // 60}:{mins % 60:02d}", font=font(108), fill=(YEL if mins == 120 else WHITE) + (A,), anchor="mm")
    if si == 2:
        ta, tb = wt(2, "двенадцать"), wt(2, "пятеро")
        if t > ta - 0.1:
            k = ease((t - ta + 0.1) / 0.25); A = int(255 * k); panel(d, 60, 450, 560, 710, k)
            d.text((310, 500), "В АВТОБУСЕ", font=font(38), fill=(190, 196, 214, A), anchor="mm")
            d.text((310, 575), "12 ЧЕЛОВЕК", font=font(62), fill=WHITE + (A,), anchor="mm")
            if t > tb: d.text((310, 655), "5 ДЕТЕЙ", font=font(66), fill=YEL, anchor="mm")
    if si == 3:
        tn = wt(3, "Нас туда")
        ku = ease((t - wt(3, "К убежищу") + 0.1) / 0.25)
        if ku > 0:
            A = int(255 * ku); panel(d, 60, 450, 640, 700, ku)
            d.text((350, 505), "ТРЕТЬЕ УБЕЖИЩЕ", font=font(46), fill=WHITE + (A,), anchor="mm")
            if t > tn + 0.3:
                kk = ease((t - tn - 0.3) / 0.15); s_ = 1 + 0.4 * (1 - kk)
                d.rounded_rectangle([350 - 235 * s_, 615 - 50 * s_, 350 + 235 * s_, 615 + 50 * s_], radius=14, outline=RED, width=7)
                d.text((350, 615), "НЕ ПУСТИЛИ", font=font(int(60 * s_)), fill=RED, anchor="mm")
            else: d.text((350, 615), "40 КМ НА СЕВЕР", font=font(44), fill=(190, 196, 214, A), anchor="mm")
    if si == 4:
        panel(d, 60, 450, 780, 720)
        b = t > wt(4, "С ними")
        d.text((100, 510), "ЕДЫ В УБЕЖИЩЕ", font=font(38), fill=(190, 196, 214), anchor="lm")
        d.text((100, 590), "40 человек", font=font(48), fill=WHITE, anchor="lm"); d.text((740, 590), "9 ДНЕЙ", font=font(56), fill=WHITE if b else YEL, anchor="rm")
        if b:
            d.text((100, 665), "52 человека", font=font(48), fill=WHITE, anchor="lm")
            if t > wt(4, "на семь"): d.text((740, 665), "7 ДНЕЙ", font=font(56), fill=RED, anchor="rm")
    if si == 5:
        sh.cta(d, t, wt(5, "Пиши") - 0.1, "ВЗЯТЬ", "НЕ БРАТЬ")
        te = sh.DUR[5] - 1.7
        if t > te: stroke_text(d, (W / 2, 1650), "СЕРИЯ 6 — СКОРО", font(50), WHITE + (int(255 * ease((t - te) / 0.3)),), 6)

def sound(sh, add, SR, n, tt):
    wt = sh.wt; ST = sh.STARTS; TOTAL = sh.TOTAL; rnd = np.random.default_rng(10)
    def T_(dur): return np.arange(int(dur * SR)) / SR
    def band(sig, lo, hi):
        f = np.fft.rfft(sig); fr = np.fft.rfftfreq(len(sig), 1 / SR); f[(fr < lo) | (fr > hi)] = 0; return np.fft.irfft(f, len(sig))
    def noise(dur, lo, hi):
        s_ = band(rnd.standard_normal(int(dur * SR)), lo, hi); return s_ / (np.abs(s_).max() + 1e-9)
    def thud(f=60, dur=0.4, dec=10): t_ = T_(dur); return np.sin(2 * np.pi * f * t_ * (1 + 0.6 * np.exp(-t_ * 30))) * np.exp(-t_ * dec)
    def tick(f=1320): t_ = T_(0.12); return np.sin(2 * np.pi * f * t_) * np.exp(-t_ * 28)
    def buzz(): t_ = T_(0.28); return np.sign(np.sin(2 * np.pi * 140 * t_)) * np.exp(-t_ * 9) * 0.5 + np.sin(2 * np.pi * 70 * t_) * np.exp(-t_ * 9)
    wind = noise(TOTAL, 120, 700)[:n]; wind = np.pad(wind, (0, n - len(wind))) * (0.55 + 0.45 * np.sin(2 * np.pi * 0.13 * tt + 1))
    drone = 0.5 * np.sin(2 * np.pi * 55 * tt) + 0.3 * np.sin(2 * np.pi * 82.4 * tt) + 0.2 * np.sin(2 * np.pi * 110.3 * tt) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.2 * tt))
    beat = np.zeros(n); k = 0.0
    while k < TOTAL - 0.4:
        for off, amp in ((0.0, 1.0), (0.22, 0.6)):
            sig = amp * thud(50, 0.3, 14); s0 = int((k + off) * SR); sig = sig[: max(0, n - s0)]; beat[s0:s0 + len(sig)] += sig
        k += 0.85
    env = np.clip(tt / 0.3, 0, 1) * np.clip((TOTAL - tt) / 1.5, 0, 1)
    music = (0.09 * wind + 0.1 * drone + 0.22 * beat) * env
    add(0.8 * thud(42, 0.9, 4), 0.0)
    def beep(dur, amp): t_ = T_(dur); return amp * np.sin(2 * np.pi * 740 * t_) * np.clip(t_ / 0.01, 0, 1) * np.clip((dur - t_) / 0.02, 0, 1)
    k = 0.0
    while k < sh.DUR[0] - 0.2: add(beep(0.16, 0.22), k); k += 1.2
    for dl, f in ((0.0, 200), (0.3, 150)): add(0.45 * thud(f, 0.35, 12), wt(0, "Ты пойдёшь") - 0.05 + dl)
    for j in range(int(sh.DUR[1] / 0.26)): add(0.13 * noise(0.11, 300, 1800) * np.exp(-T_(0.11) * 22), ST[1] + j * 0.26)   # шаги
    k = 0.0
    while k < sh.DUR[1] - 0.2: add(beep(0.16, 0.12 + 0.03 * k), ST[1] + k); k += 1.0
    add(0.22 * tick(880), ST[1] + wt(1, "два") + 1.2)
    add(0.9 * thud(40, 1.3, 3.2), ST[2]); add(0.3 * tick(660), ST[2] + wt(2, "двенадцать")); add(0.3 * tick(880), ST[2] + wt(2, "пятеро")); add(0.5 * thud(60, 0.6, 6), ST[2] + wt(2, "пятеро"))
    eng = np.sin(2 * np.pi * 38 * T_(sh.DUR[2])) * (0.6 + 0.4 * np.sin(2 * np.pi * 7 * T_(sh.DUR[2]))); add(0.06 * eng, ST[2])
    add(0.22 * tick(1100), ST[3] + wt(3, "К убежищу")); add(0.5 * buzz(), ST[3] + wt(3, "Нас туда") + 0.3); add(0.9 * thud(44, 1.2, 3.5), ST[3] + wt(3, "Нас туда") + 0.3)
    add(0.22 * tick(1100), ST[4] + wt(4, "С ними")); add(0.4 * buzz(), ST[4] + wt(4, "на семь")); add(0.6 * thud(46, 0.9, 5), ST[4] + wt(4, "на семь"))
    for f in (392, 466, 587): add(0.07 * np.sin(2 * np.pi * f * T_(1.6)) * np.exp(-T_(1.6) * 2.2), ST[5] + wt(5, "Пиши") - 0.1)
    add(0.2 * tick(1320), ST[5] + wt(5, "Пиши") - 0.1)
    return music

import render as _me
SH = Show(_me) if __name__ != "__main__" else None
if __name__ == "__main__":
    import render as ep
    SH = ep.SH; ep.SH.run("posle-5")
