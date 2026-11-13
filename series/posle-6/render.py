"""«После», серия 6 «Ворота» (сезон 2, 3D). Запуск: LIBGL_ALWAYS_SOFTWARE=1 xvfb-run -a python3 render.py [preview | sheet N K | at N T]"""
import math, os, random, sys
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(D, "..", "engine3d")); sys.path.insert(0, D)
import numpy as np
from village import *
from show import *
from script import SCENES, CAPTION_NUMS

LEADS = [0.3] * 6
TAILS = [0.6, 0.6, 0.7, 0.9, 1.4, 3.0]
KEY = {"убежище", "письмо", "прошлого", "покажешь", "автобус", "руль", "всех", "север", "стена", "ворота", "прожектор", "мест", "нет", "уходите", "вершинина", "тишина", "открылись", "внутри", "комментариях"}
DAY = dict(ENV, sun_dir=(-0.5, -0.45, -0.6), fog=0.016, shadow_center=(0, 0, -20), shadow_size=26)
PI = math.pi
INK = (40, 44, 96); PAPER = (238, 230, 208); EDGE = (150, 138, 112)
FI = "/usr/share/fonts/truetype/freefont/FreeSerifBoldItalic.ttf"
_FI = {}
def hand(sz):
    if sz not in _FI: _FI[sz] = ImageFont.truetype(FI if os.path.exists(FI) else FB, sz)
    return _FI[sz]

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
BUS_G = T(-6.5, 0, -16) @ Ry(PI / 2 - 0.25)
SITE = GROUND + TREES + wall() + bus(BUS_G, 0)
WARM = (1.0, 0.82, 0.55)

