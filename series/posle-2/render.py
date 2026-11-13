"""«После», серия 2 «Письмо» (сезон 2, 3D). Запуск: LIBGL_ALWAYS_SOFTWARE=1 xvfb-run -a python3 render.py [preview | sheet N K | at N T]"""
import math, os, sys
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(D, "..", "engine3d")); sys.path.insert(0, D)
import numpy as np
from village import *
from show import *
from script import SCENES, CAPTION_NUMS

LEADS = [0.3] * 6
TAILS = [0.6, 0.6, 0.6, 0.7, 1.2, 2.8]
KEY = {"человек", "города", "пустишь", "нет", "40", "лопату", "один", "руки", "ночь", "20", "света", "связи", "ушли", "куда", "письмо", "имя", "артём", "громов", "кого", "комментариях"}
ORANGE = (1.0, 0.5, 0.22)
GLOWS = lambda p: [(GLOW_PT, (255, 105, 35), 640, 0.85 * p), (GLOW_PT, (255, 170, 80), 280, 0.5 * p)]
ROAD_ENV = dict(shadow_center=(-4, 0, 6), shadow_size=22)

def crowd(t, step=0.0):
    it = []
    for j in range(16):
        x = 3.2 + (j // 4) * 1.5 + 0.5 * math.sin(j * 2.3); z = 4.6 + (j % 4) * 1.15 + 0.3 * math.cos(j * 1.7)
        root = T(x, 0, z) @ Ry(-PI / 2 + 0.2 * math.sin(j))
        kw = dict(blink_seed=j * 0.37, look=0.25 * math.sin(t * 0.9 + j))
        if j == 1: p, _ = nina(root, t, **kw)
        elif j == 2: p, _ = mother(root, t, **kw)
        elif j == 3: p, _ = granny(root, t, **kw)
        elif j == 5: p, _ = kolyan(root, t, **kw)
        elif j == 6: p, _ = sonya(T(x - 0.5, 0, z + 0.2) @ Ry(-PI / 2), t, **kw)
        else: p, _ = villager(j, root, t, **kw)
        it += p
    return it

def scene_3d(si, t):
    wt = SH.wt; pulse = 0.85 + 0.15 * math.sin(t * 1.7 + si)
    if si == 0:                                                                 # он идёт
        it = world(t, 1.9)
        it += cat2(T(-3.6, 0, 7.95) @ Ry(-PI / 2 + 0.9), t, hiss=True, look=-0.7)
        p, _ = stranger(T(-24 + 1.3 * t, 0, 6.5) @ Ry(PI / 2), t, walk=t * 5.2); it += p
        k = ease(t / SH.DUR[0])
        return dict(items=it, eye=(lerp(1.6, 1.2, k), 1.15, 7.6), tgt=(-30, lerp(1.3, 1.6, k), 6.6), fov=lerp(40, 31, k), glows=GLOWS(pulse),
                    env=dict(shadow_center=(-10, 0, 6), shadow_size=26))
    if si == 1:                                                                 # деревня молчит, Артём выходит
        it = world(t, 1.9) + crowd(t)
        tk = wt(1, "Кирилл"); ta = wt(1, "Артём")
        o = {}
        p, _ = kirill(T(lerp(2.4, 1.6, ease((t - tk) / 0.6)), 0, 5.0) @ Ry(-PI / 2), t, arm="hold" if t > tk else None, out=o, blink_seed=0.4); it += p
        if t > tk: it += shovel(o["hand"] @ T(-0.2, 0.15, 0) @ Rz(1.2))
        ka = clamp((t - ta) / 1.6); xa = lerp(2.0, -1.4, ease(ka))
        p, _ = artyom(T(xa, 0, 6.6) @ Ry(-PI / 2), t, walk=(t - ta) * 6.5 if 0 < ka < 1 else None, blink_seed=0.7); it += p
        it += cat2(T(xa + 0.3, 0, 7.5) @ Ry(-PI / 2), t)
        k = ease(t / SH.DUR[1])
        return dict(items=it, eye=(lerp(-7.5, -6.2, k), lerp(2.6, 2.2, k), 6.9), tgt=(3, 1.5, 6.5), fov=46,
                    lights=[((-2.5, 2.2, 6.5), ORANGE, 13.0)], env=dict(shadow_center=(2, 0, 6), shadow_size=16))
    if si == 2:                                                                 # поднял руки
        it = world(t, 1.9)
        th = wt(2, "поднял") - 0.1; xs = min(-6.6, -8.2 + 1.3 * t); wk = t * 5.2 if xs < -6.6 else None
        p, _ = guest(T(xs, 0, 6.6) @ Ry(PI / 2), t, walk=wk, arm="hands_up" if t > th else None, blink_seed=1.1, mouth="o" if t > th else None); it += p
        p, _ = artyom(T(-3.2, 0, 6.2) @ Ry(-PI / 2), t, blink_seed=0.7); it += p
        k = ease(t / SH.DUR[2])
        return dict(items=it, eye=(lerp(-0.2, -0.9, k), 2.25, 7.3), tgt=(-6.6, 1.55, 6.55), fov=lerp(40, 36, k), glows=GLOWS(pulse * 0.8), env=ROAD_ENV)
    if si == 3:                                                                 # пустой город
        k = t / SH.DUR[3]
        return dict(items=CITY, eye=(0.6, 2.0, lerp(13, 5, k)), tgt=(0, lerp(7.5, 6.0, k), -40), fov=50,
                    env=dict(fog=0.011, shadow_center=(0, 0, -10), shadow_size=34, sun_dir=(-0.6, -0.5, -0.5)))
    it = world(t, 1.9)
    if si == 4:                                                                 # письмо
        tl = wt(4, "Он достал")
        o = {}
        p, _ = guest(T(-5.95, 0, 6.5) @ Ry(PI / 2), t, arm="phone" if t > tl else None, out=o, blink_seed=1.1, look=0.3 * math.sin(t)); it += p
        if t > tl: it += envelope(o["hand"] @ T(0, -0.14, 0.05) @ Rx(-0.4))
        p, _ = artyom(T(-4.25, 0, 6.5) @ Ry(-PI / 2), t, blink_seed=0.7, mouth="o" if t > wt(4, "На конверте") else None); it += p
        it += cat2(T(-5.1, 0, 7.6) @ Ry(PI), t, look=0.5 * math.sin(t * 1.3))
        k = ease(t / SH.DUR[4])
        return dict(items=it, eye=(-5.1, lerp(2.0, 1.9, k), lerp(14.6, 13.6, k)), tgt=(-5.1, 1.75, 6.5), fov=40, env=ROAD_ENV)
    o = {}                                                                      # 5: вопрос
    p, _ = artyom(T(-3.9, 0, 6.5) @ Ry(-PI / 2 + 0.5), t, arm="phone", out=o, blink_seed=0.7, mouth="o", look=0.1 * math.sin(t * 2)); it += p
    it += envelope(o["hand"] @ T(0, -0.14, 0.05) @ Rx(-0.4))
    p, _ = guest(T(-6.3, 0, 6.5) @ Ry(PI / 2), t, blink_seed=1.1); it += p
    k = ease(t / SH.DUR[5])
    return dict(items=it, eye=(lerp(-7.0, -6.6, k), 2.0, lerp(10.2, 9.4, k)), tgt=(-4.0, 1.75, 6.5), fov=lerp(40, 34, k), env=ROAD_ENV)

def overlay(sh, si, t, d):
    wt = sh.wt
    stroke_text(d, (W / 2, 250), "ПОСЛЕ УЛЬТИМАТУМА", font(60), WHITE, 6)
    stroke_text(d, (W / 2, 350), "ДЕНЬ 31", font(122), YEL, 9)
    def tiles(tq, a, b, y=1340):
        for j, (x, lab, c, dl) in enumerate(((290, a, GREEN, 0.0), (790, b, RED, 0.3))):
            k = ease((t - tq - dl) / 0.25)
            if k <= 0: continue
            A = int(255 * k); yy = y + 30 * (1 - k)
            d.rounded_rectangle([x - 225, yy, x + 225, yy + 170], radius=36, fill=PANEL + (int(230 * k),), outline=c + (A,), width=6)
            d.text((x, yy + 85), lab, font=font(60), fill=c + (A,), anchor="mm")
    if si == 0: tiles(wt(0, "Ты его"), "ПУСТИТЬ?", "НЕТ?")
    if si == 1:
        d.rounded_rectangle([60, 450, 480, 690], radius=28, fill=PANEL + (215,))
        one = t > wt(1, "один") - 0.1
        d.text((270, 500), "ВПЕРЁД ВЫШЛИ" if one else "СТОЯТ МОЛЧА", font=font(38), fill=(190, 196, 214), anchor="mm")
        d.text((270, 600), "1" if one else "40", font=font(110), fill=YEL if one else WHITE, anchor="mm")
    if si == 2:
        t0 = wt(2, "Двадцать")
        if t > t0 - 0.2:
            k = ease((t - t0 + 0.2) / 0.25); n = int(round(20 * ease((t - t0) / 0.9)))
            d.rounded_rectangle([60, 450, 480, 690], radius=28, fill=PANEL + (int(215 * k),))
            d.text((270, 500), "ПРОШЁЛ ПЕШКОМ", font=font(36), fill=(190, 196, 214, int(255 * k)), anchor="mm")
            d.text((270, 600), f"{n} КМ", font=font(100), fill=(YEL if n == 20 else WHITE) + (int(255 * k),), anchor="mm")
    if si == 3:
        sh.checklist(d, t, [("СВЕТ", wt(3, "нет света") + 0.3, False), ("СВЯЗЬ", wt(3, "Нет связи") + 0.3, False), ("ДОМА ЦЕЛЫ", wt(3, "Но дома") + 0.4, True), ("ЛЮДИ", wt(3, "Люди") + 0.5, False)], y=450)
    if si == 4:
        t0 = wt(4, "На конверте") - 0.1
        if t > t0:
            k = ease((t - t0) / 0.3); A = int(255 * k); y0 = 480 + 60 * (1 - k); x0, x1, y1 = 130, 950, y0 + 440
            d.rounded_rectangle([x0 + 10, y0 + 14, x1 + 10, y1 + 14], radius=14, fill=(0, 0, 0, int(110 * k)))
            d.rounded_rectangle([x0, y0, x1, y1], radius=14, fill=(238, 230, 208, A), outline=(150, 138, 112, A), width=5)
            d.line([(x0 + 6, y0 + 6), (W / 2, y0 + 190), (x1 - 6, y0 + 6)], fill=(170, 158, 130, A), width=5)
            d.rounded_rectangle([x1 - 150, y0 + 30, x1 - 40, y0 + 160], radius=6, outline=(160, 60, 50, A), width=5)
            d.text((x1 - 95, y0 + 95), "1962", font=font(34), fill=(160, 60, 50, A), anchor="mm")
            tn = wt(4, "Артём Громов"); name = "АРТЁМУ ГРОМОВУ"; n = int(clamp((t - tn) / 0.9) * len(name))
            d.text((x0 + 70, y0 + 255), "КОМУ:", font=font(38), fill=(120, 108, 90, A), anchor="lm")
            d.line([(x0 + 70, y0 + 370), (x1 - 70, y0 + 370)], fill=(150, 138, 112, A), width=4)
            if n: d.text((x0 + 70, y0 + 325), name[:n], font=font(64), fill=(40, 44, 96, A), anchor="lm")
    if si == 5:
        sh.cta(d, t, wt(5, "Пиши") - 0.1, "ОТ ДЕДА", "НЕ ОН")
        te = sh.DUR[5] - 1.7
        if t > te: stroke_text(d, (W / 2, 1650), "СЕРИЯ 3 — СКОРО", font(50), WHITE + (int(255 * ease((t - te) / 0.3)),), 6)

def sound(sh, add, SR, n, tt):
    wt = sh.wt; ST = sh.STARTS; TOTAL = sh.TOTAL; rnd = np.random.default_rng(4)
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
    city = ((tt > ST[3]) & (tt < ST[4])).astype(float)
    music = (0.07 * wind * (1 + 1.5 * city) + 0.1 * drone + 0.22 * beat * (1 - 0.8 * city)) * env
    add(0.8 * thud(42, 0.9, 4), 0.0)
    ch = noise(0.9, 2500, 9000) * np.clip(T_(0.9) / 0.05, 0, 1) * np.exp(-T_(0.9) * 2.5); add(0.25 * ch, 0.15)
    for j in range(int(sh.DUR[0] / 0.6)): add((0.06 + 0.015 * j) * noise(0.12, 300, 1800) * np.exp(-T_(0.12) * 22), 0.3 + j * 0.6)
    for dl, f in ((0.0, 200), (0.3, 150)): add(0.45 * thud(f, 0.35, 12), wt(0, "Ты его") + dl)
    add(0.35 * tick(520), ST[1] + wt(1, "Кирилл") + 0.3); add(0.3 * noise(0.25, 800, 4000) * np.exp(-T_(0.25) * 14), ST[1] + wt(1, "Кирилл") + 0.3)
    for j in range(5): add(0.14 * noise(0.12, 300, 1800) * np.exp(-T_(0.12) * 22), ST[1] + wt(1, "Артём") + j * 0.3)
    add(0.5 * thud(48, 0.9, 5), ST[1] + wt(1, "один"))
    add(0.5 * thud(70, 0.5, 8), ST[2] + wt(2, "поднял")); add(0.22 * tick(880), ST[2] + wt(2, "Двадцать") + 0.9)
    for sub, dl, ok in (("нет света", 0.3, 0), ("Нет связи", 0.3, 0), ("Но дома", 0.4, 1), ("Люди", 0.5, 0)):
        add((0.22 * tick(1320)) if ok else 0.3 * buzz(), ST[3] + wt(3, sub) + dl)
    add(0.3 * noise(0.35, 1500, 6000) * np.exp(-T_(0.35) * 9), ST[4] + wt(4, "Он достал") + 0.1)                   # шорох бумаги
    add(0.6 * thud(46, 1.0, 4), ST[4] + wt(4, "На конверте"))
    for j in range(14): add(0.12 * tick(1900 + 60 * (j % 3)), ST[4] + wt(4, "Артём Громов") + j * 0.064)            # буквы
    add(0.8 * thud(40, 1.2, 3.5), ST[4] + wt(4, "Артём Громов") + 0.95)
    for f in (392, 466, 587): add(0.07 * np.sin(2 * np.pi * f * T_(1.6)) * np.exp(-T_(1.6) * 2.2), ST[5] + wt(5, "Пиши") - 0.1)
    add(0.2 * tick(1320), ST[5] + wt(5, "Пиши") - 0.1)
    return music

CITY = city()
import render as _me
SH = Show(_me) if __name__ != "__main__" else None
if __name__ == "__main__":
    import render as ep
    SH = ep.SH; ep.SH.run("posle-2")
