"""«После», серия 9 «Колонна» (сезон 2, 3D). Запуск: LIBGL_ALWAYS_SOFTWARE=1 xvfb-run -a python3 render.py [preview | sheet N K | at N T]"""
import math, os, random, sys
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(D, "..", "engine3d")); sys.path.insert(0, D)
import numpy as np
from village import *
from show import *
from script import SCENES, CAPTION_NUMS

LEADS = [0.3] * 6
TAILS = [0.6, 0.6, 0.8, 0.9, 1.4, 3.0]
KEY = {"солдат", "выгнать", "ворот", "сделают", "5", "первым", "никого", "правду", "удара", "не", "было", "договорились", "рыжее", "топлива", "свет", "связь", "30", "целым", "один", "будет", "комментариях"}
DAY = dict(ENV, sun_dir=(-0.5, -0.45, -0.6), fog=0.012, shadow_center=(0, 0, -16), shadow_size=24)
IN_ENV = dict(sun_col=(0, 0, 0), amb_top=(0.2, 0.19, 0.17), amb_bot=(0.1, 0.09, 0.08), fog=0.02, fog_col=(0.08, 0.07, 0.06),
              sky=((0.03, 0.03, 0.03),) * 3, shadow_center=(0, 0, -6), shadow_size=24)
PI = math.pi
SEP = (196, 170, 128); SEP_D = (92, 74, 54)

def forest(z0, z1, seed=7, gap=3.2, n=46):
    rnd = random.Random(seed); it = []
    for _ in range(n):
        x = rnd.uniform(gap, 30) * rnd.choice((-1, 1)); it += pine(T(x, 0, rnd.uniform(z1, z0)), rnd.uniform(4.5, 7.5))
    return it
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

GROUND = [box(T(0, -0.25, -20) @ S(240, 0.5, 240), C["snow"]), box(T(0, 0.012, -10) @ S(7, 0.02, 200), rgb((196, 204, 224)), cast=False)]
TREES = [x for x in forest(40, -80, 21, 6.0, 90) if abs(x[1][0, 3]) > 11]
CON = rgb((122, 124, 132)); CON_D = rgb((96, 98, 108)); IRON = rgb((70, 76, 86))
GZ = -30.0
def wall():
    it = [box(T(-23, 3, GZ) @ S(40, 6, 1.6), CON), box(T(23, 3, GZ) @ S(40, 6, 1.6), CON), box(T(0, 6.6, GZ) @ S(6.4, 1.2, 1.6), CON_D)]
    for x in range(-40, 41, 4):
        if abs(x) > 4: it.append(box(T(x, 3, GZ + 0.82) @ S(0.25, 6, 0.06), CON_D, cast=False))
    for x in (-43, -3, 3, 43): it.append(box(T(x, 6.15, GZ) @ S(40 if abs(x) > 5 else 0.01, 0.3, 1.8), C["snow"]))
    it.append(box(T(0, 0.05, GZ - 3) @ S(6, 0.1, 6), rgb((255, 196, 120)), emit=1.2, cast=False))     # свет изнутри
    it.append(box(T(0, 3, GZ - 0.9) @ S(5.6, 6, 0.1), rgb((255, 196, 120)), emit=1.5, cast=False))
    it.append(box(T(-3.6, 7.6, GZ) @ S(0.5, 1.6, 0.5), C["dark"])); it.append(cyl(T(-3.6, 8.5, GZ + 0.3) @ Rx(PI / 2 - 0.25) @ S(0.9, 0.6, 0.9), C["dark"]))
    it.append(cyl(T(-3.6, 8.55, GZ + 0.62) @ Rx(PI / 2 - 0.25) @ S(0.75, 0.05, 0.75), rgb((255, 250, 230)), emit=12.0, cast=False))
    it.append(box(T(3.6, 5.2, GZ + 0.85) @ S(0.7, 0.7, 0.12), C["dark"], cast=False))                # динамик
    return it
SEARCH = (-3.6, 8.55, GZ + 0.7); SPEAK = (3.6, 5.2, GZ + 1.0)
def gate(g):
    it = []
    for sgn in (-1, 1):
        x = sgn * (1.5 + 3.0 * g)
        it.append(box(T(x, 3, GZ + 0.2) @ S(3.0, 6, 0.4), IRON))
        for y in (1.2, 3, 4.8): it.append(box(T(x, y, GZ + 0.42) @ S(2.8, 0.14, 0.06), rgb((56, 60, 70)), cast=False))
        it.append(box(T(x - sgn * 1.2, 3, GZ + 0.42) @ S(0.12, 5.6, 0.06), rgb((56, 60, 70)), cast=False))
    return it

