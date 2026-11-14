"""«Нас двое» — хоррор-ролик (3D). Запуск: LIBGL_ALWAYS_SOFTWARE=1 xvfb-run -a python3 render.py [preview | sheet N K | at N T]"""
import math, os, random, sys
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(D, "..", "engine3d")); sys.path.insert(0, D)
import numpy as np
from models import *
from show import *
from script import SCENES, CAPTION_NUMS

PI = math.pi
LEADS = [0.3] * 12
TAILS = [0.7, 0.6, 0.7, 0.6, 0.9, 0.7, 0.7, 0.9, 1.0, 0.8, 1.2, 3.2]
KEY = {"аварии", "один", "не", "живы", "все", "брат", "брата", "карточка", "твоя", "твоё", "лицо", "пустые", "почерком", "первым", "подожду", "сама", "наконец-то",
       "холодные", "ждал", "смотрел", "зеркал", "зеркалу", "отражении", "спиной", "готово", "зеркале", "ты", "выжил", "отражение", "молчат", "голоса", "нет", "настоящий", "комментариях"}
NIGHT = dict(sun_dir=(0.4, -0.6, -0.7), sun_col=(0.12, 0.16, 0.26), amb_top=(0.10, 0.12, 0.17), amb_bot=(0.05, 0.06, 0.08), fog=0.02, fog_col=(0.02, 0.03, 0.05),
             sky=((0.01, 0.015, 0.03),) * 3, hz=0.5, shadow_center=(0, 1.0, 0), shadow_size=6)
ENV = NIGHT
DAY = dict(NIGHT, sun_col=(0.55, 0.58, 0.6), amb_top=(0.32, 0.34, 0.36), amb_bot=(0.16, 0.17, 0.18), fog_col=(0.6, 0.62, 0.65), sky=((0.5, 0.55, 0.6),) * 3)
WALL = rgb((196, 210, 206)); WALL_D = rgb((150, 170, 168)); FLOOR = rgb((150, 156, 150)); WHITE_ = rgb((236, 238, 236)); METAL = rgb((150, 156, 166))
def _c(body, hair, legs, skin=(241, 203, 168)): b = rgb(body); return dict(body=b, body_d=tuple(v * 0.75 for v in b), hat=rgb(hair), hat_b=rgb(hair), legs=rgb(legs), pack=None, skin=rgb(skin))
GOWN = _c((150, 192, 190), (52, 40, 32), (150, 192, 190))
DOUBLE = _c((150, 192, 190), (52, 40, 32), (150, 192, 190), skin=(226, 200, 180))
DOC = _c((236, 236, 236), (140, 140, 146), (60, 64, 76))
NURSE = _c((140, 180, 214), (236, 236, 236), (140, 180, 214))
CEIL = 2.8; MIR_X = -1.8; DOOR_Z = 1.3

def bandage(head): return [cyl(head @ T(0, 0.13, -0.01) @ S(0.67, 0.12, 0.63), WHITE_)]
def hero_lying(t, mood=None, look=0.0, face=True):
    p, head = person(T(-0.1, 0.98, -0.45) @ Rz(-PI / 2), t, colors=GOWN, hat="hair", blink_seed=0.7, mouth=mood, look=look, face=face)
    return p + bandage(head) + [box(T(0.6, 0.86, -0.55) @ S(1.6, 0.2, 1.25), rgb((220, 226, 230)))]
def double(root, t, **kw):
    p, head = person(root, t, colors=DOUBLE, hat="hair", **kw); return p + bandage(head)
def doctor(root, t, **kw): p, _ = person(root, t, colors=DOC, hat="hair", **kw); return p
def nurse(root, t, **kw): p, _ = person(root, t, colors=NURSE, hat="bun", skirt=rgb((140, 180, 214)), scale=0.94, **kw); return p

