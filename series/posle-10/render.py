"""«После», серия 10 «Домой» — финал сезона 2 (3D). Запуск: LIBGL_ALWAYS_SOFTWARE=1 xvfb-run -a python3 render.py [preview | sheet N K | at N T]"""
import math, os, random, sys
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(D, "..", "engine3d")); sys.path.insert(0, D)
import numpy as np
from village import *
from show import *
from script import SCENES, CAPTION_NUMS

LEADS = [0.3] * 6
TAILS = [0.6, 0.7, 0.9, 1.4, 1.6, 3.4]
KEY = {"месяц", "конца", "света", "наступил", "первым", "домой", "еда", "деревни", "ждали", "кекс", "руки", "свет", "окна", "тетрадь", "договорились", "люк", "засыпаю", "второй", "раз", "комментариях"}
PI = math.pi
DAY = dict(ENV, sun_dir=(-0.6, -0.5, -0.4), fog=0.011, shadow_center=(-8, 0, 6), shadow_size=24)
DUSK = dict(sun_dir=(-0.8, -0.25, -0.3), sun_col=(0.22, 0.18, 0.3), amb_top=(0.09, 0.1, 0.2), amb_bot=(0.04, 0.04, 0.08), fog=0.012, fog_col=(0.06, 0.06, 0.13),
            sky=((0.02, 0.03, 0.1), (0.16, 0.12, 0.24), (0.1, 0.08, 0.16)), hz=0.5, shadow_center=(-4, 0, 0), shadow_size=24)
NIGHT = dict(sun_dir=(0.4, -0.7, -0.5), sun_col=(0.12, 0.15, 0.27), amb_top=(0.05, 0.07, 0.15), amb_bot=(0.02, 0.03, 0.06), fog=0.012, fog_col=(0.025, 0.035, 0.08),
             sky=((0.004, 0.008, 0.03), (0.03, 0.045, 0.1), (0.025, 0.035, 0.08)), hz=0.5, shadow_center=(-2, 0, 2), shadow_size=20)
WARM = (1.0, 0.72, 0.42)
INK = (40, 44, 96); PAPER = (238, 230, 208); EDGE = (150, 138, 112)
FI = "/usr/share/fonts/truetype/freefont/FreeSerifBoldItalic.ttf"
_FI = {}
def hand(sz):
    if sz not in _FI: _FI[sz] = ImageFont.truetype(FI if os.path.exists(FI) else FB, sz)
    return _FI[sz]

OLIVE = rgb((92, 104, 70)); OLIVE_D = rgb((70, 80, 54)); CANVAS = rgb((112, 116, 86))
def truck(m, t, lights=True):
    it = [box(m @ T(0, 0.75, -0.2) @ S(2.4, 0.3, 7.4), C["dark"]),
          box(m @ T(0, 1.55, -2.7) @ S(2.3, 1.9, 1.5), OLIVE), box(m @ T(0, 1.0, -3.75) @ S(2.2, 0.9, 0.8), OLIVE_D),
          box(m @ T(0, 2.0, -3.46) @ S(2.0, 0.8, 0.04), rgb((30, 38, 50)), cast=False),
          box(m @ T(0, 2.1, 1.0) @ S(2.45, 2.6, 4.8), CANVAS), box(m @ T(0, 3.45, 1.0) @ S(2.5, 0.12, 4.9), C["snow"])]
    for z in (-2.9, 0.0, 2.3):
        for sx in (-1.15, 1.15): it.append(cyl(m @ T(sx, 0.5, z) @ Rz(PI / 2) @ S(1.0, 0.35, 1.0), C["dark"]))
    if lights:
        for sx in (-0.75, 0.75): it.append(ball(m @ T(sx, 1.05, -4.17) @ S(0.3, 0.3, 0.08), rgb((255, 244, 210)), emit=6.0, cast=False))
    it.append(box(m @ T(0, 2.2, 3.43) @ S(2.0, 1.4, 0.04), rgb((20, 22, 18)), cast=False))
    return it

