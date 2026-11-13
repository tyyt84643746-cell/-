"""«После», серия 7 «Чужие» (сезон 2, 3D). Запуск: LIBGL_ALWAYS_SOFTWARE=1 xvfb-run -a python3 render.py [preview | sheet N K | at N T]"""
import math, os, random, sys
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(D, "..", "engine3d")); sys.path.insert(0, D)
import numpy as np
from village import *
from show import *
from script import SCENES, CAPTION_NUMS

LEADS = [0.3] * 6
TAILS = [0.6, 0.6, 0.8, 1.0, 1.0, 2.9]
KEY = {"чужое", "фото", "деда", "возможно", "охранник", "письмо", "вниз", "свет", "тепло", "еда", "300", "1962", "громов", "савельев", "вершинин", "вашей", "деревни", "мы", "выгнать", "вместе", "комментариях"}
DAY = dict(ENV, sun_dir=(-0.5, -0.45, -0.6), fog=0.016, shadow_center=(0, 0, -24), shadow_size=20)
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

LAMP = (1.9, 1.5, 1.0)
def hall():
    CON = rgb((118, 116, 112)); CON_D = rgb((90, 88, 86)); WD = rgb((112, 84, 60))
    it = [box(T(0, -0.1, -10) @ S(30, 0.2, 40), CON_D, cast=False), box(T(0, 5.0, -10) @ S(30, 0.2, 40), CON_D, cast=False),
          box(T(-15, 2.5, -10) @ S(0.2, 5, 40), CON, cast=False), box(T(15, 2.5, -10) @ S(0.2, 5, 40), CON, cast=False), box(T(0, 2.5, -30) @ S(30, 5, 0.2), CON, cast=False)]
    for x in (-7, 0, 7):
        for z in (-4, -14, -24): it.append(box(T(x, 2.5, z) @ S(0.6, 5, 0.6), CON))
    for x in (-10, -3.5, 3.5, 10):
        for z in (-2, -9, -16, -23):
            it.append(cyl(T(x, 4.85, z) @ S(0.6, 0.1, 0.6), C["dark"], cast=False)); it.append(ball(T(x, 4.7, z) @ S(0.35), rgb((255, 226, 170)), emit=4.0, cast=False))
    for k in range(10):                                                         # нары вдоль стен
        z = -27 + k * 3.0
        for sx in (-13.6, 13.6):
            if sx > 0 and -11 < z < -4: continue                               # место под фото
            for y in (0.5, 1.7): it.append(box(T(sx, y, z) @ S(2.2, 0.14, 2.4), WD)); it.append(box(T(sx, y + 0.14, z) @ S(2.1, 0.14, 2.3), rgb((120, 124, 110))))
    for j in range(6): it.append(box(T(-4 + j * 1.6, 0.4, -20) @ S(1.2, 0.8, 1.0), rgb((150, 116, 80)) if j % 2 else rgb((96, 110, 84))))   # ящики с едой
    it.append(box(T(4, 0.8, -6) @ S(3, 0.1, 1.2), WD)); it.append(cyl(T(4, 1.0, -6) @ S(0.5, 0.3, 0.5), rgb((180, 180, 190))))            # стол, котёл
    it.append(ball(T(4, 1.3, -6) @ S(0.6, 0.2, 0.6), rgb((240, 240, 250)), emit=0.6, cast=False))
    # фото на стене справа (z=-8)
    it.append(box(T(14.85, 2.4, -8) @ S(0.06, 1.6, 2.2), rgb((70, 52, 36)), cast=False)); it.append(box(T(14.8, 2.4, -8) @ S(0.04, 1.36, 1.96), rgb(SEP), emit=0.15, cast=False))
    for j, dz in enumerate((-0.6, 0, 0.6)):
        it.append(ball(T(14.76, 2.65, -8 + dz) @ S(0.02, 0.24, 0.22), rgb(SEP_D), cast=False)); it.append(box(T(14.76, 2.15, -8 + dz) @ S(0.02, 0.6, 0.36), rgb(SEP_D), cast=False))
    return it
HALL = hall()
HALL_L = [((x, 4.4, z), LAMP, 9.0) for x, z in ((-3.5, -2), (3.5, -2), (-3.5, -9), (3.5, -9), (10, -9), (-3.5, -16), (3.5, -16), (10, -2))]
CROWD = []
_r = random.Random(4)
for j in range(34):
    x = _r.uniform(-12, 12); z = _r.uniform(-27, -3)
    if abs(x) < 2.2 and z > -12: continue
    CROWD.append((j, x, z, _r.uniform(-PI, PI)))
