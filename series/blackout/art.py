"""Общая графика сериала: палитра, сглаженное рисование, свечение, герой и соседи."""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 1080, 1920
NAVY0 = (8, 14, 30); NAVY1 = (14, 24, 48); NAVY2 = (24, 38, 70); NAVY3 = (36, 54, 94)
AMBER = (255, 178, 64); WARM = (255, 226, 170); SNOW = (232, 238, 248); RED = (230, 58, 58)
ICE = (190, 225, 250)
# Артём — паспорт персонажа в цветах
YELLOW = (246, 194, 42); YELLOW_D = (214, 160, 28); YELLOW_DD = (190, 138, 22)
SKIN = (241, 203, 168); CHEEK = (240, 178, 158)
BEANIE = (34, 46, 92); BEANIE_B = (44, 60, 116)
PANTS = (40, 46, 68); SHOE = (22, 24, 36); PACK = (106, 112, 126); PACK_D = (84, 90, 104)
EYE = (22, 22, 32); BROW = (70, 46, 34)


def lerp(a, b, k): return a + (b - a) * k
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(k): k = clamp(k); return k * k * (3 - 2 * k)
def mixc(c1, c2, k): return tuple(int(lerp(a, b, clamp(k))) for a, b in zip(c1, c2))


class P:
    """ImageDraw с масштабом и смещением: рисуем в 2x и потом уменьшаем = сглаживание."""
    def __init__(s, img, k=2.0, ox=0.0, oy=0.0):
        s.d = ImageDraw.Draw(img); s.k = k; s.ox = ox; s.oy = oy
    def _p(s, x, y): return ((x + s.ox) * s.k, (y + s.oy) * s.k)
    def _b(s, x0, y0, x1, y1):
        a = s._p(x0, y0); b = s._p(x1, y1)
        return [min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])]
    def rr(s, x0, y0, x1, y1, r, fill, outline=None, width=0):
        b = s._b(x0, y0, x1, y1); r = min(r * s.k, (b[2] - b[0]) / 2, (b[3] - b[1]) / 2)
        s.d.rounded_rectangle(b, radius=max(0, r), fill=fill, outline=outline, width=int(width * s.k))
    def rect(s, x0, y0, x1, y1, fill): s.d.rectangle(s._b(x0, y0, x1, y1), fill=fill)
    def el(s, x0, y0, x1, y1, fill=None, outline=None, width=0):
        s.d.ellipse(s._b(x0, y0, x1, y1), fill=fill, outline=outline, width=int(width * s.k))
    def circ(s, x, y, r, fill): s.el(x - r, y - r, x + r, y + r, fill)
    def chord(s, x0, y0, x1, y1, a0, a1, fill): s.d.chord(s._b(x0, y0, x1, y1), a0, a1, fill=fill)
    def pie(s, x0, y0, x1, y1, a0, a1, fill): s.d.pieslice(s._b(x0, y0, x1, y1), a0, a1, fill=fill)
    def arc(s, x0, y0, x1, y1, a0, a1, fill, width): s.d.arc(s._b(x0, y0, x1, y1), a0, a1, fill=fill, width=int(width * s.k))
    def poly(s, pts, fill): s.d.polygon([s._p(x, y) for x, y in pts], fill=fill)
    def line(s, pts, fill, width, round_caps=True):
        q = [s._p(x, y) for x, y in pts]
        s.d.line(q, fill=fill, width=int(width * s.k), joint="curve")
        if round_caps:
            r = width * s.k / 2
            for x, y in (q[0], q[-1]): s.d.ellipse([x - r, y - r, x + r, y + r], fill=fill)
    def text(s, x, y, t, font, fill): s.d.text(s._p(x, y), t, font=font, fill=fill)


def layer(w, h, fn, ss=2):
    """Статичный слой: рисуем в ss-кратном размере, уменьшаем LANCZOS."""
    img = Image.new("RGBA", (int(w * ss), int(h * ss)), (0, 0, 0, 0))
    fn(P(img, ss))
    return img.resize((int(w), int(h)), Image.LANCZOS)


