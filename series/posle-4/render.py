"""«После», серия 4 «Сигнал» (сезон 2, 3D). Запуск: LIBGL_ALWAYS_SOFTWARE=1 xvfb-run -a python3 render.py [preview | sheet N K | at N T]"""
import math, os, random, sys
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(D, "..", "engine3d")); sys.path.insert(0, D)
import numpy as np
from village import *
from show import *
from script import SCENES, CAPTION_NUMS

LEADS = [0.3] * 6
TAILS = [0.6, 0.7, 0.7, 0.8, 1.3, 2.8]
KEY = {"еды", "9", "всё", "уйдёшь", "останешься", "40", "никто", "дед", "один", "вернулся", "дойдёт", "трое", "кекс", "3", "свет", "коротких", "длинных", "помощь", "ловушку", "комментариях"}
ROAD_ENV = dict(shadow_center=(0, 0, 6), shadow_size=16)
IN_ENV = dict(sun_col=(0, 0, 0), amb_top=(0.16, 0.15, 0.14), amb_bot=(0.08, 0.07, 0.07), fog=0.0, fog_col=(0.01, 0.01, 0.012),
              sky=((0.01, 0.01, 0.012),) * 3, shadow_center=(0, 0, 0), shadow_size=20)
NIGHT = dict(sun_dir=(0.4, -0.7, -0.5), sun_col=(0.16, 0.2, 0.34), amb_top=(0.05, 0.07, 0.15), amb_bot=(0.02, 0.03, 0.06), fog=0.014, fog_col=(0.025, 0.035, 0.08),
             sky=((0.004, 0.008, 0.03), (0.03, 0.045, 0.1), (0.025, 0.035, 0.08)), shadow_center=(0, 0, 0), shadow_size=24)
LAMP = (1.9, 1.4, 0.85)
IN_LIGHTS = [((0, 3.0, z), LAMP, 10.5) for z in (-8, -2, 4)] + [((3.5, 2.2, 2.5), (0.9, 0.7, 0.45), 9.0)]

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
FIELD = [box(T(0, -0.25, -20) @ S(240, 0.5, 240), C["snow"])] + forest(2, -75, 9, 3.6, 60) + tracks(9, -62)

def shelter(n_crates=18):
    """Убежище изнутри: нары слева, полки с ящиками справа, три лампы."""
    CON = rgb((104, 106, 112)); CON_D = rgb((80, 82, 90)); WD = rgb((112, 84, 60))
    it = [box(T(0, -0.1, -2) @ S(14, 0.2, 24), CON_D, cast=False), box(T(0, 3.5, -2) @ S(14, 0.2, 24), CON_D, cast=False),
          box(T(-7.1, 1.7, -2) @ S(0.2, 3.6, 24), CON, cast=False), box(T(7.1, 1.7, -2) @ S(0.2, 3.6, 24), CON, cast=False), box(T(0, 1.7, -14.1) @ S(14, 3.6, 0.2), CON, cast=False)]
    it.append(box(T(0, 1.4, -13.95) @ S(2.0, 2.8, 0.12), rgb((70, 76, 86)), cast=False)); it.append(cyl(T(0, 1.5, -13.85) @ Rx(PI / 2) @ S(0.6, 0.08, 0.6), rgb((120, 60, 50)), cast=False))
    for z in (-8, -2, 4):
        it.append(cyl(T(0, 3.25, z) @ S(0.5, 0.1, 0.5), C["dark"], cast=False)); it.append(ball(T(0, 3.1, z) @ S(0.3), rgb((255, 220, 160)), emit=4.0, cast=False))
    for k in range(6):                                                          # нары
        z = -12 + k * 2.6
        for y in (0.5, 1.7):
            it.append(box(T(-5.9, y, z) @ S(2.0, 0.12, 2.2), WD)); it.append(box(T(-5.9, y + 0.12, z) @ S(1.9, 0.14, 2.1), rgb((120, 124, 110))))
            it.append(box(T(-5.9, y + 0.24, z - 0.8) @ S(1.4, 0.14, 0.45), rgb((200, 200, 190))))
        for dx in (-0.95, 0.95):
            for dz in (-1.05, 1.05): it.append(box(T(-5.9 + dx, 1.1, z + dz) @ S(0.1, 2.2, 0.1), WD))
    for y in (0.5, 1.3, 2.1): it.append(box(T(6.3, y, -3) @ S(1.3, 0.08, 13), WD))   # полки
    for z in (-9.5, -6.2, -3, 0.2, 3.5):
        it.append(box(T(6.3, 1.2, z) @ S(1.3, 2.4, 0.1), WD))
    cols = [rgb((150, 116, 80)), rgb((96, 110, 84)), rgb((130, 100, 76))]
    for j in range(n_crates):
        r, c = j % 3, j // 3
        it.append(box(T(6.3, 0.84 + r * 0.8, 2.6 - c * 1.9) @ Ry(0.1 * math.sin(j * 3)) @ S(0.9, 0.56, 1.1), cols[j % 3]))
    return it