GUARD = dict(body=rgb((66, 80, 62)), body_d=rgb((50, 60, 46)), hat=rgb((40, 48, 38)), hat_b=rgb((56, 66, 52)), legs=rgb((40, 44, 40)), pack=None)
def guard(root, t, **kw): return person(root, t, colors=GUARD, **kw)


OLIVE = rgb((92, 104, 70)); OLIVE_D = rgb((70, 80, 54)); CANVAS = rgb((112, 116, 86))
def truck(m, t, lights=True):
    it = [box(m @ T(0, 0.75, -0.2) @ S(2.4, 0.3, 7.4), C["dark"]),
          box(m @ T(0, 1.55, -2.7) @ S(2.3, 1.9, 1.5), OLIVE), box(m @ T(0, 1.0, -3.75) @ S(2.2, 0.9, 0.8), OLIVE_D),
          box(m @ T(0, 2.0, -3.46) @ S(2.0, 0.8, 0.04), rgb((30, 38, 50)), cast=False),
          box(m @ T(0, 2.1, 1.0) @ S(2.45, 2.6, 4.8), CANVAS), box(m @ T(0, 3.45, 1.0) @ S(2.5, 0.12, 4.9), C["snow"])]
    for z in (-2.9, 0.0, 2.3):
        for sx in (-1.15, 1.15): it.append(cyl(m @ T(sx, 0.5, z) @ Rz(PI / 2) @ S(1.0, 0.35, 1.0), C["dark"]))
    if lights:
        for sx in (-0.75, 0.75): it.append(ball(m @ T(sx, 1.05, -4.17) @ S(0.3, 0.3, 0.08), rgb((255, 244, 210)), emit=6.0, cast=False))
    it.append(box(m @ T(0, 2.2, 3.43) @ S(2.0, 1.4, 0.04), rgb((20, 22, 18)), cast=False))
    return it
OFF = dict(body=rgb((92, 104, 70)), body_d=rgb((70, 80, 54)), hat=rgb((60, 70, 48)), hat_b=rgb((150, 40, 40)), legs=rgb((60, 66, 50)), pack=None)
def officer(root, t, **kw): return person(root, t, colors=OFF, **kw)
GLEB = dict(body=rgb((40, 36, 40)), body_d=rgb((30, 26, 30)), hat=rgb((110, 112, 120)), hat_b=rgb((130, 132, 140)), legs=rgb((34, 32, 36)), pack=None)
def gleb(root, t, **kw): return person(root, t, colors=GLEB, beard=rgb((60, 50, 46)), **kw)
KIDC = [dict(body=rgb(c), body_d=rgb(tuple(int(v * 0.7) for v in c)), hat=rgb(h), hat_b=rgb(h), legs=rgb((60, 60, 80)), pack=None)
        for c, h in (((232, 140, 170), (240, 240, 244)), ((90, 150, 200), (220, 90, 70)), ((110, 180, 120), (60, 70, 120)))]
SITE = GROUND + TREES + wall() + gate(1.0)
TRUCK_Z = [-11.5 + j * 9.5 for j in range(5)]
def column(t, arrive=1.0):
    """arrive: 0 — колонна далеко, 1 — стоит у ворот."""
    it = []
    for j, z in enumerate(TRUCK_Z):
        zz = z + 60 * (1 - arrive) + 3 * j * (1 - arrive)
        it += truck(T(0.2, 0.03 * math.sin(t * 14 + j) * (1 - arrive), zz), t)
    return it

def people(t, mood=None, n=14):
    """Деревенские и городские у ворот, лицом к дороге."""
    it = []
    p, _ = artyom(T(-1.4, 0, -24.0), t, blink_seed=0.7, mouth=mood, look=0.1 * math.sin(t)); it += p
    it += cat2(T(-0.6, 0, -23.2), t, look=0.3 * math.sin(t * 1.3))
    p, _ = kolyan(T(0.2, 0, -24.6), t, blink_seed=0.2, mouth=mood); it += p
    p, _ = guest(T(-2.8, 0, -24.8), t, blink_seed=1.1, mouth=mood); it += p
    for j in range(3):
        p, _ = person(T(1.4 + j * 0.8, 0, -24.2 - 0.3 * j), t, colors=KIDC[j], scale=0.58, blink_seed=j * 0.6, mouth=mood); it += p
    r = random.Random(3)
    for j in range(n):
        x = r.uniform(-4.5, 4.5); z = r.uniform(-28.6, -25.6)
        p, _ = villager(j, T(x, 0, z) @ Ry(r.uniform(-0.3, 0.3)), t, blink_seed=j * 0.3, mouth=mood if j % 2 else None); it += p
    return it

