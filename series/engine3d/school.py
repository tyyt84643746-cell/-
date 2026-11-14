"""Сериал «Последний урок»: школа (класс на 2 этаже, коридор, двор) и персонажи."""
import math, random
from models import *
PI = math.pi

def _c(body, hair, legs=(48, 56, 84), pack=None, skin=(241, 203, 168)):
    b = rgb(body); h = rgb(hair)
    return dict(body=b, body_d=tuple(v * 0.7 for v in b), hat=h, hat_b=h, legs=rgb(legs), pack=pack, skin=rgb(skin))

MAX = _c((214, 52, 48), (52, 36, 28), pack=rgb((70, 74, 86)))            # Макс: красная толстовка — единственный яркий цвет
LIZA = _c((70, 120, 120), (200, 160, 90), (60, 60, 80))
TIMUR = _c((70, 72, 80), (24, 22, 22), (40, 44, 56))
TEACHER = _c((120, 90, 130), (150, 150, 156), (70, 64, 80))
PE = _c((40, 70, 150), (60, 60, 60), (40, 66, 140), skin=(150, 168, 138))   # физрук-зомби: синий спортивный костюм, серая кожа
GUARD = _c((34, 36, 42), (30, 30, 30), (30, 32, 38), skin=(150, 168, 138))
_KID = [((150, 150, 160), (60, 44, 34)), ((60, 90, 70), (30, 26, 24)), ((180, 170, 150), (120, 80, 50)), ((90, 80, 120), (40, 30, 26)),
        ((70, 110, 160), (200, 170, 110)), ((160, 120, 90), (20, 18, 18)), ((120, 60, 70), (90, 60, 40)), ((200, 200, 205), (50, 40, 34))]
def kid_col(j): b, h = _KID[j % len(_KID)]; return _c(b, h)

def max_(root, t, **kw): return person(root, t, colors=MAX, hat="hair", **kw)
def liza(root, t, **kw): return person(root, t, colors=LIZA, hat="bun", scale=0.92, **kw)
def timur(root, t, **kw): return person(root, t, colors=TIMUR, hat="hair", scale=1.08, **kw)
def teacher(root, t, **kw): return person(root, t, colors=TEACHER, hat="bun", skirt=rgb((70, 64, 80)), scale=0.95, **kw)
def kid(j, root, t, **kw): return person(root, t, colors=kid_col(j), hat="bun" if j % 3 == 1 else "hair", scale=0.9 + 0.04 * (j % 3), **kw)
def zombie(root, t, colors=PE, **kw):
    kw.setdefault("arm", "zombie"); kw.setdefault("mouth", "o")
    return person(root, t, colors=colors, hat="hair", **kw)

WOOD = rgb((176, 140, 100)); WALL = rgb((214, 206, 186)); WALL_D = rgb((150, 160, 150)); WHITE_ = rgb((236, 236, 232))
DESK = rgb((196, 170, 130)); METAL = rgb((90, 96, 106)); BOARD = rgb((40, 70, 56))
WIN_Z = (-4.6, -0.6, 3.4); WIN_W = 2.6                                          # окна в левой стене x=-6
DOOR_Z = -5.8                                                                   # дверь в правой стене x=6
SEATS = [(cx + dx, z) for z in (-3.6, -1.2, 1.2, 3.6) for cx in (-3.4, 0.0, 3.4) for dx in (-0.42, 0.42)]
MAX_SEAT = 22                                                                   # (3.0, 3.6) — задняя парта у правого ряда

def desk(x, z, ry=0.0):
    m = T(x, 0, z) @ Ry(ry)
    it = [box(m @ T(0, 0.78, 0) @ S(1.6, 0.06, 0.7), DESK), box(m @ T(0, 0.5, -0.33) @ S(1.56, 0.5, 0.04), METAL)]
    for sx in (-0.74, 0.74): it.append(box(m @ T(sx, 0.38, 0) @ S(0.05, 0.76, 0.62), METAL))
    return it

def chair(x, z):
    return [box(T(x, 0.46, z) @ S(0.5, 0.05, 0.46), DESK), box(T(x, 0.8, z + 0.22) @ S(0.5, 0.5, 0.04), DESK), box(T(x, 0.22, z) @ S(0.46, 0.44, 0.42), METAL)]

