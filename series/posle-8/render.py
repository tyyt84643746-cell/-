"""«После», серия 8 «Глеб» (сезон 2, 3D). Запуск: LIBGL_ALWAYS_SOFTWARE=1 xvfb-run -a python3 render.py [preview | sheet N K | at N T]"""
import math, os, random, sys
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(D, "..", "engine3d")); sys.path.insert(0, D)
import numpy as np
from village import *
from show import *
from script import SCENES, CAPTION_NUMS

LEADS = [0.3] * 6
TAILS = [0.6, 0.6, 0.9, 1.0, 1.2, 3.0]
KEY = {"всех", "нельзя", "сделаешь", "глеб", "мало", "чужие", "склад", "400", "год", "соврал", "замолчали", "женщина", "10", "рации", "слово", "приезжайте", "кого", "комментариях"}
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
HALL = [x for x in hall() if not (abs(x[1][0, 3] - 4) < 2 and abs(x[1][2, 3] + 6) < 1)]   # без стола с котлом в центре
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


GLEB = dict(body=rgb((40, 36, 40)), body_d=rgb((30, 26, 30)), hat=rgb((110, 112, 120)), hat_b=rgb((130, 132, 140)), legs=rgb((34, 32, 36)), pack=None)
def gleb(root, t, **kw): return person(root, t, colors=GLEB, beard=rgb((60, 50, 46)), **kw)
WOMAN = dict(body=rgb((150, 60, 70)), body_d=rgb((110, 44, 52)), hat=rgb((220, 210, 190)), hat_b=rgb((236, 226, 206)), legs=rgb((60, 50, 60)), pack=None)
CR = [(dict(body=rgb(c), body_d=rgb(tuple(int(v * 0.7) for v in c)), hat=rgb(h), hat_b=rgb(h), legs=rgb((50, 50, 60)), pack=None))
      for c, h in (((96, 78, 70), (60, 66, 90)), ((70, 84, 100), (120, 70, 60)), ((110, 96, 80), (50, 60, 56)), ((80, 70, 96), (90, 96, 110)), ((66, 90, 84), (36, 40, 52)))]
A0 = (1.9, -9.0); G0 = (5.3, -9.0)                                          # Артём и Глеб в центре зала

def duel(t, gm=None, am=None, ga=None):
    it = []
    p, _ = artyom(T(A0[0], 0, A0[1]) @ Ry(PI / 2), t, blink_seed=0.7, mouth=am, look=0.1 * math.sin(t)); it += p
    it += cat2(T(A0[0] - 0.6, 0, A0[1] + 0.9) @ Ry(PI / 2), t, look=0.3)
    p, _ = gleb(T(G0[0], 0, G0[1]) @ Ry(-PI / 2), t, blink_seed=0.4, mouth=gm, arm=ga); it += p
    return it