def depot(t):
    it = [box(T(0, -0.25, 0) @ S(240, 0.5, 240), rgb((120, 108, 104)))]
    for j, (x, z) in enumerate(((-6, -4), (0, -6), (6, -4), (-3, -12), (4, -12))):
        it.append(cyl(T(x, 2.2, z) @ S(4.4, 4.4, 4.4), rgb((150, 150, 156)) if j != 1 else rgb((50, 46, 44))))
    r = random.Random(5)
    for k in range(26):
        ph = (t * 0.25 + k / 26) % 1.0
        x = 0 + 2.5 * math.sin(k * 2.1) + 3 * ph; y = 4 + ph * 22; s_ = 2.2 + ph * 6
        it.append(ball(T(x, y, -6 - ph * 3) @ S(s_), rgb((40, 38, 40)), cast=False))
    for k in range(10):
        f = 0.75 + 0.25 * math.sin(t * 13 + k * 1.7)
        it.append(ball(T(1.8 * math.sin(k), 4.4 + 0.8 * (k % 3) * f, -6 + 1.4 * math.cos(k)) @ S(1.6 * f, 2.6 * f, 1.6 * f), rgb((255, 130, 40)), emit=7.0, cast=False))
    for x in range(-30, 31, 6): it += pine(T(x, 0, 14 + (x % 4)), 5)
    return it
FIRE_ENV = dict(sun_dir=(0.3, -0.6, 0.5), sun_col=(0.1, 0.06, 0.05), amb_top=(0.12, 0.06, 0.04), amb_bot=(0.05, 0.03, 0.03), fog=0.01, fog_col=(0.3, 0.12, 0.05),
                sky=((0.06, 0.02, 0.02), (0.45, 0.16, 0.05), (0.3, 0.12, 0.05)), hz=0.45, shadow_center=(0, 0, -6), shadow_size=24)

