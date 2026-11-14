"""«Последний урок», серия 2 «Карниз» (3D). Запуск: LIBGL_ALWAYS_SOFTWARE=1 xvfb-run -a python3 render.py [preview | sheet N K | at N T]"""
import math, os, random, sys
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(D, "..", "engine3d")); sys.path.insert(0, D)
import numpy as np
from school import *
from show import *
from script import SCENES, CAPTION_NUMS

LEADS = [0.3] * 6
TAILS = [0.6, 0.6, 0.8, 0.9, 1.2, 3.0]
KEY = {"зомби", "крышу", "20", "заперт", "рискнёшь", "лиза", "ключ", "завхоза", "лестницы", "тимур", "окно", "карнизу", "второй", "асфальт", "первым", "шаг", "охранник", "голову", "гвозде", "завхоз", "спиной", "успеет", "комментариях"}
PI = math.pi
ENV = dict(sun_dir=(0.65, -0.55, 0.25), sun_col=(1.1, 0.95, 0.75), amb_top=(0.34, 0.36, 0.42), amb_bot=(0.2, 0.19, 0.18), fog=0.006, fog_col=(0.6, 0.66, 0.78),
           sky=((0.32, 0.5, 0.82), (0.66, 0.76, 0.9), (0.7, 0.74, 0.8)), hz=0.45, shadow_center=(-2, 0, -1), shadow_size=12)
CORR = dict(ENV, sun_col=(0, 0, 0), amb_top=(0.2, 0.2, 0.2), amb_bot=(0.1, 0.1, 0.1), fog=0.03, fog_col=(0.1, 0.1, 0.1), shadow_center=(8, 0, -14), shadow_size=18)
ROOM = classroom() + yard() + facade()
BARR = desks_all(skip=((3.4, -3.6), (3.4, -1.2), (0.0, -3.6))) + desk(5.1, DOOR_Z - 0.2, PI / 2) + desk(5.1, DOOR_Z + 0.05, PI / 2)
STORE = storeroom()
OUT = dict(ENV, shadow_center=(-8, -2, -6), shadow_size=16)
ST_ENV = dict(ENV, sun_col=(0, 0, 0), amb_top=(0.16, 0.15, 0.13), amb_bot=(0.08, 0.07, 0.06), fog=0.0, sky=((0.02, 0.02, 0.02),) * 3, shadow_center=(32, 0, 0), shadow_size=6)