def crowd(t, n=99, avoid=None):
    it = []
    for j, x, z, a in CROWD[:n]:
        if avoid and math.hypot(x - avoid[0], z - avoid[1]) < avoid[2]: continue
        p, _ = villager(j, T(x, 0, z) @ Ry(a), t, blink_seed=j * 0.3, look=0.3 * math.sin(t * 0.8 + j)); it += p
    return it

def scene_3d(si, t):
    wt = SH.wt
    if si == 1:                                                                 # охранник у ворот
        tr = wt(1, "Он прочитал") - 0.1; td = wt(1, "И молча")
        it = GROUND + TREES + wall() + gate(1.0); o = {}
        p, _ = guard(T(0.3, 0, GZ + 1.2), t, arm="phone" if t > tr else None, out=o, blink_seed=0.3, look=0.15 * math.sin(t)); it += p
        if t > tr: it += envelope(o["hand"] @ T(0, -0.14, 0.05) @ Rx(-0.4))
        p, _ = artyom(T(-0.6, 0, GZ + 3.0) @ Ry(PI + 0.3), t, blink_seed=0.7); it += p
        it += cat2(T(-1.4, 0, GZ + 3.3) @ Ry(PI), t)
        k = ease(t / SH.DUR[1])
        gl = [((0, 2.4, GZ - 1), (255, 190, 110), 500, 0.6)]
        return dict(items=it, eye=(lerp(3.4, 2.8, k), 1.9, GZ + lerp(7.6, 6.8, k)), tgt=(-0.25, 1.75, GZ + 1.6), fov=44, glows=gl, env=DAY,
                    lights=[((0, 3, GZ + 1.5), (1.0, 0.82, 0.55), 12.0), ((0.5, 2.5, GZ + 4.0), (0.8, 0.8, 0.8), 5.0)])
    if si == 2:                                                                 # зал
        k = ease(t / SH.DUR[2]); n = int(len(CROWD) * clamp(0.3 + t / max(0.1, wt(2, "И триста"))))
        it = HALL + crowd(t, n)
        p, _ = artyom(T(0, 0, 2.0) @ Ry(PI), t, blink_seed=0.7); it += p
        it += cat2(T(0.9, 0, 2.4) @ Ry(PI), t)
        return dict(items=it, eye=(lerp(-1.5, 1.5, k), lerp(4.2, 3.4, k), lerp(7.5, 6.5, k)), tgt=(0, 1.0, -14), fov=54, lights=HALL_L, env=IN_ENV, snow=False)
    # 0, 3, 4, 5 — у фото / с охранником / решение
    it = HALL + crowd(t)
    if si in (0, 3):
        it = HALL + crowd(t, 99, avoid=(10.5, -8.5, 4.8))
        p, _ = artyom(T(12.4, 0, -7.4) @ Ry(PI / 2 - 0.15), t, blink_seed=0.7, look=0.2 * math.sin(t * 0.9), mouth="o" if si == 0 and t > wt(0, "деда") else None); it += p
        it += cat2(T(12.8, 0, -6.4) @ Ry(PI / 2), t, look=-0.3)
        k = ease(t / SH.DUR[si])
        if si == 0: eye, tgt = (lerp(9.0, 10.4, k), 2.3, lerp(-5.2, -6.2, k)), (14.8, 2.2, -8.2)
        else: eye, tgt = (lerp(9.0, 9.6, k), 2.2, lerp(-12.4, -11.8, k)), (13.0, 1.9, -7.4)
        return dict(items=it, eye=eye, tgt=tgt, fov=44, lights=HALL_L[:6] + [((12.5, 3.2, -8), LAMP, 6.0)], env=IN_ENV, snow=False)
    if si == 4:
        tm = wt(4, "А заняли")
        it = [x for x in HALL if not (abs(x[1][0, 3] - 4) < 2 and abs(x[1][2, 3] + 6) < 1)] + crowd(t, 99, avoid=(3.8, -8.0, 3.6))
        p, _ = guard(T(4.6, 0, -9.0) @ Ry(-PI / 2 - 0.3), t, arm="point" if t > tm else None, blink_seed=0.3, look=-0.1); it += p
        p, _ = artyom(T(3.0, 0, -9.6) @ Ry(PI / 2 + 0.2), t, blink_seed=0.7, mouth="o" if t > tm else None); it += p
        k = ease(t / SH.DUR[4])
        return dict(items=it, eye=(lerp(3.9, 3.7, k), 1.9, lerp(-4.0, -5.0, k)), tgt=(3.8, 1.7, -9.3), fov=46, lights=HALL_L, env=IN_ENV, snow=False)
    p, _ = artyom(T(-0.3, 0, -1.0) @ Ry(PI), t, blink_seed=0.7); it += p               # 5: свои против чужих
    p, _ = kolyan(T(1.0, 0, -0.6) @ Ry(PI), t, blink_seed=0.2); it += p
    p, _ = guest(T(-1.6, 0, -0.6) @ Ry(PI), t, blink_seed=1.1); it += p
    it += cat2(T(0.4, 0, -1.6) @ Ry(PI), t)
    k = ease(t / SH.DUR[5])
    return dict(items=it, eye=(0.2, lerp(2.4, 2.8, k), lerp(4.6, 5.6, k)), tgt=(0, 1.4, -12), fov=50, lights=HALL_L, env=IN_ENV, snow=False)