def scene_3d(si, t):
    wt = SH.wt
    if si in (0, 4, 5):
        if si == 0: g = 0.0
        elif si == 4: g = ease((t - wt(4, "И ворота") - 0.2) / 1.6)
        else: g = 1.0
        it = SITE + gate(g); o = {}
        up = si == 0 or (si == 4 and t > wt(4, "поднял") - 0.1) or si == 5
        x0 = -0.9 if si == 5 else -0.3; z0 = lerp(-21.0, -24.0, ease((t - 0.3) / 1.6)) if si == 4 else -24.0
        p, _ = artyom(T(x0, 0, z0) @ Ry(PI), t, arm="up" if up else None, out=o, walk=t * 6 if si == 4 and t < 1.9 else None, blink_seed=0.7); it += p
        if up: it += envelope(o["hand"] @ T(0, -0.12, 0.05) @ Rx(-PI / 2) @ Ry(PI))
        it += cat2(T(1.0, 0, z0 + 0.6) @ Ry(PI), t)
        if si >= 4:
            p, _ = kolyan(T(3.6, 0, -20.5) @ Ry(PI - 0.2), t, blink_seed=0.2); it += p
            p, _ = guest(T(-3.4, 0, -20.0) @ Ry(PI + 0.2), t, blink_seed=1.1); it += p
        if g > 0.4:
            p, _ = stranger(T(0.3, 0, GZ - 0.5) @ Ry(0), t); it += p
        if si == 0: eye, tgt, fov = (lerp(0.9, 0.5, ease(t / SH.DUR[0])), 1.3, -17.5), (-0.3, 3.0, GZ), 50
        elif si == 4: k = ease(t / SH.DUR[4]); eye, tgt, fov = (lerp(1.2, 0.6, k), 1.6, lerp(-14.0, -15.5, k)), (-0.2, 3.0, GZ), 48
        else: k = ease(t / SH.DUR[5]); eye, tgt, fov = (0.1, lerp(1.5, 1.4, k), lerp(-15.6, -17.0, k)), (-0.2, 2.4, GZ), 48
        gl = [(SEARCH, (255, 250, 230), 520, 0.85), (SEARCH, (255, 255, 245), 120, 1.0)]
        if g > 0: gl.append(((0, 2.4, GZ - 1), (255, 190, 110), int(200 + 500 * g), 0.9 * g))
        lights = [((0, 3, GZ + 1.5), WARM, 4 + 16 * g), ((-0.3, 3.0, -20.5), (1.0, 0.95, 0.85), 7.0)]
        return dict(items=it, eye=eye, tgt=tgt, fov=fov, glows=gl, lights=lights, env=DAY)
    if si == 1:
        tg = wt(1, "Колян") - 0.1
        if t < tg:                                                              # откапывают
            m = T(0, 0, 4) @ Ry(PI / 2); it = GROUND + TREES + bus(m, t)
            for (x, z, s_) in ((-1.7, 1.2, 1.4), (1.7, 2.0, 1.2), (-1.6, 6.0, 1.3)): it.append(ball(T(x, 0.1, z) @ S(s_ * (1 - 0.5 * clamp(t / tg)), 0.8, s_), C["snow"]))
            for j, (fn, x, z, a) in enumerate(((artyom, -2.8, 2.0, PI / 2), (kolyan, 2.8, 3.0, -PI / 2), (guest, -2.8, 6.0, PI / 2))):
                root = T(x, 0, z) @ Ry(a); p, _ = fn(root, t + j, arm="dig", blink_seed=j * 0.6); it += p
                dg = math.sin((t + j) * 4.5); it += shovel(root @ T(0.1, 1.2 + 0.15 * dg, 0.55) @ Rx(0.5 + 0.2 * dg))
            k = ease(t / tg)
            return dict(items=it, eye=(lerp(-6.5, -7.5, k), 5.0, lerp(14.5, 13.0, k)), tgt=(0, 1.0, 3.8), fov=46, env=dict(DAY, shadow_center=(0, 0, 4)))
        tt_ = t - tg; zb = 4 - 4.5 * tt_ - 1.0 * tt_ * tt_                          # едут
        m = T(0, 0, zb) @ Ry(PI / 2) @ T(0, 0.03 * math.sin(t * 13), 0); it = GROUND + TREES + bus(m, t)
        return dict(items=it, eye=(-6.0, 2.6, zb + 8.5), tgt=(0, 1.6, zb - 2), fov=48, env=dict(DAY, shadow_center=(0, 0, zb)))
    if si == 2:                                                                 # стена
        it = SITE + gate(0.0)
        k = ease(t / SH.DUR[2])
        gl = [(SEARCH, (255, 250, 230), lerp(500, 760, k), 0.9), (SEARCH, (255, 255, 245), 140, 1.0)]
        return dict(items=it, eye=(lerp(5.0, 2.0, k), lerp(1.4, 1.1, k), lerp(-4.0, -12.0, k)), tgt=(0, lerp(3.4, 4.6, k), GZ), fov=50, glows=gl, env=DAY,
                    lights=[((0, 3, GZ + 1.5), WARM, 4)])
    # 3: динамик
    it = SITE + gate(0.0)
    on = int(t * 7) % 2 == 0
    gl = [(SEARCH, (255, 250, 230), 380, 0.8)] + ([(SPEAK, (255, 60, 50), 110, 0.9)] if on else [])
    it.append(ball(T(SPEAK[0], SPEAK[1] + 0.55, SPEAK[2]) @ S(0.22), rgb((255, 60, 50)), emit=6.0 if on else 0.4, cast=False))
    k = ease(t / SH.DUR[3])
    return dict(items=it, eye=(lerp(5.8, 5.4, k), 4.4, GZ + lerp(7.0, 5.6, k)), tgt=(3.6, 5.2, GZ), fov=42, glows=gl, env=DAY,
                lights=[((3.6, 5.6, GZ + 1.6), (1.0, 0.25, 0.2), 5.0 if on else 0.01)])