def scene_3d(si, t):
    wt = SH.wt
    if si == 0:                                                                 # дверь трясётся, план
        it = ROOM + BARR + door(0.0, 0.04 * math.sin(t * 38))
        p, _ = max_(T(2.4, 0, -2.8) @ Ry(PI / 2 + 0.4), t, blink_seed=0.7, mouth="o", look=-0.3 * math.sin(t * 0.8)); it += p
        for j, (x, z) in enumerate(((2.6, -1.0), (1.4, -4.6), (-0.4, -3.4))):
            p, _ = kid(j * 4 + 2, T(x, 0, z) @ Ry(PI / 2 - 0.2), t, blink_seed=j * 0.4, mouth="o"); it += p
        k = ease(t / SH.DUR[0])
        return dict(items=it, eye=(lerp(-1.2, -0.6, k), 2.5, lerp(0.8, 0.2, k)), tgt=(5.2, 1.4, -5.0), fov=52, lights=LIGHTS_IN, snow=False)
    if si == 1:                                                                 # Лиза
        it = ROOM + BARR + door(0.0, 0.03 * math.sin(t * 38))
        p, _ = liza(T(0.0, 0, -2.0) @ Ry(0.35), t, blink_seed=1.3, mouth="o" if int(t * 5) % 2 else None); it += p
        p, _ = max_(T(1.5, 0, -2.4) @ Ry(-0.6), t, blink_seed=0.7); it += p
        k = ease(t / SH.DUR[1])
        return dict(items=it, eye=(lerp(0.9, 0.7, k), 2.0, lerp(2.4, 1.6, k)), tgt=(0.6, 1.8, -2.2), fov=44, lights=LIGHTS_IN, snow=False)
    if si == 2:                                                                 # окно и карниз снаружи
        it = ROOM + BARR
        p, _ = timur(T(-5.5, 0, -0.6) @ Ry(-PI / 2), t, arm="point", blink_seed=0.2); it += p
        p, _ = zombie(T(-11.5, -4, 3.5 - 0.3 * t) @ Ry(PI), t, colors=GUARD, walk=t * 3.0); it += p
        k = ease(t / SH.DUR[2])
        return dict(items=it, eye=(lerp(-19.0, -17.5, k), lerp(-1.4, -0.8, k), lerp(5.0, 4.0, k)), tgt=(-6.4, 1.0, lerp(-2.0, -3.4, k)), fov=46, lights=LIGHTS_IN, env=OUT, snow=False)
    if si == 3:                                                                 # по карнизу
        ts = wt(3, "Шаг"); zm = -0.6 - 0.7 * clamp((t - ts) / 0.6) - 0.7 * clamp((t - wt(3, "Ещё шаг")) / 0.6) - 0.5 * clamp((t - wt(3, "А внизу")) / 1.4)
        it = ROOM + BARR
        p, _ = max_(T(-6.55, 0.91, zm) @ Ry(PI / 2), t, blink_seed=0.7, look=-0.6 if t > wt(3, "А внизу") else 0.2 * math.sin(t)); it += p
        p, _ = timur(T(-5.5, 0, -0.6) @ Ry(-PI / 2 - 0.4), t, blink_seed=0.2); it += p
        tu = wt(3, "поднял") - 0.2
        gr = Ry(PI) if t < tu else Ry(lerp(PI, PI / 2, ease((t - tu) / 0.8)))
        p, _ = zombie(T(-9.4, -4, -3.4) @ gr, t, colors=GUARD, walk=t * 3.0 if t < tu else None); it += p
        k = ease(t / SH.DUR[3])
        return dict(items=it, eye=(lerp(-11.2, -11.6, k), lerp(0.6, 0.2, k), lerp(-9.0, -10.0, k)), tgt=(lerp(-7.2, -8.0, ease((t - tu) / 1.2)), lerp(1.4, -1.4, ease((t - tu) / 1.2)), lerp(-1.8, -2.6, k)), fov=52, lights=LIGHTS_IN, env=OUT, snow=False)
    if si == 4:                                                                 # каморка
        it = STORE + key(0.7 + 0.3 * math.sin(t * 4))
        p, _ = janitor(T(31.6, -0.9, -0.6) @ Ry(PI + 0.2), t, blink_seed=5.0); it += p
        zm = lerp(2.4, 1.2, ease(t / 2.0))
        p, _ = max_(T(32.5, 0, zm) @ Ry(PI), t, walk=t * 4 if t < 2.0 else None, blink_seed=0.7); it += p
        k = ease(t / SH.DUR[4])
        return dict(items=it, eye=(lerp(30.6, 30.9, k), 2.7, lerp(3.4, 2.8, k)), tgt=(32.8, 0.8, -1.0), fov=58, lights=[((32, 2.6, 0), (1.6, 1.4, 1.0), 6.0)], env=ST_ENV, snow=False,
                    glows=[(KEY_PT, (255, 220, 120), 40, 0.6)])
    it = STORE + key(0.7 + 0.3 * math.sin(t * 4))                               # 5: тянется к ключу
    lk = 0.6 * ease((t - SH.DUR[5] + 2.6) / 1.4)
    p, _ = janitor(T(31.6, -0.9, -0.6) @ Ry(PI + 0.2), t, blink_seed=5.0, look=lk); it += p
    p, _ = max_(T(33.3, 0, -0.9) @ Ry(PI + 0.25), t, arm="point", blink_seed=0.7, look=0.4); it += p
    k = ease(t / SH.DUR[5])
    return dict(items=it, eye=(lerp(30.6, 30.8, k), 2.7, lerp(2.6, 2.2, k)), tgt=(32.6, 1.1, -1.4), fov=54, lights=[((32, 2.6, 0), (1.6, 1.4, 1.0), 6.0)], env=ST_ENV, snow=False,
                glows=[(KEY_PT, (255, 220, 120), 60, 0.8)])