def blink(sh, t):
    """SOS: (включён ли свет, сколько вспышек из 9 уже началось)."""
    tx = sh.ep.SCENES[4]["text"]; st = sh.ALN[4]["character_start_times_seconds"]
    a = st[tx.find("Три коротких")] + 0.3; b = st[tx.find("Три длинных")] + 0.3; c = st[tx.rfind("Три коротких")] + 0.3
    fl = [(a + j * 0.3, 0.13) for j in range(3)] + [(b + j * 0.45, 0.32) for j in range(3)] + [(c + j * 0.3, 0.13) for j in range(3)]
    return any(t0 <= t < t0 + d_ for t0, d_ in fl), sum(1 for t0, _ in fl if t >= t0), fl

def night(t, on):
    it = list(FIELD); o = {}
    p, _ = artyom(T(-0.5, 0, 6.6) @ Ry(PI), t, blink_seed=0.7, lamp=True, look=0.15 * math.sin(t * 0.9)); it += p
    it += cat2(T(-1.6, 0, 7.2) @ Ry(PI), t, look=0.3 * math.sin(t * 1.4))
    p, _ = kolyan(T(1.0, 0, 6.2) @ Ry(PI), t, blink_seed=0.2); it += p
    SRC = (1.5, 3.0, -58)
    gl = [(SRC, (255, 235, 190), 330, 1.0), (SRC, (255, 250, 230), 90, 1.3)] if on else []
    if on: it.append(ball(T(*SRC) @ S(1.6), rgb((255, 240, 200)), emit=30.0, cast=False))
    return it, gl

