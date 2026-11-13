"""«После», серия 1 «Тишина» (сезон 2, 3D). Запуск: LIBGL_ALWAYS_SOFTWARE=1 xvfb-run -a python3 render.py [preview | sheet N K | at N T]"""
import math, os, sys
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(D, "..", "engine3d")); sys.path.insert(0, D)
import numpy as np
from cast import *
from show import *
from script import SCENES, CAPTION_NUMS

LEADS = [0.3, 0.3, 0.3, 0.3, 0.3, 3.4]
TAILS = [0.5, 0.6, 0.6, 0.8, 1.0, 2.8]
KEY = {"30", "люк", "тишина", "огня", "звука", "молчат", "сети", "шипит", "свет", "40", "удар", "нет", "рыжее", "другой", "кто", "комментариях"}
ENV = dict(sun_dir=(-0.82, -0.30, -0.46), sun_col=(0.95, 0.72, 0.52), amb_top=(0.26, 0.31, 0.46), amb_bot=(0.13, 0.14, 0.22),
           fog_col=(0.42, 0.42, 0.52), fog=0.012, sky=((0.05, 0.10, 0.26), (0.46, 0.44, 0.54), (0.42, 0.42, 0.52)), hz=0.5,
           shadow_center=(0, 0, 3), shadow_size=18)
PI = math.pi
GLOW_PT = (-95, 5, 6.5); SUN_PT = (80, 10, 34)
SNOW2 = rgb((198, 206, 226))

def world(t, lid=0.0, hglow=0.0):
    it = [box(T(0, -0.25, 0) @ S(240, 0.5, 240), C["snow"])]
    it.append(box(T(-20, 0.012, 6.5) @ S(200, 0.02, 3.4), SNOW2, cast=False))
    for k in range(40):                                                         # колея на дороге
        it.append(box(T(-78 + k * 4.0, 0.02, 5.9 + 0.1 * math.sin(k * 1.7)) @ S(2.6, 0.02, 0.16), rgb((176, 184, 206)), cast=False))
        it.append(box(T(-76 + k * 4.0, 0.02, 7.1 + 0.1 * math.cos(k * 1.3)) @ S(2.6, 0.02, 0.16), rgb((176, 184, 206)), cast=False))
    it += house2(T(-3.5, 0, -6), 0) + house2(T(-13, 0, -7) @ Ry(0.15), 1) + house2(T(5.5, 0, -11) @ Ry(-0.2), 2) + house2(T(-24, 0, -10) @ Ry(0.3), 3) + house2(T(27, 0, -10), 4)
    it += barn(T(15, 0, -8))
    for x, z, h in ((-9, -12, 5), (-7, -16, 6), (1, -15, 5.5), (10, -15, 4.5), (22, -16, 6), (-18, -11, 5), (-30, -14, 6), (-2, -20, 7), (33, -13, 5), (-38, -8, 6),
                    (-46, -2, 7), (-52, 14, 6), (-44, 16, 5), (-30, 15, 5.5), (-16, 16, 6), (40, -4, 6), (46, 4, 5), (30, 16, 6), (12, 17, 5), (-60, 1, 7), (-64, 12, 6), (-70, -6, 7)):
        it += pine(T(x, 0, z), h)
    it += fence(-9, -0.6, -1.8)
    it += hatch(T(1.6, 0, 1.6), lid, hglow)
    for x in range(-70, 51, 12): it += pole(x, 12.4)
    it += wires(-70, 50, 12.4)
    it += house2(T(24, 0, 24) @ Ry(PI + 0.3), 5) + pine(T(34, 0, 22), 6) + pine(T(17, 0, 27), 5)
    it += doghouse(T(-8.5, 0, -2.2) @ Ry(0.4), t)
    return it