def room(door_a=0.0, card=False, mirror_fig=None, t=0.0):
    it = [box(T(0, -0.1, 0) @ S(6.4, 0.2, 6.4), FLOOR, cast=False), box(T(0, CEIL + 0.1, 0) @ S(6.4, 0.2, 6.4), WHITE_, cast=False)]
    it += [box(T(3.1, CEIL / 2, 0) @ S(0.2, CEIL, 6.4), WALL, cast=False)]
    it += [box(T(-3.1, CEIL / 2, -1.2) @ S(0.2, CEIL, 3.8), WALL, cast=False), box(T(-3.1, CEIL / 2, 2.6) @ S(0.2, CEIL, 1.2), WALL, cast=False), box(T(-3.1, 2.55, DOOR_Z) @ S(0.2, 0.5, 1.4), WALL, cast=False)]
    # задняя стена с проёмом-зеркалом x -2.4..-1.2, y 0.5..2.3
    it += [box(T(0.45, CEIL / 2, -3.1) @ S(3.3, CEIL, 0.2), WALL, cast=False), box(T(-2.75, CEIL / 2, -3.1) @ S(0.7, CEIL, 0.2), WALL, cast=False),
           box(T(MIR_X, 0.25, -3.1) @ S(1.2, 0.5, 0.2), WALL, cast=False), box(T(MIR_X, 2.55, -3.1) @ S(1.2, 0.5, 0.2), WALL, cast=False)]
    for (x, y, sx, sy) in ((MIR_X, 0.5, 1.32, 0.06), (MIR_X, 2.3, 1.32, 0.06), (MIR_X - 0.63, 1.4, 0.06, 1.86), (MIR_X + 0.63, 1.4, 0.06, 1.86)):
        it.append(box(T(x, y, -2.99) @ S(sx, sy, 0.04), rgb((200, 204, 214)), cast=False))
    # зазеркалье: тусклая копия палаты
    it += [box(T(MIR_X, -0.1, -4.4) @ S(2.0, 0.2, 2.6), FLOOR, cast=False), box(T(MIR_X, 1.4, -5.7) @ S(2.0, 2.8, 0.1), WALL_D, cast=False),
           box(T(MIR_X - 1.0, 1.4, -4.4) @ S(0.1, 2.8, 2.6), WALL_D, cast=False), box(T(MIR_X + 1.0, 1.4, -4.4) @ S(0.1, 2.8, 2.6), WALL_D, cast=False), box(T(MIR_X, 2.85, -4.4) @ S(2.0, 0.1, 2.6), WALL_D, cast=False)]
    if mirror_fig == "sit": it += [box(T(MIR_X, 0.3, -4.9) @ S(1.6, 0.6, 0.9), rgb((140, 150, 156)))]
    it += [box(T(0.9, 0.35, -0.5) @ S(2.8, 0.1, 1.3), METAL), box(T(0.9, 0.62, -0.5) @ S(2.7, 0.3, 1.2), WHITE_), box(T(2.0, 0.85, -0.5) @ S(0.5, 0.16, 0.9), WHITE_)]
    for x in (-0.4, 2.2):
        for z in (-1.05, 0.05): it.append(box(T(x, 0.18, z) @ S(0.06, 0.36, 0.06), METAL))
    it.append(box(T(2.3, 0.6, 0.0) @ S(0.03, 1.2, 0.03), METAL)); it.append(box(T(2.3, 1.2, 0.0) @ S(0.03, 0.03, 1.0), METAL))
    it += [box(T(2.75, 0.35, -1.7) @ S(0.6, 0.7, 0.5), rgb((210, 214, 210)))]                                        # тумбочка
    it += [box(T(2.8, 1.25, -2.6) @ S(0.5, 0.4, 0.3), rgb((40, 44, 50))), box(T(2.8, 1.25, -2.44) @ S(0.42, 0.32, 0.02), rgb((10, 30, 20)), emit=0.6, cast=False)]
    beat = (t * 1.1) % 1.0
    for j in range(6):
        y = 1.25 + (0.08 if j == int(beat * 6) else 0.0)
        it.append(box(T(2.62 + j * 0.07, y, -2.42) @ S(0.06, 0.012, 0.01), rgb((80, 255, 120)), emit=3.0, cast=False))
    if card: it += [box(T(2.7, 0.71, -1.65) @ Ry(0.2) @ S(0.28, 0.01, 0.2), WHITE_, emit=0.4), box(T(2.66, 0.72, -1.66) @ Ry(0.2) @ S(0.08, 0.01, 0.1), rgb((120, 120, 130)), cast=False)]
    m = T(-3.05, 0, DOOR_Z - 0.65) @ Ry(door_a) @ T(0, 0, 0.65)
    it += [box(m @ T(0, 1.15, 0) @ S(0.08, 2.3, 1.3), rgb((180, 190, 196))), box(m @ T(0.07, 1.1, 0.5) @ S(0.06, 0.06, 0.14), METAL),
           box(m @ T(0.0, 1.7, 0) @ S(0.09, 0.4, 0.5), rgb((30, 40, 50)), cast=False)]
    it.append(box(T(-4.0, 1.2, DOOR_Z) @ S(1.6, 2.4, 1.4), rgb((200, 210, 200)), emit=0.4 * (door_a != 0), cast=False))      # коридор за дверью
    for x in (-1.2, 1.2): it.append(box(T(x, CEIL - 0.01, 0) @ S(1.4, 0.02, 0.3), rgb((255, 255, 250)), emit=1.0, cast=False))
    return it
