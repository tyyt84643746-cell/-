"""«Соседи сверху» — пробный хоррор-ролик (3D). Запуск: LIBGL_ALWAYS_SOFTWARE=1 xvfb-run -a python3 render.py [preview | sheet N K | at N T]"""
import math, os, random, sys
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(D, "..", "engine3d")); sys.path.insert(0, D)
import numpy as np
from models import *
from show import *
from script import SCENES, CAPTION_NUMS

PI = math.pi
LEADS = [0.3] * 9
TAILS = [0.7, 0.6, 0.7, 0.9, 0.6, 1.0, 0.8, 1.0, 3.2]
KEY = {"три", "шкаф", "год", "никто", "живёт", "пустует", "прописан", "пыль", "следа", "упало", "шаги", "свет", "смотрел", "голос", "стучит", "не", "стучал", "ласково", "перестанет",
       "слесарь", "полу", "царапины", "снизу", "твоей", "кровати", "над", "ним", "пора", "хрустнул", "дальше", "комментариях"}
NIGHT = dict(sun_dir=(0.3, -0.5, 0.8), sun_col=(0.14, 0.17, 0.32), amb_top=(0.09, 0.10, 0.17), amb_bot=(0.045, 0.045, 0.07), fog=0.02, fog_col=(0.01, 0.012, 0.025),
             sky=((0.004, 0.006, 0.02),) * 3, hz=0.5, shadow_center=(0, 2.5, 0), shadow_size=7)
ENV = NIGHT
DAY = dict(NIGHT, sun_col=(0.7, 0.66, 0.6), amb_top=(0.3, 0.3, 0.32), amb_bot=(0.16, 0.15, 0.15), fog_col=(0.5, 0.5, 0.55), sky=((0.4, 0.45, 0.55),) * 3)
WALL = rgb((150, 160, 150)); WALL2 = rgb((120, 108, 96)); FLOOR = rgb((110, 80, 58)); SLAB = rgb((90, 92, 98)); WHITE_ = rgb((226, 226, 220))
HERO = dict(body=rgb((96, 100, 112)), body_d=rgb((70, 74, 84)), hat=rgb((50, 40, 34)), hat_b=rgb((50, 40, 34)), legs=rgb((50, 54, 66)), pack=None)
GHOST = dict(body=rgb((26, 26, 30)), body_d=rgb((18, 18, 22)), hat=rgb((20, 20, 24)), hat_b=rgb((20, 20, 24)), legs=rgb((20, 20, 24)), pack=None, skin=rgb((60, 62, 66)))
OLD = dict(body=rgb((70, 90, 120)), body_d=rgb((50, 66, 90)), hat=rgb((150, 150, 150)), hat_b=rgb((150, 150, 150)), legs=rgb((50, 54, 66)), pack=None)
CEIL = 2.7; UP = 3.0

