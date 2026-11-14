"""«Последний урок», серия 1 «Звонок» (3D). Запуск: LIBGL_ALWAYS_SOFTWARE=1 xvfb-run -a python3 render.py [preview | sheet N K | at N T]"""
import math, os, random, sys
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(D, "..", "engine3d")); sys.path.insert(0, D)
import numpy as np
from school import *
from show import *
from script import SCENES, CAPTION_NUMS

LEADS = [0.3] * 6
TAILS = [0.6, 0.6, 0.8, 0.8, 1.3, 3.0]
KEY = {"уроке", "5", "кричит", "откроешь", "окно", "охранник", "странно", "видел", "физрук", "серое", "пустые", "повернулся", "захлопнул", "парты", "24", "одна", "дверь", "связи", "звонок", "все", "выбраться", "комментариях"}
PI = math.pi
ENV = dict(sun_dir=(0.65, -0.55, 0.25), sun_col=(1.1, 0.95, 0.75), amb_top=(0.34, 0.36, 0.42), amb_bot=(0.2, 0.19, 0.18), fog=0.006, fog_col=(0.6, 0.66, 0.78),
           sky=((0.32, 0.5, 0.82), (0.66, 0.76, 0.9), (0.7, 0.74, 0.8)), hz=0.45, shadow_center=(-2, 0, -1), shadow_size=12)
CORR = dict(ENV, sun_col=(0, 0, 0), amb_top=(0.2, 0.2, 0.2), amb_bot=(0.1, 0.1, 0.1), fog=0.03, fog_col=(0.1, 0.1, 0.1), shadow_center=(8, 0, -14), shadow_size=18)
ROOM = classroom() + yard()
STUDENTS_UP = [(4.6, -4.2, 3), (3.6, -4.8, 7), (4.4, -3.2, 11), (2.6, -3.8, 15)]