L_NIGHT = [((2.8, 1.4, -2.0), (0.3, 0.9, 0.5), 2.5), ((-3.6, 1.6, DOOR_Z), (0.6, 0.65, 0.7), 4.0), ((0, 2.4, 0), (0.25, 0.3, 0.4), 6.0)]
L_DAY = [((-1.2, 2.5, 0), (1.3, 1.35, 1.4), 7.0), ((1.2, 2.5, 0), (1.3, 1.35, 1.4), 7.0)]
L_MIR = [((MIR_X, 2.2, -4.4), (0.5, 0.55, 0.7), 4.0)]

def corridor():
    it = [box(T(30, -0.1, 0) @ S(4, 0.2, 14), FLOOR, cast=False), box(T(30, 2.9, 0) @ S(4, 0.2, 14), WHITE_, cast=False),
          box(T(28.1, 1.4, 0) @ S(0.2, 2.8, 14), WALL, cast=False), box(T(31.9, 1.4, 0) @ S(0.2, 2.8, 14), WALL, cast=False), box(T(30, 1.4, -7) @ S(4, 2.8, 0.2), WALL, cast=False)]
    for z in (-4, 0, 4): it.append(box(T(30, 2.79, z) @ S(1.4, 0.02, 0.3), rgb((255, 255, 250)), emit=1.2, cast=False))
    it.append(box(T(31.85, 1.15, 1.0) @ S(0.06, 2.3, 1.2), rgb((180, 190, 196)), cast=False)); it.append(box(T(31.8, 1.7, 1.0) @ S(0.06, 0.4, 0.5), rgb((30, 40, 50)), cast=False))
    it.append(box(T(31.8, 2.4, 1.0) @ S(0.05, 0.2, 0.5), rgb((40, 120, 60)), emit=0.6, cast=False))
    return it
CORR = corridor()