def scene_3d(si, t):
    wt = SH.wt
    if si == 0:
        to = wt(0, "открываешь")
        lid = 1.9 * ease((t - to) / 0.6)
        for t0 in (0.45, 1.25):
            if t0 < t < t0 + 0.3 and t < to: lid = 0.1 * abs(math.sin((t - t0) / 0.3 * PI * 2))
        op = clamp(lid / 1.9)
        it = world(t, lid, 1.6 * op)
        lights = [((1.6, 0.9, 1.6), (1.0, 0.6, 0.25), 6.0 * op + 0.01)]
        tc = to + 0.45                                                          # кот первым
        if t > tc:
            k = clamp((t - tc) / 0.6)
            it += cat2(T(lerp(1.6, 2.9, k), 0.3 * (1 - k) + 0.45 * math.sin(k * PI), lerp(1.6, 2.7, k)) @ Ry(lerp(0.8, 0.5, k)), t, look=0.6 * math.sin(t * 2) if k >= 1 else 0)
        ta = to + 0.9
        if t > ta:
            k = ease((t - ta) / 1.2)
            p, _ = artyom(T(1.6, lerp(-2.4, -0.72, k), 1.6) @ Ry(0.45), t, look=0.9 * math.sin((t - ta - 1.0) * 2.0) if t > ta + 1.0 else 0, lamp=True, mouth="o", blink_seed=0.7)
            it += p; lights.append(((1.75, lerp(-0.2, 1.2, k), 2.0), (1.0, 0.95, 0.8), 3.0))
        k = ease((t - to - 0.5) / 2.6)
        return dict(items=it, eye=lerp3((3.7, 1.15, 5.3), (5.4, 2.7, 9.0), k), tgt=lerp3((1.6, 0.45, 1.6), (1.2, 0.75, 1.0), k), lights=lights)
    if si == 1:
        it = world(t, 1.9)
        p, _ = artyom(T(0.2, 0, 3.4) @ Ry(PI - 0.2), t, look=1.2 * math.sin(t * 1.1), blink_seed=0.7); it += p
        it += cat2(T(1.1, 0, 3.7) @ Ry(PI + 0.3), t, look=0.5 * math.sin(t * 1.5 + 1))
        k = t / SH.DUR[1]
        return dict(items=it, eye=(lerp(-7.0, 3.0, k), 3.4, 11.0), tgt=(lerp(-6.5, -1.5, k), 1.2, -4), fov=48)
    if si == 2:
        it = world(t, 1.9)
        o = {}
        p, _ = artyom(T(0.6, 0, 3.6) @ Ry(0.12), t, arm="phone", out=o, blink_seed=0.7, look=0.1 * math.sin(t * 1.3),
                      mouth="o" if t > wt(2, "Сети нет") + 0.2 else None); it += p
        on = not (t > wt(2, "Сети нет") and int(t * 6) % 2 == 0 and t < wt(2, "Сети нет") + 0.7)
        ph = o["hand"] @ T(0, -0.16, 0.06)
        it += phone(ph, on)
        pp = (ph @ np.array([0, 0, 0.2, 1], "f4"))[:3]
        g, _ = granny(T(-1.3, 0, 2.2) @ Ry(0.45), t + 1, arm="hold", blink_seed=1.9, look=-0.4); it += g
        it += radio(T(-1.3, 0, 2.2) @ Ry(0.45) @ S(0.9) @ T(0, 1.14, 0.6))
        it += cat2(T(1.7, 0, 4.0) @ Ry(-0.5), t, look=-0.5)
        k = ease(t / SH.DUR[2])
        return dict(items=it, eye=(0.9, 2.0, lerp(9.2, 8.4, k)), tgt=(0.45, 1.9, 3.4), lights=[(tuple(pp), (0.5, 0.65, 1.0), 1.6 if on else 0.01)])
    if si == 3:
        it = world(t, 1.9)
        for j in range(18):
            tj = t - (j * 0.24 - 2.2)
            if tj < 0: continue
            sx = ((j * 37) % 11) / 10 - 0.5
            zt = -1.6 + (j % 6) * 1.25 + (j // 6) * 0.3; z = min(zt, -5.0 + tj * 1.5)
            k = clamp((z + 5.0) / 3.0); x = 15 + sx * (1.2 + 7.5 * k)
            walk = tj * 6.5 if z < zt else None
            root = T(x, 0, z) @ Ry(sx * 0.5 * k)
            kw = dict(walk=walk, blink_seed=j * 0.37, look=0.5 * math.sin(t * 1.2 + j) if walk is None else 0)
            if j == 0: p, _ = kirill(root, t, **kw)
            elif j == 1: p, _ = nina(root, t, **kw)
            elif j == 2: p, _ = mother(root, t, **kw)
            elif j == 3: p, _ = sonya(root, t, **kw)
            elif j == 4: p, _ = kolyan(root, t, **kw)
            else: p, _ = villager(j, root, t, **kw)
            it += p
        k = ease(t / SH.DUR[3])
        return dict(items=it, eye=(lerp(13.4, 16.2, k), lerp(3.2, 2.6, k), lerp(11.0, 9.4, k)), tgt=(15, 1.5, -2), fov=48,
                    env=dict(shadow_center=(15, 0, 0)))
    if si == 4:
        ts = wt(4, "А солнце") - 0.25
        k = ease((t - ts) / 0.8)
        it = world(t, 1.9)
        hl = lerp(0.0, 2.2, ease((t - ts) / 0.6))
        p, _ = kolyan(T(-0.6, 0, 8.0) @ Ry(-PI / 2), t, arm="point" if t < ts + 0.2 else None, look=hl, blink_seed=0.2); it += p
        p, _ = artyom(T(0.9, 0, 9.3) @ Ry(-PI / 2), t, look=hl, blink_seed=0.7); it += p
        p, _ = granny(T(0.3, 0, 6.6) @ Ry(-PI / 2), t, look=hl * 0.8, blink_seed=1.9); it += p
        it += cat2(T(-1.6, 0, 9.0) @ Ry(-PI / 2), t, look=0.3 * math.sin(t))
        pulse = 0.85 + 0.15 * math.sin(t * 1.7)
        it.append(ball(T(*SUN_PT) @ S(8), rgb((255, 236, 200)), emit=14.0, cast=False))
        eye = (7.2, 3.3, 8.3)
        yaw = lerp(-1.59, 1.17, k); pit = lerp(0.02, 0.1, k)
        tgt = (eye[0] + 20 * math.sin(yaw), eye[1] + 20 * pit, eye[2] + 20 * math.cos(yaw))
        return dict(items=it, eye=eye, tgt=tgt, fov=lerp(44, 40, k), glows=[(GLOW_PT, (255, 105, 35), 700, 0.85 * pulse), (GLOW_PT, (255, 170, 80), 300, 0.5 * pulse), (SUN_PT, (255, 226, 180), 380, 0.5)])
    # 5: кто-то идёт
    it = world(t, 1.9)
    it += cat2(T(-3.6, 0, 7.95) @ Ry(-PI / 2 + 0.9), t, hiss=t > 0.35, look=-0.7)
    x = -31 + 1.25 * t
    p, _ = stranger(T(x, 0, 6.5) @ Ry(PI / 2), t, walk=t * 5.2); it += p
    pulse = 0.85 + 0.15 * math.sin(t * 1.7 + 2)
    k = ease(t / SH.DUR[5])
    return dict(items=it, eye=(lerp(1.6, 1.3, k), lerp(1.1, 1.2, k), 7.6), tgt=(-30, lerp(1.2, 1.5, k), 6.6), fov=lerp(42, 33, k),
                glows=[(GLOW_PT, (255, 105, 35), 640, 0.85 * pulse), (GLOW_PT, (255, 170, 80), 280, 0.5 * pulse)], env=dict(shadow_center=(-10, 0, 6), shadow_size=26))

def overlay(sh, si, t, d):
    wt = sh.wt; gt = sh.STARTS[si] + t
    to = wt(0, "открываешь")
    new = si > 0 or t > to + 0.3
    stroke_text(d, (W / 2, 250), "ПОСЛЕ УЛЬТИМАТУМА" if new else "ТЫ ЖДАЛ КОНЦА СВЕТА", font(60), WHITE, 6)
    flash = si == 0 and to + 0.3 < t < to + 1.5 and int(t * 5) % 2 == 0
    stroke_text(d, (W / 2, 350), "ДЕНЬ 31" if new else "ДЕНЬ 30", font(122), RED if flash else YEL, 9)
    if si == 1:
        sh.checklist(d, t, [("ДОМА ЦЕЛЫ", wt(1, "Дома") + 0.35, True), ("ОГНИ", wt(1, "Но ни") + 0.5, False), ("ЗВУКИ", wt(1, "Ни одного звука") + 0.5, False)], y=450)
    if si == 2:
        sh.checklist(d, t, [("СВЯЗЬ", wt(2, "Сети нет") + 0.3, False), ("РАДИО", wt(2, "Радио") + 0.6, False), ("СВЕТ", wt(2, "Свет не") + 0.5, False)], y=450, w=360)
    if si == 3:
        t1 = wt(3, "сорок") + 0.5
        n = int(round(6 + 34 * ease(t / t1)))
        d.rounded_rectangle([60, 450, 420, 690], radius=28, fill=PANEL + (215,))
        d.text((240, 500), "ВЫШЛИ", font=font(44), fill=(190, 196, 214), anchor="mm")
        d.text((240, 600), f"{n}/40", font=font(104), fill=YEL if n == 40 else WHITE, anchor="mm")
        tq = wt(3, "Удар был")
        if t > tq:
            for j, (x, lab, c, dl) in enumerate(((290, "БЫЛ", RED, 0.0), (790, "НЕ БЫЛО", GREEN, 0.35))):
                k = ease((t - tq - dl) / 0.25)
                if k <= 0: continue
                A = int(255 * k); yy = 1340 + 30 * (1 - k)
                d.rounded_rectangle([x - 225, yy, x + 225, yy + 170], radius=36, fill=PANEL + (int(230 * k),), outline=c + (A,), width=6)
                d.text((x, yy + 85), lab + "?", font=font(64), fill=c + (A,), anchor="mm")
    if si == 5:
        if 0.8 < t < LEADS[5] - 0.1:
            k = ease((t - 0.8) / 0.2)
            stroke_text(d, (W / 2, 1180 + 20 * (1 - k)), "КТО-ТО ИДЁТ…", font(104), RED, 9)
            stroke_text(d, (W / 2, 1070), "ПО ДОРОГЕ ИЗ ГОРОДА", font(54), WHITE, 6)
        sh.cta(d, t, wt(5, "Пиши") - 0.1, "ДРУГ", "ВРАГ")
        te = sh.DUR[5] - 1.7
        if t > te: stroke_text(d, (W / 2, 1650), "СЕРИЯ 2 — СКОРО", font(50), WHITE + (int(255 * ease((t - te) / 0.3)),), 6)

def sound(sh, add, SR, n, tt):
    wt = sh.wt; ST = sh.STARTS; TOTAL = sh.TOTAL; rnd = np.random.default_rng(3)
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
        k += 1.0
    env = np.clip(tt / 0.3, 0, 1) * np.clip((TOTAL - tt) / 1.5, 0, 1)
    s5 = ST[5]; ramp = 1 + 0.9 * np.clip((tt - ST[4]) / 6, 0, 1)
    music = (0.07 * wind + 0.085 * drone * ramp + 0.2 * beat * ramp) * env
    to = ST[0] + wt(0, "открываешь")
    add(0.75 * thud(42, 0.9, 4), 0.0)
    for t0 in (0.45, 0.6, 1.25, 1.4): add(0.5 * thud(110, 0.18, 22), t0)                      # стук изнутри
    t_ = T_(0.6); add(0.22 * np.sin(2 * np.pi * np.cumsum(220 + 260 * t_ / 0.6 + 30 * np.sin(2 * np.pi * 23 * t_)) / SR) * np.clip(t_ / 0.05, 0, 1) * np.clip((0.6 - t_) / 0.1, 0, 1), to)   # скрип
    add(0.6 * thud(70, 0.5, 8), to + 0.6)
    add(0.3 * noise(0.5, 300, 3000) * np.exp(-T_(0.5) * 6), to + 0.6)
    for i, subs in ((1, ("Дома",)),): 
        for sub in subs: add(0.22 * tick(1320), ST[i] + wt(i, sub) + 0.35); add(0.16 * tick(1760), ST[i] + wt(i, sub) + 0.43)
    for i, sub, dl in ((1, "Но ни", 0.5), (1, "Ни одного звука", 0.5), (2, "Сети нет", 0.3), (2, "Радио", 0.6), (2, "Свет не", 0.5)):
        add(0.3 * buzz(), ST[i] + wt(i, sub) + dl)
    hs = noise(1.3, 1500, 7000) * np.clip(T_(1.3) / 0.1, 0, 1) * np.clip((1.3 - T_(1.3)) / 0.3, 0, 1) * (0.7 + 0.3 * np.sin(2 * np.pi * 9 * T_(1.3)))
    add(0.13 * hs, ST[2] + wt(2, "Радио") + 0.3)                                               # шипение радио
    for j in range(22): add(0.12 * noise(0.09, 500, 2500) * np.exp(-T_(0.09) * 30), ST[3] + 0.2 + j * 0.21 + 0.03 * math.sin(j * 5))   # шаги толпы
    add(0.22 * tick(880), ST[3] + wt(3, "сорок") + 0.5)
    for dl, f in ((0.0, 150), (0.35, 200)): add(0.45 * thud(f, 0.35, 12), ST[3] + wt(3, "Удар был") + dl)
    t_ = T_(2.2); add(0.3 * np.sin(2 * np.pi * np.cumsum(60 + 40 * t_ / 2.2) / SR) * np.clip(t_ / 1.5, 0, 1) ** 2 * np.clip((2.2 - t_) / 0.2, 0, 1), ST[4] + wt(4, "Там") - 0.4)  # нарастание
    ws = noise(0.7, 400, 5000) * np.sin(np.pi * T_(0.7) / 0.7) ** 2; add(0.3 * ws, ST[4] + wt(4, "А солнце") - 0.3)   # свист панорамы
    add(0.55 * thud(48, 1.0, 4), ST[4] + wt(4, "А солнце") + 0.4)
    ch = noise(0.9, 2500, 9000) * np.clip(T_(0.9) / 0.05, 0, 1) * np.exp(-T_(0.9) * 2.5); add(0.3 * ch, s5 + 0.35)       # шипение кота
    add(0.8 * thud(40, 1.2, 3.5), s5 + 0.8)
    for j in range(14): add((0.05 + 0.012 * j) * noise(0.12, 300, 1800) * np.exp(-T_(0.12) * 22), s5 + 1.0 + j * 0.6)    # шаги по снегу
    for f in (392, 466, 587): add(0.07 * np.sin(2 * np.pi * f * T_(1.6)) * np.exp(-T_(1.6) * 2.2), s5 + wt(5, "Пиши") - 0.1)
    add(0.2 * tick(1320), s5 + wt(5, "Пиши") - 0.1)
    return music

import render as _me
SH = Show(_me) if __name__ != "__main__" else None
if __name__ == "__main__":
    import render as ep
    SH = ep.SH; ep.SH.run("posle-1")
