"""«Последний урок», серия 6 «Будильник» (3D). Запуск: LIBGL_ALWAYS_SOFTWARE=1 xvfb-run -a python3 render.py [preview | sheet N K | at N T]"""
import math, os, random, sys
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(D, "..", "engine3d")); sys.path.insert(0, D)
import numpy as np
from school import *
from show import *
from script import SCENES, CAPTION_NUMS

LEADS = [0.3] * 6
TAILS = [0.6, 0.6, 0.9, 0.7, 0.9, 3.0]
KEY = {"12", "40", "мимо", "звонок", "звук", "будильник", "телефон", "зазвонил", "повернулись", "лестнице", "побежали", "20.", "10.", "заперта", "захрипел", "открылась", "11", "димы", "бинт", "скажешь", "комментариях"}
PI = math.pi
ENV = dict(sun_dir=(0.65, -0.55, 0.25), sun_col=(1.1, 0.95, 0.75), amb_top=(0.34, 0.36, 0.42), amb_bot=(0.2, 0.19, 0.18), fog=0.006, fog_col=(0.6, 0.66, 0.78),
           sky=((0.32, 0.5, 0.82), (0.66, 0.76, 0.9), (0.7, 0.74, 0.8)), hz=0.45, shadow_center=(-2, 0, -1), shadow_size=12)
CORR = dict(ENV, sun_col=(0, 0, 0), amb_top=(0.2, 0.2, 0.2), amb_bot=(0.1, 0.1, 0.1), fog=0.03, fog_col=(0.1, 0.1, 0.1), shadow_center=(8, 0, -14), shadow_size=18)
ROOF_ENV = dict(ENV, sun_dir=(0.5, -0.5, -0.4), sun_col=(0.9, 0.7, 0.55), sky=((0.28, 0.32, 0.5), (0.7, 0.55, 0.5), (0.6, 0.5, 0.48)), fog=0.006, fog_col=(0.62, 0.52, 0.5),
                shadow_center=(64, -2, 0), shadow_size=14)
WX = 67.8                                                                       # фасад со стороны двора
def roof_world(t):
    it = [x for x in roof_set(t) if not (abs(x[1][0, 3] - 60) < 0.1 and abs(x[1][1, 3] + 4) < 0.1)]   # без сплошного куба здания
    F = rgb((200, 186, 160))
    it += [box(T(60, -4, -8.0 + 0.1) @ S(15.6, 8, 0.2), F), box(T(60, -4, 8.0 - 0.1) @ S(15.6, 8, 0.2), F), box(T(52.2, -4, 0) @ S(0.2, 8, 15.6), F)]
    it += [box(T(WX, -6.1, 0) @ S(0.2, 3.8, 15.6), F), box(T(WX, -0.5, 0) @ S(0.2, 1.0, 15.6), F),
           box(T(WX, -2.1, -4.6) @ S(0.2, 2.2, 6.6), F), box(T(WX, -2.1, 4.6) @ S(0.2, 2.2, 6.6), F)]                # проём окна z -1.3..1.3, y -3.2..-1.0
    it += [box(T(64, -4.05, 0) @ S(7.4, 0.1, 15.6), WOOD, cast=False), box(T(60.5, -2.1, 0) @ S(0.2, 4.2, 15.6), WALL, cast=False)]
    it.append(box(T(66, -1.3, 0) @ S(1.0, 0.06, 0.3), rgb((255, 250, 235)), emit=2.0, cast=False))
    for z in (-6, 6):
        for y in (-6.1, -2.1): it.append(box(T(WX + 0.11, y, z) @ S(0.04, 1.8, 2.4), rgb((40, 50, 70)), cast=False))
    return it
def hose(y_end):
    L = 0.9 - y_end
    return [cyl(T(WX + 0.45, 0.9 - L / 2, 0.3) @ S(0.12, L, 0.12), rgb((200, 40, 36))), cyl(T(WX - 0.1, 0.92, 0.3) @ Rz(PI / 2) @ S(0.12, 1.1, 0.12), rgb((200, 40, 36)))]
def climber(j, y, t, col_fn=None):
    root = T(WX + 0.75, y, 0.3) @ Ry(-PI / 2)
    if col_fn: p, _ = col_fn(root, t, arm="up", blink_seed=j)
    else: p, _ = kid(j, root, t, arm="up", blink_seed=j * 0.3)
    return p