HOUSES = [(T(-3.5, 0, -6), 0), (T(-13, 0, -7) @ Ry(0.15), 1), (T(5.5, 0, -11) @ Ry(-0.2), 2), (T(-24, 0, -10) @ Ry(0.3), 3), (T(27, 0, -10), 4)]
WIN = []
for m, seed in HOUSES:
    r = random.Random(seed); r.uniform(4.2, 5.4); d = r.uniform(3.2, 3.8)
    for x in (-1.2, 1.2): WIN.append(m @ T(x, 1.3, d / 2 + 0.035))
def windows(k):
    if k <= 0: return []
    return [box(m @ S(0.82, 0.92, 0.03), rgb((255, 196, 110)), emit=2.4 * k, cast=False) for m in WIN]
def win_pt(m, dz=0.0): return tuple((m @ np.array([0, 0, dz, 1], "f4"))[:3])
def win_lights(k): return [(win_pt(m, 1.2), WARM, 6.0 * k + 0.01) for m in WIN[:6]]
def win_glows(k): return [(win_pt(m), (255, 180, 90), 90, 0.7 * k) for m in WIN] if k > 0 else []
VILLAGE = world(0, 0.0)
FRONT = [x for x in VILLAGE if x[1][2, 3] < 10.5]                            # без ёлок, столбов и проводов перед камерой
TRUCK_ROT = Ry(-PI / 2)
def column_x(x0):
    it = []
    for j in range(5): it += truck(T(x0 - j * 9.5, 0, 6.5) @ TRUCK_ROT, 0)
    return it

FAM = [("БАБА ВАЛЯ", granny, (1.4, 0, 8.0), 1.9), ("НИНА", nina, (2.4, 0, 7.6), 2.2), ("КИРИЛЛ", kirill, (3.3, 0, 7.2), 0.4), ("СОНЯ", sonya, (0.5, 0, 8.3), 0.9)]
def family(t, face=-PI / 2, granny_hold=False, mood=None):
    it = []
    for name, fn, (x, y, z), bs in FAM:
        kw = dict(blink_seed=bs, mouth=mood)
        if fn is granny and granny_hold: kw["arm"] = "hold"
        p, _ = fn(T(x, y, z) @ Ry(face), t, **kw); it += p
    return it