def vgrad(w, h, stops):
    """Вертикальный градиент: stops = [(0..1, (r,g,b)), ...]."""
    ys = np.linspace(0, 1, h)[:, None]
    out = np.zeros((h, 3), np.float32)
    pos = [p for p, _ in stops]; cols = np.array([c for _, c in stops], np.float32)
    for ch in range(3): out[:, ch] = np.interp(ys[:, 0], pos, cols[:, ch])
    arr = np.repeat(out[:, None, :], w, axis=1)
    a = np.full((h, w, 1), 255, np.float32)
    return Image.fromarray(np.concatenate([arr, a], 2).astype(np.uint8), "RGBA")


_GLOW = {}
def glow_sprite(r, color, a=1.0, power=2.0):
    key = (int(r), color, round(a, 3), power)
    if key not in _GLOW:
        n = int(r) * 2 + 1
        yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
        d = np.sqrt((xx - r) ** 2 + (yy - r) ** 2) / max(r, 1)
        al = np.clip(1 - d, 0, 1) ** power * 255 * a
        arr = np.zeros((n, n, 4), np.uint8); arr[..., :3] = color; arr[..., 3] = al.astype(np.uint8)
        _GLOW[key] = Image.fromarray(arr, "RGBA")
    return _GLOW[key]


def comp(base, spr, x, y):
    """alpha_composite с отрицательными координатами."""
    x, y = int(round(x)), int(round(y))
    sx0, sy0 = max(0, -x), max(0, -y)
    sx1, sy1 = min(spr.width, base.width - x), min(spr.height, base.height - y)
    if sx1 <= sx0 or sy1 <= sy0: return
    base.alpha_composite(spr.crop((sx0, sy0, sx1, sy1)), (x + sx0, y + sy0))


def glow(base, cx, cy, r, color, a=1.0, power=2.0):
    comp(base, glow_sprite(r, color, a, power), cx - r, cy - r)


class Snow:
    def __init__(s, n, seed, size=(2, 6), speed=(60, 160), w=W, h=H):
        rnd = random.Random(seed); s.w, s.h = w, h
        s.p = [(rnd.random() * w, rnd.random() * h, rnd.uniform(*speed), rnd.uniform(*size), rnd.random() * 6.28) for _ in range(n)]
    def draw(s, img, t, alpha=220, dx=0):
        d = ImageDraw.Draw(img)
        for x, y, v, r, ph in s.p:
            yy = (y + v * t) % (s.h + 20) - 10
            xx = (x + 18 * math.sin(t * 0.8 + ph) + dx) % s.w
            d.ellipse([xx - r, yy - r, xx + r, yy + r], fill=SNOW + (alpha,))


def steam(img, x, y, t, period=2.6, scale=1.0, offset=0.0):
    """Пар изо рта: облачко выдоха раз в period секунд."""
    k = ((t + offset) % period) / 1.4
    if k > 1: return
    for j in range(3):
        kk = clamp(k - j * 0.12)
        if kk <= 0: continue
        r = (10 + 34 * kk) * scale
        cx = x + (20 + 60 * kk) * scale * (1 if j % 2 == 0 else 0.8); cy = y - (10 + 50 * kk) * scale - j * 6
        glow(img, cx, cy, r, (235, 240, 250), a=0.55 * (1 - kk), power=1.4)