def _wall_x(x, z0, z1, holes, y0, y1, col):
    """Стена вдоль z с проёмами holes=[(zc, w, ya, yb)]."""
    it = []; cuts = sorted(holes)
    z = z0
    for zc, w, ya, yb in cuts:
        a, b = zc - w / 2, zc + w / 2
        if a > z: it.append(box(T(x, (y0 + y1) / 2, (z + a) / 2) @ S(0.2, y1 - y0, a - z), col))
        if ya > y0: it.append(box(T(x, (y0 + ya) / 2, zc) @ S(0.2, ya - y0, w), col))
        if yb < y1: it.append(box(T(x, (yb + y1) / 2, zc) @ S(0.2, y1 - yb, w), col))
        z = b
    if z < z1: it.append(box(T(x, (y0 + y1) / 2, (z + z1) / 2) @ S(0.2, y1 - y0, z1 - z), col))
    return it

def classroom():
    it = [box(T(0, -0.1, -1) @ S(12.4, 0.2, 14.4), WOOD, cast=False), box(T(0, 3.7, -1) @ S(12.4, 0.2, 14.4), WHITE_, cast=False)]
    it += _wall_x(-6.1, -8, 6, [(z, WIN_W, 1.0, 2.9) for z in WIN_Z], 0, 3.6, WALL)
    it += _wall_x(6.1, -8, 6, [(DOOR_Z, 1.5, 0, 2.5)], 0, 3.6, WALL)
    it.append(box(T(0, 1.8, -8.1) @ S(12.4, 3.6, 0.2), WALL, cast=False)); it.append(box(T(0, 1.8, 6.1) @ S(12.4, 3.6, 0.2), WALL, cast=False))
    it.append(box(T(0, 0.5, -7.98) @ S(12, 1.0, 0.04), WALL_D, cast=False)); it.append(box(T(0, 0.5, 5.98) @ S(12, 1.0, 0.04), WALL_D, cast=False))
    it.append(box(T(0, 1.9, -7.97) @ S(5.2, 1.5, 0.06), BOARD, cast=False)); it.append(box(T(0, 1.12, -7.9) @ S(5.2, 0.06, 0.16), METAL, cast=False))
    for k, (x, y) in enumerate(((-1.6, 2.2), (-0.4, 2.0), (0.9, 2.3))): it.append(box(T(x, y, -7.93) @ S(0.9 - 0.2 * k, 0.04, 0.02), WHITE_, cast=False))
    it.append(ball(T(4.2, 3.0, -7.95) @ S(0.6, 0.6, 0.06), WHITE_, cast=False))                       # часы
    for z in WIN_Z:
        for dz in (-WIN_W / 2, WIN_W / 2): it.append(box(T(-6.05, 1.95, z + dz) @ S(0.12, 1.9, 0.08), WHITE_, cast=False))
        for y in (1.0, 2.9): it.append(box(T(-6.05, y, z) @ S(0.12, 0.08, WIN_W), WHITE_, cast=False))
    it.append(box(T(-1.2, 0.78, -6.6) @ S(2.0, 0.08, 0.9), DESK)); it.append(box(T(-1.2, 0.4, -6.6) @ S(1.9, 0.76, 0.8), METAL))   # стол учителя
    for x in (-3, 3):
        for z in (-4, 2): it.append(box(T(x, 3.58, z) @ S(1.4, 0.06, 0.3), rgb((255, 250, 235)), emit=2.0, cast=False))
    return it
LIGHTS_IN = [((x, 3.2, z), (1.6, 1.55, 1.45), 8.5) for x in (-3, 3) for z in (-4, 2)]

def desks_all(skip=()):
    it = []
    for j, (z) in enumerate((-3.6, -1.2, 1.2, 3.6)):
        for cx in (-3.4, 0.0, 3.4):
            if (cx, z) in skip: continue
            it += desk(cx, z - 0.55)
    return it

def seated(t, which=None, skip=(), mood=None):
    """Ученики «сидят»: тело опущено, ноги уходят под пол, низ прячет парта."""
    it = []
    for j, (x, z) in enumerate(SEATS):
        if j in skip: continue
        root = T(x, -0.62, z) @ Ry(PI)
        if j == MAX_SEAT: p, _ = max_(root, t, blink_seed=0.7, look=0.2 * math.sin(t * 0.7), mouth=mood)
        else: p, _ = kid(j, root, t, blink_seed=j * 0.37, look=0.25 * math.sin(t * 0.6 + j), mouth=mood if j % 2 else None)
        it += p
    return it