def scene_3d(si, t):
    wt = SH.wt
    if si == 0:
        it = room(t=t) + hero_lying(t, look=0.4 * math.sin(t * 0.6))
        k = ease(t / SH.DUR[0])
        return dict(items=it, eye=(lerp(0.4, 0.8, k), lerp(2.6, 2.1, k), lerp(6.8, 4.6, k)), tgt=(0.8, 0.9, -0.6), fov=48, lights=L_NIGHT, snow=False)
    if si == 1:
        tu = wt(1, "Улыбка дрогнула")
        it = room(t=t) + hero_lying(t, look=-0.4) + doctor(T(-0.3, 0, 0.7) @ Ry(PI / 2 + 0.7), t, blink_seed=1.4, mouth="smile" if t < tu else None)
        k = ease(t / SH.DUR[1])
        return dict(items=it, eye=(lerp(1.6, 1.3, k), 1.9, lerp(3.6, 3.0, k)), tgt=(lerp(0.4, -0.2, ease((t - tu) / 1.0)), 1.6, 0.0), fov=46, env=DAY, lights=L_DAY, snow=False)
    if si == 2:
        tt_ = wt(2, "оборачивается")
        a = lerp(-PI / 2, PI / 2 - 0.3, ease((t - tt_) / 0.9))
        it = room(door_a=1.5, t=t) + hero_lying(t, look=-0.6, mood="o" if t > wt(2, "У меня") else None) + nurse(T(-2.1, 0, DOOR_Z - 0.3) @ Ry(a), t, blink_seed=2.0)
        k = ease(t / SH.DUR[2])
        return dict(items=it, eye=(lerp(1.4, 1.1, k), 1.9, lerp(2.6, 2.2, k)), tgt=(-1.6, 1.3, DOOR_Z - 0.4), fov=50, lights=L_NIGHT, snow=False)
    if si in (3, 4):
        it = room(card=True, t=t) + hero_lying(t, look=0.6)
        k = ease(t / SH.DUR[si])
        return dict(items=it, eye=(lerp(2.4, 2.5, k), 2.2, lerp(0.8, 0.5, k)), tgt=(2.7, 0.7, -1.65), fov=40, env=DAY, lights=L_DAY, snow=False)
    if si == 5:
        to = wt(5, "Дверь открывается") + 0.3; da = 1.4 * ease((t - to) / 1.2)
        it = room(door_a=da, t=t) + hero_lying(t, look=-0.8, mood="o" if t > wt(5, "На пороге") else None)
        if da > 0.6: it += double(T(-3.4, 0, DOOR_Z) @ Ry(PI / 2), t, blink_seed=3.3, mouth="smile")
        k = ease(t / SH.DUR[5])
        return dict(items=it, eye=(lerp(1.8, 1.6, k), 1.35, lerp(-0.3, -0.1, k)), tgt=(-3.2, lerp(1.3, 1.55, k), DOOR_Z), fov=lerp(50, 38, k), env=DAY, lights=L_DAY + [((-3.6, 1.6, DOOR_Z), (0.8, 0.85, 0.9), 5.0)], snow=False)
    if si == 6:
        it = room(t=t) + hero_lying(t, look=-0.5, mood="o") + double(T(0.6, -0.35, 0.35) @ Ry(0.5), t, arm="hold", blink_seed=3.3, look=0.3 * math.sin(t * 0.5))
        k = ease(t / SH.DUR[6])
        return dict(items=it, eye=(lerp(2.6, 2.4, k), 1.8, lerp(2.6, 2.2, k)), tgt=(0.6, 1.2, -0.2), fov=50, env=DAY, lights=L_DAY, snow=False)
    if si == 7:
        tr = wt(7, "В отражении") + 0.2; ra = lerp(0.0, 0.9, ease((t - tr) / 1.0))
        it = room(t=t) + hero_lying(t, look=-0.5) + double(T(MIR_X - 0.4, 0, -2.3) @ Ry(PI), t, blink_seed=3.3)
        it += double(T(MIR_X - 0.4, 0, -3.9) @ Ry(ra), t, blink_seed=3.3, mouth="smile" if ra > 0.6 else None)
        k = ease(t / SH.DUR[7])
        return dict(items=it, eye=(lerp(0.4, 0.2, k), 1.8, lerp(1.4, 1.0, k)), tgt=(MIR_X - 0.2, 1.5, -3.1), fov=46, env=DAY, lights=L_DAY + L_MIR, snow=False)
    if si == 8:
        it = room(mirror_fig="sit", t=t) + hero_lying(t, look=-0.5)
        p, head = person(T(MIR_X, -0.25, -4.6), t, colors=GOWN, hat="hair", face=False); it += p + bandage(head)
        for sx in (-0.11, 0.11): it.append(ball(head @ T(sx, -0.05, 0.29) @ S(0.09, 0.09, 0.04), rgb((250, 250, 250)), emit=0.6, cast=False))
        k = ease(t / SH.DUR[8])
        return dict(items=it, eye=(MIR_X + 0.2, 1.4, lerp(0.4, -0.8, k)), tgt=(MIR_X, 1.2, -4.0), fov=lerp(46, 36, k), env=DAY, lights=L_DAY + L_MIR, snow=False)
    if si == 9:
        tb = wt(9, "А ты сиди") - 0.3
        it = room(door_a=1.2, t=t) + hero_lying(t, look=-0.8, mood="o", face=True)
        a = PI / 2 + 0.3 if t < tb else -PI / 2 + 0.6 + 0.0
        x = lerp(-1.0, -2.6, ease(t / max(0.1, tb)))
        it += double(T(x, 0, DOOR_Z) @ Ry(-PI / 2 if t < tb else PI / 2 - 0.5), t, walk=t * 4 if t < tb else None, blink_seed=3.3, mouth="smile" if t > tb else None)
        k = ease(t / SH.DUR[9])
        return dict(items=it, eye=(1.8, 1.35, -0.2), tgt=(lerp(-1.2, -2.6, k), 1.55, DOOR_Z), fov=44, env=DAY, lights=L_DAY, snow=False)
    if si == 10:
        it = room(t=t) + hero_lying(t, look=-0.4, mood="o" if t > wt(10, "Ты открываешь") else None) + nurse(T(-0.2, 0, 0.8) @ Ry(PI / 2 + 0.6), t, blink_seed=2.0, mouth="smile")
        tv = wt(10, "Ты открываешь")
        k = ease((t - tv + 0.5) / 2.0)
        return dict(items=it, eye=(lerp(1.0, 1.4, k), lerp(2.1, 2.7, k), lerp(3.0, 2.4, k)), tgt=(lerp(0.4, 1.9, k), lerp(1.3, 0.95, k), lerp(0.2, -0.45, k)), fov=lerp(50, 40, k), env=DAY, lights=L_DAY, snow=False)
    it = CORR + double(T(30.4, 0, 0.8) @ Ry(PI + 0.5), t, blink_seed=3.3, mouth="smile") + doctor(T(29.4, 0, -0.2) @ Ry(0.6), t, blink_seed=1.4)   # 11: коридор
    k = ease(t / SH.DUR[11])
    return dict(items=it, eye=(lerp(30.4, 30.0, k), 1.75, lerp(-4.0, -3.4, k)), tgt=(30.1, 1.5, 0.4), fov=46, env=DAY, lights=[((30, 2.4, 0), (1.3, 1.35, 1.4), 8.0)], snow=False)