def scene_3d(si, t):
    wt = SH.wt
    base = HALL + crowd(t, 99, avoid=(3.6, -7.5, 4.6)) if si != 2 else HALL
    if si == 0:
        it = base + duel(t, ga="up" if t > wt(0, "деревенским") else None)
        k = ease(t / SH.DUR[0])
        return dict(items=it, eye=(lerp(3.5, 3.7, k), lerp(3.0, 2.5, k), lerp(2.6, 1.0, k)), tgt=(3.6, 1.5, -9.0), fov=48, lights=HALL_L, env=IN_ENV, snow=False)
    if si == 1:
        it = base + duel(t, gm="o" if int(t * 5) % 2 else None)
        k = ease(t / SH.DUR[1])
        return dict(items=it, eye=(lerp(3.0, 3.3, k), 2.0, lerp(-6.4, -6.9, k)), tgt=(G0[0], 2.0, G0[1]), fov=40, lights=HALL_L, env=IN_ENV, snow=False)
    if si == 2:                                                                 # склад
        it = list(HALL)
        cols = [rgb((150, 116, 80)), rgb((96, 110, 84)), rgb((130, 100, 76)), rgb((120, 120, 130))]
        to = wt(2, "Артём открыл") + 0.4; door = ease((t - to) / 0.8)
        for r in range(4):
            for c in range(10):
                for h in range(3):
                    it.append(box(T(-11 + c * 1.3, 0.4 + h * 0.82, -27 + r * 1.6) @ S(1.1, 0.75, 1.3), cols[(r + c + h) % 4]))
        it.append(box(T(-5.0 - 2.2 * door, 1.8, -20.6) @ S(2.2, 3.6, 0.2), rgb((70, 76, 86))))
        it.append(box(T(-0.6 + 2.2 * door, 1.8, -20.6) @ S(2.2, 3.6, 0.2), rgb((70, 76, 86))))
        it.append(box(T(-9.8, 1.8, -20.6) @ S(7.4, 3.6, 0.2), rgb((96, 98, 104)))); it.append(box(T(5.0, 1.8, -20.6) @ S(9, 3.6, 0.2), rgb((96, 98, 104))))
        it.append(box(T(-2.8, 4.3, -20.6) @ S(28, 1.4, 0.2), rgb((96, 98, 104))))
        p, _ = artyom(T(-2.8, 0, -18.4) @ Ry(PI), t, blink_seed=0.7, walk=t * 6 if door >= 1 and t < to + 2.0 else None); it += p
        it += cat2(T(-2.0, 0, -18.0) @ Ry(PI), t)
        k = ease(t / SH.DUR[2])
        L = HALL_L[:5] + [((-4, 3.0, -24), (2.0, 1.6, 1.1), 10 * door + 0.01), ((-8, 3.0, -25), (2.0, 1.6, 1.1), 10 * door + 0.01)]
        return dict(items=it, eye=(lerp(-1.6, -2.4, k), lerp(2.6, 2.4, k), lerp(-12.5, -15.0, k)), tgt=(-3.5, 1.4, -24), fov=50, lights=L, env=IN_ENV, snow=False)
    if si == 3:                                                                 # люди встают рядом
        tw = wt(3, "Потом одна") + 0.5; tt_ = wt(3, "Потом ещё") + 0.4
        it = HALL + crowd(t, 99, avoid=(1.0, -9.0, 5.2)) + duel(t)
        n = (1 if t > tw else 0) + int(10 * clamp((t - tt_) / 1.4))
        for j in range(n):
            if j == 0: root = T(A0[0] - 0.2, 0, A0[1] - 1.2) @ Ry(PI / 2); p, _ = person(root, t, colors=WOMAN, hat="scarf", skirt=rgb((60, 50, 60)), blink_seed=1.3)
            else:
                r, c = (j - 1) // 5, (j - 1) % 5
                root = T(A0[0] - 1.4 - r * 1.1, 0, A0[1] - 2.4 + c * 1.1) @ Ry(PI / 2); p, _ = person(root, t, colors=CR[j % 5], blink_seed=j * 0.4)
            it += p
        k = ease(t / SH.DUR[3])
        return dict(items=it, eye=(lerp(5.4, 5.0, k), lerp(3.0, 2.8, k), lerp(-4.2, -4.8, k)), tgt=(1.2, 1.3, -9.4), fov=50, lights=HALL_L, env=IN_ENV, snow=False)
    # 4, 5: рация
    it = HALL + crowd(t, 99, avoid=(-10.5, -24.0, 4.0))
    it.append(box(T(-11, 0.8, -26.5) @ S(2.4, 0.1, 1.0), rgb((112, 84, 60))))
    for dx in (-1.0, 1.0): it.append(box(T(-11 + dx, 0.4, -26.5) @ S(0.1, 0.8, 0.8), rgb((112, 84, 60))))
    it.append(box(T(-11.2, 1.1, -26.7) @ S(1.0, 0.5, 0.4), rgb((60, 66, 60))))
    on = int(t * 4) % 2 == 0
    it.append(ball(T(-10.85, 1.2, -26.48) @ S(0.08), rgb((255, 60, 50)), emit=8.0 if on else 0.5, cast=False))
    o = {}
    talk = si == 4 and t > wt(4, "И сказал") - 0.1
    p, _ = gleb(T(-11.0, 0, -25.4) @ Ry(PI if si == 4 else 0.3), t, arm="phone" if talk or si == 5 else None, out=o, blink_seed=0.4, mouth="o" if talk else None); it += p
    if "hand" in o: it.append(box(o["hand"] @ T(0, -0.12, 0.06) @ S(0.12, 0.22, 0.08), C["dark"]))
    k = ease(t / SH.DUR[si])
    if si == 4: eye, tgt = (lerp(-6.4, -6.8, k), 2.1, lerp(-22.8, -23.4, k)), (-11.0, 1.6, -26.0)
    else: eye, tgt = (lerp(-11.6, -11.4, k), lerp(1.9, 1.8, k), lerp(-22.2, -22.8, k)), (-11.0, 1.95, -25.4)
    L = HALL_L[:6] + [((-10.85, 1.4, -26.2), (1.0, 0.2, 0.15), 3.0 if on else 0.01), ((-10, 3.2, -24), LAMP, 6.0)]
    return dict(items=it, eye=eye, tgt=tgt, fov=44, lights=L, env=IN_ENV, snow=False)

