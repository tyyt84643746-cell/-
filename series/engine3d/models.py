"""3D-модели персонажей и окружения из примитивов. Каждая функция возвращает список items для Renderer.render()."""
import math, random
from engine import *

C = {k: rgb(v) for k, v in dict(
    yellow=(246, 194, 42), yellow_d=(214, 160, 28), skin=(241, 203, 168), beanie=(40, 52, 104), beanie_b=(52, 68, 128),
    pants=(40, 46, 68), shoe=(26, 26, 34), pack=(106, 112, 126), eye=(20, 20, 26), brow=(70, 46, 34), cheek=(236, 160, 150),
    snow=(222, 230, 245), log=(118, 82, 56), log_d=(92, 62, 44), roof=(70, 74, 92), window=(255, 190, 100), pine=(34, 64, 58),
    fence=(120, 94, 70), dirt=(92, 68, 52), dark=(14, 12, 14), metal=(150, 156, 172), wood=(140, 104, 70), cat=(206, 132, 70),
    cat_w=(240, 232, 220), lamp=(255, 246, 214)).items()}


def box(m, col, emit=0.0, cast=True): return ("cube", m, col, emit, cast)
def ball(m, col, emit=0.0, cast=True): return ("sphere", m, col, emit, cast)
def cyl(m, col, emit=0.0, cast=True): return ("cyl", m, col, emit, cast)
def cone(m, col, emit=0.0, cast=True): return ("cone", m, col, emit, cast)
def prism(m, col, emit=0.0, cast=True): return ("prism", m, col, emit, cast)


def person(root, t, walk=None, look=0.0, blink_seed=0.0, lamp=False, arm=None, colors=None, face=True, mouth=None, hat="beanie", scale=1.0, out=None, beard=None, skirt=None):
    """Стилизованный человек (голова крупная). root — 4x4 (позиция ног, поворот). arm: None | 'dig' | 'wave' | 'up'."""
    col = dict(body=C["yellow"], body_d=C["yellow_d"], legs=C["pants"], hat=C["beanie"], hat_b=C["beanie_b"], pack=C["pack"], skin=C["skin"])
    if colors: col.update(colors)
    R = root @ S(scale)
    it = []
    breath = 0.015 * math.sin(t * 2.2)
    ph = walk if walk is not None else 0.0
    sw = math.sin(ph) * 0.55 if walk is not None else 0.0
    bob = abs(math.sin(ph)) * 0.04 if walk is not None else 0.0
    B = R @ T(0, bob, 0)
    for sx, k in ((-0.14, 1), (0.14, -1)):
        leg = B @ T(sx, 0.82, 0) @ Rx(sw * k) @ T(0, -0.41, 0)
        it.append(box(leg @ S(0.22, 0.82, 0.24), col["legs"]))
        it.append(box(leg @ T(0, -0.36, 0.05) @ S(0.25, 0.14, 0.34), C["shoe"]))
    torso = B @ T(0, 1.26 + breath, 0)
    it.append(box(torso @ S(0.64, 0.86, 0.42), col["body"]))
    it.append(box(torso @ T(0, -0.38, 0) @ S(0.66, 0.1, 0.44), col["body_d"]))
    it.append(box(torso @ T(0, 0, 0.212) @ S(0.03, 0.8, 0.01), col["body_d"]))
    if col["pack"] is not None: it.append(box(torso @ T(0, 0.06, -0.32) @ S(0.5, 0.62, 0.24), col["pack"]))
    for sx, k in ((-0.42, 1), (0.42, -1)):
        rx, rz = sw * k, 0.0
        if arm == "dig": rx = 0.9 - 0.35 * math.sin(t * 4.5)
        elif arm == "wave" and k < 0: rz = math.pi * 0.85 + 0.25 * math.sin(t * 9)
        elif arm == "up" and k < 0: rz = math.pi * 0.9
        elif arm == "phone" and k < 0: rx, rz = -1.15 + 0.03 * math.sin(t * 1.7), -0.3
        elif arm == "point" and k < 0: rx, rz = -2.45 + 0.04 * math.sin(t * 3), -0.5
        elif arm == "hold": rx = -0.75
        elif arm == "hands_up": rz = (2.6 + 0.04 * math.sin(t * 5)) * (1 if k < 0 else -1)
        sh = torso @ T(sx, 0.34, 0) @ Rz(rz) @ Rx(rx)
        it.append(box(sh @ T(0, -0.34, 0) @ S(0.18, 0.72, 0.2), col["body"]))
        it.append(ball(sh @ T(0, -0.74, 0) @ S(0.16), col["skin"]))
        if out is not None and k < 0: out["hand"] = sh @ T(0, -0.74, 0)
    it.append(box(torso @ T(0, 0.45, -0.08) @ S(0.5, 0.14, 0.3), col["body_d"]))
    head = B @ T(0, 2.02 + breath * 1.5, 0) @ Ry(look * 0.6)
    it.append(ball(head @ S(0.64, 0.62, 0.6), col["skin"]))
    if hat == "beanie":
        it.append(ball(head @ T(0, 0.17, -0.02) @ S(0.68, 0.5, 0.64), col["hat"]))
        it.append(cyl(head @ T(0, 0.13, -0.01) @ S(0.69, 0.1, 0.65), col["hat_b"]))
    elif hat == "pompom":
        it.append(ball(head @ T(0, 0.17, -0.02) @ S(0.68, 0.5, 0.64), col["hat"]))
        it.append(cyl(head @ T(0, 0.13, -0.01) @ S(0.69, 0.1, 0.65), col["hat_b"]))
        it.append(ball(head @ T(0, 0.46, -0.02) @ S(0.2), C["cat_w"]))
    elif hat == "scarf":
        it.append(ball(head @ T(0, 0.07, -0.09) @ S(0.74, 0.68, 0.62), col["hat"]))
        it.append(ball(head @ T(0, -0.3, 0.2) @ S(0.2, 0.14, 0.14), col["hat_b"]))
    elif hat == "bun":
        it.append(ball(head @ T(0, 0.12, -0.08) @ S(0.68, 0.54, 0.58), col["hat"]))
        it.append(ball(head @ T(0, 0.2, -0.34) @ S(0.24), col["hat"]))
    if beard is not None: it.append(ball(head @ T(0, -0.2, 0.17) @ S(0.44, 0.3, 0.3), beard))
    if skirt is not None: it.append(box(B @ T(0, 0.6, 0) @ S(0.62, 0.62, 0.42), skirt))
    if lamp:
        it.append(cyl(head @ T(0, 0.14, 0.32) @ Rx(math.pi / 2) @ S(0.1, 0.05, 0.1), C["lamp"], emit=3.0, cast=False))
    if face:
        bl = ((t + blink_seed) % 3.4) < 0.13
        for sx in (-0.11, 0.11):
            it.append(ball(head @ T(sx, -0.05, 0.29) @ S(0.07, 0.012 if bl else 0.075, 0.04), C["eye"], cast=False))
            it.append(box(head @ T(sx, 0.04, 0.295) @ Rz(0.15 if sx > 0 else -0.15) @ S(0.1, 0.02, 0.02), C["brow"], cast=False))
            it.append(ball(head @ T(sx * 1.6, -0.1, 0.25) @ S(0.08, 0.05, 0.03), C["cheek"], cast=False))
        if mouth == "o": it.append(ball(head @ T(0, -0.16, 0.29) @ S(0.06, 0.07, 0.03), C["eye"], cast=False))
        elif mouth == "smile": it.append(box(head @ T(0, -0.16, 0.29) @ S(0.12, 0.025, 0.02), C["eye"], cast=False))
    return it, head