def scene_3d(si, t):
    wt = SH.wt
    if si == 0:                                                                 # урок, крик в коридоре
        tk = wt(0, "кричит")
        it = ROOM + desks_all() + seated(t) + door()
        p, _ = teacher(T(-1.0, 0, -7.0), t, blink_seed=1.2, look=0.6 if t > tk else 0.2 * math.sin(t)); it += p
        k = ease(t / SH.DUR[0])
        return dict(items=it, eye=(lerp(5.0, 5.3, k), 3.3, lerp(5.6, 5.2, k)), tgt=(lerp(1.0, 4.6, ease((t - tk) / 1.0)), lerp(0.9, 1.2, ease((t - tk) / 1.0)), lerp(-7.0, -6.4, ease((t - tk) / 1.0))), fov=52, lights=LIGHTS_IN, snow=False)
    if si == 1:                                                                 # окно, охранник во дворе
        it = ROOM + desks_all() + seated(t, skip=(MAX_SEAT,)) + door()
        p, _ = max_(T(-5.3, 0, 1.3) @ Ry(-PI / 2 - 0.5), t, blink_seed=0.7); it += p
        gz = -3.2 + 0.4 * t
        p, _ = zombie(T(-11.5, -4, gz) @ Ry(0.15 * math.sin(t * 0.8)), t, colors=GUARD, walk=t * 3.2, look=0.3 * math.sin(t * 0.7)); it += p
        k = ease(t / SH.DUR[1])
        return dict(items=it, eye=(lerp(-5.0, -5.4, k), 2.5, lerp(0.0, -0.3, k)), tgt=(-11.5, -3.2, lerp(-2.0, -1.4, k)), fov=lerp(48, 38, k), lights=LIGHTS_IN, snow=False)
    if si == 2:                                                                 # коридор, физрук
        tr = wt(2, "И он медленно") + 0.3
        it = corridor() + corridor_lamps(t) + door(1.3)
        a = PI + PI * ease((t - tr) / 1.4)
        p, _ = zombie(T(7.9, 0, -16) @ Ry(a), t, arm="zombie" if t > tr + 0.6 else None, blink_seed=99, look=0.3 * math.sin(t * 0.9)); it += p
        k = ease(t / SH.DUR[2])
        return dict(items=it, eye=(6.6, 2.05, lerp(-5.4, -6.4, k)), tgt=(7.9, 1.75, -16), fov=lerp(46, 30, k), lights=corridor_lights(t), env=CORR, snow=False)
    if si == 3:                                                                 # баррикада
        ts = wt(3, "Весь класс") - 0.2
        it = ROOM + desks_all(skip=((3.4, -3.6), (3.4, -1.2), (0.0, -3.6))) + door(1.3 * (1 - ease(t / 0.35)))
        for j, (cx, z0) in enumerate(((3.4, -3.6), (3.4, -1.2), (0.0, -3.6))):
            kk = ease((t - ts - 0.4 * j) / 1.6)
            it += desk(lerp(cx, 5.1, kk), lerp(z0 - 0.55, DOOR_Z - 0.2 + 0.25 * j, kk), lerp(0, PI / 2, kk))
            if j == 2 and kk >= 1: it[-4:] = [(m_, T(0, 0.82, 0) @ M_, c_, e_, s_) for (m_, M_, c_, e_, s_) in it[-4:]]
        p, _ = max_(T(5.2, 0, -4.6) @ Ry(PI / 2 + 0.3), t, arm="push" if t > ts else None, blink_seed=0.7, mouth="o"); it += p
        for x, z, j in STUDENTS_UP:
            if t > ts: p, _ = kid(j, T(x, 0, z) @ Ry(PI / 2 + 0.6), t, arm="push", blink_seed=j * 0.3); it += p
        it += seated(t, skip=(MAX_SEAT, 3, 7, 11, 15, 4, 5, 10, 16, 17))
        k = ease(t / SH.DUR[3])
        return dict(items=it, eye=(lerp(0.6, 1.0, k), 3.3, lerp(-7.6, -7.4, k)), tgt=(5.2, 0.8, -4.4), fov=52, lights=LIGHTS_IN, snow=False)
    if si == 4:                                                                 # звонок, дверь трясётся
        tb = wt(4, "звонок"); shake = 0.04 * math.sin(t * 40) if t > tb + 1.0 else 0.0
        it = ROOM + desks_all(skip=((3.4, -3.6), (3.4, -1.2), (0.0, -3.6))) + door(0.0, shake)
        for j in range(3): it += desk(5.1, DOOR_Z - 0.2 + 0.25 * j, PI / 2) if j < 2 else [(m_, T(0, 0.82, 0) @ M_, c_, e_, s_) for (m_, M_, c_, e_, s_) in desk(5.1, DOOR_Z + 0.3, PI / 2)]
        o = {}
        p, _ = max_(T(2.0, 0, -3.6) @ Ry(PI / 2 - 0.2), t, arm="phone", out=o, blink_seed=0.7, mouth="o" if t > tb else None); it += p
        it += [box(o["hand"] @ T(0, -0.16, 0.06) @ S(0.16, 0.3, 0.03), C["dark"]), box(o["hand"] @ T(0, -0.16, 0.078) @ S(0.13, 0.26, 0.004), rgb((190, 215, 255)), 1.2, False)]
        for (x, z), j in zip(((3.6, -7.2), (2.8, -6.9), (4.4, -6.8), (2.0, -6.4)), (3, 7, 11, 15)): p, _ = kid(j, T(x, 0, z) @ Ry(PI / 2 - 0.3), t, blink_seed=j * 0.3, mouth="o" if t > tb else None); it += p
        k = ease(t / SH.DUR[4])
        return dict(items=it, eye=(lerp(0.4, 1.0, k), 2.5, lerp(-0.8, -1.4, k)), tgt=(5.4, 1.3, -5.4), fov=50, lights=LIGHTS_IN, snow=False)
    it = ROOM + desks_all(skip=((3.4, -3.6), (3.4, -1.2), (0.0, -3.6))) + door(0.0, 0.03 * math.sin(t * 37))   # 5: что делать
    for j in range(2): it += desk(5.1, DOOR_Z - 0.2 + 0.25 * j, PI / 2)
    p, _ = max_(T(1.8, 0, -4.4) @ Ry(PI), t, blink_seed=0.7, look=0.4 * math.sin(t * 0.8)); it += p
    for j, (x, z) in enumerate(((0.4, -3.4), (3.2, -3.6), (-0.8, -2.4), (2.2, -2.2), (4.0, -2.0))):
        p, _ = kid(j * 3 + 1, T(x, 0, z) @ Ry(PI + 0.3 * math.sin(j)), t, blink_seed=j * 0.4, look=0.3 * math.sin(t + j)); it += p
    k = ease(t / SH.DUR[5])
    return dict(items=it, eye=(lerp(1.8, 1.9, k), lerp(2.1, 2.3, k), lerp(-7.6, -7.8, k)), tgt=(1.8, 1.6, 0), fov=48, lights=LIGHTS_IN, snow=False)