def house(crack=0.0, scratches=False):
    """Разрез дома: нижняя спальня (y 0..2.7) и пустая квартира сверху (y 3..5.7). Передней стены нет."""
    it = [box(T(0, -0.1, 0) @ S(6.4, 0.2, 6.4), FLOOR, cast=False), box(T(0, (CEIL + UP) / 2, 0) @ S(6.4, UP - CEIL, 6.4), SLAB),
          box(T(0, UP + 0.02, 0) @ S(6.2, 0.04, 6.2), rgb((96, 86, 76)), cast=False), box(T(0, 5.85, 0) @ S(6.4, 0.3, 6.4), SLAB)]
    for y0, col in ((0, WALL), (UP, WALL2)):
        it += [box(T(-3.1, y0 + 1.35, 0) @ S(0.2, 2.7, 6.4), col, cast=False), box(T(3.1, y0 + 1.35, 0) @ S(0.2, 2.7, 6.4), col, cast=False),
               box(T(0, y0 + 1.35, -3.1) @ S(6.4, 2.7, 0.2), col, cast=False)]
    it.append(box(T(-1.6, 1.6, -2.99) @ S(1.4, 1.2, 0.03), rgb((40, 60, 110)), emit=0.5, cast=False))            # окно внизу
    for p in ((-1.6, 1.6, -2.97), ): it += [box(T(*p) @ S(0.06, 1.2, 0.03), WHITE_, cast=False), box(T(*p) @ S(1.4, 0.06, 0.03), WHITE_, cast=False)]
    it += [box(T(1.2, 0.3, -0.4) @ S(2.6, 0.6, 1.6), rgb((110, 70, 50))), box(T(1.2, 0.68, -0.4) @ S(2.5, 0.18, 1.5), rgb((220, 220, 226))),
           box(T(2.3, 0.85, -0.4) @ S(0.4, 0.16, 1.0), WHITE_), box(T(2.55, 0.8, -0.4) @ S(0.1, 1.6, 1.6), rgb((110, 70, 50)))]
    it += [box(T(2.75, 0.3, -1.6) @ S(0.5, 0.6, 0.5), rgb((110, 70, 50)))]                                         # тумбочка
    for k in range(6): it.append(box(T(-2.95, 0.5, -0.8 + k * 0.16) @ S(0.08, 0.7, 0.1), rgb((180, 180, 176))))     # батарея
    it.append(box(T(-1.8, UP + 0.02, 1.2) @ S(1.6, 0.012, 1.6), rgb((140, 130, 118)), cast=False))                   # пыль сверху
    it += [box(T(0, 5.4, 0) @ S(0.02, 0.6, 0.02), C["dark"], cast=False)]
    if scratches:
        r = random.Random(3)
        for k in range(5):
            cx, cz, a = 1.2 + r.uniform(-0.7, 0.7), -0.4 + r.uniform(-0.6, 0.6), r.uniform(-0.6, 0.6)
            for q in range(3):
                it.append(box(T(cx, UP + 0.06, cz) @ Ry(a) @ T(0, 0, (q - 1) * 0.06) @ S(0.55, 0.008, 0.018), rgb((175, 155, 125)), cast=False))
    if crack > 0:
        r = random.Random(11); cx, cz = 1.9, -0.4
        for k in range(5):
            a = r.uniform(0, 2 * PI); x, z = cx, cz; w = 0.02
            for q in range(4):
                a += r.uniform(-0.7, 0.7); L = r.uniform(0.05, 0.12) * crack
                it.append(box(T(x + math.cos(a) * L / 2, CEIL - 0.005, z + math.sin(a) * L / 2) @ Ry(-a) @ S(L, 0.01, w), rgb((14, 12, 10)), cast=False))
                x += math.cos(a) * L; z += math.sin(a) * L; w *= 0.75
    return it

def wardrobe(x, shake=0.0):
    m = T(x, UP, -1.5) @ T(shake, 0, 0)
    return [box(m @ T(0, 1.1, 0) @ S(1.1, 2.2, 0.7), rgb((70, 50, 36))), box(m @ T(0, 1.1, 0.36) @ S(0.02, 2.0, 0.02), rgb((40, 28, 20)), cast=False)]

def hero_lying(t, mood=None, look=0.0):
    root = T(-0.05, 0.98, -0.25) @ Rz(-PI / 2)
    p, _ = person(root, t, colors=HERO, hat="hair", blink_seed=0.7, mouth=mood, look=look)
    return p + [box(T(0.75, 0.88, -0.38) @ S(1.6, 0.22, 1.3), rgb((70, 90, 130)))]                                  # одеяло
def ghosts(t, xs=(-1.2, -0.3), walk=False):
    it = []
    for j, x in enumerate(xs):
        p, _ = person(T(x, UP, 0.6) @ Ry(0.3 - 0.6 * j), t, colors=GHOST, hat="hair" if j == 0 else "bun", face=False, scale=1.0 - 0.06 * j, walk=t * 3 + j if walk else None); it += p
    return it