def corridor():
    X0, X1 = 6.2, 9.6; it = [box(T(7.9, -0.1, -12) @ S(3.6, 0.2, 40), rgb((150, 140, 128)), cast=False), box(T(7.9, 3.5, -12) @ S(3.6, 0.2, 40), WHITE_, cast=False)]
    it.append(box(T(X1 + 0.1, 1.75, -12) @ S(0.2, 3.5, 40), WALL, cast=False)); it.append(box(T(7.9, 1.75, -31.9) @ S(3.6, 3.5, 0.2), WALL, cast=False))
    it.append(box(T(7.9, 1.9, -31.78) @ S(1.6, 1.6, 0.04), rgb((220, 232, 255)), emit=1.4, cast=False))
    it.append(box(T(6.2 - 0.1, 1.75, -20) @ S(0.2, 3.5, 24), WALL, cast=False))
    it.append(box(T(6.2 - 0.1, 1.75, 2) @ S(0.2, 3.5, 12), WALL, cast=False))
    for z in range(-30, 6, 1):
        if -8 < z < -4: continue
        it.append(box(T(X1 - 0.25, 1.0, z + 0.5) @ S(0.4, 2.0, 0.9), rgb((70, 110, 140)) if z % 2 else rgb((64, 100, 128))))
    for z in (-26, -18, -10): it.append(box(T(6.12, 1.6, z) @ S(0.06, 2.4, 1.4), rgb((130, 96, 70)), cast=False))   # двери других классов
    return it
def corridor_lights(t, flick=True):
    L = []
    for j, z in enumerate((-28, -20, -12, -4)):
        on = 1.0 if not flick or j != 2 else (0.15 if (t * 7 + j) % 3 < 1 else 1.0)
        L.append(((7.9, 3.1, z), (1.5, 1.5, 1.4), 9.0 * on + 0.01))
    return L
def corridor_lamps(t, flick=True):
    it = []
    for j, z in enumerate((-28, -20, -12, -4)):
        on = 1.0 if not flick or j != 2 else (0.15 if (t * 7 + j) % 3 < 1 else 1.0)
        it.append(box(T(7.9, 3.38, z) @ S(1.4, 0.06, 0.3), rgb((255, 250, 235)), emit=2.2 * on, cast=False))
    return it

def door(open_a=0.0, shake=0.0):
    m = T(6.1, 0, DOOR_Z - 0.75) @ Ry(-open_a) @ T(0, 0, 0.75) @ T(shake, 0, 0)
    return [box(m @ T(0, 1.25, 0) @ S(0.08, 2.5, 1.48), rgb((130, 96, 70))), box(m @ T(-0.08, 1.15, 0.55) @ S(0.06, 0.06, 0.14), METAL)]

def tree(x, z, h=4.0, col=(214, 130, 50)):
    return [cyl(T(x, -4 + h * 0.3, z) @ S(0.3, h * 0.6, 0.3), rgb((90, 64, 46))), ball(T(x, -4 + h * 0.75, z) @ S(h * 0.7, h * 0.6, h * 0.7), rgb(col))]

def yard():
    r = random.Random(9)
    it = [box(T(-40, -4.1, 0) @ S(80, 0.2, 120), rgb((120, 120, 118)), cast=False), box(T(-6.3, -2, -1) @ S(0.2, 4.0, 14.4), rgb((200, 186, 160)), cast=False)]
    it.append(box(T(-24, -3.99, 0) @ S(14, 0.02, 30), rgb((96, 130, 80)), cast=False))
    for k in range(12): it.append(box(T(-31, -3.4, -20 + k * 4) @ S(0.08, 1.2, 0.08), METAL))
    it.append(box(T(-31, -2.9, 0) @ S(0.06, 0.06, 48), METAL))
    for k in range(14):
        z = -22 + k * 3.4 + r.uniform(-1, 1)
        it += tree(-34 - r.uniform(0, 6), z, r.uniform(3.5, 5.5), r.choice(((214, 130, 50), (196, 150, 60), (170, 100, 50))))
    it.append(box(T(-50, 2, -6) @ S(10, 12, 30), rgb((180, 166, 146))))
    for y in (0, 3, 6):
        for z in range(-18, 8, 3): it.append(box(T(-44.94, y + 0.5, z) @ S(0.04, 1.4, 1.6), rgb((140, 170, 200)), cast=False))
    return it

