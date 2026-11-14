"""«Последний урок», серия 5 «Одиннадцать» (3D). Запуск: LIBGL_ALWAYS_SOFTWARE=1 xvfb-run -a python3 render.py [preview | sheet N K | at N T]"""
import math, os, random, sys
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(D, "..", "engine3d")); sys.path.insert(0, D)
import numpy as np
from school import *
from show import *
from script import SCENES, CAPTION_NUMS

LEADS = [0.3] * 6
TAILS = [0.6, 0.7, 0.9, 0.8, 1.6, 3.0]
KEY = {"шланге", "зомби", "2", "успеешь", "сил", "успел", "физрук", "вцепился", "разжал", "13", "11", "столовую", "листок", "пойдёте", "двор", "комментариях"}
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
CAF = dict(x=86.0)
def canteen():
    F = rgb((196, 176, 150)); it = [box(T(91, -5.0, 0) @ S(10, 6.2, 14), F), box(T(91, -1.7, 0) @ S(10.4, 0.4, 14.4), rgb((110, 90, 80)))]
    for z in (-4.5, -1.5, 1.5, 4.5): it.append(box(T(85.9, -4.6, z) @ S(0.04, 1.8, 2.2), rgb((50, 62, 80)), cast=False))
    it.append(box(T(85.84, -4.6, 1.5) @ S(0.03, 1.0, 1.4), rgb((250, 250, 245)), emit=0.5, cast=False))      # листок
    for k in range(4): it.append(box(T(85.8, -4.3 - k * 0.18, 1.5) @ S(0.02, 0.06, 0.9 - 0.15 * (k % 2)), rgb((30, 30, 40)), cast=False))
    return it
CANTEEN = canteen()
SIGN_PT = (85.9, -4.6, 1.5)