def panel(d, x0, y0, x1, y1, k=1.0): d.rounded_rectangle([x0, y0, x1, y1], radius=28, fill=PANEL + (int(215 * k),))
def photo(d, k, names=0, y0=450):
    """Сепийная фотография 1962 года: трое у входа."""
    A = int(255 * k); x0, x1, y1 = 130, 950, y0 + 470
    d.rounded_rectangle([x0 + 10, y0 + 14, x1 + 10, y1 + 14], radius=8, fill=(0, 0, 0, int(110 * k)))
    d.rectangle([x0, y0, x1, y1], fill=(236, 226, 204, A))
    d.rectangle([x0 + 22, y0 + 22, x1 - 22, y1 - 80], fill=SEP + (A,))
    d.rectangle([x0 + 22, y1 - 200, x1 - 22, y1 - 80], fill=(176, 150, 112, A))
    d.rectangle([x0 + 300, y0 + 70, x1 - 300, y1 - 200], fill=(150, 124, 92, A)); d.rectangle([x0 + 355, y0 + 140, x1 - 355, y1 - 200], fill=SEP_D + (A,))
    for j, cx in enumerate((x0 + 150, x0 + 410, x0 + 670)):
        d.ellipse([cx - 34, y0 + 120, cx + 34, y0 + 190], fill=SEP_D + (A,)); d.rounded_rectangle([cx - 52, y0 + 196, cx + 52, y1 - 110], radius=18, fill=SEP_D + (A,))
    d.text((x1 - 40, y0 + 50), "1962", font=font(40), fill=(110, 86, 60, A), anchor="rm")
    for j, (cx, nm) in enumerate(((x0 + 150, "ГРОМОВ"), (x0 + 410, "САВЕЛЬЕВ"), (x0 + 670, "ВЕРШИНИН"))):
        if j < names: d.text((cx, y1 - 40), nm, font=font(34), fill=(70, 56, 40, A), anchor="mm")

def overlay(sh, si, t, d):
    wt = sh.wt
    stroke_text(d, (W / 2, 250), "ПОСЛЕ УЛЬТИМАТУМА", font(60), WHITE, 6)
    stroke_text(d, (W / 2, 350), "ДЕНЬ 32", font(122), YEL, 9)
    if si == 0:
        k = ease((t - wt(0, "А на стене") + 0.1) / 0.3)
        if k > 0: photo(d, k, 1 if t > wt(0, "деда") else 0)
        tq = wt(0, "Как такое")
        if t > tq: kq = ease((t - tq) / 0.2); stroke_text(d, (W / 2, 1480 + 20 * (1 - kq)), "???", font(150), RED + (int(255 * kq),), 10)
    if si == 1 and t > wt(1, "Он прочитал") - 0.1:
        k = ease((t - wt(1, "Он прочитал") + 0.1) / 0.25); panel(d, 60, 450, 520, 630, k); A = int(255 * k)
        d.text((290, 495), "ПРОПУСК", font=font(38), fill=(190, 196, 214, A), anchor="mm")
        d.text((290, 570), "ПИСЬМО 1962", font=font(52), fill=YEL + (A,), anchor="mm")
    if si == 2:
        ta = wt(2, "Свет")
        items = [("СВЕТ", wt(2, "Свет") + 0.2), ("ТЕПЛО", wt(2, "тепло") + 0.2), ("ЕДА", wt(2, "еда") + 0.2)]
        sh.checklist(d, t, [(n_, t0, True) for n_, t0 in items], y=450, w=400)
        t3 = wt(2, "триста")
        if t > t3 - 0.1:
            n = int(round(300 * ease((t - t3 + 0.1) / 0.9))); k = ease((t - t3 + 0.1) / 0.2)
            panel(d, 560, 450, 1020, 690, k); A = int(255 * k)
            d.text((790, 500), "ИЗ ГОРОДА", font=font(38), fill=(190, 196, 214, A), anchor="mm")
            d.text((790, 600), str(n), font=font(110), fill=(RED if n == 300 else WHITE) + (A,), anchor="mm")
    if si == 3:
        nm = sum(1 for sub in ("Громов", "Савельев", "Вершинин") if t > wt(3, sub))
        photo(d, 1.0, nm)
    if si == 4:
        a, b = wt(4, "Это убежище"), wt(4, "А заняли")
        if t > a:
            k = ease((t - a) / 0.25); panel(d, 60, 450, 620, 600, k); A = int(255 * k)
            d.text((100, 490), "ПОСТРОИЛИ ДЛЯ", font=font(34), fill=(190, 196, 214, A), anchor="lm"); d.text((100, 555), "ВАШЕЙ ДЕРЕВНИ", font=font(52), fill=GREEN + (A,), anchor="lm")
        if t > b:
            k = ease((t - b) / 0.25); panel(d, 60, 620, 620, 770, k); A = int(255 * k)
            d.text((100, 660), "А ЗАНЯЛИ", font=font(34), fill=(190, 196, 214, A), anchor="lm"); d.text((100, 725), "300 ЧУЖИХ", font=font(52), fill=RED + (A,), anchor="lm")
    if si == 5:
        sh.cta(d, t, wt(5, "Пиши") - 0.1, "ВЫГНАТЬ", "ВМЕСТЕ")
        te = sh.DUR[5] - 1.7
        if t > te: stroke_text(d, (W / 2, 1650), "СЕРИЯ 8 — СКОРО", font(50), WHITE + (int(255 * ease((t - te) / 0.3)),), 6)

