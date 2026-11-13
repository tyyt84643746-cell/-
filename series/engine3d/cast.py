"""Сезон 2: персонажи и предметы поверх models.py."""
import math, random
from models import *

def _c(body, hat, legs=(40, 46, 68), pack=None):
    b = rgb(body); h = rgb(hat)
    return dict(body=b, body_d=tuple(v * 0.7 for v in b), hat=h, hat_b=tuple(min(1, v * 1.3) for v in h), legs=rgb(legs), pack=pack)

COL = dict(
    granny=_c((52, 80, 64), (150, 76, 74), (54, 48, 60)),
    kolyan=_c((84, 92, 62), (140, 62, 58), (50, 52, 58)),
    nina=_c((150, 130, 180), (206, 206, 214), (70, 66, 84)),
    kirill=_c((58, 62, 72), (22, 22, 28), (36, 38, 46)),
    sonya=_c((232, 140, 170), (240, 240, 244), (90, 80, 110)),
    mother=_c((44, 54, 96), (120, 124, 136), (36, 40, 60)),
    stranger=_c((30, 30, 36), (22, 22, 26), (24, 24, 30)),
    ded=_c((112, 104, 92), (70, 60, 50), (60, 56, 52)),
    guest=_c((98, 104, 114), (52, 46, 44), (44, 46, 54)),
)
_CROWD = [((96, 78, 70), (60, 66, 90)), ((70, 84, 100), (120, 70, 60)), ((110, 96, 80), (50, 60, 56)), ((80, 70, 96), (90, 96, 110)),
          ((66, 90, 84), (36, 40, 52)), ((120, 84, 70), (70, 74, 60)), ((84, 88, 100), (150, 120, 70)), ((100, 70, 76), (44, 48, 70))]

def artyom(root, t, **kw): return person(root, t, **kw)
def granny(root, t, **kw): return person(root, t, colors=COL["granny"], hat="scarf", skirt=rgb((54, 48, 60)), scale=0.9, **kw)
def kolyan(root, t, **kw): return person(root, t, colors=COL["kolyan"], hat="pompom", **kw)
def nina(root, t, **kw): return person(root, t, colors=COL["nina"], hat="bun", skirt=rgb((70, 66, 84)), scale=0.88, **kw)
def kirill(root, t, **kw): return person(root, t, colors=COL["kirill"], beard=rgb((40, 32, 28)), **kw)
def sonya(root, t, **kw): return person(root, t, colors=COL["sonya"], scale=0.58, **kw)
def mother(root, t, **kw): return person(root, t, colors=COL["mother"], hat="scarf", **kw)
def stranger(root, t, **kw): return person(root, t, colors=dict(COL["stranger"], skin=rgb((84, 70, 66))), face=False, **kw)
def ded(root, t, **kw): return person(root, t, colors=COL["ded"], **kw)
def guest(root, t, **kw): return person(root, t, colors=COL["guest"], beard=rgb((150, 150, 156)), **kw)
def villager(j, root, t, **kw):
    b, h = _CROWD[j % len(_CROWD)]
    return person(root, t, colors=_c(b, h), hat=("beanie", "scarf", "pompom")[j % 3], scale=0.92 + 0.05 * (j % 4), **kw)

def cat2(root, t, look=0.0, hiss=False):
    """Кекс; hiss — выгнул спину, хвост трубой."""
    if not hiss: return cat(root, t, look)
    it = []; sh = 0.012 * math.sin(t * 40)
    it.append(ball(root @ T(sh, 0.34, 0) @ S(0.3, 0.42, 0.46), C["cat"]))
    for sx in (-0.1, 0.1):
        for sz in (-0.14, 0.16): it.append(cyl(root @ T(sx, 0.1, sz) @ S(0.07, 0.2, 0.07), C["cat"]))
    h = root @ T(sh, 0.5, 0.26) @ Ry(look)
    it.append(ball(h @ S(0.3, 0.27, 0.27), C["cat"]))
    for sx in (-0.1, 0.1):
        it.append(cone(h @ T(sx, 0.13, -0.04) @ Rz(-sx * 5) @ Rx(-0.5) @ S(0.1, 0.13, 0.08), C["cat"]))
        it.append(ball(h @ T(sx * 0.7, 0.01, 0.13) @ S(0.05, 0.03, 0.03), C["eye"], cast=False))
    it.append(ball(h @ T(0, -0.07, 0.13) @ S(0.07, 0.05, 0.03), rgb((150, 60, 70)), cast=False))
    it.append(cyl(root @ T(0, 0.42, -0.2) @ Rx(-0.5) @ T(0, 0.22, 0) @ S(0.12, 0.46, 0.12), C["cat"]))
    return it