def landing():
    """Лестничная площадка верхнего этажа: дверь, вздутые обои, пыль у порога."""
    it = [box(T(30, -0.1, 0) @ S(6, 0.2, 6), rgb((96, 92, 86)), cast=False), box(T(30, 1.5, -2.1) @ S(6, 3, 0.2), rgb((120, 130, 110)), cast=False),
          box(T(27.1, 1.5, 0) @ S(0.2, 3, 6), rgb((110, 118, 100)), cast=False), box(T(30, 3.05, 0) @ S(6, 0.1, 6), rgb((90, 90, 90)), cast=False)]
    it += [box(T(30, 1.05, -1.98) @ S(1.0, 2.1, 0.06), rgb((60, 44, 36))), box(T(30.36, 1.0, -1.93) @ S(0.05, 0.05, 0.04), rgb((150, 140, 90)))]
    it.append(box(T(30.35, 1.2, -1.94) @ S(0.03, 0.06, 0.02), rgb((5, 5, 5)), cast=False))                          # скважина
    for (x, y, w, h) in ((28.4, 1.9, 0.7, 0.5), (31.4, 1.2, 0.5, 0.8), (28.0, 0.8, 0.4, 0.4)):
        it.append(ball(T(x, y, -1.98) @ S(w, h, 0.08), rgb((140, 150, 126)), cast=False))
    it.append(box(T(30, 0.008, -1.6) @ S(1.4, 0.012, 0.7), rgb((150, 146, 138)), cast=False))
    it += [box(T(31.0, 1.55, -1.97) @ S(0.16, 0.16, 0.04), rgb((70, 70, 70))), box(T(31.0, 1.55, -1.94) @ S(0.03, 0.03, 0.06), rgb((160, 60, 50)))]   # вырванный звонок
    it.append(ball(T(30, 2.85, -0.5) @ S(0.25), rgb((255, 230, 170)), emit=1.5, cast=False))
    return it
KEYHOLE = (30.35, 1.2, -1.92)
LAND = landing()

