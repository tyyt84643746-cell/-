"""«После», серия 3 «На север» (сезон 2, 3D). Запуск: LIBGL_ALWAYS_SOFTWARE=1 xvfb-run -a python3 render.py [preview | sheet N K | at N T]"""
import math, os, random, sys
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(D, "..", "engine3d")); sys.path.insert(0, D)
import numpy as np
from village import *
from show import *
from script import SCENES, CAPTION_NUMS

LEADS = [0.3] * 6
TAILS = [0.6, 0.7, 0.9, 0.8, 0.9, 2.8]
KEY = {"письмо", "1962", "имя", "откроешь", "чужой", "деду", "одинаково", "тишина", "жди", "север", "40", "убежище", "вершинин", "отца", "следы", "город", "идти", "остаться", "комментариях"}
ROAD_ENV = dict(shadow_center=(-4, 0, 6), shadow_size=22)
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
def tracks(z0, z1):
    it = []; k = 0; z = z0
    while z > z1:
        for lane, ph in ((-1.7, 0.0), (-0.9, 1.3), (0.0, 2.1), (0.8, 0.6), (1.6, 1.9)):
            x = lane + 0.35 * math.sin(k * 0.21 + ph) + (0.15 if k % 2 else -0.15)
            it.append(box(T(x, 0.025, z - ph * 0.3) @ S(0.18, 0.02, 0.36), rgb((150, 158, 182)), cast=False))
        z -= 0.75; k += 1
    return it
FOREST_N = forest(-25, -70, gap=5.0)
FIELD = [box(T(0, -0.25, -20) @ S(240, 0.5, 240), C["snow"])] + forest(2, -75, 9, 3.6, 60) + tracks(9, -62)
FIELD_ENV = dict(shadow_center=(0, 0, 0), shadow_size=24)