def panel(d, x0, y0, x1, y1, k=1.0): d.rounded_rectangle([x0, y0, x1, y1], radius=28, fill=PANEL + (int(215 * k),))
FI = "/usr/share/fonts/truetype/freefont/FreeSerifBoldItalic.ttf"
_FI = {}
def hand(sz):
    if sz not in _FI: _FI[sz] = ImageFont.truetype(FI if os.path.exists(FI) else FB, sz)
    return _FI[sz]
def quote(d, t, t0, text, who, y=1290, col=(255, 255, 255), edge=(150, 40, 40)):
    k = ease((t - t0) / 0.3)
    if k <= 0: return
    A = int(255 * k); n = int(clamp((t - t0) / (0.055 * len(text))) * len(text))
    ws = text.split(" "); lines = [""]
    for w in ws:
        if d.textlength((lines[-1] + " " + w).strip(), font=hand(62)) > 800: lines.append(w)
        else: lines[-1] = (lines[-1] + " " + w).strip()
    h = 110 + 72 * len(lines)
    d.rounded_rectangle([90, y, 990, y + h], radius=30, fill=(6, 8, 12, int(225 * k)), outline=edge + (A,), width=4)
    d.text((140, y + 48), who, font=font(32), fill=(170, 170, 180, A), anchor="lm")
    left = n
    for j, ln in enumerate(lines):
        part = ln[:max(0, left)]; left -= len(ln) + 1
        if part: d.text((140, y + 112 + j * 72), part, font=hand(62), fill=col + (A,), anchor="lm")