def panel(d, x0, y0, x1, y1, k=1.0): d.rounded_rectangle([x0, y0, x1, y1], radius=28, fill=PANEL + (int(215 * k),))




def clock(sh, si, t):
    gt = sh.STARTS[si] + t; return f"12:0{min(5, 1 + int(5 * gt / sh.TOTAL))}"

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
            d.text((x, yy + 85), lab, font=font(54), fill=c + (A,), anchor="mm")
    if si == 0:
        t20 = wt(0, "До выхода"); tz = wt(0, "Но люк")
        if t > t20:
            k = ease((t - t20) / 0.25); A = int(255 * k); panel(d, 60, 450, 560, 700, k)
            d.text((100, 500), "ДО КРЫШИ", font=font(36), fill=(190, 196, 214, A), anchor="lm"); d.text((100, 575), "20 М", font=font(80), fill=WHITE + (A,), anchor="lm")
            if t > tz: d.text((100, 655), "ЛЮК: ЗАПЕРТ", font=font(48), fill=RED, anchor="lm")
        tiles(wt(0, "Рискнёшь") - 0.05, "РИСКНУТЬ?", "ЖДАТЬ?")
    if si == 1:
        k = ease((t - 0.1) / 0.25); A = int(255 * k); panel(d, 60, 450, 560, 600, k)
        d.text((100, 490), "НОВЕНЬКАЯ", font=font(34), fill=(190, 196, 214, A), anchor="lm"); d.text((100, 555), "ЛИЗА", font=font(60), fill=YEL + (A,), anchor="lm")
        tk = wt(1, "Ключ")
        if t > tk:
            k = ease((t - tk) / 0.25); A = int(255 * k); panel(d, 60, 620, 700, 770, k)
            d.text((100, 660), "КЛЮЧ ОТ КРЫШИ", font=font(34), fill=(190, 196, 214, A), anchor="lm"); d.text((100, 725), "У ЗАВХОЗА", font=font(56), fill=GREEN + (A,), anchor="lm")
    if si == 2:
        t2 = wt(2, "Второй")
        if t > t2:
            k = ease((t - t2) / 0.25); A = int(255 * k); panel(d, 60, 450, 560, 690, k)
            d.text((100, 500), "ВЫСОТА", font=font(36), fill=(190, 196, 214, A), anchor="lm"); d.text((100, 600), "2 ЭТАЖ", font=font(80), fill=RED + (A,), anchor="lm")
    if si == 3:
        ts = wt(3, "Шаг"); m = int(round(12 - 2 * clamp((t - ts) / 0.6) - 2 * clamp((t - wt(3, "Ещё шаг")) / 0.6) - 1.5 * clamp((t - wt(3, "А внизу")) / 1.4)))
        panel(d, 480, 450, 1020, 690)
        d.text((520, 500), "ДО ЛЕСТНИЦЫ", font=font(36), fill=(190, 196, 214), anchor="lm"); d.text((520, 600), f"{m} М", font=font(100), fill=YEL, anchor="lm")
        tu = wt(3, "поднял")
        if t > tu: k = ease((t - tu) / 0.15); stroke_text(d, (W / 2, 900 + 6 * math.sin(t * 30)), "ОН ВИДИТ!", font(100), RED + (int(255 * k),), 9)
    if si == 4:
        tk = wt(4, "ключ")
        if t > tk:
            k = ease((t - tk) / 0.25); A = int(255 * k); panel(d, 60, 450, 520, 600, k)
            d.text((100, 490), "КЛЮЧ", font=font(34), fill=(190, 196, 214, A), anchor="lm"); d.text((100, 555), "НАЙДЕН", font=font(56), fill=GREEN + (A,), anchor="lm")
        tz = wt(4, "завхоз")
        if t > tz:
            k = ease((t - tz) / 0.25); A = int(255 * k); panel(d, 60, 620, 640, 770, k)
            d.text((100, 660), "ЗАВХОЗ", font=font(34), fill=(190, 196, 214, A), anchor="lm"); d.text((100, 725), "ЖИВОЙ?", font=font(56), fill=RED + (A,), anchor="lm")
    if si == 5:
        sh.cta(d, t, wt(5, "Пиши") - 0.1, "УСПЕЕТ", "НЕ УСПЕЕТ")
        te = sh.DUR[5] - 1.7
        if t > te: stroke_text(d, (W / 2, 1650), "СЕРИЯ 3 — СКОРО", font(50), WHITE + (int(255 * ease((t - te) / 0.3)),), 6)