def scene_3d(si, t):
    wt = SH.wt
    L_lamp = [((2.75, 1.0, -1.6), (0.6, 0.45, 0.3), 3.0)]
    if si == 0:                                                                 # разрез дома, шкаф едет
        x = -1.0 + 0.6 * math.sin(t * 0.9); sh_ = 0.03 * math.sin(t * 30)
        it = house() + wardrobe(x, sh_) + hero_lying(t, look=-0.5 * math.sin(t * 0.7))
        k = ease(t / SH.DUR[0])
        return dict(items=it, eye=(lerp(0.4, 0.3, k), lerp(3.2, 3.0, k), lerp(9.6, 8.6, k)), tgt=(0.2, 2.7, 0), fov=50, env=NIGHT, snow=False,
                    lights=[((0, 5.2, 0.5), (0.18, 0.2, 0.35), 6.0)] + L_lamp)
    if si == 1:                                                                 # документ
        it = house() + wardrobe(-2.0) + hero_lying(t)
        k = ease(t / SH.DUR[1])
        return dict(items=it, eye=(lerp(-0.4, 0.4, k), 4.6, 8.0), tgt=(0, 4.3, -1), fov=46, env=NIGHT, snow=False, lights=[((0, 5.2, 0.5), (0.18, 0.2, 0.35), 6.0)])
    if si in (2, 3):                                                            # площадка и дверь
        p, _ = person(T(30.3, 0, 0.3 if si == 2 else -0.9) @ Ry(PI), t, colors=HERO, hat="hair", blink_seed=0.7, mouth="o" if si == 3 else None)
        it = LAND + p
        tf = wt(2, "А за дверью") if si == 2 else 0
        gl = []
        if si == 3:
            on = wt(3, "мелькнул") < t < wt(3, "мелькнул") + 1.4
            if on: gl = [(KEYHOLE, (255, 240, 200), 160, 1.0), (KEYHOLE, (255, 255, 240), 40, 1.0)]
            k = ease(t / 1.0)
            return dict(items=it, eye=(lerp(31.2, 30.8, k), 1.3, lerp(-0.6, -1.0, k)), tgt=(30.35, 1.25, -1.94), fov=lerp(40, 22, k), env=NIGHT, snow=False, glows=gl,
                        lights=[((30, 2.8, -0.5), (0.9, 0.8, 0.6), 6.0)])
        k = ease(t / SH.DUR[2]); shake = 0.02 * math.sin(t * 40) if t > tf else 0
        return dict(items=it, eye=(lerp(32.4, 31.8, k), 1.6, lerp(2.6, 2.0, k)) if t < tf else (31.6 + shake, 1.4, 1.4), tgt=(30.0, 1.0, -1.8), fov=50, env=NIGHT, snow=False,
                    lights=[((30, 2.8, -0.5), (0.9, 0.8, 0.6), 6.0)])
    if si in (4, 5):                                                            # голоса наверху
        it = house() + wardrobe(-2.0) + hero_lying(t, mood="o", look=0.3) + ghosts(t)
        k = ease(t / SH.DUR[si])
        if si == 4: eye, tgt = (lerp(0.6, 0.3, k), lerp(2.2, 2.5, k), lerp(8.8, 8.0, k)), (0.4, 2.4, -0.3)
        else: eye, tgt = (lerp(-0.3, -0.6, k), 4.4, lerp(6.4, 5.6, k)), (-0.8, 4.4, 0.4)
        return dict(items=it, eye=eye, tgt=tgt, fov=46, env=NIGHT, snow=False, lights=[((-0.8, 5.0, 1.5), (0.15, 0.18, 0.32), 5.0)] + L_lamp)
    if si == 6:                                                                 # слесарь, царапины
        tsc = wt(6, "А в полу")
        if t < tsc:
            o = {}
            p, _ = person(T(-1.5, 0, 1.0) @ Ry(0.4), t, colors=HERO, hat="hair", arm="phone", out=o, blink_seed=0.7); it = house() + p
            it += [box(o["hand"] @ T(0, -0.16, 0.06) @ S(0.16, 0.3, 0.03), C["dark"])]
            k = ease(t / tsc)
            return dict(items=it, eye=(lerp(-0.6, -0.8, k), 1.8, lerp(5.0, 4.4, k)), tgt=(-1.4, 1.7, 0.8), fov=44, env=DAY, snow=False)
        it = house(scratches=True) + wardrobe(-2.0)
        kk = ease((t - tsc) / 2.5)
        return dict(items=it, eye=(lerp(1.3, 1.2, kk), lerp(4.9, 4.4, kk), lerp(1.6, 0.9, kk)), tgt=(1.2, UP, -0.4), fov=50, env=NIGHT, snow=False,
                    lights=[((1.2, 4.6, 0.4), (0.9, 0.9, 1.1), 5.0)])
    if si == 7:                                                                 # шкаф едет к кровати
        tm = wt(7, "Ну вот") - 0.2
        x = lerp(-2.0, 1.9, ease(t / max(0.1, tm)) ); sh_ = 0.04 * math.sin(t * 34) if t < tm else 0
        it = house() + wardrobe(x, sh_) + hero_lying(t, mood="o", look=0.5) + ghosts(t, xs=(lerp(-1.2, 1.0, ease(t / max(0.1, tm))), lerp(-0.3, 2.2, ease(t / max(0.1, tm)))), walk=t < tm)
        k = ease(t / SH.DUR[7])
        return dict(items=it, eye=(lerp(0.2, 0.9, k), lerp(3.0, 2.9, k), lerp(10.0, 8.4, k)), tgt=(lerp(0.2, 1.3, k), 2.6, -0.2), fov=46, env=NIGHT, snow=False,
                    lights=[((0, 5.2, 0.5), (0.18, 0.2, 0.35), 6.0)] + L_lamp)
    tc = wt(8, "хрустнул"); kc = ease((t - tc + 0.2) / 0.8)                      # 8: трещина над лицом
    it = house(crack=kc) + wardrobe(1.9) + hero_lying(t, mood="o", look=0.0)
    r = random.Random(1)
    for j in range(6):
        tt_ = t - tc - j * 0.15
        if tt_ > 0: it.append(box(T(1.9 + r.uniform(-0.15, 0.15), max(1.0, CEIL - 4.9 * tt_ * tt_), -0.4 + r.uniform(-0.15, 0.15)) @ S(0.035), rgb((220, 216, 206))))
    sh_ = 0.02 * math.sin(t * 50) if t > tc else 0
    k = ease(t / 2.0)
    return dict(items=it, eye=(1.9 + sh_, lerp(1.6, 1.25, k), lerp(1.4, 0.6, k)), tgt=(1.9, CEIL, -0.4), fov=lerp(58, 52, k), env=NIGHT, snow=False,
                lights=[((2.3, 1.3, 0.4), (0.5, 0.4, 0.3), 4.0)])

def panel(d, x0, y0, x1, y1, k=1.0): d.rounded_rectangle([x0, y0, x1, y1], radius=28, fill=PANEL + (int(215 * k),))
FI = "/usr/share/fonts/truetype/freefont/FreeSerifBoldItalic.ttf"
_FI = {}
def hand(sz):
    if sz not in _FI: _FI[sz] = ImageFont.truetype(FI if os.path.exists(FI) else FB, sz)
    return _FI[sz]
