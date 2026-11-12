"""Новые персонажи сериала «Тридцать дней»: кот Кекс, баба Валя, Колян, дед (силуэт)."""
import math, os, sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "blackout"))
import numpy as np
from PIL import Image
from art import *

CAT = (206, 132, 70); CAT_D = (176, 106, 54); CAT_W = (240, 232, 220); PINK = (224, 150, 150)


def _finish(base, img, size, cw, ch, ax, ay, x, y, dark):
    small = img.resize((int(cw * size), int(ch * size)), Image.LANCZOS)
    if dark < 1.0:
        a = np.asarray(small).astype(np.float32); a[..., :3] *= dark
        small = Image.fromarray(a.astype(np.uint8), "RGBA")
    comp(base, small, x - ax * size, y - ay * size)


def cat(base, x, y, size, t, pose="sit", look=0.0, yawn=False, ears_back=False, dark=1.0, head_only=False):
    """Кекс. (x, y) — низ кота. Высота сидя ~ 260*size."""
    S = 2.0 * size; cw, ch = 360, 340
    img = Image.new("RGBA", (int(cw * S), int(ch * S)), (0, 0, 0, 0))
    p = P(img, S, ox=180, oy=320)
    br = 2 * math.sin(t * 2.6)
    if pose == "lie":
        hx, hy = -86, -96 + br * 0.5
        if not head_only:
            p.el(-150, -14, 150, 14, (0, 0, 0, 70))
            tw = 20 * math.sin(t * 1.7)
            p.line([(100, -30), (150, -40 + tw), (170, -80 + tw)], CAT_D, 26)
            p.el(-120, -100 + br, 130, 0, CAT)
            for k in (-20, 30, 80): p.line([(k, -96 + br), (k + 14, -60 + br)], CAT_D, 9)
            p.el(-130, -26, -70, 4, CAT_W)
    else:
        hx, hy = 0, -200 + br
        if not head_only:
            p.el(-80, -14, 80, 14, (0, 0, 0, 70))
            tw = 22 * math.sin(t * 1.9)
            p.line([(50, -16), (110, -26), (124 + tw * 0.4, -90 + tw)], CAT_D, 26)
            p.el(-72, -170 + br, 72, 0, CAT)
            p.el(-34, -150 + br, 34, -36, CAT_W)
            p.el(-44, -22, -8, 6, CAT_W); p.el(8, -22, 44, 6, CAT_W)
    # голова
    lx = look * 12
    ea = 26 if ears_back else 0
    p.poly([(hx - 58, hy - 20), (hx - 52 - ea, hy - 92 + ea), (hx - 12, hy - 50)], CAT)
    p.poly([(hx + 58, hy - 20), (hx + 52 + ea, hy - 92 + ea), (hx + 12, hy - 50)], CAT)
    p.poly([(hx - 48, hy - 34), (hx - 46 - ea * 0.8, hy - 74 + ea * 0.8), (hx - 22, hy - 48)], PINK)
    p.poly([(hx + 48, hy - 34), (hx + 46 + ea * 0.8, hy - 74 + ea * 0.8), (hx + 22, hy - 48)], PINK)
    p.el(hx - 66, hy - 64, hx + 66, hy + 50, CAT)
    for k in (-16, 0, 16): p.line([(hx + k, hy - 62), (hx + k * 1.2, hy - 38)], CAT_D, 8)
    p.el(hx - 30 + lx, hy + 2, hx + 30 + lx, hy + 44, CAT_W)
    bl = (t % 4.3) < 0.15 or yawn
    for sx in (-24, 24):
        if bl: p.line([(hx + sx - 9 + lx, hy - 4), (hx + sx + 9 + lx, hy - 4)], EYE, 5)
        else:
            p.circ(hx + sx + lx, hy - 4, 10, (150, 170, 70)); p.el(hx + sx + lx - 3, hy - 13, hx + sx + lx + 3, hy + 5, EYE)
    p.poly([(hx - 7 + lx, hy + 10), (hx + 7 + lx, hy + 10), (hx + lx, hy + 18)], PINK)
    if yawn: p.el(hx - 14 + lx, hy + 18, hx + 14 + lx, hy + 46, (150, 60, 70))
    for sgn in (-1, 1):
        for dy in (-4, 6):
            p.line([(hx + lx + sgn * 26, hy + 22 + dy), (hx + lx + sgn * 70, hy + 16 + dy * 1.8)], (250, 246, 240), 3, round_caps=False)
    _finish(base, img, size, cw, ch, 180, 320, x, y, dark)