def scene_3d(si, t):
    wt = SH.wt
    if si == 0:                                                                 # конверт в руках
        it = world(t, 1.9); o = {}
        p, _ = artyom(T(-3.9, 0, 6.5) @ Ry(-PI / 2 + 0.5), t, arm="phone", out=o, blink_seed=0.7, mouth="o", look=0.1 * math.sin(t * 2)); it += p
        it += envelope(o["hand"] @ T(0, -0.14, 0.05) @ Rx(-0.4))
        p, _ = guest(T(-6.3, 0, 6.5) @ Ry(PI / 2), t, blink_seed=1.1); it += p
        k = ease(t / SH.DUR[0])
        return dict(items=it, eye=(lerp(-6.8, -7.2, k), 2.0, lerp(10.4, 11.0, k)), tgt=(-4.0, 2.06, 6.5), fov=38, env=ROAD_ENV)
    if si == 1:
        td = wt(1, "Его деду") - 0.15
        if t < td:                                                              # читает
            it = world(t, 1.9); o = {}
            p, _ = artyom(T(-3.9, 0, 6.5) @ Ry(-PI / 2 + 0.9), t, arm="phone", out=o, blink_seed=0.7, look=-0.1); it += p
            it += envelope(o["hand"] @ T(0, -0.14, 0.05) @ Rx(-0.4))
            it += cat2(T(-4.6, 0, 7.9) @ Ry(0.6), t, look=0.4)
            k = ease(t / td)
            return dict(items=it, eye=(-5.8, 2.0, lerp(11.6, 10.8, k)), tgt=(-4.0, 2.06, 6.5), fov=38, env=ROAD_ENV)
        tt_ = t - td                                                            # 1962: дед копает
        root = T(1.0, 0, 3.0) @ Ry(0.5)
        it = world(t, 1.9)
        p, _ = ded(root, t, blink_seed=0.3, look=0.3 * math.sin(t * 1.2)); it += p
        it += shovel(root @ T(0.62, 0.95, 0.12) @ Rz(0.06))
        k = ease(tt_ / 3.0)
        return dict(items=it, eye=(lerp(4.8, 4.2, k), 2.4, lerp(8.6, 7.8, k)), tgt=(1.0, 1.5, 2.8), fov=42, sepia=1.0)
    if si == 2:                                                                 # маршрут на север
        tn = wt(2, "Иди на север")
        it = [x for x in world(t, 1.9) if not 11.5 < x[1][2, 3] < 13.3] + FOREST_N   # без столбов и проводов перед камерой
        kk = clamp((t - tn) / 1.8)
        for j in range(int(12 * kk)):
            it.append(box(T(0.8 * math.sin(j * 0.5), 0.06, -14 - j * 2.8) @ S(0.7, 0.06, 1.7), rgb((240, 60, 50)), emit=1.6, cast=False))
        gl = []
        if t > wt(2, "Там") - 0.2:
            pu = 0.8 + 0.2 * math.sin(t * 6)
            it.append(ball(T(0, 0.4, -52) @ S(7, 2.4, 6), rgb((70, 74, 84))))
            it.append(box(T(0, 1.0, -48.9) @ S(1.6, 2.0, 0.2), rgb((255, 190, 90)), emit=3.0, cast=False))
            gl = [((0, 2, -49), (255, 150, 60), 240, 0.9 * pu)]
        k = ease(t / SH.DUR[2])
        return dict(items=it, eye=(0, lerp(16, 30, k), lerp(26, 20, k)), tgt=(0, 0, lerp(-8, -34, k)), fov=50, glows=gl,
                    env=dict(fog=0.007, shadow_center=(0, 0, -30), shadow_size=52))
    if si == 3:                                                                 # Нина
        it = world(t, 1.9)
        pale = t > wt(3, "Нина побледнела")
        p, _ = nina(T(-5.0, 0, 6.5) @ Ry(0.05), t, blink_seed=2.2, mouth="o" if pale else None, look=0.1 * math.sin(t)); it += p
        p, _ = artyom(T(-3.7, 0, 5.3) @ Ry(-0.4), t, blink_seed=0.7, look=-0.5); it += p
        p, _ = granny(T(-6.3, 0, 5.4) @ Ry(0.4), t, blink_seed=1.9, look=0.5); it += p
        k = ease((t - wt(3, "Нина") + 0.2) / 1.2)
        return dict(items=it, eye=(-5.0, 1.9, lerp(11.8, 10.4, k)), tgt=(-5.0, lerp(1.8, 1.72, k), 6.5), fov=36, env=ROAD_ENV)
    it = list(FIELD)
    if si == 4:                                                                 # следы
        p, _ = guest(T(2.5, 0, 6.2) @ Ry(PI), t, arm="point", blink_seed=1.1); it += p
        k = ease(t / SH.DUR[4])
        return dict(items=it, eye=(lerp(3.2, 2.2, k), lerp(2.2, 3.4, k), lerp(10.5, 11.5, k)), tgt=(0, 1.0, lerp(-6, -20, k)), fov=46, env=FIELD_ENV)
    p, _ = artyom(T(-0.5, 0, 6.6) @ Ry(PI), t, blink_seed=0.7, look=0.5 * math.sin(t * 0.9)); it += p   # 5: решение
    p, _ = guest(T(1.0, 0, 6.2) @ Ry(PI), t, blink_seed=1.1); it += p
    it += cat2(T(-1.5, 0, 7.2) @ Ry(PI), t, look=0.4 * math.sin(t * 1.4))
    k = ease(t / SH.DUR[5])
    return dict(items=it, eye=(0.2, lerp(3.0, 3.3, k), lerp(13.4, 12.6, k)), tgt=(0.2, 1.2, -20), fov=44, env=FIELD_ENV)

def paper(d, y0, h, k, x0=120, x1=960):
    A = int(255 * k); y0 += 60 * (1 - k)
    d.rounded_rectangle([x0 + 10, y0 + 14, x1 + 10, y0 + h + 14], radius=14, fill=(0, 0, 0, int(110 * k)))
    d.rounded_rectangle([x0, y0, x1, y0 + h], radius=14, fill=PAPER + (A,), outline=EDGE + (A,), width=5)
    return y0, A