def horde(t, n=9, reach=True):
    r = random.Random(7); it = []
    for j in range(n):
        x = WX + 1.6 + r.uniform(0, 3.5); z = r.uniform(-3.5, 3.5)
        p, _ = zombie(T(x, -8, z) @ Ry(-PI / 2 + r.uniform(-0.5, 0.5)), t + j, colors=GUARD if j % 2 else PE, blink_seed=99, look=0.2 * math.sin(t + j)); it += p
    return it
OUT_L = [((66, -1.6, 0), (1.4, 1.3, 1.1), 7.0)]
DOOR_C = (86.0, -8.0, 4.6)
def canteen(door_a=0.0, lit=0.0):
    F = rgb((196, 176, 150)); it = [box(T(91, -5.0, -1.5) @ S(10, 6.2, 11), F), box(T(91, -5.0, 6.4) @ S(10, 6.2, 1.2), F), box(T(91, -3.3, 4.6) @ S(10, 2.8, 2.4), F),
                                     box(T(91, -1.7, 0) @ S(10.4, 0.4, 14.4), rgb((110, 90, 80)))]
    for z in (-4.5, -1.5, 1.5): it.append(box(T(85.9, -4.6, z) @ S(0.04, 1.8, 2.2), rgb((50, 62, 80)), cast=False))
    it.append(box(T(85.84, -4.6, 1.5) @ S(0.03, 1.0, 1.4), rgb((250, 250, 245)), emit=0.5, cast=False))
    it.append(box(T(87.5, -6.3, 4.6) @ S(3.0, 3.4, 2.4), rgb((255, 220, 160)), emit=1.6 * lit, cast=False))            # проём изнутри
    m = T(86.0, -8.0, 3.5) @ Ry(door_a) @ T(0, 0, 1.1)
    it += [box(m @ T(0, 1.35, 0) @ S(0.1, 2.7, 2.2), rgb((120, 130, 140))), box(m @ T(-0.08, 1.3, 0.8) @ S(0.06, 0.06, 0.16), METAL)]
    return it
LADDER_Z = 6.6
def ladder():
    it = []
    for dz in (-0.3, 0.3): it.append(box(T(WX + 0.2, -4.0, LADDER_Z + dz) @ S(0.06, 8.6, 0.06), METAL))
    for k in range(20): it.append(box(T(WX + 0.2, -8 + 0.42 * k, LADDER_Z) @ S(0.05, 0.05, 0.6), METAL))
    return it