def scene_3d(si, t):
    wt = SH.wt
    if si == 0:                                                                 # утро, колонна готова
        it = VILLAGE + column_x(-20)
        p, _ = artyom(T(-14.2, 0, 8.4) @ Ry(0.25), t, blink_seed=0.7, look=0.2 * math.sin(t)); it += p
        it += cat2(T(-13.2, 0, 8.9) @ Ry(0.2), t, look=0.3 * math.sin(t * 1.4))
        k = ease(t / SH.DUR[0])
        return dict(items=it, eye=(lerp(-12.4, -12.8, k), 2.1, lerp(13.6, 12.8, k)), tgt=(-14.6, 1.8, 7.6), fov=42, env=DAY)
    if si == 1:                                                                 # едут
        x0 = -40 + 6.0 * t
        it = FRONT + column_x(x0)
        return dict(items=it, eye=(x0 - 4, 3.0, 17.5), tgt=(x0 - 12, 1.5, 6.5), fov=50, env=dict(DAY, shadow_center=(x0 - 12, 0, 6)))
    if si == 2:                                                                 # встреча
        it = FRONT + column_x(-6)
        tk = wt(2, "Кекс прыгнул") - 0.1
        ka = ease(t / 1.6); ax = lerp(-4.0, -0.6, ka)
        p, _ = artyom(T(ax, 0, 8.0) @ Ry(PI / 2), t, walk=t * 6 if ka < 1 else None, blink_seed=0.7, mouth="smile" if ka >= 1 else None); it += p
        it += family(t, face=-PI / 2 + 0.7, granny_hold=t > tk, mood="smile" if t > wt(2, "Баба") else None)
        kc = clamp((t - tk) / 0.6)
        if t < tk: it += cat2(T(ax + 0.5, 0, 8.7) @ Ry(PI / 2), t)
        else:
            cx = lerp(-0.1, 1.55, kc); cy = lerp(0, 0.95, kc) + 0.9 * math.sin(kc * PI); cz = lerp(8.7, 8.45, kc)
            it += cat2(T(cx, cy, cz) @ Ry(PI) @ S(0.8), t)
        k = ease(t / SH.DUR[2])
        return dict(items=it, eye=(lerp(1.1, 1.4, k), 2.5, lerp(18.6, 17.6, k)), tgt=(1.5, 1.3, 8.0), fov=44, env=dict(DAY, shadow_center=(0, 0, 8), shadow_size=14))
    if si == 3:                                                                 # свет
        tl = wt(3, "зажёгся") + 0.1; kl = ease((t - tl) / 0.25)
        flick = 1.0 if t > tl + 0.25 else (0.6 if int(t * 20) % 2 else 0.2) * (t > tl)
        kl = kl * flick
        it = VILLAGE + windows(kl) + family(t, face=PI, mood="smile" if kl > 0.5 else None)
        p, _ = artyom(T(-0.6, 0, 8.0) @ Ry(PI), t, blink_seed=0.7); it += p
        k = ease(t / SH.DUR[3])
        return dict(items=it, eye=(lerp(1.0, 0.0, k), lerp(2.6, 3.2, k), lerp(15.5, 17.0, k)), tgt=(-2.0, 2.0, -6), fov=50, env=DUSK,
                    lights=win_lights(kl), glows=win_glows(kl))
    if si == 4:                                                                 # тетрадь у люка
        it = VILLAGE + windows(1.0); o = {}
        p, _ = artyom(T(0.4, 0, 3.0) @ Ry(-0.6), t, arm="phone", out=o, lamp=True, blink_seed=0.7, look=-0.1); it += p
        it.append(box(o["hand"] @ T(0, -0.14, 0.06) @ Rx(-0.5) @ S(0.34, 0.26, 0.04), rgb((120, 70, 50))))
        it += cat2(T(1.1, 0, 3.7) @ Ry(-0.4), t, look=0.3)
        k = ease(t / SH.DUR[4])
        return dict(items=it, eye=(lerp(-1.6, -1.3, k), 1.9, lerp(6.6, 6.0, k)), tgt=(0.9, 1.4, 1.8), fov=44, env=NIGHT,
                    lights=[((0.4, 2.2, 3.6), (1.0, 0.95, 0.8), 4.5)] + win_lights(1.0)[:4], glows=win_glows(1.0))
    it = FRONT + windows(1.0) + family(t, face=0, mood="smile")                   # 5: финал
    p, _ = artyom(T(-0.6, 0, 8.0), t, blink_seed=0.7, mouth="smile"); it += p
    p, _ = kolyan(T(-1.8, 0, 7.7), t, blink_seed=0.2, mouth="smile"); it += p
    it += cat2(T(0.2, 0, 8.9), t, look=0.3 * math.sin(t))
    k = ease(t / SH.DUR[5])
    return dict(items=it, eye=(0.6, lerp(2.5, 4.5, k), lerp(16.0, 20.0, k)), tgt=(0.4, lerp(1.6, 2.0, k), 2), fov=46, env=NIGHT,
                lights=[((0.6, 3.0, 11.0), WARM, 9.0)] + win_lights(1.0)[:6], glows=win_glows(1.0))

def panel(d, x0, y0, x1, y1, k=1.0): d.rounded_rectangle([x0, y0, x1, y1], radius=28, fill=PANEL + (int(215 * k),))