def quote(d, t, t0, text, who, y=520, col=(255, 255, 255)):
    k = ease((t - t0) / 0.3)
    if k <= 0: return
    A = int(255 * k); n = int(clamp((t - t0) / (0.06 * len(text))) * len(text))
    d.rounded_rectangle([90, y, 990, y + 230], radius=30, fill=(6, 6, 10, int(225 * k)), outline=(150, 40, 40, A), width=4)
    d.text((140, y + 50), who, font=font(32), fill=(170, 170, 180, A), anchor="lm")
    ws = text.split(" "); lines = [""]
    for w in ws:
        if d.textlength((lines[-1] + " " + w).strip(), font=hand(64)) > 800: lines.append(w)
        else: lines[-1] = (lines[-1] + " " + w).strip()
    left = n
    for j, ln in enumerate(lines):
        part = ln[:max(0, left)]; left -= len(ln) + 1
        if part: d.text((140, y + 115 + j * 72), part, font=hand(64), fill=col + (A,), anchor="lm")

def clock(sh, si, t):
    if si == 6 and t < sh.wt(6, "А в полу"): return "09:12"
    if si == 1: return "11:30"
    if si in (2, 3): return "21:40"
    gt = sh.STARTS[si] + t
    return "03:00" if si < 7 else "03:0" + str(min(3, int((gt - sh.STARTS[7]) / 4)))