def sound(sh, add, SR, n, tt):
    wt = sh.wt; ST = sh.STARTS; TOTAL = sh.TOTAL; rnd = np.random.default_rng(31)
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
    outside = ((tt > ST[2]) & (tt < ST[4])).astype(float); inside_st = (tt > ST[4]).astype(float)
    wind2 = noise(TOTAL, 200, 1200)[:n]; wind2 = np.pad(wind2, (0, n - len(wind2))) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.2 * tt))
    music = (0.09 * wind2 * outside + 0.1 * drone * (1 - 0.5 * inside_st) + 0.24 * beat * (1 - 0.7 * inside_st)) * env
    def groan(at, dur=1.6, amp=0.2):
        t_ = T_(dur); g = noise(dur, 90, 420) * (0.5 + 0.5 * np.sin(2 * np.pi * 2.3 * t_)) * np.clip(t_ / 0.3, 0, 1) * np.clip((dur - t_) / 0.4, 0, 1); add(amp * g, at)
    for j in range(int(sh.DUR[0] / 0.45)): add(0.35 * thud(85 + 10 * (j % 3), 0.25, 14), 0.1 + j * 0.45)                      # удары в дверь
    for j in range(int(sh.DUR[1] / 0.7)): add(0.18 * thud(85, 0.25, 14), ST[1] + j * 0.7)
    groan(0.3, 2.0, 0.22); groan(ST[1] + 0.5, 2.0, 0.12)
    add(0.22 * tick(1100), wt(0, "До выхода")); add(0.4 * buzz(), wt(0, "Но люк") + 0.2)
    for dl, f in ((0.0, 200), (0.3, 150)): add(0.45 * thud(f, 0.35, 12), wt(0, "Рискнёшь") - 0.05 + dl)
    add(0.22 * tick(1320), ST[1] + wt(1, "Ключ"))
    add(0.3 * noise(0.6, 300, 2500) * np.exp(-T_(0.6) * 5), ST[2] + wt(2, "открыл"))                                           # скрип окна
    add(0.5 * thud(50, 0.8, 5), ST[2] + wt(2, "Второй")); add(0.5 * thud(46, 0.8, 5), ST[2] + wt(2, "асфальт"))
    for sub in ("Шаг", "Ещё шаг"): add(0.18 * noise(0.12, 300, 2000) * np.exp(-T_(0.12) * 20), ST[3] + wt(3, sub) + 0.3)
    add(0.9 * thud(40, 1.2, 3.2), ST[3] + wt(3, "поднял")); groan(ST[3] + wt(3, "поднял") + 0.2, 2.2, 0.3)
    add(0.3 * noise(0.5, 300, 2000) * np.exp(-T_(0.5) * 5), ST[4] + 0.1)                                                        # дверь каморки
    t_ = T_(0.6); add(0.12 * np.sin(2 * np.pi * 2600 * t_) * np.exp(-t_ * 6), ST[4] + wt(4, "ключ"))                             # блеск ключа
    add(0.6 * thud(46, 0.9, 5), ST[4] + wt(4, "завхоз"))
    groan(ST[5] + sh.DUR[5] - 2.6, 1.8, 0.25)
    for f in (392, 466, 587): add(0.07 * np.sin(2 * np.pi * f * T_(1.6)) * np.exp(-T_(1.6) * 2.2), ST[5] + wt(5, "Пиши") - 0.1)
    add(0.2 * tick(1320), ST[5] + wt(5, "Пиши") - 0.1)
    return music

import render as _me
SH = Show(_me) if __name__ != "__main__" else None
if __name__ == "__main__":
    import render as ep
    SH = ep.SH; ep.SH.run("shkola-2")