def overlay(sh, si, t, d):
    wt = sh.wt
    stroke_text(d, (W / 2, 250), "ПОСЛЕ УЛЬТИМАТУМА", font(60), WHITE, 6)
    stroke_text(d, (W / 2, 350), "ДЕНЬ 33", font(122), YEL, 9)
    def tiles(tq, a, b, ca=GREEN, cb=RED, y=1340):
        for j, (x, lab, c, dl) in enumerate(((290, a, ca, 0.0), (790, b, cb, 0.3))):
            k = ease((t - tq - dl) / 0.25)
            if k <= 0: continue
            A = int(255 * k); yy = y + 30 * (1 - k)
            d.rounded_rectangle([x - 225, yy, x + 225, yy + 170], radius=36, fill=PANEL + (int(230 * k),), outline=c + (A,), width=6)
            d.text((x, yy + 85), lab, font=font(54), fill=c + (A,), anchor="mm")
    if si == 0: tiles(wt(0, "Куда") - 0.05, "ДОМОЙ?", "В ГОРОД?", GREEN, (90, 150, 230))
    if si == 1:
        te = wt(1, "еда")
        if t > te - 0.1:
            k = ease((t - te + 0.1) / 0.25); A = int(255 * k); panel(d, 60, 450, 640, 690, k)
            d.text((100, 500), "ЕДА ДЛЯ ДЕРЕВНИ", font=font(36), fill=(190, 196, 214, A), anchor="lm")
            d.text((100, 600), "60 ЖИТЕЛЕЙ", font=font(70), fill=GREEN + (A,), anchor="lm")
    if si == 2:
        sp = scene_3d(2, t)
        subs = {"БАБА ВАЛЯ": "Баба", "НИНА": "Нина", "КИРИЛЛ": "Кирилл", "СОНЯ": "Соня"}
        for name, fn, (x, y, z), _ in FAM:
            t0 = wt(2, subs[name]); k = ease((t - t0) / 0.2)
            if k <= 0: continue
            h = {granny: 2.35, nina: 2.3, kirill: 2.65, sonya: 1.5}[fn]
            px, py, _ = project((x, h, z), sp["eye"], sp["tgt"], sp["fov"]); A = int(255 * k)
            f_ = font(34); w_ = d.textlength(name, font=f_) / 2 + 18
            d.rounded_rectangle([px - w_, py - 30 - 10 * (1 - k), px + w_, py + 26 - 10 * (1 - k)], radius=16, fill=PANEL + (int(225 * k),), outline=YEL + (A,), width=4)
            d.text((px, py - 2 - 10 * (1 - k)), name, font=f_, fill=YEL + (A,), anchor="mm")
    if si == 3:
        tl = wt(3, "зажёгся") + 0.1
        sh.checklist(d, t, [("СВЕТ", tl, True), ("ВСЕ ОКНА", wt(3, "Все окна") + 0.2, True)], y=450, w=440)
    if si == 4:
        k = ease((t - 0.2) / 0.3); A = int(255 * k); y0 = 440 + 60 * (1 - k); x0, x1, y1 = 100, 980, y0 + 560
        d.rounded_rectangle([x0 + 10, y0 + 14, x1 + 10, y1 + 14], radius=12, fill=(0, 0, 0, int(110 * k)))
        d.rounded_rectangle([x0, y0, x1, y1], radius=12, fill=PAPER + (A,), outline=EDGE + (A,), width=5)
        for j in range(7): d.line([(x0 + 40, y0 + 90 + j * 66), (x1 - 40, y0 + 90 + j * 66)], fill=(200, 190, 170, A), width=2)
        d.text((x0 + 50, y0 + 60), "28 октября 1962.", font=hand(46), fill=(140, 130, 150, A), anchor="lm")
        d.text((x0 + 50, y0 + 126), "Договорились. Больше не копаю.", font=hand(46), fill=(140, 130, 150, A), anchor="lm")
        d.text((x0 + 50, y0 + 192), "Но люк не засыпаю.", font=hand(46), fill=(140, 130, 150, A), anchor="lm")
        lines = [("День 33.", wt(4, "и написал") - 0.2), ("Договорились.", wt(4, "Договорились")), ("Но люк не засыпаю.", wt(4, "Но люк"))]
        for j, (s_, t0) in enumerate(lines):
            n = int(clamp((t - t0) / 0.8) * len(s_))
            if n: d.text((x0 + 50, y0 + 300 + j * 76), s_[:n], font=hand(62), fill=INK + (A,), anchor="lm")
        d.text((x1 - 40, y0 + 60), "А. Громов", font=hand(36), fill=(150, 140, 120, A), anchor="rm")
    if si == 5:
        sh.cta(d, t, wt(5, "Пиши") - 0.1, "ПОВЕРИЛ БЫ", "НЕТ")
        te = sh.DUR[5] - 2.0
        if t > te:
            k = ease((t - te) / 0.4)
            stroke_text(d, (W / 2, 1660), "КОНЕЦ 2 СЕЗОНА", font(64), YEL + (int(255 * k),), 7)

