"""«Последний урок», серия 3 «Крыша» (3D). Запуск: LIBGL_ALWAYS_SOFTWARE=1 xvfb-run -a python3 render.py [preview | sheet N K | at N T]"""
import math, os, random, sys
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(D, "..", "engine3d")); sys.path.insert(0, D)
import numpy as np
from school import *
from show import *
from script import SCENES, CAPTION_NUMS

LEADS = [0.3] * 6
TAILS = [0.6, 0.7, 0.6, 0.9, 1.2, 3.0]
KEY = {"ключом", "поворачиваться", "схватишь", "замрёшь", "схватил", "серое", "лицо", "уже", "наверх", "ступенька", "ближе", "замок", "дрожали", "щелчок", "открылась", "сеть", "мамы", "сиди", "закрыт", "класс", "вернётся", "комментариях"}
PI = math.pi
ENV = dict(sun_dir=(0.65, -0.55, 0.25), sun_col=(1.1, 0.95, 0.75), amb_top=(0.34, 0.36, 0.42), amb_bot=(0.2, 0.19, 0.18), fog=0.006, fog_col=(0.6, 0.66, 0.78),
           sky=((0.32, 0.5, 0.82), (0.66, 0.76, 0.9), (0.7, 0.74, 0.8)), hz=0.45, shadow_center=(-2, 0, -1), shadow_size=12)
CORR = dict(ENV, sun_col=(0, 0, 0), amb_top=(0.2, 0.2, 0.2), amb_bot=(0.1, 0.1, 0.1), fog=0.03, fog_col=(0.1, 0.1, 0.1), shadow_center=(8, 0, -14), shadow_size=18)
STORE = storeroom()
STAIRS = stairs()
ST_ENV = dict(ENV, sun_col=(0, 0, 0), amb_top=(0.16, 0.15, 0.13), amb_bot=(0.08, 0.07, 0.06), fog=0.0, sky=((0.02, 0.02, 0.02),) * 3, shadow_center=(32, 0, 0), shadow_size=6)
STAIR_ENV = dict(ST_ENV, shadow_center=(41, 2, 1), shadow_size=8)
ROOF_ENV = dict(ENV, sun_dir=(0.5, -0.5, -0.4), sun_col=(0.9, 0.7, 0.55), sky=((0.28, 0.32, 0.5), (0.7, 0.55, 0.5), (0.6, 0.5, 0.48)), fog=0.006, fog_col=(0.62, 0.52, 0.5),
                shadow_center=(60, 0, 0), shadow_size=12)
STORE_L = [((32, 2.6, 0), (1.6, 1.4, 1.0), 6.0)]