# ---------------------------------------------------------------- Артём
def hero(base, x, y, size, t, view="front", look=(0.0, 0.0), walk=None, lamp=False, brows="calm",
         mouth=None, arm=None, dark=1.0, blink_seed=0.0, phone_on=False):
    """Рисует Артёма. (x, y) — точка между ступнями. Высота ~ 590*size px.
    Возвращает словарь опорных точек в координатах кадра."""
    S = 2.0 * size
    cw, ch = 420, 680
    img = Image.new("RGBA", (int(cw * S), int(ch * S)), (0, 0, 0, 0))
    p = P(img, S, ox=210, oy=650)
    bob = 3.0 * math.sin(t * 2.2)                  # дыхание
    ph = walk if walk is not None else None
    if ph is not None: bob += -6 * abs(math.sin(ph))
    by = -bob
    pts = {}

    # тень
    p.el(-96, -14, 96, 14, (0, 0, 0, 80))

    def legs():
        for side in (-1, 1):
            lift = 0.0; sx = 0.0
            if ph is not None:
                s_ = math.sin(ph) * side
                lift = max(0.0, s_) * 16; sx = s_ * 10
            x0 = side * 30 + sx
            p.rr(x0 - 22, -165 - lift * 0.3, x0 + 22, -10 - lift, 18, PANTS)
            p.rr(x0 - 28 + side * 4, -30 - lift, x0 + 26 + side * 4, 4 - lift, 13, SHOE)

    def arm_line(sx, sy, ex, ey, hand=True, col=YELLOW):
        p.line([(sx, sy), (ex, ey)], col, 34)
        if hand: p.circ(ex, ey + 4, 16, SKIN)

    if view == "back":
        legs()
        p.rr(-70, -398 + by, 70, -130, 46, YELLOW)
        p.rr(30, -398 + by, 70, -130, 40, YELLOW_D)
        p.rr(-70, -162, 70, -130, 20, YELLOW_D)
        sw = 0 if ph is None else math.sin(ph) * 10
        arm_line(-64, -372 + by, -84 + sw, -226 + by)
        arm_line(64, -372 + by, 84 - sw, -226 + by)
        p.rr(-60, -384 + by, 60, -186 + by, 30, PACK)          # рюкзак на спине
        p.rr(-60, -384 + by, 60, -330 + by, 26, PACK_D)
        p.rr(-36, -290 + by, 36, -236 + by, 12, PACK_D)
        p.el(-66, -438 + by, 66, -362 + by, YELLOW_D)           # капюшон
        p.el(-86, -556 + by, 86, -386 + by, (64, 44, 32))       # затылок
        p.chord(-92, -604 + by, 92, -408 + by, 180, 360, BEANIE)
        p.rr(-95, -526 + by, 95, -490 + by, 16, BEANIE_B)
        if lamp:
            p.rr(-95, -518 + by, 95, -504 + by, 6, (20, 20, 26))
        pts["head"] = (0, -480 + by)
    else:
        lx = look[0] * 22; ly = look[1] * 10
        p.rr(-80, -384 + by, 80, -172 + by, 30, PACK_D)          # края рюкзака за спиной
        legs()
        p.rr(-70, -398 + by, 70, -130, 46, YELLOW)
        p.rr(32, -398 + by, 70, -130, 40, YELLOW_D)
        p.rr(-70, -162, 70, -130, 20, YELLOW_D)
        p.line([(0, -384 + by), (0, -146)], YELLOW_DD, 4, round_caps=False)
        p.line([(-50, -236 + by), (-22, -236 + by)], YELLOW_DD, 4)
        p.line([(22, -236 + by), (50, -236 + by)], YELLOW_DD, 4)
        p.line([(-46, -380 + by), (-40, -250 + by)], PACK_D, 10)  # лямки
        p.line([(46, -380 + by), (40, -250 + by)], PACK_D, 10)
        sw = 0 if ph is None else math.sin(ph) * 14
        # левая рука
        arm_line(-64, -372 + by, -84 + sw, -222 + by)
        # правая рука
        if arm == "phone":
            p.line([(64, -372 + by), (84, -276 + by)], YELLOW, 34)
            p.line([(84, -276 + by), (30, -300 + by)], YELLOW, 32)
            p.rr(4, -350 + by, 50, -262 + by, 8, (18, 20, 28))
            p.rr(9, -342 + by, 45, -270 + by, 5, (205, 228, 255) if phone_on else (40, 56, 90))
            p.circ(30, -264 + by, 16, SKIN)
            pts["phone"] = (27, -306 + by)
        elif arm == "reach":
            arm_line(64, -372 + by, 150, -300 + by)
            pts["hand"] = (150, -296 + by)
        elif arm == "up":
            arm_line(64, -372 + by, 118, -540 + by)
            pts["hand"] = (118, -536 + by)
        else:
            arm_line(64, -372 + by, 84 - sw, -222 + by)
        p.el(-64, -444 + by, 64, -368 + by, YELLOW_D)           # капюшон за головой
        p.el(-88, -560 + by, 88, -384 + by, SKIN)               # голова
        p.el(-64 + lx * 0.4, -452 + by, -36 + lx * 0.4, -432 + by, CHEEK)
        p.el(36 + lx * 0.4, -452 + by, 64 + lx * 0.4, -432 + by, CHEEK)
        p.chord(-92, -604 + by, 92, -416 + by, 180, 360, BEANIE)
        p.rr(-95, -528 + by, 95, -492 + by, 16, BEANIE_B)
        if lamp:
            p.rr(-95, -518 + by, 95, -504 + by, 6, (20, 20, 26))
            p.el(-18 + lx * 0.3, -530 + by, 18 + lx * 0.3, -494 + by, (150, 156, 172))
            p.el(-11 + lx * 0.3, -523 + by, 11 + lx * 0.3, -501 + by, (255, 246, 214))
        # глаза, моргание каждые ~3.4 с
        bl = ((t + blink_seed) % 3.4) < 0.13
        ex = lx; ey = ly
        for sx in (-31, 31):
            if bl: p.line([(sx - 9 + ex, -456 + by + ey), (sx + 9 + ex, -456 + by + ey)], EYE, 5)
            else: p.circ(sx + ex, -456 + by + ey, 9.5, EYE)
        if brows == "worried":
            p.line([(-46 + ex, -478 + by), (-18 + ex, -490 + by)], BROW, 6)
            p.line([(18 + ex, -490 + by), (46 + ex, -478 + by)], BROW, 6)
        else:
            p.line([(-46 + ex, -484 + by), (-18 + ex, -486 + by)], BROW, 6)
            p.line([(18 + ex, -486 + by), (46 + ex, -484 + by)], BROW, 6)
        if mouth == "smile": p.arc(-20 + ex, -444 + by, 20 + ex, -418 + by, 20, 160, EYE, 5)
        elif mouth == "o": p.el(-8 + ex, -432 + by, 8 + ex, -416 + by, EYE)
        elif mouth == "flat": p.line([(-10 + ex, -424 + by), (10 + ex, -424 + by)], EYE, 5)
        pts["mouth"] = (ex + 14, -424 + by)
        pts["lamp"] = (lx * 0.3, -512 + by)
        pts["head"] = (0, -480 + by)

    small = img.resize((int(cw * size), int(ch * size)), Image.LANCZOS)
    if dark < 1.0:
        a = np.asarray(small).astype(np.float32); a[..., :3] *= dark
        small = Image.fromarray(a.astype(np.uint8), "RGBA")
    comp(base, small, x - 210 * size, y - 650 * size)
    return {k: (x + v[0] * size, y + v[1] * size) for k, v in pts.items()}