def sound(sh, add, SR, n, tt):
    wt = sh.wt; ST = sh.STARTS; TOTAL = sh.TOTAL; rnd = np.random.default_rng(20)
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
    happy = np.clip((tt - ST[3] - wt(3, "зажёгся")) / 1.0, 0, 1)
    music = (0.07 * wind + 0.08 * drone * (1 - 0.6 * happy) + 0.2 * beat * (1 - 0.85 * happy)) * env
    chord = np.zeros(n)
    for f in (196, 247, 294, 392):
        chord += np.sin(2 * np.pi * f * tt) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.25 * tt + f))
    music += 0.025 * chord * happy * env
    add(0.8 * thud(42, 0.9, 4), 0.0)
    for dl, f in ((0.0, 200), (0.3, 150)): add(0.45 * thud(f, 0.35, 12), wt(0, "Куда") - 0.05 + dl)
    eng = (np.sin(2 * np.pi * 34 * T_(sh.DUR[1])) + 0.5 * np.sin(2 * np.pi * 51 * T_(sh.DUR[1]))) * (0.6 + 0.4 * np.sin(2 * np.pi * 8 * T_(sh.DUR[1])))
    add(0.12 * eng * np.clip(T_(sh.DUR[1]) / 0.5, 0, 1) * np.clip((sh.DUR[1] - T_(sh.DUR[1])) / 0.6, 0, 1), ST[1])
    add(0.22 * tick(1320), ST[1] + wt(1, "еда"))
    for j in range(6): add(0.13 * noise(0.12, 300, 1800) * np.exp(-T_(0.12) * 22), ST[2] + j * 0.28)
    for sub, f in (("Баба", 523), ("Нина", 587), ("Кирилл", 659), ("Соня", 784)): add(0.2 * tick(f * 2), ST[2] + wt(2, sub))
    t_ = T_(0.4); add(0.15 * np.sin(2 * np.pi * np.cumsum(600 + 500 * t_ / 0.4) / SR) * np.exp(-t_ * 6), ST[2] + wt(2, "Кекс прыгнул"))     # «мяу»-свист
    add(0.4 * thud(110, 0.2, 18), ST[2] + wt(2, "Кекс прыгнул") + 0.5)
    tl = ST[3] + wt(3, "зажёгся") + 0.1
    for j in range(3): add(0.25 * noise(0.05, 2000, 8000), tl + j * 0.08)                                                          # щелчки
    t_ = T_(0.8); add(0.15 * np.sin(2 * np.pi * 100 * t_) * np.exp(-t_ * 2), tl)
    for f in (392, 494, 587, 784): add(0.08 * np.sin(2 * np.pi * f * T_(2.6)) * np.exp(-T_(2.6) * 1.2), tl + 0.25)
    for sub in ("и написал", "Договорились", "Но люк"):
        for j in range(9): add(0.08 * tick(1900 + 60 * (j % 3)), ST[4] + wt(4, sub) + j * 0.09)
    add(0.5 * thud(50, 0.8, 5), ST[4] + wt(4, "Но люк") + 0.9)
    for f in (392, 494, 587): add(0.07 * np.sin(2 * np.pi * f * T_(1.6)) * np.exp(-T_(1.6) * 2.2), ST[5] + wt(5, "Пиши") - 0.1)
    for f in (196, 294, 392, 494): add(0.07 * np.sin(2 * np.pi * f * T_(3.0)) * np.exp(-T_(3.0) * 0.9), ST[5] + sh.DUR[5] - 2.0)
    return music

import render as _me
SH = Show(_me) if __name__ != "__main__" else None
if __name__ == "__main__":
    import render as ep
    SH = ep.SH; ep.SH.run("posle-10")