def panel(d, x0, y0, x1, y1, k=1.0): d.rounded_rectangle([x0, y0, x1, y1], radius=28, fill=PANEL + (int(215 * k),))



def clock(sh, si, t):
    gt = sh.STARTS[si] + t; tb = sh.STARTS[4] + sh.wt(4, "звонок")
    if gt >= tb: return "12:00", True
    m = 55 + int(5 * gt / tb); return f"11:{min(m, 59):02d}", False

def overlay(sh, si, t, d):
    wt = sh.wt
    stroke_text(d, (W / 2, 250), "ПОСЛЕДНИЙ УРОК", font(60), WHITE, 6)
    s_, bell = clock(sh, si, t)
    flash = bell and int(t * 6) % 2 == 0
    stroke_text(d, (W / 2, 350), s_, font(122), RED if flash or (si == 5) else YEL, 9)
    def tiles(tq, a, b, y=1340):
        for j, (x, lab, c, dl) in enumerate(((290, a, GREEN, 0.0), (790, b, RED, 0.3))):
            k = ease((t - tq - dl) / 0.25)
            if k <= 0: continue
            A = int(255 * k); yy = y + 30 * (1 - k)
            d.rounded_rectangle([x - 225, yy, x + 225, yy + 170], radius=36, fill=PANEL + (int(230 * k),), outline=c + (A,), width=6)
            d.text((x, yy + 85), lab, font=font(54), fill=c + (A,), anchor="mm")
    if si == 0:
        tk = wt(0, "кричит")
        if t > tk:
            k = ease((t - tk) / 0.15); stroke_text(d, (W - 180, 760 + 6 * math.sin(t * 30)), "!!!", font(120), RED + (int(255 * k),), 9)
        tiles(wt(0, "Откроешь") - 0.05, "ОТКРЫТЬ?", "НЕТ?")
    if si == 2:
        tr = wt(2, "Серое")
        if t > tr:
            k = ease((t - tr) / 0.25); A = int(255 * k); panel(d, 60, 450, 560, 600, k)
            d.text((100, 490), "ФИЗРУК", font=font(34), fill=(190, 196, 214, A), anchor="lm"); d.text((100, 555), "УЖЕ НЕ ОН", font=font(56), fill=RED + (A,), anchor="lm")
    if si == 3:
        t24 = wt(3, "Двадцать"); t1 = wt(3, "Одна")
        if t > t24 - 0.1:
            k = ease((t - t24 + 0.1) / 0.25); A = int(255 * k); panel(d, 60, 450, 520, 700, k)
            d.text((100, 510), "В КЛАССЕ", font=font(36), fill=(190, 196, 214, A), anchor="lm"); d.text((100, 580), "24", font=font(80), fill=WHITE + (A,), anchor="lm")
            if t > t1: d.text((100, 655), "ДВЕРЬ: 1", font=font(52), fill=RED, anchor="lm")
    if si == 4:
        tc = wt(4, "Связи")
        if t > tc - 0.1:
            k = ease((t - tc + 0.1) / 0.25); A = int(255 * k); panel(d, 60, 450, 520, 600, k)
            d.text((100, 490), "ТЕЛЕФОН", font=font(34), fill=(190, 196, 214, A), anchor="lm"); d.text((100, 555), "НЕТ СЕТИ", font=font(56), fill=RED + (A,), anchor="lm")
        tb = wt(4, "звонок")
        if t > tb:
            k = ease((t - tb) / 0.2); sh_ = 8 * math.sin(t * 50)
            stroke_text(d, (W / 2 + sh_, 1560), "ДЗЫНЬ!", font(110), YEL + (int(255 * k),), 10)
    if si == 5:
        sh.cta(d, t, wt(5, "Пиши") - 0.1, "ОКНО", "КРЫША")
        te = sh.DUR[5] - 1.7
        if t > te: stroke_text(d, (W / 2, 1650), "СЕРИЯ 2 — СКОРО", font(50), WHITE + (int(255 * ease((t - te) / 0.3)),), 6)