def overlay(sh, si, t, d):
    wt = sh.wt
    stroke_text(d, (W / 2, 250), "СОСЕДИ СВЕРХУ", font(64), WHITE, 6)
    blink = si in (0, 7, 8) and int(t * 2) % 2 == 0
    stroke_text(d, (W / 2, 355), clock(sh, si, t), font(118), RED if not blink else (140, 40, 40), 9)
    if si == 0:
        tw = wt(0, "Только")
        if t > tw:
            k = ease((t - tw) / 0.25); A = int(255 * k); panel(d, 60, 450, 600, 600, k)
            d.text((100, 490), "КВАРТИРА СВЕРХУ", font=font(34), fill=(190, 196, 214, A), anchor="lm"); d.text((100, 555), "ПУСТАЯ", font=font(60), fill=RED + (A,), anchor="lm")
    if si == 1:
        k = ease((t - 0.2) / 0.3); A = int(255 * k); y0 = 470 + 40 * (1 - k)
        d.rounded_rectangle([140, y0, 940, y0 + 420], radius=10, fill=(240, 238, 230, A))
        d.text((W / 2, y0 + 60), "УПРАВЛЯЮЩАЯ КОМПАНИЯ", font=font(36), fill=(60, 60, 70, A), anchor="mm")
        d.line([(190, y0 + 105), (890, y0 + 105)], fill=(150, 150, 150, A), width=3)
        d.text((200, y0 + 170), "Кв. 47: пустует", font=font(48), fill=(30, 30, 40, A), anchor="lm")
        if t > wt(1, "Никто"):
            d.text((200, y0 + 250), "Прописано: 0 чел.", font=font(48), fill=(30, 30, 40, A), anchor="lm")
            kk = ease((t - wt(1, "Никто")) / 0.15); s_ = 1 + 0.4 * (1 - kk)
            d.rounded_rectangle([W / 2 - 200 * s_, y0 + 330 - 40 * s_, W / 2 + 200 * s_, y0 + 330 + 40 * s_], radius=8, outline=(190, 40, 40, A), width=6)
            d.text((W / 2, y0 + 330), "НИКТО НЕ ЖИВЁТ", font=font(int(40 * s_)), fill=(190, 40, 40, A), anchor="mm")
    if si == 2:
        tp = wt(2, "На пороге")
        if t > tp and t < wt(2, "А за дверью"):
            k = ease((t - tp) / 0.25); A = int(255 * k); panel(d, 60, 450, 600, 600, k)
            d.text((100, 490), "НА ПОРОГЕ ПЫЛЬ", font=font(34), fill=(190, 196, 214, A), anchor="lm"); d.text((100, 555), "СЛЕДОВ: 0", font=font(56), fill=YEL + (A,), anchor="lm")
        tb = wt(2, "что-то упало")
        if t > tb: k = ease((t - tb) / 0.12); stroke_text(d, (W / 2 + 6 * math.sin(t * 40), 880), "БУМ!", font(130), RED + (int(255 * k),), 10)
        ts = wt(2, "И шаги")
        if t > ts:
            for j in range(4):
                if t > ts + j * 0.35: stroke_text(d, (300 + j * 160, 1560 - j * 30), "ТОП", font(48), (200, 200, 210), 5)
    if si == 4:
        quote(d, t, wt(4, "Опять") - 0.1, "Опять он стучит по батарее.", "МУЖСКОЙ ГОЛОС СВЕРХУ")
        tn = wt(4, "Но ты")
        if t > tn: k = ease((t - tn) / 0.2); stroke_text(d, (W / 2, 1560), "ТЫ НЕ СТУЧАЛ", font(90), RED + (int(255 * k),), 9)
    if si == 5: quote(d, t, wt(5, "Потерпи") - 0.1, "Потерпи. Скоро он перестанет.", "ЖЕНСКИЙ ГОЛОС СВЕРХУ", col=(255, 210, 210))
    if si == 6:
        tsc = wt(6, "А в полу")
        if t < tsc:
            k = ease((t - 0.2) / 0.25); A = int(255 * k); panel(d, 60, 450, 640, 600, k)
            d.text((100, 490), "СЛЕСАРЬ, 30 ЛЕТ В ДОМЕ", font=font(32), fill=(190, 196, 214, A), anchor="lm")
            if t > wt(6, "Их нашли"): d.text((100, 555), "СЕМЬЮ НАШЛИ", font=font(52), fill=RED, anchor="lm")
            else: d.text((100, 555), "ТАМ ЖИЛА СЕМЬЯ", font=font(48), fill=WHITE + (A,), anchor="lm")
        else:
            k = ease((t - tsc) / 0.25); A = int(255 * k); panel(d, 60, 450, 640, 600, k)
            d.text((100, 490), "ЦАРАПИНЫ В ПОЛУ", font=font(34), fill=(190, 196, 214, A), anchor="lm"); d.text((100, 555), "СНИЗУ", font=font(60), fill=RED + (A,), anchor="lm")
    if si == 7:
        quote(d, t, wt(7, "Ну вот") - 0.1, "Ну вот. Мы прямо над ним.", "ЖЕНСКИЙ ГОЛОС", col=(255, 210, 210))
        tp = wt(7, "Пора")
        if t > tp: k = ease((t - tp) / 0.12); stroke_text(d, (W / 2, 1560), "— ПОРА.", font(110), RED + (int(255 * k),), 10)
    if si == 8:
        tc = wt(8, "хрустнул")
        if t > tc and t < wt(8, "Что было") : k = ease((t - tc) / 0.1); stroke_text(d, (W / 2 + 8 * math.sin(t * 50), 900), "ХРУСТ", font(130), WHITE + (int(255 * k),), 10)
        sh.cta(d, t, wt(8, "Пиши") - 0.1, "ЕЩЁ ЧАСТЬ", "СВОЯ ВЕРСИЯ")