def panel(d, x0, y0, x1, y1, k=1.0): d.rounded_rectangle([x0, y0, x1, y1], radius=28, fill=PANEL + (int(215 * k),))

def overlay(sh, si, t, d):
    wt = sh.wt
    stroke_text(d, (W / 2, 250), "ПОСЛЕ УЛЬТИМАТУМА", font(60), WHITE, 6)
    stroke_text(d, (W / 2, 350), "ДЕНЬ 32", font(122), YEL, 9)
    def tiles(tq, a, b, y=1340):
        for j, (x, lab, c, dl) in enumerate(((290, a, GREEN, 0.0), (790, b, RED, 0.3))):
            k = ease((t - tq - dl) / 0.25)
            if k <= 0: continue
            A = int(255 * k); yy = y + 30 * (1 - k)
            d.rounded_rectangle([x - 225, yy, x + 225, yy + 170], radius=36, fill=PANEL + (int(230 * k),), outline=c + (A,), width=6)
            d.text((x, yy + 85), lab, font=font(54), fill=c + (A,), anchor="mm")
    if si == 0:
        panel(d, 60, 450, 560, 690)
        d.text((100, 500), "МЕСТ В УБЕЖИЩЕ", font=font(34), fill=(190, 196, 214), anchor="lm")
        d.text((100, 560), "400", font=font(56), fill=GREEN, anchor="lm"); d.text((100, 635), "НАС 352", font=font(46), fill=WHITE, anchor="lm")
        tiles(wt(0, "Что ты") - 0.05, "СПОРИТЬ?", "УЙТИ?")
    if si == 1:
        k = ease((t - wt(1, "Глеб") + 0.1) / 0.25)
        if k > 0:
            panel(d, 60, 450, 520, 600, k); A = int(255 * k)
            d.text((100, 490), "ГЛАВНЫЙ", font=font(34), fill=(190, 196, 214, A), anchor="lm"); d.text((100, 555), "ГЛЕБ", font=font(60), fill=RED + (A,), anchor="lm")
    if si == 2:
        a = wt(2, "Еды"); b = wt(2, "На целый"); c = wt(2, "Глеб соврал")
        if t > a - 0.1:
            k = ease((t - a + 0.1) / 0.25); A = int(255 * k); panel(d, 60, 450, 600, 690, k)
            d.text((100, 500), "ЕДЫ НА СКЛАДЕ", font=font(34), fill=(190, 196, 214, A), anchor="lm")
            d.text((100, 565), "400 ЧЕЛОВЕК", font=font(52), fill=WHITE + (A,), anchor="lm")
            if t > b: d.text((100, 640), "1 ГОД", font=font(56), fill=GREEN, anchor="lm")
        if t > c:
            kk = ease((t - c) / 0.15); s_ = 1 + 0.4 * (1 - kk)
            d.rounded_rectangle([W / 2 - 360 * s_, 1560 - 70 * s_, W / 2 + 360 * s_, 1560 + 70 * s_], radius=16, outline=RED, width=9, fill=PANEL + (200,))
            d.text((W / 2, 1560), "ГЛЕБ СОВРАЛ", font=font(int(80 * s_)), fill=RED, anchor="mm")
    if si == 3:
        tw = wt(3, "Потом одна") + 0.5; tt_ = wt(3, "Потом ещё") + 0.4
        n = (1 if t > tw else 0) + int(10 * clamp((t - tt_) / 1.4))
        panel(d, 60, 450, 560, 690)
        d.text((100, 500), "ЗА АРТЁМА", font=font(36), fill=(190, 196, 214), anchor="lm")
        d.text((100, 600), f"+{n}", font=font(110), fill=GREEN if n else WHITE, anchor="lm")
    if si == 4:
        tg = wt(4, "Приезжайте")
        if t > tg - 0.05:
            s_ = "ПРИЕЗЖАЙТЕ"; n = int(clamp((t - tg + 0.05) / 0.7) * len(s_))
            panel(d, 110, 1380, 970, 1560)
            d.text((150, 1420), "РАЦИЯ:", font=font(34), fill=(190, 196, 214), anchor="lm")
            d.text((150, 1500), s_[:n] + ("_" if int(t * 4) % 2 else ""), font=font(70), fill=RED, anchor="lm")
    if si == 5:
        sh.cta(d, t, wt(5, "Пиши") - 0.1, "ВОЕННЫХ", "БАНДИТОВ")
        te = sh.DUR[5] - 1.7
        if t > te: stroke_text(d, (W / 2, 1650), "СЕРИЯ 9 — СКОРО", font(50), WHITE + (int(255 * ease((t - te) / 0.3)),), 6)