def scene_3d(si, t):
    wt = SH.wt
    if si == 0:                                                                 # тянется к ключу
        lk = 0.9 * ease((t - wt(0, "А за спиной")) / 2.4)
        it = STORE + key(0.7 + 0.3 * math.sin(t * 4))
        p, _ = janitor(T(31.6, -0.9, -0.6) @ Ry(PI + 0.2), t, blink_seed=5.0, look=lk); it += p
        p, _ = max_(T(33.3, 0, -0.9) @ Ry(PI + 0.25), t, arm="point", blink_seed=0.7, look=0.4 + 0.3 * lk); it += p
        k = ease(t / SH.DUR[0])
        return dict(items=it, eye=(lerp(30.8, 30.6, k), 2.7, lerp(2.2, 2.6, k)), tgt=(32.6, 1.1, -1.4), fov=54, lights=STORE_L, env=ST_ENV, snow=False, glows=[(KEY_PT, (255, 220, 120), 60, 0.8)])
    if si == 1:                                                                 # завхоз встаёт
        tg = wt(1, "схватил") + 0.2; tu = wt(1, "Завхоз встал") - 0.1
        it = list(STORE); o = {}
        p, _ = max_(T(33.3, 0, -0.9) @ Ry(PI + 0.25 + 2.4 * ease((t - tu - 0.3) / 0.8)), t, arm="point" if t < tg else "phone", out=o, blink_seed=0.7, mouth="o" if t > tu else None); it += p
        if t < tg: it += key(1.0)
        else: it.append(box(o["hand"] @ T(0, -0.14, 0.05) @ S(0.1, 0.24, 0.02), rgb((230, 190, 70)), emit=0.8, cast=False))
        ku = ease((t - tu) / 1.0)
        p, _ = zombie(T(31.6, lerp(-0.9, 0, ku), -0.6) @ Ry(lerp(PI + 0.2, 0.9, ku)), t, colors=JANITOR, arm="zombie" if ku > 0.6 else None, blink_seed=99); it += p
        k = ease(t / SH.DUR[1])
        return dict(items=it, eye=(lerp(33.4, 33.6, k), 2.2, lerp(2.4, 2.0, k)), tgt=(lerp(32.6, 32.0, ku), 1.5, -0.8), fov=50, lights=STORE_L, env=ST_ENV, snow=False)
    if si == 2:                                                                 # лестница
        s = clamp(0.1 + t / (SH.DUR[2] + 0.4) * 0.9); zm, ym = stair_pos(s); zj, yj = stair_pos(max(0, s - 0.35))
        it = STAIRS + roof_door(0) + padlock()
        p, _ = max_(T(40.65, ym, zm) @ Ry(PI), t, walk=t * 9, blink_seed=0.7, mouth="o"); it += p
        p, _ = zombie(T(41.45, yj, zj) @ Ry(PI), t, colors=JANITOR, walk=t * 6, blink_seed=99); it += p
        return dict(items=it, eye=(41.3, STAIR_TOP + 2.2, -2.6), tgt=(41.0, lerp(1.6, 2.6, s), 2.6), fov=58, lights=[((41, 6.0, -1.8), (1.6, 1.5, 1.3), 9.0), ((41, 3, 3), (1.0, 0.9, 0.8), 5.0)], env=STAIR_ENV, snow=False)
    if si == 3:                                                                 # замок
        tc = wt(3, "Щелчок"); to = wt(3, "И дверь") + 0.2
        op = ease((t - tc) / 0.2); da = 1.8 * ease((t - to) / 0.9)
        it = STAIRS + roof_door(da) + (padlock(op) if da < 0.3 else []); o = {}
        p, _ = max_(T(40.6, STAIR_TOP, -2.3) @ Ry(PI - 0.35), t, arm="phone", out=o, blink_seed=0.7, look=0.05 * math.sin(t * 30) if t < tc else 0); it += p
        if t < to: it.append(box(o["hand"] @ T(0.02 * math.sin(t * 40) if t < tc else 0, -0.14, 0.05) @ S(0.1, 0.24, 0.02), rgb((230, 190, 70)), emit=0.6, cast=False))
        it.append(box(T(41, STAIR_TOP + 1.2, -3.36) @ S(1.6, 2.3, 0.04), rgb((255, 230, 190)), emit=3.0 * ease((t - to) / 0.6), cast=False))
        k = ease(t / SH.DUR[3])
        L = [((41, 6.0, -1.8), (1.6, 1.5, 1.3), 9.0), ((41, STAIR_TOP + 1.2, -3.6), (2.0, 1.8, 1.5), 12.0 * ease((t - to) / 0.6) + 0.01)]
        return dict(items=it, eye=(lerp(41.85, 41.8, k), STAIR_TOP + 2.0, lerp(-1.0, -1.3, k)), tgt=(40.9, STAIR_TOP + 1.2, -3.0), fov=lerp(44, 52, ease((t - to) / 1.0)), lights=L, env=STAIR_ENV, snow=False)
    R_ = roof_set(t)
    if si == 4:                                                                 # сообщение
        o = {}
        p, _ = max_(T(60, 0, 1.5) @ Ry(-0.3), t, arm="phone", out=o, blink_seed=0.7, look=-0.15, mouth="o" if t > wt(4, "Сиди") else None); it = R_ + p
        it += [box(o["hand"] @ T(0, -0.16, 0.06) @ S(0.16, 0.3, 0.03), C["dark"]), box(o["hand"] @ T(0, -0.16, 0.078) @ S(0.13, 0.26, 0.004), rgb((190, 215, 255)), 1.4, False)]
        k = ease(t / SH.DUR[4])
        return dict(items=it, eye=(lerp(59.0, 58.6, k), 2.0, lerp(5.6, 5.0, k)), tgt=(60.6, 2.4, 0.5), fov=48, env=ROOF_ENV, snow=False)
    p, _ = max_(T(67.2, 0, 0.4) @ Ry(PI / 2 - 0.2), t, blink_seed=0.7, look=0.3 * math.sin(t * 0.7)); it = R_ + p      # 5: смотрит вниз
    r = random.Random(7)
    for j in range(8):
        p, _ = zombie(T(70.5 + r.uniform(0, 5), -8, r.uniform(-5, 5)) @ Ry(r.uniform(-PI, PI)), t + j, colors=GUARD if j % 2 else PE, walk=t * 3 + j, blink_seed=99); it += p
    k = ease(t / SH.DUR[5])
    return dict(items=it, eye=(lerp(65.8, 66.0, k), lerp(6.3, 6.7, k), lerp(1.8, 1.4, k)), tgt=(72, -7.5, -0.5), fov=54, env=ROOF_ENV, snow=False)