def house2(root, seed=0):
    rnd = random.Random(seed); it = []
    w, d = rnd.uniform(4.2, 5.4), rnd.uniform(3.2, 3.8)
    for k in range(6): it.append(box(root @ T(0, 0.2 + k * 0.38, 0) @ S(w, 0.36, d), C["log"] if k % 2 == 0 else C["log_d"]))
    it.append(prism(root @ T(0, 3.2, 0) @ S(w + 0.6, 1.5, d + 0.8), C["roof"]))
    it.append(prism(root @ T(0, 3.32, 0) @ S(w + 0.65, 1.36, d + 0.5), C["snow"]))
    it.append(box(root @ T(-1.2, 3.6, -0.4) @ S(0.45, 1.2, 0.45), C["log_d"]))
    for x in (-1.2, 1.2):
        it.append(box(root @ T(x, 1.3, d / 2 + 0.01) @ S(0.9, 1.0, 0.06), rgb((26, 30, 44)), cast=False))
        it.append(box(root @ T(x, 1.3, d / 2 + 0.04) @ S(1.05, 0.07, 0.06), C["snow"]))
        it.append(box(root @ T(x, 1.3, d / 2 + 0.04) @ S(0.07, 1.1, 0.06), C["snow"]))
    return it

def barn(root):
    it = [box(root @ T(0, 2.2, 0) @ S(10, 4.4, 7), rgb((104, 84, 70)))]
    for k in range(9): it.append(box(root @ T(-4.4 + k * 1.1, 2.2, 3.51) @ S(0.08, 4.4, 0.04), rgb((80, 62, 52)), cast=False))
    it.append(prism(root @ T(0, 5.5, 0) @ S(10.8, 2.2, 7.8), C["roof"]))
    it.append(prism(root @ T(0, 5.64, 0) @ S(10.85, 2.0, 7.4), C["snow"]))
    it.append(box(root @ T(0, 1.5, 3.52) @ S(3.0, 3.0, 0.06), rgb((6, 6, 9)), cast=False))
    for sx in (-1, 1): it.append(box(root @ T(sx * 2.25, 1.5, 3.7) @ Ry(sx * 0.5) @ S(1.5, 3.0, 0.1), rgb((84, 66, 54))))
    return it

def pole(x, z, h=6.0):
    return [cyl(T(x, h / 2, z) @ S(0.16, h, 0.16), C["log_d"]), box(T(x, h - 0.5, z) @ S(0.1, 0.1, 1.4), C["log_d"])]

def wires(x0, x1, z, h=5.5):
    it = []
    for dz in (-0.6, 0.6): it.append(box(T((x0 + x1) / 2, h, z + dz) @ S(x1 - x0, 0.025, 0.025), C["dark"], cast=False))
    return it

def hatch(root, a=0.0, glow=0.0):
    """Люк погреба: рама 1.5x1.5, крышка на петлях сзади, a — угол открытия."""
    it = []; W_ = rgb((112, 84, 60)); D_ = rgb((84, 60, 44))
    for sx in (-0.75, 0.75): it.append(box(root @ T(sx, 0.16, 0) @ S(0.16, 0.32, 1.66), D_))
    for sz in (-0.75, 0.75): it.append(box(root @ T(0, 0.16, sz) @ S(1.66, 0.32, 0.16), D_))
    it.append(box(root @ T(0, 0.02, 0) @ S(1.4, 0.03, 1.4), rgb((250, 190, 110)) if glow > 0 else C["dark"], emit=glow, cast=False))
    lid = root @ T(0, 0.34, -0.8) @ Rx(-a) @ T(0, 0, 0.8)
    it.append(box(lid @ S(1.6, 0.08, 1.6), W_))
    for k in range(4): it.append(box(lid @ T(-0.6 + k * 0.4, 0.045, 0) @ S(0.03, 0.02, 1.6), D_, cast=False))
    it.append(box(lid @ T(0, 0.06, 0.4) @ S(1.6, 0.05, 0.1), rgb((60, 62, 70))))
    it.append(box(lid @ T(0, 0.06, -0.4) @ S(1.6, 0.05, 0.1), rgb((60, 62, 70))))
    if a < 0.5: it.append(ball(lid @ T(0.3, 0.1, 0.2) @ S(1.0, 0.16, 0.9), C["snow"]))
    return it