PHONE_PT = (79.0, -7.9, -16.0)
_r = random.Random(7)
HZ = [(WX + 1.6 + _r.uniform(0, 3.5), _r.uniform(-3.5, 3.5), _r.uniform(-0.5, 0.5)) for _ in range(12)]
def horde2(t, k=0.0, skip=()):
    it = []
    for j, (x, z, a) in enumerate(HZ):
        if j in skip: continue
        tx, tz = PHONE_PT[0] - 1.5 + (j % 4) * 1.0, PHONE_PT[2] + 1.5 + (j // 4) * 1.0
        kk = clamp(k * 1.3 - j * 0.03)
        px, pz = lerp(x, tx, kk), lerp(z, tz, kk)
        ang = math.atan2(tx - x, tz - z) if kk > 0 else -PI / 2 + a
        p, _ = zombie(T(px, -8, pz) @ Ry(ang), t + j, colors=GUARD if j % 2 else PE, walk=t * 3 + j if 0 < kk < 1 else None, blink_seed=99); it += p
    return it
def phone_on(t, ring):
    c = rgb((190, 215, 255)) if (not ring or int(t * 6) % 2) else rgb((255, 240, 160))
    return [box(T(*PHONE_PT) @ S(0.2, 0.04, 0.34), C["dark"]), box(T(PHONE_PT[0], PHONE_PT[1] + 0.025, PHONE_PT[2]) @ S(0.16, 0.01, 0.28), c, emit=2.5, cast=False)]
YARD = roof_world(0) + ladder()

TABLE = rgb((170, 140, 110))
def hall2():
    it = [box(T(120, -0.1, 0) @ S(14, 0.2, 14), rgb((170, 160, 150)), cast=False), box(T(120, 3.6, 0) @ S(14, 0.2, 14), WHITE_, cast=False)]
    for (x, z, sx, sz) in ((113, 0, 0.2, 14), (127, 0, 0.2, 14), (120, -7, 14, 0.2), (120, 7, 14, 0.2)): it.append(box(T(x, 1.8, z) @ S(sx, 3.6, sz), rgb((214, 200, 170)), cast=False))
    for z in (-3.5, 0.0):
        it.append(box(T(120, 0.75, z) @ S(8, 0.08, 1.2), TABLE)); it.append(box(T(120, 0.38, z) @ S(7.6, 0.74, 0.1), METAL))
    for x in (117, 123): it.append(box(T(x, 3.55, -2) @ S(1.6, 0.06, 0.3), rgb((255, 250, 235)), emit=2.0, cast=False))
    it.append(box(T(126.9, 1.2, 4.6) @ S(0.06, 2.4, 2.0), rgb((120, 130, 140)), cast=False))
    return it
HALL2 = hall2()
HALL2_L = [((117, 3.2, -2), (1.6, 1.5, 1.3), 9.0), ((123, 3.2, -2), (1.6, 1.5, 1.3), 9.0), ((121, 2.5, 4), (1.0, 0.9, 0.8), 6.0)]
IN2 = dict(ENV, sun_col=(0, 0, 0), amb_top=(0.2, 0.19, 0.17), amb_bot=(0.1, 0.09, 0.08), fog=0.0, sky=((0.03, 0.03, 0.03),) * 3, shadow_center=(120, 0, 0), shadow_size=9)
DIMA = (122.4, 0, 1.6)

def trio(t, base, face, walk=None, gap=0.9, mood=None):
    it = []
    for j, fn in enumerate((liza, max_, timur)):
        x, y, z = base
        r = T(x + math.cos(face) * 0 - (j - 1) * gap * math.cos(face), y, z + (j - 1) * gap * math.sin(face)) @ Ry(face)
        p, _ = fn(r, t, walk=(walk + j * 1.3) if walk is not None else None, blink_seed=j * 0.6, mouth=mood); it += p
    return it

def scene_3d(si, t):
    wt = SH.wt
    if si == 0:                                                                 # двор сверху
        it = YARD + horde2(t) + canteen()
        for j, (fn, z) in enumerate(((liza, -1.4), (max_, -0.4), (timur, 0.6))):
            p, _ = fn(T(67.4, 0.3, z) @ Ry(PI / 2), t, blink_seed=j * 0.6); it += p
        k = ease(t / SH.DUR[0])
        return dict(items=it, eye=(lerp(83.0, 84.0, k), lerp(2.6, 3.0, k), lerp(10.0, 10.6, k)), tgt=(70.0, -2.0, -0.2), fov=52, env=ROOF_ENV, snow=False)
    if si == 1:                                                                 # будильник и бросок
        tb = wt(1, "и бросил") + 0.3; o = {}
        it = YARD + horde2(t) + canteen()
        p, _ = max_(T(67.3, 0.3, -0.4) @ Ry(PI / 2), t, arm="phone" if t < tb else "up", out=o, blink_seed=0.7); it += p
        p, _ = timur(T(67.2, 0.3, 0.8) @ Ry(PI / 2 - 0.4), t, blink_seed=0.2); it += p
        if t < tb: it += [box(o["hand"] @ T(0, -0.16, 0.06) @ S(0.16, 0.3, 0.03), C["dark"]), box(o["hand"] @ T(0, -0.16, 0.078) @ S(0.13, 0.26, 0.004), rgb((190, 215, 255)), 1.4, False)]
        else:
            kf = clamp((t - tb) / 1.4); px = lerp(68.0, PHONE_PT[0], kf); pz = lerp(-0.4, PHONE_PT[2], kf); py = lerp(2.4, PHONE_PT[1], kf) + 9 * math.sin(kf * PI)
            it.append(box(T(px, py, pz) @ Rx(t * 12) @ S(0.2, 0.34, 0.04), C["dark"]))
        k = ease(t / SH.DUR[1])
        if t > tb + 0.25:
            gl = [((PHONE_PT[0], PHONE_PT[1] + 0.2, PHONE_PT[2]), (190, 215, 255), 70, 0.8)] if t > tb + 1.4 else []
            if t > tb + 1.4: it += phone_on(t, False)
            return dict(items=it, eye=(83.0, 6.0, 15.0), tgt=(75.5, -7.0, -5.0), fov=60, env=ROOF_ENV, snow=False, glows=gl)
        return dict(items=it, eye=(lerp(71.5, 73.5, k), lerp(0.4, 1.2, k), lerp(4.6, 6.0, k)), tgt=(67.6, 1.6, -0.2), fov=52, env=ROOF_ENV, snow=False)
    if si == 2:                                                                 # зомби идут на звук
        kz = ease((t - wt(2, "И все") + 0.3) / (SH.DUR[2] - 0.6))
        it = YARD + horde2(t, kz) + canteen() + phone_on(t, True)
        k = ease(t / SH.DUR[2])
        return dict(items=it, eye=(lerp(88, 89, k), lerp(6.0, 7.0, k), lerp(12.0, 13.0, k)), tgt=(77.0, -7.4, lerp(-1.0, -6.0, k)), fov=56, env=ROOF_ENV, snow=False,
                    glows=[((PHONE_PT[0], PHONE_PT[1] + 0.2, PHONE_PT[2]), (255, 240, 180), 90, 0.9 if int(t * 6) % 2 else 0.4)])
    if si == 3:                                                                 # спуск и бег
        tr = wt(3, "и побежали"); kd = ease(t / max(0.1, tr)); kr = ease((t - tr) / (SH.DUR[3] - tr - 0.3))
        it = YARD + horde2(t + 9, 1.0) + canteen() + phone_on(t, True)
        if t < tr:
            for j, fn in enumerate((liza, max_, timur)):
                y = lerp(0.2, -8, clamp(kd * 1.3 - j * 0.15)); p, _ = fn(T(WX + 0.55, y, LADDER_Z) @ Ry(-PI / 2), t, arm="up", blink_seed=j * 0.6); it += p
            eye, tgt = (77.0, -5.4, 11.5), (WX + 0.5, lerp(-2.0, -6.0, kd), LADDER_Z)
        else:
            x = lerp(WX + 1.0, DOOR_C[0] - 1.0, kr); z = lerp(LADDER_Z, DOOR_C[2] + 0.4, kr)
            it += trio(t, (x, -8, z), PI / 2, walk=t * 9)
            eye, tgt = (x - 4.5, -5.6, z + 5.0), (x + 3.0, -7.0, z - 1.0)
        return dict(items=it, eye=eye, tgt=tgt, fov=56, env=dict(ROOF_ENV, shadow_center=(78, -8, 4), shadow_size=16), snow=False,
                    glows=[((PHONE_PT[0], PHONE_PT[1] + 0.2, PHONE_PT[2]), (255, 240, 180), 70, 0.8 if int(t * 6) % 2 else 0.3)])
    if si == 4:                                                                 # дверь
        to = wt(4, "И тут дверь") + 0.2; th = wt(4, "Сзади")
        da = -1.6 * ease((t - to) / 0.6); lit = ease((t - to) / 0.6)
        it = YARD + canteen(da, lit)
        it += trio(t, (DOOR_C[0] - 1.1, -8, DOOR_C[2] - 0.2), PI / 2, mood="o" if t > th else None)
        zx = lerp(80.6, 83.0, clamp((t - th + 0.4) / (SH.DUR[4] - th + 0.4)))
        p, _ = zombie(T(zx, -8, 6.6) @ Ry(PI / 2), t, colors=GUARD, walk=t * 3, blink_seed=99); it += p
        k = ease(t / SH.DUR[4])
        L = [((87.0, -6.0, 4.6), (2.0, 1.7, 1.2), 10 * lit + 0.01)]
        return dict(items=it, eye=(lerp(82.4, 82.0, k), -6.0, lerp(11.6, 12.0, k)), tgt=(82.4, -6.8, 4.6), fov=64, lights=L, env=dict(ROOF_ENV, shadow_center=(84, -8, 4), shadow_size=10), snow=False)
    tb = wt(5, "Но у Димы") - 0.1; kb = ease((t - tb) / 1.4)                     # 5: внутри
    it = list(HALL2); o = {}
    for j in range(10):
        x = 116 + (j % 5) * 1.3 + (0.4 if j >= 5 else 0); z = 2.4 + (j // 5) * 1.2
        p, _ = kid(j * 2 + 4, T(x, 0, z) @ Ry(PI / 2 + 0.6 * (1 if x < 120 else -1) * 0.5), t, blink_seed=j * 0.3, mouth="smile" if j % 3 == 0 else None); it += p
    p, _ = kid(13, T(*DIMA) @ Ry(PI / 2 + 0.6), t, arm="hold", out=o, blink_seed=4.4, look=-0.5 * kb); it += p
    it.append(cyl(o["hand"] @ T(0, 0.2, 0) @ S(0.25, 0.34, 0.25), rgb((250, 250, 245)), emit=0.6))
    it += trio(t, (125.2, 0, 4.2), -PI / 2 - 0.2, gap=0.9, mood="smile")
    eye = (lerp(119.0, 125.4, kb), lerp(2.6, 1.9, kb), lerp(-3.0, -0.4, kb)); tgt = (lerp(121.0, DIMA[0] + 0.3, kb), lerp(1.0, 1.4, kb), lerp(3.0, DIMA[2], kb))
    return dict(items=it, eye=eye, tgt=tgt, fov=lerp(54, 44, kb), lights=HALL2_L, env=IN2, snow=False)

def panel(d, x0, y0, x1, y1, k=1.0): d.rounded_rectangle([x0, y0, x1, y1], radius=28, fill=PANEL + (int(215 * k),))








def clock(sh, si, t):
    gt = sh.STARTS[si] + t; return f"12:{min(25, 19 + int(7 * gt / sh.TOTAL)):02d}"

def overlay(sh, si, t, d):
    wt = sh.wt
    stroke_text(d, (W / 2, 250), "ПОСЛЕДНИЙ УРОК", font(60), WHITE, 6)
    stroke_text(d, (W / 2, 350), clock(sh, si, t), font(122), RED, 9)
    if si == 0:
        panel(d, 520, 450, 1020, 700)
        d.text((560, 500), "ВО ДВОРЕ", font=font(36), fill=(190, 196, 214), anchor="lm"); d.text((560, 570), "12 ЗОМБИ", font=font(60), fill=RED, anchor="lm")
        if t > wt(0, "До столовой"): d.text((560, 650), "ДО СТОЛОВОЙ 40 М", font=font(40), fill=YEL, anchor="lm")
    if si == 1:
        ta = wt(1, "завёл")
        if t > ta and t < wt(1, "и бросил") + 0.3:
            k = ease((t - ta) / 0.25); A = int(255 * k)
            d.rounded_rectangle([240, 460, 840, 720], radius=40, fill=(20, 22, 30, int(235 * k)))
            d.text((W / 2, 530), "БУДИЛЬНИК", font=font(40), fill=(190, 196, 214, A), anchor="mm"); d.text((W / 2, 630), "12:21", font=font(110), fill=WHITE + (A,), anchor="mm")
    if si == 2:
        tz = wt(2, "зазвонил")
        if t > tz: stroke_text(d, (W / 2 + 8 * math.sin(t * 40), 900), "ДЗЫНЬ-ДЗЫНЬ!", font(96), YEL, 9)
    if si == 3:
        tr = wt(3, "и побежали"); kr = ease((t - tr) / (sh.DUR[3] - tr - 0.3))
        if t > tr:
            m = int(round(40 * (1 - kr)))
            panel(d, 560, 450, 1020, 690)
            d.text((600, 500), "ДО СТОЛОВОЙ", font=font(36), fill=(190, 196, 214), anchor="lm"); d.text((600, 600), f"{m} М", font=font(100), fill=GREEN if m == 0 else YEL, anchor="lm")
    if si == 4:
        to = wt(4, "И тут дверь") + 0.2
        if t < to:
            k = ease((t - 0.1) / 0.2); stroke_text(d, (W / 2, 900), "ЗАПЕРТО", font(110), RED + (int(255 * k),), 10)
        else:
            k = ease((t - to) / 0.2); stroke_text(d, (W / 2, 900), "ОТКРЫЛИ!", font(110), GREEN + (int(255 * k),), 10)
    if si == 5:
        tb = wt(5, "Но у Димы") - 0.1
        if t < tb:
            panel(d, 60, 450, 560, 600)
            d.text((100, 490), "ВМЕСТЕ", font=font(34), fill=(190, 196, 214), anchor="lm"); d.text((100, 555), "24 ИЗ 24", font=font(58), fill=GREEN, anchor="lm")
        else:
            k = ease((t - tb - 0.6) / 0.25); A = int(255 * k); panel(d, 640, 450, 1020, 600, k)
            d.text((680, 490), "ДИМА", font=font(34), fill=(190, 196, 214, A), anchor="lm"); d.text((680, 555), "БИНТ?", font=font(58), fill=RED + (A,), anchor="lm")
        sh.cta(d, t, wt(5, "Пиши") - 0.1, "СКАЗАТЬ", "МОЛЧАТЬ")
        te = sh.DUR[5] - 1.7
        if t > te: stroke_text(d, (W / 2, 1650), "СЕРИЯ 7 — СКОРО", font(50), WHITE + (int(255 * ease((t - te) / 0.3)),), 6)

def sound(sh, add, SR, n, tt):
    wt = sh.wt; ST = sh.STARTS; TOTAL = sh.TOTAL; rnd = np.random.default_rng(35)
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
    wind2 = noise(TOTAL, 200, 1200)[:n]; wind2 = np.pad(wind2, (0, n - len(wind2))) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.2 * tt))
    inside = (tt > ST[5]).astype(float)
    fast = np.zeros(n); k = ST[3]
    while k < ST[4] + 0.2:
        sig = thud(52, 0.25, 16); s0 = int(k * SR); sig = sig[: max(0, n - s0)]; fast[s0:s0 + len(sig)] += sig; k += 0.42
    run = ((tt > ST[3]) & (tt < ST[4] + 0.2)).astype(float)
    music = (0.09 * wind2 * (1 - inside) + 0.1 * drone + 0.22 * beat * (1 - run) * (1 - 0.5 * inside) + 0.3 * fast) * env
    def groan(at, dur=1.6, amp=0.2):
        t_ = T_(dur); g = noise(dur, 90, 420) * (0.5 + 0.5 * np.sin(2 * np.pi * 2.3 * t_)) * np.clip(t_ / 0.3, 0, 1) * np.clip((dur - t_) / 0.4, 0, 1); add(amp * g, at)
    groan(0.3, sh.DUR[0] - 0.3, 0.16)
    add(0.22 * tick(1320), wt(0, "До столовой"))
    for j in range(3): add(0.12 * tick(1900), ST[1] + wt(1, "завёл") + j * 0.12)
    add(0.3 * noise(0.5, 400, 4000) * np.sin(np.pi * T_(0.5) / 0.5) ** 2, ST[1] + wt(1, "и бросил") + 0.3)
    t_ = T_(sh.DUR[2] + sh.DUR[3]); ring = (np.sin(2 * np.pi * 880 * t_) + 0.6 * np.sin(2 * np.pi * 1320 * t_)) * (np.sin(2 * np.pi * 3 * t_) > 0) * np.clip((sh.DUR[2] + sh.DUR[3] - t_) / 0.5, 0, 1)
    add(0.06 * ring, ST[2] + wt(2, "зазвонил"))
    groan(ST[2] + wt(2, "И все"), 3.0, 0.3)
    for j in range(8): add(0.1 * noise(0.08, 1500, 5000) * np.exp(-T_(0.08) * 30), ST[3] + 0.2 + j * 0.25)          # лестница
    for j in range(int((sh.DUR[3] - wt(3, "и побежали")) / 0.2)): add(0.12 * noise(0.08, 300, 1800) * np.exp(-T_(0.08) * 25), ST[3] + wt(3, "и побежали") + j * 0.2)
    for sub, f in (("Сорок", 660), ("Двадцать", 880), ("Десять", 1100)): add(0.2 * tick(f), ST[3] + wt(3, sub))
    for j in range(3): add(0.4 * thud(100, 0.15, 20) + 0.15 * noise(0.15, 800, 3000) * np.exp(-T_(0.15) * 20), ST[4] + 0.2 + j * 0.3)   # дёргают дверь
    add(0.4 * buzz(), ST[4] + 0.4)
    groan(ST[4] + wt(4, "Сзади"), 1.8, 0.35)
    to = ST[4] + wt(4, "И тут дверь") + 0.2
    add(0.4 * noise(0.6, 300, 2000) * np.exp(-T_(0.6) * 4), to); add(0.9 * thud(40, 1.2, 3.2), to + 0.5)
    for f in (523, 659, 784): add(0.07 * np.sin(2 * np.pi * f * T_(1.4)) * np.exp(-T_(1.4) * 2), ST[5])
    add(0.8 * thud(44, 1.1, 3.5), ST[5] + wt(5, "Но у Димы") + 0.6); add(0.4 * buzz(), ST[5] + wt(5, "бинт"))
    for f in (392, 466, 587): add(0.07 * np.sin(2 * np.pi * f * T_(1.6)) * np.exp(-T_(1.6) * 2.2), ST[5] + wt(5, "Пиши") - 0.1)
    add(0.2 * tick(1320), ST[5] + wt(5, "Пиши") - 0.1)
    return music

import render as _me
SH = Show(_me) if __name__ != "__main__" else None
if __name__ == "__main__":
    import render as ep
    SH = ep.SH; ep.SH.run("shkola-6")