def lamp_glow(base, pt, on=True, beam=None, size=1.0):
    if not on: return
    glow(base, pt[0], pt[1], 70 * size, (255, 246, 214), 0.9, 2.2)
    glow(base, pt[0], pt[1], 22 * size, (255, 255, 240), 1.0, 1.2)


# ---------------------------------------------------------------- соседи
def old_man(base, x, y, size, t, look=0.0, bottle=False, dark=1.0, blink_seed=1.3):
    """Пётр Ильич: серое пальто, коричневая кепка, седые усы, очки, трость."""
    S = 2.0 * size; cw, ch = 420, 640
    img = Image.new("RGBA", (int(cw * S), int(ch * S)), (0, 0, 0, 0))
    p = P(img, S, ox=210, oy=610)
    by = -2.0 * math.sin(t * 1.8 + 1)
    p.el(-90, -12, 90, 12, (0, 0, 0, 80))
    p.line([(96, -10), (84, -250 + by)], (92, 64, 44), 12)                     # трость
    for side in (-1, 1): p.rr(side * 28 - 20, -120, side * 28 + 20, -8, 16, (54, 56, 64))
    for side in (-1, 1): p.rr(side * 28 - 26, -26, side * 28 + 26, 4, 12, (30, 28, 30))
    p.rr(-74, -360 + by, 74, -96, 40, (112, 114, 126))
    p.rr(30, -360 + by, 74, -96, 36, (94, 96, 108))
    for yy in (-300, -250, -200, -150): p.circ(0, yy + by, 6, (70, 72, 82))
    p.line([(-66, -340 + by), (-80, -200 + by)], (112, 114, 126), 32); p.circ(-80, -196 + by, 15, SKIN)
    p.line([(66, -340 + by), (86, -250 + by)], (112, 114, 126), 32); p.circ(86, -246 + by, 15, SKIN)
    if bottle:
        p.rr(-104, -300 + by, -60, -170 + by, 12, (170, 205, 230, 200))
        p.rr(-90, -320 + by, -74, -298 + by, 4, (90, 130, 200))
        p.circ(-80, -200 + by, 15, SKIN)
    p.rr(-36, -390 + by, 36, -350 + by, 14, (140, 60, 50))                     # шарф (приглушённый)
    p.el(-74, -520 + by, 74, -372 + by, SKIN)
    lx = look * 16
    p.chord(-80, -560 + by, 80, -440 + by, 180, 360, (96, 70, 50))           # кепка
    p.rr(-84 + lx * 0.6, -504 + by, 40 + lx * 0.6, -488 + by, 8, (80, 58, 40))
    for sx in (-26, 26):
        p.el(sx - 16 + lx, -468 + by, sx + 16 + lx, -438 + by, None, (60, 60, 70), 4)
        if ((t + blink_seed) % 4.1) < 0.13: p.line([(sx - 6 + lx, -453 + by), (sx + 6 + lx, -453 + by)], EYE, 4)
        else: p.circ(sx + lx, -453 + by, 7, EYE)
    p.line([(-10 + lx, -453 + by), (10 + lx, -453 + by)], (60, 60, 70), 4)
    p.el(-30 + lx, -428 + by, 30 + lx, -406 + by, (236, 236, 240))            # усы
    small = img.resize((int(cw * size), int(ch * size)), Image.LANCZOS)
    if dark < 1.0:
        a = np.asarray(small).astype(np.float32); a[..., :3] *= dark
        small = Image.fromarray(a.astype(np.uint8), "RGBA")
    comp(base, small, x - 210 * size, y - 610 * size)
    return {"mouth": (x + (lx + 20) * size, y + (-420 + by) * size)}