def sound(sh, add, SR, n, tt):
    wt = sh.wt; ST = sh.STARTS; TOTAL = sh.TOTAL; rnd = np.random.default_rng(14)
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
    inside = (tt > ST[2]).astype(float)
    hum = 0.5 * np.sin(2 * np.pi * 100 * tt) + 0.3 * np.sin(2 * np.pi * 150 * tt)
    murmur = noise(TOTAL, 180, 900)[:n]; murmur = np.pad(murmur, (0, n - len(murmur))) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.7 * tt))
    out = ((tt > ST[1]) & (tt < ST[2])).astype(float)
    music = (0.08 * wind * out + 0.03 * hum * (1 - out) + 0.05 * murmur * (1 - out) + 0.1 * drone + 0.22 * beat) * env
    add(0.8 * thud(42, 0.9, 4), 0.0)
    add(0.6 * thud(50, 0.8, 5), wt(0, "А на стене")); add(0.5 * thud(70, 0.5, 7), wt(0, "деда"))
    for dl, f in ((0.0, 200), (0.3, 150), (0.6, 120)): add(0.4 * thud(f, 0.35, 12), wt(0, "Как такое") + dl)
    add(0.3 * noise(0.35, 1500, 6000) * np.exp(-T_(0.35) * 9), ST[1] + wt(1, "Он прочитал"))
    add(0.22 * tick(1100), ST[1] + wt(1, "Он прочитал") + 0.2)
    for j in range(6): add(0.13 * noise(0.12, 300, 1800) * np.exp(-T_(0.12) * 22), ST[1] + wt(1, "И молча") + j * 0.3)
    add(0.9 * thud(40, 1.3, 3.2), ST[2])
    for sub in ("Свет", "тепло", "еда"): add(0.22 * tick(1320), ST[2] + wt(2, sub) + 0.2); add(0.16 * tick(1760), ST[2] + wt(2, sub) + 0.28)
    for j in range(12): add(0.09 * tick(900 + 40 * j), ST[2] + wt(2, "триста") + j * 0.07)
    add(0.6 * thud(46, 0.9, 5), ST[2] + wt(2, "триста") + 0.9)
    add(0.6 * thud(50, 0.8, 5), ST[3])
    for sub in ("Громов", "Савельев", "Вершинин"): add(0.25 * tick(660), ST[3] + wt(3, sub))
    add(0.5 * thud(60, 0.6, 6), ST[4] + wt(4, "Это убежище")); add(0.9 * thud(40, 1.3, 3.2), ST[4] + wt(4, "А заняли")); add(0.4 * buzz(), ST[4] + wt(4, "А заняли") + 0.1)
    for f in (392, 466, 587): add(0.07 * np.sin(2 * np.pi * f * T_(1.6)) * np.exp(-T_(1.6) * 2.2), ST[5] + wt(5, "Пиши") - 0.1)
    add(0.2 * tick(1320), ST[5] + wt(5, "Пиши") - 0.1)
    return music

import render as _me
SH = Show(_me) if __name__ != "__main__" else None
if __name__ == "__main__":
    import render as ep
    SH = ep.SH; ep.SH.run("posle-7")