def scene_3d(si, t):
    wt = SH.wt
    if si == 0:                                                                 # запасы тают
        t9 = wt(0, "девять")
        n = int(round(lerp(18, 5, ease((t - 0.3) / (t9 - 0.1)))))
        it = shelter(n)
        p, _ = artyom(T(3.6, 0, -0.6) @ Ry(PI / 2 - 0.3), t, blink_seed=0.7, look=0.3 * math.sin(t * 1.1), mouth="o" if t > t9 else None); it += p
        it += cat2(T(3.2, 0, 0.9) @ Ry(PI / 2), t, look=0.4 * math.sin(t * 1.5))
        k = ease(t / SH.DUR[0])
        return dict(items=it, eye=(lerp(-1.6, -0.6, k), 1.9, lerp(5.2, 4.4, k)), tgt=(6.0, 1.45, -1.6), fov=44, lights=IN_LIGHTS, env=IN_ENV, snow=False)
    if si == 1:                                                                 # Кирилл считает
        it = shelter(5); tn = wt(1, "никто")
        p, _ = kirill(T(3.6, 0, -1.2) @ Ry(-PI / 4), t, arm="up" if t > tn else None, blink_seed=0.4, look=0.2 * math.sin(t)); it += p
        for j, (x, z) in enumerate(((0.2, -3.6), (1.4, -4.6), (-1.0, -4.4), (2.6, -5.4), (-2.2, -3.2), (0.4, -5.8))):
            p, _ = villager(j + 2, T(x, 0, z) @ Ry(0.5), t, blink_seed=j * 0.4, look=0.3 * math.sin(t + j)); it += p
        k = ease(t / SH.DUR[1])
        return dict(items=it, eye=(lerp(-0.6, 0.2, k), 1.9, lerp(4.4, 3.4, k)), tgt=(3.2, 1.75, -1.6), fov=44, lights=IN_LIGHTS, env=IN_ENV, snow=False)
    if si == 2:
        t0, t1 = wt(2, "Дед") - 0.15, wt(2, "Внук") - 0.15
        if t0 <= t < t1:                                                        # 1962: дед уходит на север
            tt_ = t - t0; it = list(FIELD)
            p, _ = ded(T(0.2, 0, 5.0 - 1.4 * tt_) @ Ry(PI), t, walk=tt_ * 6.0); it += p
            return dict(items=it, eye=(1.2, 2.6, 10.5), tgt=(0, 1.3, -20), fov=44, sepia=1.0, env=dict(shadow_center=(0, 0, 0), shadow_size=24))
        it = [x for x in shelter(5) if not (x[0] != "cube" and x[1][1, 3] > 3.0 and x[1][2, 3] > -3)]   # без ближних ламп: лезла на заголовок
        p, _ = granny(T(-1.0, 0, 0.0), t, blink_seed=1.9, look=0.15 * math.sin(t), mouth="smile" if t >= t1 else None); it += p
        p, _ = nina(T(-2.8, 0, -1.6) @ Ry(0.5), t, blink_seed=2.2, look=0.4); it += p
        p, _ = sonya(T(0.6, 0, -1.2) @ Ry(-0.4), t, blink_seed=0.9, look=-0.4); it += p
        p, _ = artyom(T(1.9, 0, -2.0) @ Ry(-0.5), t, blink_seed=0.7, look=-0.4); it += p
        k = ease(t / SH.DUR[2])
        return dict(items=it, eye=(-1.0, 1.75, lerp(3.9, 3.3, k)), tgt=(-1.0, 1.5, 0), fov=52, lights=IN_LIGHTS, env=IN_ENV, snow=False)
    if si == 3:                                                                 # трое и кот
        it = world(t, 1.9)
        ts = [wt(3, "Артём"), wt(3, "Колян"), wt(3, "гость"), wt(3, "Кекс")]
        def hop(t0): return 0.18 * math.sin(clamp((t - t0) / 0.3) * PI) if t > t0 else 0
        p, _ = artyom(T(0, hop(ts[0]), 6.5), t, blink_seed=0.7); it += p
        p, _ = kolyan(T(0.98, hop(ts[1]), 6.4) @ Ry(-0.1), t, blink_seed=0.2, mouth="smile"); it += p
        p, _ = guest(T(-0.98, hop(ts[2]), 6.4) @ Ry(0.1), t, blink_seed=1.1); it += p
        it += cat2(T(0.55, hop(ts[3]) * 1.5, 7.7), t, look=0.3 * math.sin(t * 1.3))
        k = ease(t / SH.DUR[3])
        return dict(items=it, eye=(0, 2.0, lerp(15.8, 15.0, k)), tgt=(0, 1.98, 6.5), fov=40, env=ROAD_ENV)
    on = blink(SH, t)[0] if si == 4 else (t % 1.2) < 0.14
    it, gl = night(t, on)
    k = ease(t / SH.DUR[si]) if si == 4 else 1.0
    hl = (np.array([-0.5, 2.16, 6.26]),)
    return dict(items=it, eye=(0.2, lerp(3.4, 3.1, k), lerp(13.6, 12.8, k)), tgt=(0.4, 1.4, -20), fov=44, glows=gl, env=NIGHT,
                lights=[((-0.5, 2.1, 5.6), (1.0, 0.9, 0.7), 5.0)] + ([((1.5, 3.0, -50), (1.0, 0.9, 0.7), 60.0)] if on else []))

def panel(d, x0, y0, x1, y1, k=1.0): d.rounded_rectangle([x0, y0, x1, y1], radius=28, fill=PANEL + (int(215 * k),))