def granny(base, x, y, size, t, mug=False, look=0.0, dark=1.0, sit=False):
    """Баба Валя: платок в цветочек, зелёная телогрейка, валенки."""
    S = 2.0 * size; cw, ch = 420, 620
    img = Image.new("RGBA", (int(cw * S), int(ch * S)), (0, 0, 0, 0))
    p = P(img, S, ox=210, oy=600)
    by = -2 * math.sin(t * 1.9 + 0.5)
    p.el(-84, -12, 84, 12, (0, 0, 0, 80))
    if not sit:
        for side in (-1, 1): p.rr(side * 26 - 24, -96, side * 26 + 24, 4, 16, (96, 92, 100))   # валенки
        p.rr(-64, -200, 64, -80, 30, (54, 48, 60))                                           # юбка
    p.rr(-72, -372 + by, 72, -170, 44, (52, 80, 64))                                          # телогрейка
    p.rr(28, -372 + by, 72, -170, 40, (44, 68, 54))
    for yy in (-330, -290, -250, -210): p.line([(-66, yy + by), (66, yy + by)], (42, 64, 50), 4, round_caps=False)
    p.line([(-66, -350 + by), (-76, -226 + by)], (52, 80, 64), 32); p.circ(-76, -222 + by, 15, SKIN)
    if mug:
        p.line([(66, -350 + by), (60, -270 + by)], (52, 80, 64), 32)
        p.line([(60, -270 + by), (10, -280 + by)], (52, 80, 64), 30)
        p.rr(-16, -320 + by, 36, -262 + by, 10, (196, 200, 214)); p.arc(26, -310 + by, 52, -276 + by, 270, 90, (196, 200, 214), 7)
        p.circ(12, -272 + by, 14, SKIN)
    else:
        p.line([(66, -350 + by), (76, -226 + by)], (52, 80, 64), 32); p.circ(76, -222 + by, 15, SKIN)
    # голова и платок
    p.el(-80, -540 + by, 80, -360 + by, (150, 76, 74))                                       # платок сзади
    p.el(-62, -510 + by, 62, -380 + by, SKIN)
    p.chord(-80, -560 + by, 80, -420 + by, 180, 360, (150, 76, 74))
    p.poly([(-30, -386 + by), (30, -386 + by), (0, -350 + by)], (150, 76, 74))              # узел
    for k, (dx, dy) in enumerate([(-50, -500), (-20, -530), (16, -520), (46, -496), (-60, -470), (60, -464)]):
        p.circ(dx, dy + by, 6, (226, 196, 120) if k % 2 else (230, 230, 220))
    lx = look * 12
    for sx in (-22, 22):
        if ((t + 2.1) % 4.4) < 0.14: p.line([(sx - 7 + lx, -450 + by), (sx + 7 + lx, -450 + by)], EYE, 4)
        else: p.circ(sx + lx, -450 + by, 7, EYE)
        p.line([(sx - 12 + lx, -468 + by), (sx + 10 + lx, -472 + by)], (150, 140, 140), 4)
    p.line([(-12 + lx, -416 + by), (12 + lx, -416 + by)], (150, 96, 90), 4)
    p.line([(-44, -432 + by), (-34, -428 + by)], (214, 170, 140), 3); p.line([(34, -428 + by), (44, -432 + by)], (214, 170, 140), 3)
    _finish(base, img, size, cw, ch, 210, 600, x, y, dark)
    return {"mug": (x + 10 * size, y + (-330 + by) * size)}