def panel(d, x0, y0, x1, y1, k=1.0): d.rounded_rectangle([x0, y0, x1, y1], radius=28, fill=PANEL + (int(215 * k),))
def paper(d, y0, h, k, x0=120, x1=960):
    A = int(255 * k); y0 += 60 * (1 - k)
    d.rounded_rectangle([x0 + 10, y0 + 14, x1 + 10, y0 + h + 14], radius=14, fill=(0, 0, 0, int(110 * k)))
    d.rounded_rectangle([x0, y0, x1, y0 + h], radius=14, fill=PAPER + (A,), outline=EDGE + (A,), width=5)
    return y0, A

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
    if si == 0: tiles(wt(0, "Покажешь") - 0.05, "ПОКАЗАТЬ?", "НЕТ?")
    if si == 1:
        tg = wt(1, "Колян") - 0.1; tv = wt(1, "Взяли всех")
        if t > tv - 0.1:
            k = ease((t - tv + 0.1) / 0.25); A = int(255 * k); panel(d, 60, 450, 540, 690, k)
            d.text((300, 500), "В АВТОБУСЕ", font=font(38), fill=(190, 196, 214, A), anchor="mm")
            d.text((300, 600), "15 + КЕКС", font=font(80), fill=YEL + (A,), anchor="mm")
    if si == 2:
        km = max(0, int(round(lerp(32, 0, ease(t / max(0.1, wt(2, "стена")))))))
        panel(d, 60, 450, 540, 690)
        d.text((300, 500), "ДО УБЕЖИЩА", font=font(38), fill=(190, 196, 214), anchor="mm")
        d.text((300, 600), f"{km} КМ", font=font(100), fill=YEL if km == 0 else WHITE, anchor="mm")
    if si == 3:
        for sub, txt in (("Мест нет", "МЕСТ НЕТ"), ("Уходите", "УХОДИТЕ")):
            t0 = wt(3, sub)
            if t > t0:
                kk = ease((t - t0) / 0.15); s_ = 1 + 0.35 * (1 - kk); y = 1420 if sub == "Мест нет" else 1570
                d.rounded_rectangle([W / 2 - 330 * s_, y - 62 * s_, W / 2 + 330 * s_, y + 62 * s_], radius=18, fill=PANEL + (225,), outline=RED, width=8)
                d.text((W / 2, y), txt, font=font(int(86 * s_)), fill=RED, anchor="mm")
    if si == 4:
        tp = wt(4, "Подпись") - 0.1; to = wt(4, "И ворота")
        k = ease((t - tp) / 0.3) * (1 - ease((t - to) / 0.3))
        if k > 0:
            y0, A = paper(d, 450, 250, k)
            d.text((180, y0 + 60), "ПОДПИСЬ:", font=font(36), fill=(120, 108, 90, A), anchor="lm")
            d.line([(180, y0 + 190), (900, y0 + 190)], fill=EDGE + (A,), width=4)
            d.text((200, y0 + 140), "Вершинин", font=hand(96), fill=INK + (A,), anchor="lm")
            d.text((900, y0 + 70), "1962", font=font(40), fill=(170, 50, 40, A), anchor="rm")
        if t > to + 0.3:
            k = ease((t - to - 0.3) / 0.3); stroke_text(d, (W / 2, 560 + 20 * (1 - k)), "ВОРОТА ОТКРЫТЫ", font(80), GREEN + (int(255 * k),), 8)
    if si == 5:
        sh.cta(d, t, wt(5, "Пиши") - 0.1, "ВЕРШИНИН", "ДРУГОЙ")
        te = sh.DUR[5] - 1.7
        if t > te: stroke_text(d, (W / 2, 1650), "СЕРИЯ 7 — СКОРО", font(50), WHITE + (int(255 * ease((t - te) / 0.3)),), 6)