TIMES = ["04:12", "10:30", "02:40", "07:15", "07:15", "07:20", "07:22", "07:24", "07:25", "07:27", "08:27", "08:28"]
def overlay(sh, si, t, d):
    wt = sh.wt
    stroke_text(d, (W / 2, 250), "НАС ДВОЕ", font(70), WHITE, 6)
    stroke_text(d, (W / 2, 355), TIMES[si], font(118), RED, 9)
    if si == 0:
        k = ease((t - 0.3) / 0.25); A = int(255 * k); panel(d, 60, 450, 560, 700, k)
        d.text((100, 500), "В ПАЛАТЕ", font=font(36), fill=(190, 196, 214, A), anchor="lm"); d.text((100, 570), "1 ПАЦИЕНТ", font=font(56), fill=WHITE + (A,), anchor="lm")
        if t > wt(0, "В машине"): d.text((100, 650), "В МАШИНЕ БЫЛО: 2", font=font(42), fill=RED, anchor="lm")
    if si == 1:
        if t < wt(1, "Ты спрашиваешь"): quote(d, t, wt(1, "Все живы") - 0.1, "Все живы. Отделались ушибами.", "ВРАЧ", edge=(80, 140, 200))
        elif t < wt(1, "Улыбка"): quote(d, t, wt(1, "Ты спрашиваешь"), "Кто все?", "ТЫ", edge=(200, 200, 200))
        else: quote(d, t, wt(1, "Ты. Один") - 0.1, "Ты. Один.", "ВРАЧ", edge=(80, 140, 200))
    if si == 2:
        if t < wt(2, "У меня"): quote(d, t, wt(2, "А где") - 0.1, "А где твой брат? Он ведь с тобой приехал.", "МЕДСЕСТРА", edge=(80, 140, 200))
        else: quote(d, t, wt(2, "У меня") - 0.05, "У меня нет брата.", "ТЫ", edge=(200, 200, 200))
    if si in (3, 4):
        k = ease((t - 0.2) / 0.3) if si == 3 else 1.0; A = int(255 * k); x0, y0 = 120, 450
        d.rounded_rectangle([x0, y0, W - x0, y0 + 520], radius=16, fill=(240, 240, 236, A), outline=(160, 170, 180, A), width=4)
        d.rectangle([x0, y0, W - x0, y0 + 70], fill=(70, 130, 170, A)); d.text((W / 2, y0 + 35), "КАРТОЧКА ПАЦИЕНТА №2", font=font(36), fill=(255, 255, 255, A), anchor="mm")
        rows = [("Фамилия:", "Фамилия", "твоя"), ("Имя:", "Имя", "твоё"), ("Дата рожд.:", "Имя", "твоя")]
        for j, (lab, sub, val) in enumerate(rows):
            on = si == 4 or t > wt(3, sub) + 0.3 + 0.4 * (j == 2)
            d.text((x0 + 40, y0 + 120 + j * 64), lab, font=font(36), fill=(90, 90, 100, A), anchor="lm")
            if on: d.text((x0 + 300, y0 + 120 + j * 64), val.upper(), font=font(40), fill=(30, 30, 40, A), anchor="lm")
        px0, py0 = W - x0 - 250, y0 + 90
        d.rectangle([px0, py0, px0 + 200, py0 + 240], fill=(200, 205, 210, A))
        if si == 4 or t > wt(3, "На фото"):
            d.ellipse([px0 + 50, py0 + 40, px0 + 150, py0 + 150], fill=(230, 200, 175, A)); d.ellipse([px0 + 48, py0 + 30, px0 + 152, py0 + 90], fill=(60, 46, 36, A))
            d.rounded_rectangle([px0 + 30, py0 + 150, px0 + 170, py0 + 240], radius=20, fill=(150, 192, 190, A))
            ey = (255, 255, 255, A) if (si == 4 or t > wt(3, "пустые")) else (20, 20, 26, A)
            for ex in (px0 + 80, px0 + 120): d.ellipse([ex - 9, py0 + 95, ex + 9, py0 + 113], fill=ey)
        if si == 4:
            s_ = "Он очнётся первым. Я подожду."; n = int(clamp((t - wt(4, "Он очнётся") + 0.1) / 2.2) * len(s_))
            if n: d.text((x0 + 40, y0 + 400), s_[:n], font=hand(58), fill=(140, 30, 30, A), anchor="lm")
    if si == 5 and t > wt(5, "Ну наконец"): quote(d, t, wt(5, "Ну наконец") - 0.1, "Ну наконец-то. Я думал, ты дольше будешь.", "ОН", edge=(160, 160, 170))
    if si == 6:
        tc = wt(6, "Пальцы")
        if t < wt(6, "Я тот"):
            if t > tc: k = ease((t - tc) / 0.25); panel(d, 60, 450, 560, 600, k); d.text((100, 490), "ПАЛЬЦЫ", font=font(34), fill=(190, 196, 214), anchor="lm"); d.text((100, 555), "ХОЛОДНЫЕ", font=font(56), fill=(140, 200, 255), anchor="lm")
        else: quote(d, t, wt(6, "Я тот") - 0.1, "Я тот, кто ждал. Ты жил. А я смотрел. Из зеркал.", "ОН", edge=(160, 160, 170))
    if si == 7 and t > wt(7, "Видишь"): quote(d, t, wt(7, "Видишь") - 0.1, "Видишь? Место готово.", "ОН", edge=(160, 160, 170))
    if si == 8 and t > wt(8, "И глаза"):
        k = ease((t - wt(8, "И глаза")) / 0.2); stroke_text(d, (W / 2, 900), "ЭТО ТЫ", font(110), RED + (int(255 * k),), 10)
    if si == 9:
        if t < wt(9, "А ты сиди") - 0.3: quote(d, t, 0.3, "Я пошёл. Скажу врачу, что я единственный, кто выжил.", "ОН", edge=(160, 160, 170))
        else: quote(d, t, wt(9, "А ты сиди") - 0.3, "А ты сиди тихо. Отражения молчат.", "ОН", edge=(160, 40, 40), col=(255, 210, 210))
    if si == 10:
        if t < wt(10, "Ты открываешь"): quote(d, t, wt(10, "Как вы") - 0.1, "Как вы себя чувствуете?", "МЕДСЕСТРА", edge=(80, 140, 200))
        else:
            k = ease((t - wt(10, "Ты открываешь")) / 0.3); A = int(255 * k)
            d.rounded_rectangle([90, 1290, 990, 1460], radius=30, fill=(6, 8, 12, int(225 * k)), outline=(200, 200, 200, A), width=4)
            d.text((140, 1338), "ТЫ", font=font(32), fill=(170, 170, 180, A), anchor="lm"); d.text((140, 1402), "...", font=hand(70), fill=(255, 255, 255, A), anchor="lm")
            if t > wt(10, "Голоса"): k2 = ease((t - wt(10, "Голоса")) / 0.2); stroke_text(d, (W / 2, 900), "ГОЛОСА НЕТ", font(104), RED + (int(255 * k2),), 10)
    if si == 11:
        if t < wt(11, "Кто из"): quote(d, t, wt(11, "Я совершенно") - 0.1, "Я совершенно один. И очень рад, что выжил.", "ОН — ВРАЧУ", edge=(160, 160, 170))
        sh.cta(d, t, wt(11, "Пиши") - 0.1, "В ПАЛАТЕ", "В КОРИДОРЕ")
        te = sh.DUR[11] - 1.7
        if t > te: stroke_text(d, (W / 2, 1650), "КТО НАСТОЯЩИЙ?", font(54), WHITE + (int(255 * ease((t - te) / 0.3)),), 6)