def sound(sh, add, SR, n, tt):
    wt = sh.wt; ST = sh.STARTS; TOTAL = sh.TOTAL; rnd = np.random.default_rng(16)
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
    hum = 0.5 * np.sin(2 * np.pi * 100 * tt) + 0.3 * np.sin(2 * np.pi * 150 * tt)
    murmur = noise(TOTAL, 180, 900)[:n]; murmur = np.pad(murmur, (0, n - len(murmur))) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.7 * tt))
    quiet = ((tt > ST[3] + wt(3, "замолчали")) & (tt < ST[3] + wt(3, "Потом одна"))).astype(float)
    music = (0.03 * hum + 0.05 * murmur * (1 - quiet) + 0.1 * drone + 0.22 * beat * (1 - 0.8 * quiet)) * env
    add(0.8 * thud(42, 0.9, 4), 0.0)
    add(0.5 * thud(70, 0.5, 7), wt(0, "деревенским"))
    for dl, f in ((0.0, 200), (0.3, 150)): add(0.45 * thud(f, 0.35, 12), wt(0, "Что ты") - 0.05 + dl)
    add(0.5 * thud(60, 0.6, 6), ST[1] + wt(1, "Глеб")); add(0.4 * buzz(), ST[1] + wt(1, "Чужие"))
    to = ST[2] + wt(2, "Артём открыл") + 0.4
    t_ = T_(0.9); add(0.4 * noise(0.9, 40, 300) * (0.6 + 0.4 * np.sin(2 * np.pi * 17 * t_)) * np.clip((0.9 - t_) / 0.2, 0, 1), to); add(0.6 * thud(46, 0.9, 5), to + 0.8)
    add(0.22 * tick(1100), ST[2] + wt(2, "Еды")); add(0.22 * tick(1320), ST[2] + wt(2, "На целый"))
    add(0.9 * thud(40, 1.3, 3.2), ST[2] + wt(2, "Глеб соврал")); add(0.4 * buzz(), ST[2] + wt(2, "Глеб соврал"))
    add(0.4 * thud(90, 0.3, 14), ST[3] + wt(3, "Потом одна") + 0.5)
    for j in range(10): add(0.13 * noise(0.12, 300, 1800) * np.exp(-T_(0.12) * 22) + 0.12 * tick(880 + 50 * j)[:int(0.12 * SR)], ST[3] + wt(3, "Потом ещё") + 0.4 + j * 0.14)
    st = noise(2.5, 1500, 7000) * 0.5; add(0.08 * st, ST[4] + wt(4, "Глеб ушёл"))                                                         # шум рации
    for j in range(2): t_ = T_(0.12); add(0.12 * np.sin(2 * np.pi * 1200 * t_), ST[4] + wt(4, "И сказал") - 0.3 + j * 0.16)
    add(0.9 * thud(38, 1.5, 3.0), ST[4] + wt(4, "Приезжайте") + 0.6); add(0.3 * noise(0.5, 1500, 6000) * np.exp(-T_(0.5) * 6), ST[4] + wt(4, "Приезжайте") + 0.7)
    for f in (392, 466, 587): add(0.07 * np.sin(2 * np.pi * f * T_(1.6)) * np.exp(-T_(1.6) * 2.2), ST[5] + wt(5, "Пиши") - 0.1)
    add(0.2 * tick(1320), ST[5] + wt(5, "Пиши") - 0.1)
    return music

import render as _me
SH = Show(_me) if __name__ != "__main__" else None
if __name__ == "__main__":
    import render as ep
    SH = ep.SH; ep.SH.run("posle-8")