def scene_3d(si, t):
    wt = SH.wt
    if si == 0:
        arr = ease(t / (SH.DUR[0] + 2.0))
        it = SITE + column(t, 0.25 + 0.4 * arr) + people(t)
        p, _ = gleb(T(0.4, 0, -20.0), t, blink_seed=0.4, look=-0.2); it += p
        k = ease(t / SH.DUR[0])
        return dict(items=it, eye=(lerp(-2.2, -1.8, k), 3.5, lerp(-29.2, -28.8, k)), tgt=(1.0, 1.2, 6), fov=48, env=DAY)
    if si == 1:
        arr = 0.65 + 0.35 * ease(t / (SH.DUR[1] - 1.2))
        it = SITE + column(t, arr) + people(t)
        tg = wt(1, "Глеб вышел"); gz = lerp(-20.0, -17.0, ease((t - tg) / 1.4))
        p, _ = gleb(T(0.4, 0, gz), t, blink_seed=0.4, walk=t * 6 if tg < t < tg + 1.4 else None); it += p
        k = ease(t / SH.DUR[1])
        return dict(items=it, eye=(lerp(-12.0, -11.0, k), lerp(4.5, 3.8, k), lerp(-6.0, -9.0, k)), tgt=(0.4, 1.0, lerp(-6, -14, k)), fov=48, env=DAY)
    if si in (2, 3) and not (si == 3 and t > wt(3, "А рыжее") - 0.1):
        it = SITE + column(t) + people(t, n=8)
        to = 0.2
        p, _ = officer(T(2.7, 0, -16.2) @ Ry(PI + 0.4), t, blink_seed=0.5, mouth="o" if int(t * 5) % 2 else None); it += p
        p, _ = gleb(T(-0.2, 0, -17.6) @ Ry(0.5), t, blink_seed=0.4, look=0.2, mouth="o" if si == 3 else None); it += p
        p, _ = artyom(T(-1.4, 0, -18.6) @ Ry(0.6), t, blink_seed=0.7, look=0.3); it += p
        k = ease(t / SH.DUR[si])
        if si == 2: eye, tgt = (lerp(-0.4, -0.7, k), 2.1, lerp(-22.4, -23.0, k)), (1.2, 1.7, -16.9)
        else: eye, tgt = (lerp(1.6, 1.4, k), 2.0, lerp(-19.8, -20.2, k)), (2.7, 2.0, -16.2)
        return dict(items=it, eye=eye, tgt=tgt, fov=42, env=DAY)
    if si == 3:                                                                 # горит склад
        tt_ = t - wt(3, "А рыжее") + 0.1; k = ease(tt_ / 3.0)
        f = 0.85 + 0.15 * math.sin(t * 9)
        return dict(items=depot(t), eye=(lerp(-14, -10, k), lerp(6, 5, k), lerp(22, 18, k)), tgt=(0, 6, -6), fov=46, env=FIRE_ENV, snow=False,
                    lights=[((0, 5, -6), (2.2, 1.0, 0.35), 40 * f)], glows=[((0, 5.5, -6), (255, 120, 40), 520, 0.8 * f), ((0, 5, -6), (255, 200, 120), 160, 0.9)])
    if si == 4:                                                                 # облегчение
        it = SITE + column(t) + people(t, mood="smile" if t > wt(4, "А мир") else None)
        k = ease(t / SH.DUR[4])
        return dict(items=it, eye=(lerp(-0.4, 0.4, k), 2.1, lerp(-17.0, -18.4, k)), tgt=(-0.5, 1.5, -26), fov=46, env=DAY)
    it = SITE + column(t)                                                       # 5: Глеб один
    r = random.Random(3)
    for j in range(10):
        x = -4 + (j % 5) * 2.0; z = -28 + (j // 5) * 1.2 + 1.3 * t
        if abs(x - 0.4) < 1.0: x += 1.4
        p, _ = villager(j, T(x, 0, z) @ Ry(PI), t, walk=t * 6 + j, blink_seed=j * 0.3); it += p
    p, _ = gleb(T(0.4, 0, -22.0), t, blink_seed=0.4, look=0.25 * math.sin(t * 0.8)); it += p
    k = ease(t / SH.DUR[5])
    return dict(items=it, eye=(lerp(0.9, 0.6, k), lerp(1.9, 2.3, k), lerp(-17.6, -16.8, k)), tgt=(0.3, 1.7, -22.5), fov=44, env=DAY)

def panel(d, x0, y0, x1, y1, k=1.0): d.rounded_rectangle([x0, y0, x1, y1], radius=28, fill=PANEL + (int(215 * k),))

def overlay(sh, si, t, d):
    wt = sh.wt
    stroke_text(d, (W / 2, 250), "ПОСЛЕ УЛЬТИМАТУМА", font(60), WHITE, 6)
    stroke_text(d, (W / 2, 350), "ДЕНЬ 33", font(122), YEL, 9)
    def tiles(tq, a, b, y=1340):
        for j, (x, lab, c, dl) in enumerate(((290, a, RED, 0.0), (790, b, GREEN, 0.3))):
            k = ease((t - tq - dl) / 0.25)
            if k <= 0: continue
            A = int(255 * k); yy = y + 30 * (1 - k)
            d.rounded_rectangle([x - 225, yy, x + 225, yy + 170], radius=36, fill=PANEL + (int(230 * k),), outline=c + (A,), width=6)
            d.text((x, yy + 85), lab, font=font(54), fill=c + (A,), anchor="mm")
    if si == 0: tiles(wt(0, "Что они") - 0.05, "ВЫГОНЯТ?", "НЕТ?")
    if si == 1:
        t5 = wt(1, "пять")
        n = int(round(5 * ease((t - t5 + 0.1) / 0.8))) if t > t5 - 0.1 else 0
        if n:
            panel(d, 60, 450, 520, 690)
            d.text((100, 500), "ГРУЗОВИКОВ", font=font(38), fill=(190, 196, 214), anchor="lm")
            d.text((100, 600), str(n), font=font(110), fill=YEL if n == 5 else WHITE, anchor="lm")
    if si == 2:
        tn = wt(2, "Никого")
        if t > tn:
            k = ease((t - tn) / 0.25); A = int(255 * k); panel(d, 60, 450, 700, 600, k)
            d.text((100, 490), "ОФИЦЕР", font=font(34), fill=(190, 196, 214, A), anchor="lm"); d.text((100, 555), "НИКОГО НЕ ВЫГОНЯТЬ", font=font(46), fill=GREEN + (A,), anchor="lm")
        tp = wt(2, "правду")
        if t > tp: k = ease((t - tp) / 0.25); stroke_text(d, (W / 2, 1560 + 20 * (1 - k)), "ПРАВДА", font(100), YEL + (int(255 * k),), 9)
    if si == 3:
        sh.checklist(d, t, [("УДАР", wt(3, "Удара") + 0.3, False), ("ДОГОВОРИЛИСЬ", wt(3, "Договорились") + 0.3, True), ("ПОЖАР НА СКЛАДЕ", wt(3, "склад") + 0.2, True)], y=450, w=560)
    if si == 4:
        sh.checklist(d, t, [("СВЕТ", wt(4, "свет") + 0.2, False), ("СВЯЗЬ", wt(4, "связь") + 0.2, False)], y=450, w=400)
        t30 = wt(4, "Тридцать")
        if t > t30:
            k = ease((t - t30) / 0.25); A = int(255 * k); panel(d, 500, 450, 1020, 690, k)
            d.text((760, 500), "ДНЕЙ СТРАХА", font=font(38), fill=(190, 196, 214, A), anchor="mm"); d.text((760, 600), "30", font=font(110), fill=RED + (A,), anchor="mm")
        tm = wt(4, "А мир")
        if t > tm: k = ease((t - tm) / 0.25); stroke_text(d, (W / 2, 1560 + 20 * (1 - k)), "МИР ЦЕЛ", font(110), GREEN + (int(255 * k),), 10)
    if si == 5:
        sh.cta(d, t, wt(5, "Пиши") - 0.1, "ПРОСТИТЬ", "ВЫГНАТЬ")
        te = sh.DUR[5] - 1.7
        if t > te: stroke_text(d, (W / 2, 1650), "ФИНАЛ СЕЗОНА — СКОРО", font(50), WHITE + (int(255 * ease((t - te) / 0.3)),), 6)

def sound(sh, add, SR, n, tt):
    wt = sh.wt; ST = sh.STARTS; TOTAL = sh.TOTAL; rnd = np.random.default_rng(18)
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
    murmur = noise(TOTAL, 180, 900)[:n]; murmur = np.pad(murmur, (0, n - len(murmur))) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.7 * tt))
    fire = ((tt > ST[3] + wt(3, "А рыжее") - 0.1) & (tt < ST[4])).astype(float)
    eng_env = np.clip((tt - 0.0) / 1.0, 0, 1) * np.clip((ST[2] + 0.5 - tt) / 1.0, 0, 1)
    eng = (np.sin(2 * np.pi * 34 * tt) + 0.5 * np.sin(2 * np.pi * 51 * tt)) * (0.6 + 0.4 * np.sin(2 * np.pi * 8 * tt)) * eng_env
    crack = noise(TOTAL, 800, 6000)[:n]; crack = np.pad(crack, (0, n - len(crack))) * (rnd.random(n) > 0.995)
    happy = (tt > ST[4] + wt(4, "А мир")).astype(float)
    music = (0.07 * wind * (1 - fire) + 0.12 * eng + 0.05 * murmur * (1 - fire) + 0.25 * crack * fire + 0.1 * drone * (1 - 0.7 * happy) + 0.22 * beat * (1 - happy)) * env
    add(0.8 * thud(42, 0.9, 4), 0.0)
    for dl, f in ((0.0, 200), (0.3, 150)): add(0.45 * thud(f, 0.35, 12), wt(0, "Что они") - 0.05 + dl)
    for j in range(5): add(0.18 * tick(880 + 110 * j), ST[1] + wt(1, "пять") + j * 0.16)
    t_ = T_(0.8); add(0.3 * noise(0.8, 2000, 8000) * np.exp(-t_ * 4), ST[1] + sh.DUR[1] - 1.4)                                   # тормоза
    add(0.5 * thud(90, 0.25, 16), ST[2] + 0.15)                                                                                  # дверь кабины
    add(0.5 * thud(60, 0.6, 6), ST[2] + wt(2, "Никого")); add(0.6 * thud(46, 0.9, 5), ST[2] + wt(2, "правду"))
    add(0.4 * buzz(), ST[3] + wt(3, "Удара") + 0.3); add(0.25 * tick(1320), ST[3] + wt(3, "Договорились") + 0.3)
    add(0.9 * thud(38, 1.5, 3.0), ST[3] + wt(3, "А рыжее") - 0.1)
    for sub in ("свет", "связь"): add(0.35 * buzz(), ST[4] + wt(4, sub) + 0.2)
    add(0.6 * thud(46, 0.9, 5), ST[4] + wt(4, "Тридцать"))
    for f in (392, 494, 587, 784): add(0.07 * np.sin(2 * np.pi * f * T_(2.6)) * np.exp(-T_(2.6) * 1.2), ST[4] + wt(4, "А мир"))
    for f in (392, 466, 587): add(0.07 * np.sin(2 * np.pi * f * T_(1.6)) * np.exp(-T_(1.6) * 2.2), ST[5] + wt(5, "Пиши") - 0.1)
    add(0.2 * tick(1320), ST[5] + wt(5, "Пиши") - 0.1)
    return music

import render as _me
SH = Show(_me) if __name__ != "__main__" else None
if __name__ == "__main__":
    import render as ep
    SH = ep.SH; ep.SH.run("posle-9")