def overlay(sh, si, t, d):
    wt = sh.wt
    old = si == 2 and wt(2, "Дед") - 0.15 <= t < wt(2, "Внук") - 0.15
    stroke_text(d, (W / 2, 250), "ПОСЛЕ УЛЬТИМАТУМА", font(60), WHITE, 6)
    stroke_text(d, (W / 2, 350), "ГОД 1962" if old else ("НОЧЬ 31" if si >= 4 else "ДЕНЬ 31"), font(122), YEL, 9)
    def tiles(tq, a, b, y=1340):
        for j, (x, lab, c, dl) in enumerate(((290, a, GREEN, 0.0), (790, b, RED, 0.3))):
            k = ease((t - tq - dl) / 0.25)
            if k <= 0: continue
            A = int(255 * k); yy = y + 30 * (1 - k)
            d.rounded_rectangle([x - 225, yy, x + 225, yy + 170], radius=36, fill=PANEL + (int(230 * k),), outline=c + (A,), width=6)
            d.text((x, yy + 85), lab, font=font(52), fill=c + (A,), anchor="mm")
    if si == 0:
        t9 = wt(0, "девять"); n = int(round(lerp(40, 9, ease((t - 0.3) / (t9 - 0.1)))))
        panel(d, 60, 450, 500, 690)
        d.text((280, 500), "ЕДЫ ОСТАЛОСЬ НА", font=font(36), fill=(190, 196, 214), anchor="mm")
        d.text((280, 600), f"{n} ДНЕЙ", font=font(76), fill=RED if n == 9 else WHITE, anchor="mm")
        tiles(wt(0, "Ты уйдёшь") - 0.05, "УЙТИ?", "ОСТАТЬСЯ?")
    if si == 1:
        panel(d, 60, 450, 560, 690)
        a = t > wt(1, "Сорок"); b = t > wt(1, "Девять")
        d.text((310, 500), "ЗАПАСЫ", font=font(36), fill=(190, 196, 214), anchor="mm")
        if a: d.text((310, 565), "40 ЧЕЛОВЕК", font=font(56), fill=WHITE, anchor="mm")
        if b: d.text((310, 640), "9 ДНЕЙ", font=font(64), fill=RED, anchor="mm")
    if old:
        panel(d, 60, 450, 600, 620)
        d.text((330, 500), "ДЕД ХОДИЛ НА СЕВЕР", font=font(36), fill=(190, 196, 214), anchor="mm")
        d.text((330, 565), "И ВЕРНУЛСЯ", font=font(56), fill=YEL, anchor="mm")
    if si == 3:
        sp = scene_3d(3, t)
        for (name, t0, pt) in (("АРТЁМ", wt(3, "Артём"), (0, 2.75, 6.5)), ("КОЛЯН", wt(3, "Колян"), (0.98, 2.75, 6.4)), ("ГОСТЬ", wt(3, "гость"), (-0.98, 2.75, 6.4)), ("КЕКС", wt(3, "Кекс"), (0.55, 1.0, 7.7))):
            k = ease((t - t0) / 0.2)
            if k <= 0: continue
            x, y, _ = project(pt, sp["eye"], sp["tgt"], sp["fov"]); A = int(255 * k); w_ = d.textlength(name, font=font(40)) / 2 + 22
            d.rounded_rectangle([x - w_, y - 34 - 10 * (1 - k), x + w_, y + 30 - 10 * (1 - k)], radius=18, fill=PANEL + (int(225 * k),), outline=YEL + (A,), width=4)
            d.text((x, y - 2 - 10 * (1 - k)), name, font=font(40), fill=YEL + (A,), anchor="mm")
        tw = wt(3, "Остальные")
        if t > tw:
            k = ease((t - tw) / 0.25); panel(d, 60, 450, 520, 690, k); A = int(255 * k)
            d.text((290, 500), "ОСТАЛЬНЫЕ ЖДУТ", font=font(36), fill=(190, 196, 214, A), anchor="mm")
            d.text((290, 600), "3 ДНЯ", font=font(100), fill=YEL + (A,), anchor="mm")
    if si >= 4:
        n = blink(sh, t)[1] if si == 4 else 9
        if n or si == 5:
            panel(d, 150, 460, 930, 640)
            sym = "···———···"; x = 215
            for j, ch in enumerate(sym):
                col = YEL if j < n else (70, 76, 96)
                if ch == "·": d.ellipse([x, 530, x + 34, 564], fill=col); x += 54
                else: d.rounded_rectangle([x, 532, x + 70, 562], radius=12, fill=col); x += 94
                if j in (2, 5): x += 26
            if n == 9 and (si == 5 or t > blink(sh, t)[2][-1][0] + 0.5):
                stroke_text(d, (W / 2, 740), "S O S", font(110), RED, 9)
    if si == 5:
        sh.cta(d, t, wt(5, "Пиши") - 0.1, "ПОМОЩЬ", "ЛОВУШКА")
        te = sh.DUR[5] - 1.7
        if t > te: stroke_text(d, (W / 2, 1650), "СЕРИЯ 5 — СКОРО", font(50), WHITE + (int(255 * ease((t - te) / 0.3)),), 6)