def facade():
    """Фасад школы со стороны двора (x≈-6.3): стены вне класса, окна, карниз, парапет."""
    F = rgb((200, 186, 160)); WIN = rgb((40, 50, 70))
    it = [box(T(-6.35, 0.1, -16) @ S(0.2, 8.2, 16), F), box(T(-6.35, 0.1, 10) @ S(0.2, 8.2, 8), F),
          box(T(-6.35, 3.9, -1) @ S(0.2, 0.6, 14.2), F), box(T(-6.5, 4.35, -5) @ S(0.5, 0.5, 40), rgb((170, 156, 132)))]
    it.append(box(T(-6.6, 0.85, -8) @ S(0.5, 0.12, 32), rgb((180, 170, 150))))                       # карниз под окнами 2 этажа
    for z in (-20, -16, -12, 9, 13):
        it.append(box(T(-6.47, 1.95, z) @ S(0.04, 1.8, 2.4), rgb((70, 90, 110)) if z == -12 else WIN, emit=0.3 if z == -12 else 0, cast=False))
    for z in (-20, -16, -12, -4.6, -0.6, 3.4, 9, 13): it.append(box(T(-6.47, -2.1, z) @ S(0.04, 1.8, 2.4), WIN, cast=False))
    return it
STAIR_Z = -12.0

def storeroom():
    """Каморка завхоза: x 30..34, z -2..2, дверь со стороны z=+2."""
    W_ = rgb((150, 156, 140)); it = [box(T(32, -0.1, 0) @ S(4.4, 0.2, 4.4), rgb((120, 110, 96)), cast=False), box(T(32, 3.0, 0) @ S(4.4, 0.2, 4.4), W_, cast=False)]
    it += [box(T(29.9, 1.5, 0) @ S(0.2, 3, 4.4), W_, cast=False), box(T(34.1, 1.5, 0) @ S(0.2, 3, 4.4), W_, cast=False), box(T(32, 1.5, -2.1) @ S(4.4, 3, 0.2), W_, cast=False)]
    for y in (0.6, 1.3, 2.0): it.append(box(T(30.4, y, 0) @ S(0.7, 0.06, 3.6), rgb((120, 90, 64))))
    for j, y in enumerate((0.75, 1.45, 2.15)):
        for k in range(3): it.append(box(T(30.4, y + 0.08, -1.2 + k * 1.1) @ S(0.5, 0.22 + 0.06 * ((j + k) % 2), 0.6), rgb((170, 130, 90)) if (j + k) % 2 else rgb((90, 110, 130))))
    for k in range(3): it.append(cyl(T(33.6, 0.9, 0.8 + k * 0.3) @ Rz(0.12) @ S(0.05, 1.8, 0.05), rgb((140, 104, 70))))
    it.append(cyl(T(33.4, 0.25, 1.5) @ S(0.5, 0.5, 0.5), rgb((70, 110, 160))))
    it.append(box(T(33.0, 1.75, -1.98) @ S(0.04, 0.04, 0.06), METAL))                                  # гвоздь
    it.append(ball(T(32, 2.85, 0) @ S(0.22), rgb((255, 230, 170)), emit=5.0, cast=False))
    return it
KEY_PT = (33.0, 1.6, -1.94)
def key(glint=1.0):
    return [box(T(33.0, 1.6, -1.95) @ S(0.1, 0.24, 0.02), rgb((230, 190, 70)), emit=0.8 * glint, cast=False), ball(T(33.0, 1.74, -1.95) @ S(0.12, 0.12, 0.03), rgb((230, 190, 70)), emit=0.8 * glint, cast=False)]
JANITOR = _c((96, 100, 92), (120, 120, 120), (60, 62, 60), skin=(190, 186, 166))
def janitor(root, t, **kw): return person(root, t, colors=JANITOR, hat="bald", **kw)