def sound(sh, add, SR, n, tt):
    wt = sh.wt; ST = sh.STARTS; TOTAL = sh.TOTAL; rnd = np.random.default_rng(77)
    def T_(dur): return np.arange(int(dur * SR)) / SR
    def band(sig, lo, hi):
        f = np.fft.rfft(sig); fr = np.fft.rfftfreq(len(sig), 1 / SR); f[(fr < lo) | (fr > hi)] = 0; return np.fft.irfft(f, len(sig))
    def noise(dur, lo, hi):
        s_ = band(rnd.standard_normal(int(dur * SR)), lo, hi); return s_ / (np.abs(s_).max() + 1e-9)
    def thud(f=60, dur=0.4, dec=10): t_ = T_(dur); return np.sin(2 * np.pi * f * t_ * (1 + 0.6 * np.exp(-t_ * 30))) * np.exp(-t_ * dec)
    drone = 0.5 * np.sin(2 * np.pi * 44 * tt) + 0.35 * np.sin(2 * np.pi * 46.3 * tt) + 0.25 * np.sin(2 * np.pi * 66 * tt) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.09 * tt))
    hiss = noise(TOTAL, 3000, 8000)[:n]; hiss = np.pad(hiss, (0, n - len(hiss)))
    env = np.clip(tt / 0.5, 0, 1) * np.clip((TOTAL - tt) / 1.5, 0, 1)
    mute = ((tt > ST[10] + wt(10, "Голоса") - 0.1) & (tt < ST[11])).astype(float)
    music = (0.12 * drone * (1 - 0.9 * mute) + 0.012 * hiss) * env
    beep_t = 0.4
    while beep_t < TOTAL - 1.0:                                                                                          # монитор
        if not (ST[11] <= beep_t): add(0.06 * np.sin(2 * np.pi * 1000 * T_(0.09)) * np.exp(-T_(0.09) * 12), beep_t)
        beep_t += 1.0 / 1.1 if beep_t < ST[5] else (0.7 if beep_t < ST[10] else 1.0)
    add(0.6 * thud(46, 0.9, 5), wt(0, "В машине"))
    add(0.5 * thud(60, 0.6, 6), ST[1] + wt(1, "Ты. Один")); add(0.4 * noise(0.8, 300, 2000) * np.exp(-T_(0.8) * 3), ST[2] + 0.2)
    add(0.7 * thud(44, 1.0, 4), ST[2] + wt(2, "У меня"))
    add(0.3 * noise(0.3, 1500, 6000) * np.exp(-T_(0.3) * 9), ST[3] + 0.2)
    add(0.7 * thud(42, 1.0, 4), ST[3] + wt(3, "пустые"))
    for j in range(20): add(0.06 * noise(0.07, 1500, 6000) * np.exp(-T_(0.07) * 25), ST[4] + wt(4, "Он очнётся") + j * 0.11)
    to = ST[5] + wt(5, "Дверь открывается") + 0.3; t_ = T_(1.4)
    add(0.3 * np.sin(2 * np.pi * np.cumsum(180 + 120 * t_ / 1.4 + 20 * np.sin(2 * np.pi * 17 * t_)) / SR) * np.clip(t_ / 0.1, 0, 1) * np.clip((1.4 - t_) / 0.3, 0, 1), to)
    add(0.8 * thud(40, 1.2, 3.5), ST[5] + wt(5, "На пороге"))
    t_ = T_(2.0); add(0.05 * np.sin(2 * np.pi * 1900 * t_) * np.clip(t_ / 0.5, 0, 1) * np.clip((2.0 - t_) / 0.5, 0, 1), ST[6] + wt(6, "Пальцы"))
    add(0.8 * thud(38, 1.3, 3.2), ST[7] + wt(7, "В отражении") + 0.4)
    for f in (233, 247): add(0.05 * np.sin(2 * np.pi * f * T_(3.0)) * np.clip(T_(3.0) / 1.0, 0, 1) * np.clip((3.0 - T_(3.0)) / 0.5, 0, 1), ST[8])
    add(0.9 * thud(36, 1.4, 3.0), ST[8] + wt(8, "И глаза"))
    add(0.4 * noise(0.6, 300, 2000) * np.exp(-T_(0.6) * 4), ST[9] + sh.DUR[9] - 0.8); add(0.8 * thud(50, 0.6, 6), ST[9] + sh.DUR[9] - 0.6)
    add(0.9 * thud(34, 1.6, 2.8), ST[10] + wt(10, "Голоса"))
    for f in (233, 277, 349): add(0.06 * np.sin(2 * np.pi * f * T_(2.0)) * np.exp(-T_(2.0) * 1.5), ST[11] + wt(11, "Пиши") - 0.1)
    return music

import render as _me
SH = Show(_me) if __name__ != "__main__" else None
if __name__ == "__main__":
    import render as ep
    SH = ep.SH; ep.SH.run("nas-dvoe")