def woman(base, x, y, size, t, dark=1.0):
    """Соседка: сливовое пальто, плед на плечах, вязаная шапка."""
    S = 2.0 * size; cw, ch = 420, 640
    img = Image.new("RGBA", (int(cw * S), int(ch * S)), (0, 0, 0, 0))
    p = P(img, S, ox=210, oy=610)
    by = -2.5 * math.sin(t * 2.0 + 2)
    p.el(-84, -12, 84, 12, (0, 0, 0, 80))
    p.rr(-70, -350 + by, 70, -40, 50, (86, 70, 100))
    p.rr(-92, -362 + by, 92, -240 + by, 50, (122, 94, 72))                      # плед на плечах
    for k in (-50, 0, 50): p.line([(k, -356 + by), (k, -246 + by)], (104, 78, 60), 7, round_caps=False)
    for k in (-320, -280): p.line([(-86, k + by), (86, k + by)], (104, 78, 60), 7, round_caps=False)
    p.circ(-70, -236 + by, 15, SKIN); p.circ(70, -236 + by, 15, SKIN)
    p.el(-70, -506 + by, 70, -366 + by, SKIN)
    p.chord(-76, -548 + by, 76, -420 + by, 180, 360, (70, 110, 104))
    p.rr(-78, -486 + by, 78, -460 + by, 12, (84, 128, 120))
    for sx in (-24, 24):
        if ((t + 0.7) % 3.7) < 0.13: p.line([(sx - 7, -436 + by), (sx + 7, -436 + by)], EYE, 4)
        else: p.circ(sx, -436 + by, 7.5, EYE)
    p.arc(-14, -420 + by, 14, -402 + by, 20, 160, EYE, 4)
    small = img.resize((int(cw * size), int(ch * size)), Image.LANCZOS)
    if dark < 1.0:
        a = np.asarray(small).astype(np.float32); a[..., :3] *= dark
        small = Image.fromarray(a.astype(np.uint8), "RGBA")
    comp(base, small, x - 210 * size, y - 610 * size)


def passenger(p, x, y, s, col, seated=True):
    """Силуэт пассажира (рисуется прямо на слое через P)."""
    hh = 64 * s
    if seated:
        p.rr(x - 50 * s, y - 190 * s, x + 50 * s, y, 34 * s, col)
        p.rr(x - 44 * s, y - 20 * s, x + 70 * s, y + 24 * s, 18 * s, col)
        p.el(x - hh / 2 - 6 * s, y - 190 * s - hh - 4 * s, x + hh / 2 + 6 * s, y - 190 * s + 8 * s, mixc(col, (255, 255, 255), 0.08))
    else:
        p.rr(x - 46 * s, y - 330 * s, x + 46 * s, y, 32 * s, col)
        p.el(x - hh / 2 - 6 * s, y - 330 * s - hh - 4 * s, x + hh / 2 + 6 * s, y - 330 * s + 8 * s, mixc(col, (255, 255, 255), 0.08))