def sound(sh, add, SR, n, tt):
    wt = sh.wt; ST = sh.STARTS; TOTAL = sh.TOTAL; rnd = np.random.default_rng(66)
    def T_(dur): return np.arange(int(dur * SR)) / SR
    def band(sig, lo, hi):
        f = np.fft.rfft(sig); fr = np.fft.rfftfreq(len(sig), 1 / SR); f[(fr < lo) | (fr > hi)] = 0; return np.fft.irfft(f, len(sig))
    def noise(dur, lo, hi):
        s_ = band(rnd.standard_normal(int(dur * SR)), lo, hi); return s_ / (np.abs(s_).max() + 1e-9)
    def thud(f=60, dur=0.4, dec=10): t_ = T_(dur); return np.sin(2 * np.pi * f * t_ * (1 + 0.6 * np.exp(-t_ * 30))) * np.exp(-t_ * dec)
    def scrape(dur, amp=0.3):
        t_ = T_(dur); s_ = noise(dur, 80, 900) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * (11 + 4 * np.sin(2 * np.pi * 0.7 * t_)) * t_)))
        return amp * s_ * np.clip(t_ / 0.1, 0, 1) * np.clip((dur - t_) / 0.2, 0, 1)
    def step(): return 0.5 * thud(70, 0.25, 16) + 0.15 * noise(0.25, 200, 1200) * np.exp(-T_(0.25) * 20)
    drone = 0.5 * np.sin(2 * np.pi * 41 * tt) + 0.35 * np.sin(2 * np.pi * 43.5 * tt) + 0.2 * np.sin(2 * np.pi * 61.7 * tt) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.11 * tt))
    hiss = noise(TOTAL, 2000, 7000)[:n]; hiss = np.pad(hiss, (0, n - len(hiss)))
    heart = np.zeros(n); k = 0.0
    while k < TOTAL - 0.4:
        for off, amp in ((0.0, 1.0), (0.2, 0.6)):
            sig = amp * thud(48, 0.3, 14); s0 = int((k + off) * SR); sig = sig[: max(0, n - s0)]; heart[s0:s0 + len(sig)] += sig
        k += 1.1 - 0.5 * min(1.0, k / TOTAL)
    env = np.clip(tt / 0.5, 0, 1) * np.clip((TOTAL - tt) / 1.5, 0, 1)
    day = ((tt > ST[6]) & (tt < ST[6] + wt(6, "А в полу"))).astype(float)
    music = (0.12 * drone + 0.01 * hiss + 0.22 * heart * (1 - 0.7 * day)) * env
    for j in range(3): add(scrape(1.6, 0.25), 0.4 + j * 2.0)
    for j in range(int(TOTAL)):
        if tt[min(n - 1, int(j * SR))] < ST[6] or tt[min(n - 1, int(j * SR))] > ST[7]: add(0.05 * np.sin(2 * np.pi * 2200 * T_(0.05)) * np.exp(-T_(0.05) * 60), j * 1.0)   # часы
    add(0.3 * noise(0.4, 1500, 5000) * np.exp(-T_(0.4) * 8), ST[1] + 0.3)
    add(0.7 * thud(50, 0.8, 5), ST[1] + wt(1, "Никто"))
    add(0.9 * thud(38, 1.2, 3.5) + 0.0, ST[2] + wt(2, "что-то упало"))
    for j in range(4): add(step(), ST[2] + wt(2, "И шаги") + j * 0.35)
    t_ = T_(1.2); add(0.08 * np.sin(2 * np.pi * 3200 * t_) * np.clip((1.2 - t_) / 0.3, 0, 1), ST[3] + wt(3, "мелькнул"))
    for j in range(5): add(0.4 * thud(140, 0.12, 30), ST[4] + 0.3 + j * 0.25)                                     # стук по батарее
    add(0.6 * thud(46, 0.9, 5), ST[4] + wt(4, "Но ты"))
    add(0.5 * thud(60, 0.6, 6), ST[6] + wt(6, "Их нашли")); add(0.3 * noise(1.2, 2000, 6000) * np.clip((1.2 - T_(1.2)) / 0.3, 0, 1), ST[6] + wt(6, "А в полу"))
    add(scrape(wt(7, "Ну вот") - 0.3, 0.4), ST[7] + 0.1)
    add(0.9 * thud(36, 1.4, 3.0), ST[7] + wt(7, "Ну вот") - 0.2)
    add(0.8 * thud(40, 1.0, 4), ST[7] + wt(7, "Пора"))
    tc = ST[8] + wt(8, "хрустнул")
    for j in range(8): add((0.5 - 0.04 * j) * noise(0.05, 800, 6000), tc + j * 0.06)
    add(0.9 * thud(34, 1.5, 3.0), tc + 0.05)
    for j in range(6): add(0.1 * noise(0.06, 2000, 7000), tc + 0.3 + j * 0.15)
    for f in (233, 277, 349): add(0.06 * np.sin(2 * np.pi * f * T_(2.0)) * np.exp(-T_(2.0) * 1.5), ST[8] + wt(8, "Пиши") - 0.1)
    return music

import render as _me
SH = Show(_me) if __name__ != "__main__" else None
if __name__ == "__main__":
    import render as ep
    SH = ep.SH; ep.SH.run("sosedi")