def overlay(sh, si, t, d):
    wt = sh.wt
    stroke_text(d, (W / 2, 250), "ПОСЛЕ УЛЬТИМАТУМА", font(60), WHITE, 6)
    old = si == 1 and t > wt(1, "Его деду") - 0.15
    stroke_text(d, (W / 2, 350), "ГОД 1962" if old else "ДЕНЬ 31", font(122), YEL, 9)
    def tiles(tq, a, b, y=1340):
        for j, (x, lab, c, dl) in enumerate(((290, a, GREEN, 0.0), (790, b, RED, 0.3))):
            k = ease((t - tq - dl) / 0.25)
            if k <= 0: continue
            A = int(255 * k); yy = y + 30 * (1 - k)
            d.rounded_rectangle([x - 225, yy, x + 225, yy + 170], radius=36, fill=PANEL + (int(230 * k),), outline=c + (A,), width=6)
            d.text((x, yy + 85), lab, font=font(58), fill=c + (A,), anchor="mm")
    if si == 0:
        k = ease((t - 0.2) / 0.3)
        if k > 0:
            y0, A = paper(d, 450, 400, k); x0, x1 = 120, 960
            d.line([(x0 + 6, y0 + 6), (W / 2, y0 + 170), (x1 - 6, y0 + 6)], fill=(170, 158, 130, A), width=5)
            big = 1 + 0.12 * (1 - ease((t - wt(0, "шестьдесят")) / 0.4)) if t > wt(0, "шестьдесят") else 1
            cx, cy = x1 - 110, y0 + 95; r = 62 * big
            d.rounded_rectangle([cx - r, cy - r, cx + r, cy + r], radius=6, outline=(170, 50, 40, A), width=6)
            d.text((cx, cy), "1962", font=font(int(38 * big)), fill=(170, 50, 40, A), anchor="mm")
            d.text((x0 + 70, y0 + 235), "КОМУ:", font=font(36), fill=(120, 108, 90, A), anchor="lm")
            d.line([(x0 + 70, y0 + 340), (x1 - 70, y0 + 340)], fill=EDGE + (A,), width=4)
            d.text((x0 + 70, y0 + 298), "АРТЁМУ ГРОМОВУ", font=font(62), fill=(YEL if False else INK) + (A,), anchor="lm")
        tiles(wt(0, "Откроешь") - 0.1, "ОТКРЫТЬ?", "НЕТ?")
    if si == 1 and not old:
        k = ease((t - wt(1, "Почерк") + 0.3) / 0.3)
        if k > 0:
            y0, A = paper(d, 450, 330, k)
            rnd = random.Random(2)
            for j in range(4):                                                  # неразборчивый почерк
                x = 180; yy = y0 + 70 + j * 62; pts = []
                while x < (880 if j < 3 else 560):
                    pts.append((x, yy + rnd.uniform(-16, 16))); x += rnd.uniform(9, 22)
                d.line(pts, fill=INK + (A,), width=4)
    if old:
        k = ease((t - wt(1, "Его деду") + 0.15) / 0.3); A = int(255 * k)
        d.rounded_rectangle([60, 450, 600, 620], radius=28, fill=PANEL + (int(215 * k),))
        d.text((330, 500), "ДЕД", font=font(40), fill=(190, 196, 214, A), anchor="mm")
        d.text((330, 565), "АРТЁМ ГРОМОВ", font=font(52), fill=YEL + (A,), anchor="mm")
    if si == 2:
        k = ease((t - 0.1) / 0.3) * (1 - ease((t - wt(2, "Там") + 0.5) / 0.3))
        y0, A = paper(d, 450, 360, k) if k > 0 else (0, 0)
        lines = [("Артём.", wt(2, "Артём"), 56), ("Снова тишина — не жди.", wt(2, "Если"), 56), ("Иди на север.", wt(2, "Иди"), 68), ("40 км. Третье убежище.", wt(2, "Сорок"), 56)]
        for j, (s_, t0, sz) in enumerate(lines):
            n = int(clamp((t - t0) / 0.7) * len(s_))
            if n and k > 0: d.text((180, y0 + 62 + j * 80), s_[:n], font=hand(sz + 8), fill=((170, 40, 36) if j == 2 else INK) + (A,), anchor="lm")
    if si == 3:
        k = ease((t - 0.05) / 0.3)
        y0, A = paper(d, 450, 250, k)
        d.text((180, y0 + 60), "ПОДПИСЬ:", font=font(36), fill=(120, 108, 90, A), anchor="lm")
        d.line([(180, y0 + 190), (900, y0 + 190)], fill=EDGE + (A,), width=4)
        s_ = "Вершинин"; n = int(clamp((t - wt(3, "Вершинин")) / 0.6) * len(s_))
        if n: d.text((200, y0 + 140), s_[:n], font=hand(96), fill=INK + (A,), anchor="lm")
    if si == 4:
        t0 = wt(4, "Туда")
        if t > t0:
            k = ease((t - t0) / 0.3); A = int(255 * k)
            d.rounded_rectangle([60, 450, 560, 620], radius=28, fill=PANEL + (int(215 * k),))
            d.text((310, 500), "ВЕСЬ ГОРОД УШЁЛ", font=font(40), fill=(190, 196, 214, A), anchor="mm")
            d.text((310, 565), "НА СЕВЕР ↑", font=font(60), fill=YEL + (A,), anchor="mm")
    if si == 5:
        sh.cta(d, t, wt(5, "Пиши") - 0.1, "ИДТИ", "ОСТАТЬСЯ")
        te = sh.DUR[5] - 1.7
        if t > te: stroke_text(d, (W / 2, 1650), "СЕРИЯ 4 — СКОРО", font(50), WHITE + (int(255 * ease((t - te) / 0.3)),), 6)