def panel(d, x0, y0, x1, y1, k=1.0): d.rounded_rectangle([x0, y0, x1, y1], radius=28, fill=PANEL + (int(215 * k),))





def clock(sh, si, t):
    gt = sh.STARTS[si] + t; return f"12:0{min(9, 5 + int(5 * gt / sh.TOTAL))}"

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
    if si == 0: tiles(wt(0, "Схватишь") - 0.05, "СХВАТИТЬ?", "ЗАМЕРЕТЬ?")
    if si == 1:
        tz = wt(1, "Серое")
        if t > tz:
            k = ease((t - tz) / 0.25); A = int(255 * k); panel(d, 60, 450, 560, 600, k)
            d.text((100, 490), "ЗАВХОЗ", font=font(34), fill=(190, 196, 214, A), anchor="lm"); d.text((100, 555), "УЖЕ НЕ ОН", font=font(56), fill=RED + (A,), anchor="lm")
    if si == 2:
        s = clamp(0.1 + t / (sh.DUR[2] + 0.4) * 0.9); n = int(round(STEP_N * (1 - s)))
        panel(d, 60, 450, 600, 690)
        d.text((100, 500), "ДО ДВЕРИ", font=font(36), fill=(190, 196, 214), anchor="lm"); d.text((100, 600), f"{n} СТУПЕНЕЙ", font=font(64), fill=YEL, anchor="lm")
    if si == 3:
        tc = wt(3, "Щелчок")
        if t > tc: k = ease((t - tc) / 0.15); stroke_text(d, (W / 2, 900), "ЩЁЛК!", font(110), GREEN + (int(255 * k),), 10)
    if si == 4:
        tn = wt(4, "поймал")
        if t > tn:
            k = ease((t - tn) / 0.25); A = int(255 * k)
            x0, y0 = 150, 450
            d.rounded_rectangle([x0, y0, W - x0, y0 + 320], radius=36, fill=(245, 245, 250, int(240 * k)))
            for j in range(4): d.rectangle([W - x0 - 140 + j * 26, y0 + 60 - j * 10, W - x0 - 122 + j * 26, y0 + 70], fill=(40, 180, 90, A))
            d.text((x0 + 40, y0 + 50), "МАМА", font=font(40), fill=(40, 44, 60, A), anchor="lm")
            msg = "Сиди в школе. Город закрыт."; tm = wt(4, "Сиди"); n = int(clamp((t - tm) / 1.6) * len(msg))
            if t > wt(4, "Одно"): d.rounded_rectangle([x0 + 30, y0 + 110, W - x0 - 30, y0 + 280], radius=26, fill=(60, 130, 230, A))
            if n:
                words = msg[:n]
                d.text((x0 + 60, y0 + 160), words[:13], font=font(48), fill=(255, 255, 255, A), anchor="lm")
                if len(words) > 13: d.text((x0 + 60, y0 + 230), words[13:].strip(), font=font(48), fill=(255, 255, 255, A), anchor="lm")
    if si == 5:
        tk = wt(5, "Внизу")
        k = ease((t - tk) / 0.25); A = int(255 * k); panel(d, 60, 450, 560, 600, k)
        d.text((100, 490), "В КЛАССЕ", font=font(34), fill=(190, 196, 214, A), anchor="lm"); d.text((100, 555), "23 ЧЕЛОВЕКА", font=font(52), fill=YEL + (A,), anchor="lm")
        sh.cta(d, t, wt(5, "Пиши") - 0.1, "ВЕРНЁТСЯ", "НЕТ")
        te = sh.DUR[5] - 1.7
        if t > te: stroke_text(d, (W / 2, 1650), "СЕРИЯ 4 — СКОРО", font(50), WHITE + (int(255 * ease((t - te) / 0.3)),), 6)