def doghouse(root, t):
    it = [box(root @ T(0, 0.45, 0) @ S(1.1, 0.9, 1.3), C["log"]), prism(root @ T(0, 1.2, 0) @ Ry(math.pi / 2) @ S(1.5, 0.6, 1.3), C["snow"]),
          box(root @ T(0, 0.35, 0.66) @ S(0.5, 0.6, 0.04), C["dark"], cast=False)]
    d = root @ T(1.3, 0, 0.5)
    it.append(ball(d @ T(0, 0.2, 0) @ S(0.4, 0.34, 0.8), rgb((70, 60, 54))))
    it.append(ball(d @ T(0, 0.22, 0.48) @ S(0.3, 0.26, 0.34), rgb((70, 60, 54))))
    it.append(ball(d @ T(0, 0.18, 0.66) @ S(0.16, 0.13, 0.2), rgb((40, 34, 32))))
    return it

def phone(m, on=True):
    return [box(m @ S(0.16, 0.3, 0.03), C["dark"]), box(m @ T(0, 0, 0.017) @ S(0.13, 0.26, 0.004), rgb((190, 215, 255)), emit=1.2 if on else 0, cast=False)]

def radio(m):
    return [box(m @ S(0.5, 0.3, 0.18), rgb((120, 60, 50))), box(m @ T(-0.1, 0, 0.095) @ S(0.22, 0.2, 0.01), rgb((30, 30, 34)), cast=False),
            cyl(m @ T(0.2, 0.4, 0) @ Rz(-0.3) @ S(0.02, 0.6, 0.02), C["metal"])]


def envelope(m):
    return [box(m @ S(0.3, 0.2, 0.012), rgb((238, 232, 214)), emit=0.25), box(m @ T(0, 0.03, 0.008) @ S(0.3, 0.012, 0.004), rgb((170, 160, 140)), cast=False)]

def city(seed=4):
    """Пустая улица города вдоль оси Z: дома без света, машина под снегом, следы."""
    rnd = random.Random(seed); it = [box(T(0, -0.25, -40) @ S(200, 0.5, 240), C["snow"])]
    it.append(box(T(0, 0.012, -40) @ S(9, 0.02, 240), rgb((190, 198, 218)), cast=False))
    for side in (-1, 1):
        z = 16.0
        while z > -120:
            w = rnd.uniform(9, 14); h = rnd.uniform(11, 26); d = rnd.uniform(8, 12); x = side * (9 + d / 2 + rnd.uniform(0, 2))
            col = rgb(rnd.choice(((108, 112, 126), (124, 116, 110), (96, 104, 112), (130, 126, 134))))
            it.append(box(T(x, h / 2, z - w / 2) @ S(d, h, w), col))
            it.append(box(T(x, h + 0.2, z - w / 2) @ S(d + 0.3, 0.4, w + 0.3), C["snow"]))
            fx = x - side * (d / 2 + 0.02)
            for fy in range(int(h // 3)):
                for fz in range(int(w // 3)):
                    it.append(box(T(fx, 2.2 + fy * 3, z - 1.8 - fz * 3) @ S(0.04, 1.5, 1.6), rgb((20, 24, 36)), cast=False))
            z -= w + rnd.uniform(1.5, 4)
    for z in range(8, -100, -14):                                              # погасшие фонари
        for side in (-1, 1):
            it.append(cyl(T(side * 5.4, 3, z) @ S(0.14, 6, 0.14), C["dark"])); it.append(box(T(side * 4.8, 6, z) @ S(1.3, 0.12, 0.2), C["dark"]))
    car = T(2.6, 0, -6) @ Ry(0.12)
    it += [box(car @ T(0, 0.55, 0) @ S(1.8, 0.7, 4.2), rgb((120, 40, 40))), box(car @ T(0, 1.2, -0.2) @ S(1.6, 0.7, 2.2), rgb((30, 34, 46))),
           ball(car @ T(0, 1.55, -0.2) @ S(1.9, 0.5, 2.6), C["snow"]), ball(car @ T(0, 0.92, 1.5) @ S(1.8, 0.3, 1.3), C["snow"])]
    for k in range(70):                                                         # следы уходят вдаль
        for lane, ph in ((-1.6, 0.0), (-0.4, 1.3), (0.9, 2.1)):
            x = lane + 0.5 * math.sin(k * 0.21 + ph) + (0.16 if k % 2 else -0.16)
            it.append(box(T(x, 0.025, 10 - k * 0.75 - ph) @ S(0.18, 0.02, 0.36), rgb((150, 158, 182)), cast=False))
    return it