STEP_N, STEP_H, STEP_D = 16, 0.22, 0.32
def stairs():
    """Лестница на крышу: x 40..42, снизу (z=4.2) вверх по -z, площадка и дверь на крышу у z=-3.1."""
    W_ = rgb((176, 180, 170)); it = [box(T(41, -0.1, 1) @ S(2.4, 0.2, 10), rgb((130, 130, 126)), cast=False)]
    for i in range(STEP_N):
        top = (i + 1) * STEP_H; z = 4.2 - i * STEP_D
        it.append(box(T(41, top / 2, z) @ S(1.9, top, STEP_D), rgb((150, 146, 140)) if i % 2 else rgb((160, 156, 150))))
    LH = STEP_N * STEP_H
    it.append(box(T(41, LH / 2, -2.0) @ S(1.9, LH, 2.2), rgb((150, 146, 140))))
    for x in (39.95, 42.05): it.append(box(T(x, 3.0, 0.5) @ S(0.1, 7.0, 7.8), W_, cast=False))
    it.append(box(T(41, 3.0, -3.45) @ S(2.2, 7.0, 0.1), W_, cast=False)); it.append(box(T(41, 6.5, 0.5) @ S(2.2, 0.1, 7.8), W_, cast=False))
    for i in range(0, STEP_N, 2): it.append(box(T(41.85, (i + 1) * STEP_H + 0.9, 4.2 - i * STEP_D) @ S(0.05, 0.05, 0.7), METAL))   # перила
    it.append(ball(T(41, 6.3, -1.8) @ S(0.3), rgb((255, 230, 170)), emit=4.0, cast=False))
    return it
STAIR_TOP = STEP_N * STEP_H
def stair_pos(s): return 4.2 - s * (STEP_N - 0.5) * STEP_D, s * STAIR_TOP
def roof_door(a=0.0):
    m = T(41.9, STAIR_TOP, -3.1) @ Ry(a) @ T(-0.9, 0, 0)
    return [box(m @ T(0, 1.15, 0) @ S(1.7, 2.3, 0.08), rgb((90, 96, 104))), box(m @ T(0.6, 1.1, 0.06) @ S(0.08, 0.08, 0.06), METAL)]
def padlock(open_=0.0):
    p = (41.0, STAIR_TOP + 1.15, -3.0)
    return [box(T(*p) @ S(0.22, 0.2, 0.08), rgb((200, 170, 70))), box(T(p[0], p[1] + 0.16 + 0.12 * open_, p[2]) @ S(0.16, 0.14, 0.03), METAL)]

def roof_set(t):
    """Крыша школы (y=0), двор внизу (y=-8), город с дымом вдали."""
    r = random.Random(4); it = [box(T(60, -0.15, 0) @ S(16, 0.3, 16), rgb((96, 96, 100)), cast=False)]
    for (x, z, sx, sz) in ((60, -8, 16, 0.4), (60, 8, 16, 0.4), (52, 0, 0.4, 16), (68, 0, 0.4, 16)): it.append(box(T(x, 0.45, z) @ S(sx, 0.9, sz), rgb((170, 156, 132))))
    it.append(box(T(56, 1.3, 3) @ S(2.4, 2.6, 2.4), rgb((180, 168, 148)))); it.append(box(T(56, 1.15, 4.22) @ S(1.4, 2.3, 0.05), rgb((255, 240, 200)), emit=0.6, cast=False))   # будка выхода
    for (x, z) in ((63, -3), (64, 2), (58, -5)): it.append(cyl(T(x, 0.5, z) @ S(0.8, 1.0, 0.8), METAL))
    it.append(box(T(60, -8.1, 0) @ S(200, 0.2, 200), rgb((120, 120, 118)), cast=False)); it.append(box(T(60, -4, 0) @ S(15.6, 8, 15.6), rgb((200, 186, 160))))
    for k in range(22):
        x = 90 + r.uniform(0, 70); z = r.uniform(-60, 60); h = r.uniform(8, 30)
        it.append(box(T(x, h / 2 - 8, z) @ S(r.uniform(6, 12), h, r.uniform(6, 12)), rgb((150, 150, 160)) if k % 2 else rgb((130, 132, 146))))
    for c, (sx, sz) in enumerate(((120, -20), (140, 25), (105, 10))):
        for k in range(14):
            ph = (t * 0.12 + k / 14 + c * 0.3) % 1.0
            it.append(ball(T(sx + 6 * ph + 2 * math.sin(k), 10 + ph * 40, sz + 3 * math.cos(k)) @ S(4 + ph * 12), rgb((60, 58, 60)), cast=False))
    return it
