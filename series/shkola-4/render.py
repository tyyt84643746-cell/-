"""«Последний урок», серия 4 «Шланг» (3D). Запуск: LIBGL_ALWAYS_SOFTWARE=1 xvfb-run -a python3 render.py [preview | sheet N K | at N T]"""
import math, os, random, sys
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(D, "..", "engine3d")); sys.path.insert(0, D)
import numpy as np
from school import *
from show import *
from script import SCENES, CAPTION_NUMS

LEADS = [0.3] * 6
TAILS = [0.6, 0.6, 0.6, 0.8, 1.2, 3.0]
KEY = {"крыше", "безопасности", "класс", "вернёшься", "спасёшь", "шланг", "крепкий", "окну", "тимур", "лиза", "ещё", "12", "треснула", "последним", "физрук", "успеет", "подняться", "комментариях"}
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
ROOM = classroom()
BARR = desks_all(skip=((3.4, -3.6), (3.4, -1.2), (0.0, -3.6))) + desk(5.1, DOOR_Z - 0.2, PI / 2) + desk(5.1, DOOR_Z + 0.05, PI / 2)

def scene_3d(si, t):
    wt = SH.wt
    if si == 0:                                                                 # на крыше
        it = roof_world(t) + horde(t)
        p, _ = max_(T(67.75, 0.3, 0.4) @ Ry(PI / 2 - 0.2), t, blink_seed=0.7, look=0.3 * math.sin(t * 0.7)); it += p
        k = ease(t / SH.DUR[0])
        return dict(items=it, eye=(lerp(81.0, 80.0, k), lerp(-4.0, -3.6, k), lerp(5.0, 4.4, k)), tgt=(68, lerp(-0.4, 0.3, k), 0.3), fov=52, env=ROOF_ENV, snow=False)
    if si == 1:                                                                 # шланг вниз
        tt_ = wt(1, "И сбросил"); ye = lerp(0.9, -3.4, ease((t - tt_) / 0.9)) if t > tt_ else 0.9
        it = roof_world(t) + horde(t) + (hose(ye) if t > tt_ else [])
        p, _ = max_(T(67.0, 0, 0.0) @ Ry(PI / 2), t, arm="hold" if t < tt_ else None, blink_seed=0.7); it += p
        if t < tt_: it.append(cyl(T(66.0, 0.5, 0.6) @ Rx(PI / 2) @ S(0.9, 0.3, 0.9), rgb((200, 40, 36))))
        k = ease(t / SH.DUR[1])
        return dict(items=it, eye=(lerp(78, 77, k), lerp(-2.0, -2.6, k), lerp(7.0, 6.0, k)), tgt=(68, lerp(1.2, -0.4, ease((t - tt_) / 1.2)), 0), fov=54, lights=OUT_L, env=ROOF_ENV, snow=False)
    if si == 2:                                                                 # лезут
        it = roof_world(t) + horde(t) + hose(-3.4)
        p, _ = timur(T(WX - 0.5, -4.0, -0.6) @ Ry(PI / 2), t, arm="hold", blink_seed=0.2); it += p
        tl = wt(2, "Первой")
        for j in range(4):
            y = -3.6 + 3.6 * clamp((t - tl - j * 1.0) / 1.5)
            if t > tl + j * 1.0 and y < 0: it += climber(j * 5 + 1, y, t, liza if j == 0 else None)
        p, _ = max_(T(67.2, 0, 1.0) @ Ry(PI / 2), t, arm="push", blink_seed=0.7); it += p
        k = ease(t / SH.DUR[2])
        return dict(items=it, eye=(lerp(77.5, 76.5, k), lerp(-2.6, -1.8, k), lerp(6.0, 5.4, k)), tgt=(68, 0.0, 0.2), fov=54, lights=OUT_L, env=ROOF_ENV, snow=False)
    if si == 3:
        td = wt(3, "И тут") - 0.1
        if t < td:                                                              # 12 на крыше
            it = roof_world(t) + hose(-3.4)
            p, _ = max_(T(65.6, 0, 1.2) @ Ry(-PI / 2 + 0.4), t, blink_seed=0.7); it += p
            p, _ = liza(T(64.6, 0, 2.2) @ Ry(-PI / 2), t, blink_seed=1.3); it += p
            for j in range(10):
                x = 61 + (j % 5) * 0.9; z = -1.4 + (j // 5) * 1.2 + 0.3 * math.sin(j)
                p, _ = kid(j * 2 + 3, T(x, 0, z) @ Ry(PI / 2 + 0.3 * math.sin(j)), t, blink_seed=j * 0.3); it += p
            k = ease(t / td)
            return dict(items=it, eye=(lerp(66.6, 66.9, k), 2.6, lerp(-4.4, -4.8, k)), tgt=(62.6, 1.0, 0.6), fov=54, env=ROOF_ENV, snow=False)
        tt_ = t - td; sh_ = 0.08 * math.sin(t * 45)                             # дверь класса трещит
        it = ROOM + BARR + door(0.12 + 0.05 * math.sin(t * 13), sh_)
        it.append(box(T(6.05, 1.6, DOOR_Z) @ Rz(0.5) @ S(0.03, 1.2, 0.03), C["dark"], cast=False)); it.append(box(T(6.05, 1.1, DOOR_Z + 0.2) @ Rz(-0.4) @ S(0.03, 0.8, 0.03), C["dark"], cast=False))
        return dict(items=it, eye=(lerp(3.2, 3.6, ease(tt_ / 1.5)), 1.9, lerp(-3.4, -3.8, ease(tt_ / 1.5))), tgt=(6.0, 1.4, DOOR_Z), fov=50, lights=LIGHTS_IN, snow=False)
    if si == 4:                                                                 # Тимур и физрук
        tf = wt(4, "А в класс")
        it = ROOM + desks_all(skip=((3.4, -3.6), (3.4, -1.2), (0.0, -3.6))) + door(1.4 if t > tf else 0.2)
        it.append(cyl(T(-6.3, 1.8, -0.6) @ S(0.12, 6.0, 0.12), rgb((200, 40, 36))))
        p, _ = timur(T(-5.2, 0, -0.6) @ Ry(-PI / 2 + 0.6), t, arm="hold", blink_seed=0.2, mouth="o" if t > tf else None, look=1.0 * ease((t - tf - 0.3) / 0.6)); it += p
        if t > tf - 0.3:
            ka = clamp((t - tf + 0.3) / 3.0)
            p, _ = zombie(T(lerp(6.8, 2.8, ka), 0, lerp(DOOR_Z, -3.8, ka)) @ Ry(-PI / 2 - 0.3), t, walk=t * 3.2, blink_seed=99); it += p
        k = ease(t / SH.DUR[4])
        return dict(items=it, eye=(lerp(-3.4, -3.0, k), 2.4, lerp(1.8, 1.2, k)), tgt=(lerp(-5.2, 2.0, ease((t - tf) / 1.2)), 1.5, lerp(-0.6, -3.6, ease((t - tf) / 1.2))), fov=56, lights=LIGHTS_IN, snow=False)
    it = roof_world(t) + horde(t) + hose(-3.4)                                  # 5: Тимур лезет
    y = -3.6 + 1.8 * ease(t / SH.DUR[5])
    it += climber(0, y, t, timur)
    p, _ = max_(T(67.4, 0, 0.3) @ Ry(PI / 2) @ Rx(0.0), t, arm="push", blink_seed=0.7, mouth="o"); it += p
    p, _ = zombie(T(WX - 2.2 + 0.25 * t, -4.0, 0.2) @ Ry(PI / 2), t, blink_seed=99); it += p
    k = ease(t / SH.DUR[5])
    return dict(items=it, eye=(lerp(79.0, 78.2, k), lerp(-1.6, -1.2, k), lerp(5.6, 5.0, k)), tgt=(68, -0.5, 0.2), fov=54, lights=OUT_L, env=ROOF_ENV, snow=False)

def panel(d, x0, y0, x1, y1, k=1.0): d.rounded_rectangle([x0, y0, x1, y1], radius=28, fill=PANEL + (int(215 * k),))






def clock(sh, si, t):
    gt = sh.STARTS[si] + t; return f"12:{min(14, 9 + int(6 * gt / sh.TOTAL)):02d}"

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
            d.text((x, yy + 85), lab, font=font(50), fill=c + (A,), anchor="mm")
    if si == 0: tiles(wt(0, "Вернёшься") - 0.05, "ВЕРНУТЬСЯ?", "СПАСТИСЬ?")
    if si in (2, 3):
        if si == 2:
            tl = wt(2, "Первой"); n = 1 + sum(1 for j in range(4) if t > tl + j * 1.0 + 1.5)
        else: n = 12
        if si == 3 and t > wt(3, "И тут") - 0.1:
            k = ease((t - wt(3, "И тут") + 0.1) / 0.15); stroke_text(d, (W / 2, 900 + 6 * math.sin(t * 40)), "ТРЕСК!", font(120), RED + (int(255 * k),), 10)
        else:
            x0 = 680 if si == 2 else 60
            panel(d, x0, 450, x0 + 340, 690)
            d.text((x0 + 40, 500), "НА КРЫШЕ", font=font(36), fill=(190, 196, 214), anchor="lm"); d.text((x0 + 40, 600), f"{n}", font=font(110), fill=GREEN if n == 12 else WHITE, anchor="lm")
    if si == 4:
        k = ease((t - 0.1) / 0.25); A = int(255 * k); panel(d, 60, 450, 560, 600, k)
        d.text((100, 490), "В КЛАССЕ", font=font(34), fill=(190, 196, 214, A), anchor="lm"); d.text((100, 555), "ТИМУР ОДИН", font=font(52), fill=YEL + (A,), anchor="lm")
        tf = wt(4, "А в класс")
        if t > tf: k = ease((t - tf) / 0.15); stroke_text(d, (W / 2, 1560 + 6 * math.sin(t * 30)), "ФИЗРУК!", font(110), RED + (int(255 * k),), 10)
    if si == 5:
        y = -3.6 + 1.8 * ease(t / sh.DUR[5]); m = max(0.0, -y)
        panel(d, 640, 450, 1020, 690)
        d.text((680, 500), "ДО КРЫШИ", font=font(36), fill=(190, 196, 214), anchor="lm"); d.text((680, 600), f"{m:.1f} М".replace(".", ","), font=font(90), fill=YEL, anchor="lm")
        sh.cta(d, t, wt(5, "Пиши") - 0.1, "УСПЕЕТ", "НЕ УСПЕЕТ")
        te = sh.DUR[5] - 1.7
        if t > te: stroke_text(d, (W / 2, 1650), "СЕРИЯ 5 — СКОРО", font(50), WHITE + (int(255 * ease((t - te) / 0.3)),), 6)

def sound(sh, add, SR, n, tt):
    wt = sh.wt; ST = sh.STARTS; TOTAL = sh.TOTAL; rnd = np.random.default_rng(33)
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
    room = ((tt > ST[3] + wt(3, "И тут") - 0.1) & (tt < ST[5])).astype(float)
    wind2 = noise(TOTAL, 200, 1200)[:n]; wind2 = np.pad(wind2, (0, n - len(wind2))) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.2 * tt))
    music = (0.09 * wind2 * (1 - room) + 0.1 * drone + 0.24 * beat * (1 + 0.4 * (tt > ST[4]))) * env
    def groan(at, dur=1.6, amp=0.2):
        t_ = T_(dur); g = noise(dur, 90, 420) * (0.5 + 0.5 * np.sin(2 * np.pi * 2.3 * t_)) * np.clip(t_ / 0.3, 0, 1) * np.clip((dur - t_) / 0.4, 0, 1); add(amp * g, at)
    groan(0.5, 3.0, 0.14)
    for dl, f in ((0.0, 200), (0.3, 150)): add(0.45 * thud(f, 0.35, 12), wt(0, "Вернёшься") - 0.05 + dl)
    add(0.4 * noise(0.9, 200, 1500) * np.exp(-T_(0.9) * 3), ST[1] + wt(1, "И сбросил")); add(0.5 * thud(80, 0.4, 10), ST[1] + wt(1, "И сбросил") + 0.9)
    tl = ST[2] + wt(2, "Первой")
    for j in range(4):
        for q in range(5): add(0.1 * noise(0.08, 400, 2500) * np.exp(-T_(0.08) * 30), tl + j * 1.0 + q * 0.3)
        add(0.2 * tick(880 + 110 * j), tl + j * 1.0 + 1.5)
    groan(ST[2] + 0.5, 3.5, 0.18)
    add(0.22 * tick(1320), ST[3] + wt(3, "двенадцать"))
    tc = ST[3] + wt(3, "И тут") - 0.1
    add(0.9 * thud(40, 1.2, 3.2), tc); add(0.6 * noise(0.5, 200, 4000) * np.exp(-T_(0.5) * 6), tc)
    for j in range(6): add(0.4 * thud(85, 0.25, 14), tc + 0.4 + j * 0.35)
    tf = ST[4] + wt(4, "А в класс")
    add(0.5 * noise(0.4, 200, 3000) * np.exp(-T_(0.4) * 6), tf); add(0.9 * thud(40, 1.3, 3.0), tf); groan(tf + 0.2, 3.0, 0.3)
    for j in range(int(sh.DUR[5] / 0.35)): add(0.08 * noise(0.08, 400, 2500) * np.exp(-T_(0.08) * 30), ST[5] + j * 0.35)
    groan(ST[5] + 0.2, sh.DUR[5] - 0.6, 0.2)
    for f in (392, 466, 587): add(0.07 * np.sin(2 * np.pi * f * T_(1.6)) * np.exp(-T_(1.6) * 2.2), ST[5] + wt(5, "Пиши") - 0.1)
    add(0.2 * tick(1320), ST[5] + wt(5, "Пиши") - 0.1)
    return music

import render as _me
SH = Show(_me) if __name__ != "__main__" else None
if __name__ == "__main__":
    import render as ep
    SH = ep.SH; ep.SH.run("shkola-4")