def sound(sh, add, SR, n, tt):
    wt = sh.wt; ST = sh.STARTS; TOTAL = sh.TOTAL; rnd = np.random.default_rng(12)
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
    music = (0.09 * wind + 0.1 * drone + 0.22 * beat) * env
    add(0.8 * thud(42, 0.9, 4), 0.0)
    for dl, f in ((0.0, 200), (0.3, 150)): add(0.45 * thud(f, 0.35, 12), wt(0, "Покажешь") - 0.05 + dl)
    tg = ST[1] + wt(1, "Колян") - 0.1
    j = 0.0
    while ST[1] + 0.2 + j < tg: add(0.3 * thud(120, 0.15, 25) + 0.12 * noise(0.15, 800, 3000) * np.exp(-T_(0.15) * 20), ST[1] + 0.2 + j); j += 0.7
    d_ = ST[2] - tg; t_ = T_(0.6); add(0.4 * noise(0.6, 60, 400) * np.clip(t_ / 0.05, 0, 1) * np.exp(-t_ * 3), tg)                # заводится
    t_ = T_(d_); eng = np.sin(2 * np.pi * np.cumsum(36 + 10 * np.clip(t_ / 1.5, 0, 1)) / SR) * (0.6 + 0.4 * np.sin(2 * np.pi * 9 * t_)); add(0.12 * eng, tg + 0.3)
    add(0.22 * tick(1100), ST[1] + wt(1, "Взяли всех"))
    add(0.9 * thud(40, 1.3, 3.2), ST[2] + wt(2, "стена")); add(0.5 * thud(70, 0.6, 7), ST[2] + wt(2, "Железные"))
    t_ = T_(0.5); add(0.3 * noise(0.5, 2000, 8000) * np.exp(-t_ * 5), ST[2] + wt(2, "Прожектор"))                                  # щелчок прожектора
    k = 0.0
    while k < sh.DUR[3]:                                                                                                         # сигнал динамика
        t_ = T_(0.07); add(0.08 * np.sin(2 * np.pi * 980 * t_), ST[3] + k); k += 0.286
    add(0.4 * noise(0.3, 1500, 6000) * np.exp(-T_(0.3) * 6), ST[3] + 0.1)
    for sub in ("Мест нет", "Уходите"): add(0.7 * thud(44, 1.0, 4), ST[3] + wt(3, sub))
    for j in range(5): add(0.13 * noise(0.12, 300, 1800) * np.exp(-T_(0.12) * 22), ST[4] + 0.3 + j * 0.32)
    add(0.3 * noise(0.35, 1500, 6000) * np.exp(-T_(0.35) * 9), ST[4] + wt(4, "поднял"))
    add(0.5 * thud(60, 0.6, 6), ST[4] + wt(4, "Подпись"))
    sil = (tt > ST[4] + wt(4, "Тишина")) & (tt < ST[4] + wt(4, "И ворота"))
    to = ST[4] + wt(4, "И ворота") + 0.2
    t_ = T_(1.8); grind = noise(1.8, 40, 300) * (0.6 + 0.4 * np.sin(2 * np.pi * 17 * t_)) * np.clip(t_ / 0.1, 0, 1) * np.clip((1.8 - t_) / 0.3, 0, 1); add(0.45 * grind, to)
    add(0.9 * thud(38, 1.5, 3.0), to + 1.7)
    for f in (392, 494, 587, 784): add(0.06 * np.sin(2 * np.pi * f * T_(2.2)) * np.exp(-T_(2.2) * 1.5), to + 1.7)
    for f in (392, 466, 587): add(0.07 * np.sin(2 * np.pi * f * T_(1.6)) * np.exp(-T_(1.6) * 2.2), ST[5] + wt(5, "Пиши") - 0.1)
    add(0.2 * tick(1320), ST[5] + wt(5, "Пиши") - 0.1)
    return music * (1 - 0.85 * sil)

import render as _me
SH = Show(_me) if __name__ != "__main__" else None
if __name__ == "__main__":
    import render as ep
    SH = ep.SH; ep.SH.run("posle-6")