def sound(sh, add, SR, n, tt):
    wt = sh.wt; ST = sh.STARTS; TOTAL = sh.TOTAL; rnd = np.random.default_rng(6)
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
    old = 1 - 0.85 * ((tt > ST[1] + wt(1, "Его деду")) & (tt < ST[2])).astype(float)
    music = (0.08 * wind + 0.1 * drone + 0.22 * beat * old) * env
    add(0.8 * thud(42, 0.9, 4), 0.0)
    add(0.3 * tick(660), wt(0, "шестьдесят"))
    for dl, f in ((0.0, 200), (0.3, 150)): add(0.45 * thud(f, 0.35, 12), wt(0, "Откроешь") - 0.1 + dl)
    add(0.35 * noise(0.5, 1500, 7000) * np.exp(-T_(0.5) * 7), ST[1] + wt(1, "вскрыл"))                              # рвётся бумага
    add(0.25 * noise(0.3, 1500, 6000) * np.exp(-T_(0.3) * 9), ST[1] + wt(1, "Почерк") - 0.3)
    td = ST[1] + wt(1, "Его деду") - 0.15
    ws = noise(0.5, 400, 5000) * np.sin(np.pi * T_(0.5) / 0.5) ** 2; add(0.3 * ws, td - 0.25); add(0.7 * thud(44, 1.1, 3.5), td)
    for j in range(8): add(0.3 * thud(120, 0.15, 25) + 0.1 * noise(0.15, 800, 3000)[: int(0.15 * SR)] * np.exp(-T_(0.15) * 20), td + 0.5 + j * 0.7)   # лопата
    for sub in ("Артём", "Если", "Иди", "Сорок"):
        for j in range(8): add(0.09 * tick(1900 + 60 * (j % 3)), ST[2] + wt(2, sub) + j * 0.08)                     # перо
    t_ = T_(1.8); add(0.25 * np.sin(2 * np.pi * np.cumsum(70 + 60 * t_ / 1.8) / SR) * np.clip(t_ / 1.2, 0, 1) ** 2 * np.clip((1.8 - t_) / 0.2, 0, 1), ST[2] + wt(2, "Иди на север"))
    add(0.7 * thud(46, 1.0, 4), ST[2] + wt(2, "Там") - 0.2); add(0.2 * tick(880), ST[2] + wt(2, "Там") - 0.2)
    for j in range(8): add(0.09 * tick(1900 + 60 * (j % 3)), ST[3] + wt(3, "Вершинин") + j * 0.07)
    add(0.7 * thud(44, 1.1, 3.5), ST[3] + wt(3, "Нина побледнела")); add(0.5 * thud(60, 0.6, 6), ST[3] + wt(3, "Это почерк"))
    for j in range(10): add((0.14 - 0.01 * j) * noise(0.12, 300, 1800) * np.exp(-T_(0.12) * 22), ST[4] + 0.3 + j * 0.3)   # шаги уходят
    add(0.8 * thud(40, 1.2, 3.5), ST[4] + wt(4, "На север"))
    for f in (392, 466, 587): add(0.07 * np.sin(2 * np.pi * f * T_(1.6)) * np.exp(-T_(1.6) * 2.2), ST[5] + wt(5, "Пиши") - 0.1)
    add(0.2 * tick(1320), ST[5] + wt(5, "Пиши") - 0.1)
    return music

import render as _me
SH = Show(_me) if __name__ != "__main__" else None
if __name__ == "__main__":
    import render as ep
    SH = ep.SH; ep.SH.run("posle-3")