def cat(root, t, look=0.0):
    it = []
    tw = 0.4 * math.sin(t * 1.9)
    it.append(ball(root @ T(0, 0.22, 0) @ S(0.3, 0.32, 0.42), C["cat"]))
    it.append(ball(root @ T(0, 0.22, 0.12) @ S(0.2, 0.24, 0.2), C["cat_w"]))
    h = root @ T(0, 0.5, 0.12) @ Ry(look)
    it.append(ball(h @ S(0.3, 0.27, 0.27), C["cat"]))
    for sx in (-0.09, 0.09):
        it.append(cone(h @ T(sx, 0.15, 0) @ Rz(-sx * 2) @ S(0.1, 0.14, 0.08), C["cat"]))
        it.append(ball(h @ T(sx * 0.7, 0.01, 0.13) @ S(0.045), C["eye"], cast=False))
    it.append(cyl(root @ T(0, 0.2, -0.22) @ Rx(-0.8 + tw * 0.3) @ Rz(tw) @ T(0, 0.2, 0) @ S(0.07, 0.42, 0.07), C["cat"]))
    return it


def house(root, lit=True):
    it = []
    for k in range(7):
        it.append(box(root @ T(0, 0.2 + k * 0.38, 0) @ S(5.2, 0.36, 3.6), C["log"] if k % 2 == 0 else C["log_d"]))
    it.append(prism(root @ T(0, 3.8, 0) @ S(5.8, 1.6, 4.4), C["roof"]))
    it.append(prism(root @ T(0, 3.92, 0) @ S(5.85, 1.45, 4.1), C["snow"]))
    it.append(box(root @ T(1.4, 4.2, -0.6) @ S(0.5, 1.4, 0.5), C["log_d"]))
    for x in (-1.5, 1.5):
        it.append(box(root @ T(x, 1.5, 1.81) @ S(1.0, 1.1, 0.06), C["window"], emit=1.6 if lit else 0.0, cast=False))
        it.append(box(root @ T(x, 1.5, 1.84) @ S(1.15, 0.08, 0.06), C["snow"]))
        it.append(box(root @ T(x, 1.5, 1.84) @ S(0.08, 1.2, 0.06), C["snow"]))
    it.append(box(root @ T(0, 1.0, 1.82) @ S(0.9, 2.0, 0.08), C["log_d"]))
    return it


def pine(root, h=4.0, snow=True):
    it = [cyl(root @ T(0, 0.4, 0) @ S(0.25, 0.8, 0.25), C["log_d"])]
    for k in range(3):
        y = 0.8 + k * h * 0.25; r = (1.6 - k * 0.4) * h / 4
        it.append(cone(root @ T(0, y + h * 0.18, 0) @ S(r * 2, h * 0.38, r * 2), C["pine"]))
        if snow: it.append(cone(root @ T(0, y + h * 0.28, 0) @ S(r * 1.1, h * 0.18, r * 1.1), C["snow"]))
    return it


def fence(x0, x1, z, rnd=None):
    rnd = rnd or random.Random(3); it = []
    x = x0
    while x < x1:
        tilt = rnd.uniform(-0.08, 0.08)
        it.append(box(T(x, 0.6, z) @ Rz(tilt) @ S(0.16, 1.2, 0.08), C["fence"]))
        it.append(box(T(x, 1.24, z) @ S(0.18, 0.08, 0.1), C["snow"]))
        x += 0.32
    for y in (0.4, 0.95): it.append(box(T((x0 + x1) / 2, y, z - 0.07) @ S(x1 - x0, 0.1, 0.05), C["fence"]))
    return it


def shovel(m):
    return [cyl(m @ S(0.05, 1.4, 0.05), C["wood"]), box(m @ T(0, -0.8, 0) @ S(0.3, 0.36, 0.03), C["metal"])]