def sound(sh, add, SR, n, tt):
    wt = sh.wt; ST = sh.STARTS; TOTAL = sh.TOTAL; rnd = np.random.default_rng(8)
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
    inside = ((tt < ST[3]) & ~((tt > ST[2] + wt(2, "Дед")) & (tt < ST[2] + wt(2, "Внук")))).astype(float)
    hum = 0.5 * np.sin(2 * np.pi * 100 * tt) + 0.3 * np.sin(2 * np.pi * 150 * tt)
    music = (0.08 * wind * (1 - 0.8 * inside) + 0.03 * hum * inside + 0.1 * drone + 0.22 * beat * (tt < ST[4])) * env
    add(0.8 * thud(42, 0.9, 4), 0.0)
    t9 = wt(0, "девять")
    for j in range(13): add(0.12 * tick(900 - 25 * j), 0.3 + j * (t9 - 0.2) / 13)                                  # ящики исчезают
    add(0.4 * buzz(), t9 + 0.1); add(0.6 * thud(46, 0.9, 5), wt(0, "Потом"))
    for dl, f in ((0.0, 200), (0.3, 150)): add(0.45 * thud(f, 0.35, 12), wt(0, "Ты уйдёшь") - 0.05 + dl)
    add(0.22 * tick(1100), ST[1] + wt(1, "Сорок")); add(0.35 * buzz(), ST[1] + wt(1, "Девять")); add(0.8 * thud(44, 1.0, 4), ST[1] + wt(1, "никто"))
    add(0.4 * thud(90, 0.3, 14), ST[2] + wt(2, "встала"))
    td = ST[2] + wt(2, "Дед") - 0.15; ws = noise(0.5, 400, 5000) * np.sin(np.pi * T_(0.5) / 0.5) ** 2; add(0.3 * ws, td - 0.25)
    for j in range(6): add(0.13 * noise(0.12, 300, 1800) * np.exp(-T_(0.12) * 22), td + 0.2 + j * 0.35)
    add(0.3 * ws, ST[2] + wt(2, "Внук") - 0.4); add(0.6 * thud(50, 0.9, 5), ST[2] + wt(2, "дойдёт"))
    for sub, f in (("Артём", 523), ("Колян", 587), ("гость", 659), ("Кекс", 784)): add(0.25 * tick(f * 2), ST[3] + wt(3, sub)); add(0.3 * thud(110, 0.2, 20), ST[3] + wt(3, sub))
    add(0.5 * thud(50, 0.8, 5), ST[3] + wt(3, "Остальные"))
    for t0, d_ in blink(sh, 0)[2]:                                                                                 # морзянка
        t_ = T_(d_ + 0.03); add(0.3 * np.sin(2 * np.pi * 740 * t_) * np.clip(t_ / 0.01, 0, 1) * np.clip((d_ + 0.03 - t_) / 0.02, 0, 1), ST[4] + t0)
    add(0.9 * thud(40, 1.3, 3.2), ST[4] + blink(sh, 0)[2][-1][0] + 0.55)
    k = 0.0
    while k < sh.DUR[5] - 0.3:
        t_ = T_(0.16); add(0.14 * np.sin(2 * np.pi * 740 * t_) * np.clip(t_ / 0.01, 0, 1) * np.clip((0.16 - t_) / 0.02, 0, 1), ST[5] + k); k += 1.2
    for f in (392, 466, 587): add(0.07 * np.sin(2 * np.pi * f * T_(1.6)) * np.exp(-T_(1.6) * 2.2), ST[5] + wt(5, "Пиши") - 0.1)
    add(0.2 * tick(1320), ST[5] + wt(5, "Пиши") - 0.1)
    return music

import render as _me
SH = Show(_me) if __name__ != "__main__" else None
if __name__ == "__main__":
    import render as ep
    SH = ep.SH; ep.SH.run("posle-4")