def sound(sh, add, SR, n, tt):
    wt = sh.wt; ST = sh.STARTS; TOTAL = sh.TOTAL; rnd = np.random.default_rng(32)
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
    roof = (tt > ST[4]).astype(float)
    wind2 = noise(TOTAL, 200, 1200)[:n]; wind2 = np.pad(wind2, (0, n - len(wind2))) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.2 * tt))
    chase = ((tt > ST[2]) & (tt < ST[3] + wt(3, "Щелчок"))).astype(float)
    fast = np.zeros(n); k = ST[2]
    while k < ST[3] + wt(3, "Щелчок"):
        sig = thud(52, 0.25, 16); s0 = int(k * SR); sig = sig[: max(0, n - s0)]; fast[s0:s0 + len(sig)] += sig; k += 0.42
    music = (0.1 * wind2 * roof + 0.1 * drone * (1 - 0.4 * roof) + 0.22 * beat * (1 - chase) * (1 - 0.6 * roof) + 0.3 * fast) * env
    def groan(at, dur=1.6, amp=0.2):
        t_ = T_(dur); g = noise(dur, 90, 420) * (0.5 + 0.5 * np.sin(2 * np.pi * 2.3 * t_)) * np.clip(t_ / 0.3, 0, 1) * np.clip((dur - t_) / 0.4, 0, 1); add(amp * g, at)
    groan(wt(0, "А за спиной") + 0.3, 2.4, 0.15)
    for dl, f in ((0.0, 200), (0.3, 150)): add(0.45 * thud(f, 0.35, 12), wt(0, "Схватишь") - 0.05 + dl)
    add(0.2 * np.sin(2 * np.pi * 2400 * T_(0.3)) * np.exp(-T_(0.3) * 10), ST[1] + wt(1, "схватил") + 0.2)                  # звяк ключа
    add(0.9 * thud(40, 1.2, 3.2), ST[1] + wt(1, "Завхоз встал")); groan(ST[1] + wt(1, "Завхоз встал") + 0.2, 2.6, 0.3)
    for j in range(int(sh.DUR[2] / 0.26)): add(0.2 * thud(120, 0.12, 30), ST[2] + j * 0.26)                                    # шаги по ступеням
    for j in range(int(sh.DUR[2] / 0.5)): add(0.12 * thud(90, 0.15, 25), ST[2] + 0.1 + j * 0.5)
    groan(ST[2] + 1.0, 3.0, 0.22)
    for j in range(10): add(0.1 * noise(0.06, 2000, 6000), ST[3] + 0.3 + j * 0.25 + 0.05 * math.sin(j * 7))                      # ключ царапает замок
    add(0.5 * noise(0.05, 1500, 8000) + 0.0, ST[3] + wt(3, "Щелчок")); add(0.5 * thud(120, 0.2, 20), ST[3] + wt(3, "Щелчок"))
    t_ = T_(0.9); add(0.3 * noise(0.9, 300, 2000) * np.exp(-t_ * 3), ST[3] + wt(3, "И дверь") + 0.2)
    for f in (523, 659, 784): add(0.07 * np.sin(2 * np.pi * f * T_(1.6)) * np.exp(-T_(1.6) * 2), ST[3] + wt(3, "открылась"))
    for j in range(2): add(0.18 * np.sin(2 * np.pi * 1800 * T_(0.12)) * np.exp(-T_(0.12) * 20), ST[4] + wt(4, "Одно") + j * 0.15)   # вибро-сигнал
    add(0.6 * thud(46, 0.9, 5), ST[4] + wt(4, "Город")); add(0.4 * buzz(), ST[4] + wt(4, "закрыт"))
    groan(ST[5] + 0.3, sh.DUR[5] - 0.8, 0.14)
    for f in (392, 466, 587): add(0.07 * np.sin(2 * np.pi * f * T_(1.6)) * np.exp(-T_(1.6) * 2.2), ST[5] + wt(5, "Пиши") - 0.1)
    add(0.2 * tick(1320), ST[5] + wt(5, "Пиши") - 0.1)
    return music

import render as _me
SH = Show(_me) if __name__ != "__main__" else None
if __name__ == "__main__":
    import render as ep
    SH = ep.SH; ep.SH.run("shkola-3")