def sound(sh, add, SR, n, tt):
    wt = sh.wt; ST = sh.STARTS; TOTAL = sh.TOTAL; rnd = np.random.default_rng(30)
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
    tb = ST[4] + wt(4, "звонок")
    calm = (tt < ST[0] + wt(0, "кричит")).astype(float)
    room = noise(TOTAL, 150, 900)[:n]; room = np.pad(room, (0, n - len(room)))
    music = (0.03 * room * calm + 0.1 * drone * (1 - 0.7 * calm) + 0.24 * beat * (1 - calm) * (1 + 0.5 * (tt > tb))) * env
    k = 0.0
    while k < tb: add(0.06 * tick(2400), k); k += 1.0                                                              # часы тикают
    def scream(at, dur=0.7, f0=900):
        t_ = T_(dur); s_ = np.sin(2 * np.pi * np.cumsum(f0 + 200 * np.sin(2 * np.pi * 7 * t_) - 300 * t_) / SR) * np.clip(t_ / 0.05, 0, 1) * np.clip((dur - t_) / 0.3, 0, 1)
        add(0.12 * s_ + 0.08 * noise(dur, 1000, 3000) * np.clip((dur - t_) / 0.3, 0, 1), at)
    scream(wt(0, "кричит") - 0.1)
    for dl, f in ((0.0, 200), (0.3, 150)): add(0.45 * thud(f, 0.35, 12), wt(0, "Откроешь") - 0.05 + dl)
    def groan(at, dur=1.6, amp=0.2):
        t_ = T_(dur); g = noise(dur, 90, 420) * (0.5 + 0.5 * np.sin(2 * np.pi * 2.3 * t_)) * np.clip(t_ / 0.3, 0, 1) * np.clip((dur - t_) / 0.4, 0, 1); add(amp * g, at)
    groan(ST[1] + wt(1, "Странно"), 1.4, 0.12)
    for j in range(int(sh.DUR[1] / 0.9)): add(0.06 * noise(0.1, 300, 1500) * np.exp(-T_(0.1) * 25), ST[1] + j * 0.9 + 0.3)
    add(0.3 * noise(0.5, 300, 2000) * np.exp(-T_(0.5) * 5), ST[2] + 0.1)                                          # скрип двери
    buzzl = np.sign(np.sin(2 * np.pi * 100 * T_(sh.DUR[2]))) * (np.random.default_rng(3).random(len(T_(sh.DUR[2]))) > 0.6); add(0.02 * buzzl, ST[2])
    add(0.6 * thud(46, 0.9, 5), ST[2] + wt(2, "Серое")); add(0.5 * thud(60, 0.6, 6), ST[2] + wt(2, "Пустые"))
    groan(ST[2] + wt(2, "И он медленно") + 0.3, 2.0, 0.25)
    add(0.9 * thud(40, 1.2, 3.2), ST[3] + 0.1); add(0.5 * noise(0.2, 200, 3000) * np.exp(-T_(0.2) * 12), ST[3] + 0.1)        # хлопок двери
    for j in range(3):
        t_ = T_(1.4); add(0.14 * noise(1.4, 150, 1200) * (0.6 + 0.4 * np.sin(2 * np.pi * 11 * t_)) * np.clip((1.4 - t_) / 0.3, 0, 1), ST[3] + wt(3, "Весь класс") - 0.2 + 0.4 * j)
    add(0.22 * tick(1100), ST[3] + wt(3, "Двадцать")); add(0.5 * thud(60, 0.6, 6), ST[3] + wt(3, "Одна"))
    add(0.35 * buzz(), ST[4] + wt(4, "Связи") + 0.1)
    t_ = T_(2.6); bell = (np.sin(2 * np.pi * 950 * t_) + 0.7 * np.sin(2 * np.pi * 1180 * t_)) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 24 * t_))) * np.clip((2.6 - t_) / 0.2, 0, 1)
    add(0.11 * bell, tb)
    for j in range(10): add((0.4 + 0.03 * j) * thud(80 + 10 * (j % 3), 0.25, 14), tb + 1.0 + j * 0.42 + 0.08 * math.sin(j * 3))
    groan(tb + 0.9, 3.0, 0.3); groan(ST[5], sh.DUR[5] - 0.5, 0.18)
    for j in range(int(sh.DUR[5] / 0.5)): add(0.3 * thud(85, 0.25, 14), ST[5] + 0.2 + j * 0.5)
    for f in (392, 466, 587): add(0.07 * np.sin(2 * np.pi * f * T_(1.6)) * np.exp(-T_(1.6) * 2.2), ST[5] + wt(5, "Пиши") - 0.1)
    add(0.2 * tick(1320), ST[5] + wt(5, "Пиши") - 0.1)
    return music

import render as _me
SH = Show(_me) if __name__ != "__main__" else None
if __name__ == "__main__":
    import render as ep
    SH = ep.SH; ep.SH.run("shkola-1")