def scene_3d(si, t):
    wt = SH.wt
    if si == 0:                                                                 # Тимур на шланге
        it = roof_world(t) + horde(t) + hose(-3.4)
        y = -1.8 + 0.25 * math.sin(t * 2)
        it += climber(0, y, t, timur)
        p, _ = max_(T(67.75, 0.3, 0.3) @ Ry(PI / 2), t, arm="push", blink_seed=0.7, mouth="o"); it += p
        p, _ = zombie(T(WX + 0.75, -3.9, 0.3) @ Ry(-PI / 2), t, arm="up", blink_seed=99); it += p
        k = ease(t / SH.DUR[0])
        return dict(items=it, eye=(lerp(79.0, 78.0, k), lerp(-1.6, -1.2, k), lerp(5.6, 5.0, k)), tgt=(68, 0.1, 0.2), fov=54, lights=OUT_L, env=ROOF_ENV, snow=False)
    if si == 1:                                                                 # втянули
        tu = wt(1, "Тимур перевалился"); ku = ease((t - tu) / 1.0)
        it = roof_world(t) + hose(-3.4)
        if ku < 1: it += climber(0, lerp(-1.6, 0.2, ku), t, timur)
        else: p, _ = timur(T(67.6, 0.3, 1.3) @ Ry(PI / 2), t, blink_seed=0.2, mouth="o"); it += p
        p, _ = max_(T(67.75, 0.3, 0.3) @ Ry(PI / 2), t, arm="push", blink_seed=0.7); it += p
        p, _ = liza(T(67.75, 0.3, -0.6) @ Ry(PI / 2), t, arm="push", blink_seed=1.3); it += p
        k = ease(t / SH.DUR[1])
        return dict(items=it, eye=(lerp(78.0, 77.0, k), lerp(-1.4, -1.0, k), lerp(5.0, 4.4, k)), tgt=(68.0, 0.7, 0.3), fov=52, lights=OUT_L, env=ROOF_ENV, snow=False)
    if si == 2:                                                                 # физрук лезет, отпустили
        tr = wt(2, "Макс разжал") + 0.3; kf = clamp((t - tr) / 0.7)
        it = roof_world(t) + horde(t)
        yz = lerp(-3.4, -1.4, ease(t / max(0.1, tr))) - 8.0 * kf * kf
        if t < tr: it += hose(-3.4)
        else: it += [cyl(T(WX + 0.45, -3.4 - 6 * kf, 0.3) @ S(0.12, 4.0, 0.12), rgb((200, 40, 36)))]
        if yz > -9: it += climber(0, yz, t, lambda r, tt, **kw: zombie(r, tt, **dict(kw, arm="up", blink_seed=99)))
        p, _ = max_(T(67.75, 0.3, 0.3) @ Ry(PI / 2), t, arm="push" if t < tr else None, blink_seed=0.7, mouth="o"); it += p
        p, _ = timur(T(67.6, 0.3, 1.3) @ Ry(PI / 2), t, blink_seed=0.2); it += p
        k = ease(t / SH.DUR[2])
        return dict(items=it, eye=(lerp(79.0, 78.2, k), lerp(-2.4, -2.0, k), lerp(5.6, 5.0, k)), tgt=(68, -0.2, 0.2), fov=56, lights=OUT_L, env=ROOF_ENV, snow=False)
    if si == 3:                                                                 # пересчёт
        it = roof_world(t)
        p, _ = liza(T(61.0, 0, 3.8) @ Ry(0.3), t, arm="point", blink_seed=1.3, look=0.6 * math.sin(t * 1.2)); it += p
        p, _ = max_(T(62.3, 0, 4.0), t, blink_seed=0.7); it += p
        p, _ = timur(T(63.5, 0, 3.8) @ Ry(-0.3), t, blink_seed=0.2); it += p
        for j in range(10):
            x = 60.4 + (j % 5) * 1.0; z = -1.0 + (j // 5) * 1.1
            p, _ = kid(j * 2 + 3, T(x - 0.6, 0, z + 0.8) @ Ry(0.3 * math.sin(j)), t, blink_seed=j * 0.3); it += p
        k = ease(t / SH.DUR[3])
        return dict(items=it, eye=(lerp(62.0, 62.2, k), 2.4, lerp(9.4, 10.0, k)), tgt=(62.0, 1.3, 2.0), fov=54, env=ROOF_ENV, snow=False)
    if si == 4:                                                                 # столовая, листок
        ts = wt(4, "И тут")
        it = roof_world(t) + horde(t) + CANTEEN
        p, _ = timur(T(66.8, 0, 2.6) @ Ry(PI / 2), t, arm="point" if t > ts else None, blink_seed=0.2); it += p
        p, _ = max_(T(66.8, 0, 3.6) @ Ry(PI / 2), t, blink_seed=0.7); it += p
        kz = ease((t - ts) / 1.4)
        eye = (lerp(63.4, 66.0, kz), lerp(2.6, 1.6, kz), lerp(-1.6, 0.6, kz)); tgt = (lerp(80, 86, kz), lerp(-3.0, -4.6, kz), lerp(0.0, 1.5, kz))
        return dict(items=it, eye=eye, tgt=tgt, fov=lerp(48, 18, kz), env=ROOF_ENV, snow=False, glows=[(SIGN_PT, (255, 255, 240), 60, 0.4 * kz)])
    it = roof_world(t) + horde(t, 12) + CANTEEN                                 # 5: двор между
    for j, (fn, z) in enumerate(((liza, -1.4), (max_, -0.4), (timur, 0.6))):
        p, _ = fn(T(67.4, 0.3, z) @ Ry(PI / 2), t, blink_seed=j * 0.6, look=0.2 * math.sin(t + j)); it += p
    k = ease(t / SH.DUR[5])
    return dict(items=it, eye=(lerp(83.0, 84.0, k), lerp(2.6, 3.0, k), lerp(10.0, 10.6, k)), tgt=(70.0, -2.0, -0.2), fov=52, env=ROOF_ENV, snow=False)

def panel(d, x0, y0, x1, y1, k=1.0): d.rounded_rectangle([x0, y0, x1, y1], radius=28, fill=PANEL + (int(215 * k),))







def clock(sh, si, t):
    gt = sh.STARTS[si] + t; return f"12:{min(19, 14 + int(6 * gt / sh.TOTAL)):02d}"

def overlay(sh, si, t, d):
    wt = sh.wt
    stroke_text(d, (W / 2, 250), "ПОСЛЕДНИЙ УРОК", font(60), WHITE, 6)
    stroke_text(d, (W / 2, 350), clock(sh, si, t), font(122), RED, 9)
    def tiles(tq, a, b, y=1340):
        for j, (x, lab, c, dl) in enumerate(((290, a, GREEN, 0.0), (790, b, RED, 0.3))):
            k = ease((t - tq - dl) / 0.25)
            if k <= 0: continue
            A = int(255 * k); yy = y + 30 * (1 - k)
            d.rounded_rectangle([x - 225, yy, x + 225, yy + 170], radius=36, fill=PANEL + (int(230 * k),), outline=c + (A,), width=6)
            d.text((x, yy + 85), lab, font=font(52), fill=c + (A,), anchor="mm")
    if si == 0:
        panel(d, 640, 450, 1020, 690)
        d.text((680, 500), "ДО КРЫШИ", font=font(36), fill=(190, 196, 214), anchor="lm"); d.text((680, 600), "1,8 М", font=font(90), fill=YEL, anchor="lm")
        tiles(wt(0, "Успеешь") - 0.05, "УСПЕЕТ?", "НЕТ?")
    if si == 1:
        tu = wt(1, "Успел")
        if t > tu: k = ease((t - tu) / 0.15); stroke_text(d, (W / 2, 1560), "УСПЕЛ!", font(120), GREEN + (int(255 * k),), 10)
    if si == 2:
        tr = wt(2, "Макс разжал") + 0.3
        if t > tr: k = ease((t - tr) / 0.15); stroke_text(d, (W / 2, 900), "ОТПУСТИЛ!", font(110), YEL + (int(255 * k),), 10)
    if si == 3:
        t13 = wt(3, "Тринадцать"); t11 = wt(3, "А где")
        n = 1 + int(round(12 * ease((t - 0.2) / max(0.1, t13 - 0.2))))
        panel(d, 60, 450, 560, 710)
        d.text((100, 500), "НА КРЫШЕ", font=font(36), fill=(190, 196, 214), anchor="lm"); d.text((100, 590), f"{n}/24", font=font(90), fill=WHITE, anchor="lm")
        if t > t11: d.text((100, 670), "НЕТ 11", font=font(54), fill=RED, anchor="lm")
    if si == 4:
        ts = wt(4, "И тут"); tc = wt(4, "Они убежали")
        if t > tc and t < ts:
            k = ease((t - tc) / 0.25); A = int(255 * k); panel(d, 60, 450, 560, 600, k)
            d.text((100, 490), "ОСТАЛЬНЫЕ 11", font=font(34), fill=(190, 196, 214, A), anchor="lm"); d.text((100, 555), "В СТОЛОВОЙ", font=font(54), fill=YEL + (A,), anchor="lm")
        tl = wt(4, "листок") + 0.2
        if t > tl:
            k = ease((t - tl) / 0.3); A = int(255 * k); y0 = 460 + 40 * (1 - k)
            d.rounded_rectangle([200, y0, 880, y0 + 360], radius=10, fill=(250, 250, 244, A), outline=(180, 180, 170, A), width=4)
            d.text((W / 2, y0 + 120), "МЫ ЖИВЫ", font=font(96), fill=(30, 30, 40, A), anchor="mm")
            d.text((W / 2, y0 + 260), "11", font=font(130), fill=(200, 40, 36, A), anchor="mm")
    if si == 5:
        panel(d, 560, 450, 1020, 600)
        d.text((600, 490), "ВО ДВОРЕ", font=font(34), fill=(190, 196, 214), anchor="lm"); d.text((600, 555), "12 ЗОМБИ", font=font(56), fill=RED, anchor="lm")
        sh.cta(d, t, wt(5, "Пиши") - 0.1, "ИДТИ", "ЖДАТЬ")
        te = sh.DUR[5] - 1.7
        if t > te: stroke_text(d, (W / 2, 1650), "СЕРИЯ 6 — СКОРО", font(50), WHITE + (int(255 * ease((t - te) / 0.3)),), 6)

def sound(sh, add, SR, n, tt):
    wt = sh.wt; ST = sh.STARTS; TOTAL = sh.TOTAL; rnd = np.random.default_rng(34)
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
    calm = ((tt > ST[1] + wt(1, "Успел")) & (tt < ST[2])).astype(float)
    music = (0.09 * wind2 + 0.1 * drone + 0.24 * beat * (1 - 0.8 * calm)) * env
    def groan(at, dur=1.6, amp=0.2):
        t_ = T_(dur); g = noise(dur, 90, 420) * (0.5 + 0.5 * np.sin(2 * np.pi * 2.3 * t_)) * np.clip(t_ / 0.3, 0, 1) * np.clip((dur - t_) / 0.4, 0, 1); add(amp * g, at)
    groan(0.2, sh.DUR[0], 0.25)
    for dl, f in ((0.0, 200), (0.3, 150)): add(0.45 * thud(f, 0.35, 12), wt(0, "Успеешь") - 0.05 + dl)
    for j in range(6): add(0.12 * noise(0.1, 300, 2000) * np.exp(-T_(0.1) * 25), ST[1] + 0.3 + j * 0.4)
    add(0.6 * thud(70, 0.5, 8), ST[1] + wt(1, "перевалился") + 0.8)
    for f in (523, 659, 784): add(0.07 * np.sin(2 * np.pi * f * T_(1.4)) * np.exp(-T_(1.4) * 2), ST[1] + wt(1, "Успел"))
    groan(ST[2] + 0.2, 2.6, 0.3)
    tr = ST[2] + wt(2, "Макс разжал") + 0.3
    t_ = T_(0.7); add(0.3 * noise(0.7, 400, 3000) * np.clip(t_ / 0.6, 0, 1), tr); add(0.9 * thud(40, 1.2, 3.2), tr + 0.7)
    for j in range(13): add(0.12 * tick(700 + 40 * j), ST[3] + 0.2 + j * (wt(3, "Тринадцать") - 0.2) / 13)
    add(0.5 * buzz(), ST[3] + wt(3, "А где"))
    add(0.4 * noise(0.5, 400, 4000) * np.sin(np.pi * T_(0.5) / 0.5) ** 2, ST[4] + wt(4, "И тут"))
    add(0.8 * thud(44, 1.1, 3.5), ST[4] + wt(4, "листок") + 0.2)
    for f in (392, 494, 587): add(0.06 * np.sin(2 * np.pi * f * T_(1.8)) * np.exp(-T_(1.8) * 1.8), ST[4] + wt(4, "листок") + 0.3)
    groan(ST[5] + 0.2, sh.DUR[5] - 0.6, 0.18)
    for f in (392, 466, 587): add(0.07 * np.sin(2 * np.pi * f * T_(1.6)) * np.exp(-T_(1.6) * 2.2), ST[5] + wt(5, "Пиши") - 0.1)
    add(0.2 * tick(1320), ST[5] + wt(5, "Пиши") - 0.1)
    return music

import render as _me
SH = Show(_me) if __name__ != "__main__" else None
if __name__ == "__main__":
    import render as ep
    SH = ep.SH; ep.SH.run("shkola-5")