def kolyan(base, x, y, size, t, dark=1.0, rec=True, phone_up=True, serious=False, look=0.0):
    """Колян: камуфляж, шапка-петушок, телефон у лица, ухмылка."""
    S = 2.0 * size; cw, ch = 420, 680
    img = Image.new("RGBA", (int(cw * S), int(ch * S)), (0, 0, 0, 0))
    p = P(img, S, ox=210, oy=650)
    by = -3 * math.sin(t * 2.0 + 1.3)
    OL = (84, 92, 62); OLD = (64, 70, 46)
    p.el(-96, -14, 96, 14, (0, 0, 0, 80))
    for side in (-1, 1):
        p.rr(side * 30 - 22, -165, side * 30 + 22, -10, 18, (50, 52, 58))
        p.rr(side * 30 - 26, -30, side * 30 + 26, 4, 13, (30, 26, 24))
    p.rr(-74, -400 + by, 74, -130, 46, OL)
    for (a, b, c, d_) in [(-60, -380, -10, -340), (10, -320, 60, -280), (-50, -250, 0, -210), (20, -200, 64, -160)]:
        p.el(a, b + by, c, d_ + by, OLD)
    p.line([(-66, -372 + by), (-86, -226 + by)], OL, 34); p.circ(-86, -222 + by, 16, SKIN)
    if phone_up:
        p.line([(66, -372 + by), (100, -300 + by)], OL, 34); p.line([(100, -300 + by), (70, -430 + by)], OL, 32)
    else:
        p.line([(66, -372 + by), (88, -226 + by)], OL, 34)
    p.el(-84, -560 + by, 84, -390 + by, SKIN)
    p.chord(-88, -600 + by, 88, -430 + by, 180, 360, (140, 62, 58))
    p.rr(-90, -532 + by, 90, -500 + by, 14, (160, 76, 70)); p.circ(0, -606 + by, 22, (236, 232, 226))
    lx = look * 14
    for sx in (-30, 30): p.circ(sx + lx, -462 + by, 9, EYE)
    if serious:
        p.line([(-46 + lx, -480 + by), (-18 + lx, -490 + by)], BROW, 6); p.line([(18 + lx, -490 + by), (46 + lx, -480 + by)], BROW, 6)
        p.line([(-12 + lx, -424 + by), (12 + lx, -424 + by)], EYE, 6)
    else:
        p.line([(-46, -486 + by), (-18, -480 + by)], BROW, 6); p.line([(18, -480 + by), (46, -486 + by)], BROW, 6)
        p.arc(-28, -446 + by, 28, -408 + by, 10, 170, EYE, 6)
    if phone_up:
        p.rr(50, -500 + by, 106, -400 + by, 8, (18, 20, 28)); p.rr(56, -492 + by, 100, -408 + by, 5, (205, 228, 255))
        if rec and (t % 1.0) < 0.6: p.circ(78, -480 + by, 6, RED)
        p.circ(76, -420 + by, 16, SKIN)
    else:
        p.rr(70, -250 + by, 110, -170 + by, 8, (18, 20, 28)); p.circ(88, -222 + by, 16, SKIN)
    _finish(base, img, size, cw, ch, 210, 650, x, y, dark)
    return {"phone": (x + 78 * size, y + (-450 + by) * size)}


def silhouette(p, x, y, s, col, hat=None):
    p.rr(x - 50 * s, y - 330 * s, x + 50 * s, y, 34 * s, col)
    p.el(x - 38 * s, y - 420 * s, x + 38 * s, y - 330 * s, mixc(col, (255, 255, 255), 0.08))
    if hat: p.chord(x - 42 * s, y - 440 * s, x + 42 * s, y - 360 * s, 180, 360, hat)


def carrier(p, x, y, s=1.0):
    p.rr(x - 90 * s, y - 120 * s, x + 90 * s, y, 18 * s, (120, 128, 146))
    p.rr(x - 64 * s, y - 100 * s, x + 64 * s, y - 20 * s, 12 * s, (30, 34, 48))
    p.arc(x - 50 * s, y - 170 * s, x + 50 * s, y - 80 * s, 180, 360, (90, 96, 112), 12 * s)


def shovel(p, x0, y0, x1, y1):
    p.line([(x0, y0), (x1, y1)], (140, 104, 70), 12)
    dx, dy = x1 - x0, y1 - y0; L = math.hypot(dx, dy); ux, uy = dx / L, dy / L; nx, ny = -uy, ux
    p.poly([(x1 + nx * 34, y1 + ny * 34), (x1 - nx * 34, y1 - ny * 34), (x1 - nx * 26 + ux * 70, y1 - ny * 26 + uy * 70),
            (x1 + ux * 92, y1 + uy * 92), (x1 + nx * 26 + ux * 70, y1 + ny * 26 + uy * 70)], (150, 160, 178))
