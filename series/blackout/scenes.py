"""Сцены серии 1. Каждая сцена: setup() один раз, frame(t) -> (RGBA кадр, zoom, яркость)."""
import json, math, os, random, re
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from art import *
from script import SCENES, CAPTION_NUMS

D = os.path.dirname(os.path.abspath(__file__))
FPS = 30; LEAD = 0.4; TAIL = 1.0
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ALN = [json.load(open(f"{D}/v{i}.json")) for i in range(1, 10)]
NFR = [round((a["character_end_times_seconds"][-1] + LEAD + TAIL) * FPS) for a in ALN]
DUR = [n / FPS for n in NFR]
STARTS = [sum(DUR[:i]) for i in range(9)]


def wt(i, sub, end=False):
    """Время (сек от начала сцены i), когда диктор произносит sub."""
    text = SCENES[i]["text"]; k = text.find(sub)
    assert k >= 0, (i, sub)
    a = ALN[i]
    v = a["character_end_times_seconds"][k + len(sub) - 1] if end else a["character_start_times_seconds"][k]
    return v + LEAD


def walls_dark(img, k):
    a = np.asarray(img).astype(np.float32); a[..., :3] *= k
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def font(sz): return ImageFont.truetype(FB, sz)


# ======================================================================= МЕТРО (сцены 1–3)
class Metro:
    def __init__(s):
        WW = W + 240; s.WW = WW
        s.tunnel = vgrad(WW, H, [(0, (6, 9, 18)), (1, (10, 14, 26))])
        wins = [(60, 420, 420, 860), (500, 420, 860, 860), (940, 420, 1300, 860)]
        s.wins = wins
        wall = vgrad(WW, H, [(0, (22, 32, 60)), (0.16, (48, 66, 110)), (0.55, (40, 58, 98)), (1, (18, 26, 48))])
        mask = Image.new("L", (WW * 2, H * 2), 255); md = ImageDraw.Draw(mask)
        for x0, y0, x1, y1 in wins: md.rounded_rectangle([x0 * 2, y0 * 2, x1 * 2, y1 * 2], radius=80, fill=0)
        wall.putalpha(mask.resize((WW, H), Image.LANCZOS))
        def deco(p):
            for x0, y0, x1, y1 in wins:
                p.rr(x0 - 14, y0 - 14, x1 + 14, y1 + 14, 52, None, (88, 106, 146), 10)
            p.rr(-20, 236, WW + 20, 292, 20, (64, 82, 124))                       # потолочная панель
            p.rr(0, 320, WW, 338, 9, (150, 162, 186))                              # поручень
            for x in range(80, WW, 170): p.line([(x, 338), (x, 380)], (150, 162, 186), 8)
            p.rect(0, 950, WW, 985, (58, 78, 120))                                 # полоса на стене
        wall.alpha_composite(layer(WW, H, deco))
        s.wall = wall
        lamps = Image.new("RGBA", (WW, H), (0, 0, 0, 0))
        for x in range(0, WW, 60): glow(lamps, x, 262, 120, WARM, 0.22, 1.6)
        lamps.alpha_composite(layer(WW, H, lambda p: p.rr(-20, 248, WW + 20, 276, 14, (255, 240, 205))))
        s.lamps = lamps
        def mid(p):
            p.rr(-40, 1180, WW + 40, 1260, 26, (54, 74, 118))                       # спинка дивана
            p.rr(-40, 1250, WW + 40, 1340, 22, (44, 62, 102))
            p.rect(-40, 1340, WW + 40, H, (26, 36, 62))                             # пол
            p.rect(-40, 1340, WW + 40, 1352, (70, 88, 128))
            rnd = random.Random(5)
            for x in (110, 300, 980, 1150):
                passenger(p, x, 1270, 1.15, mixc((44, 56, 92), (60, 70, 104), rnd.random()))
            for x in (820,):
                passenger(p, x, 1500, 1.45, (40, 52, 86), seated=False)
            for x in (250, 1000):
                p.line([(x, 338), (x, 1340)], (150, 162, 186), 16, round_caps=False)
                p.line([(x - 4, 338), (x - 4, 1340)], (196, 206, 224), 4, round_caps=False)
        s.mid = layer(WW, H, mid)
        def fg(p):
            p.line([(70, -20), (70, H + 20)], (14, 20, 36), 44, round_caps=False)
            for x in (40, 230):
                p.line([(x, 330), (x, 420)], (20, 28, 48), 10)
                p.el(x - 34, 410, x + 34, 490, None, (20, 28, 48), 12)
        s.fg = layer(WW, H, fg)
        s.streak_rnd = [(random.random() * WW, random.uniform(470, 820), random.uniform(80, 260)) for _ in range(14)]
        s.dark_bg = None

    def background(s, t, lamp_b=1.0, pan=0.0, sway=True, streaks=True):
        img = s.tunnel.copy(); d = ImageDraw.Draw(img)
        if streaks:
            for x, y, ln in s.streak_rnd:
                xx = (x - t * 2600) % (s.WW + 600) - 300
                d.rounded_rectangle([xx, y, xx + ln, y + 6], radius=3, fill=(120, 110, 90))
        dy = 3 * math.sin(t * 3.1) if sway else 0
        img.alpha_composite(s.wall, (0, 0))
        if lamp_b > 0.02:
            if lamp_b >= 0.99: img.alpha_composite(s.lamps)
            else:
                l = np.asarray(s.lamps).copy(); l[..., 3] = (l[..., 3] * lamp_b).astype(np.uint8)
                img.alpha_composite(Image.fromarray(l, "RGBA"))
        out = Image.new("RGBA", (W, H))
        ox = -120 + pan
        out.alpha_composite(img.crop((int(-ox * 0.6) , 0, int(-ox * 0.6) + W, H)))
        comp(out, s.mid, ox, dy)
        return out, dy

    def foreground(s, out, pan, dy): comp(out, s.fg, -120 + pan * 1.35, dy * 1.4)


METRO = None
def metro():
    global METRO
    if METRO is None: METRO = Metro()
    return METRO


def flick(t, wins):
    for a, b in wins:
        if a <= t < b: return 0.18
    return 1.0


def scene1(t):
    m = metro(); dur = DUR[0]
    lb = flick(t, [(1.5, 1.62), (1.75, 2.1), (3.1, 3.22)])
    img, dy = m.background(t, lb, pan=10 * math.sin(t * 0.4))
    worried = t > 1.5
    hero(img, 540, 1560 + dy, 1.32, t, look=(0.15, -0.9) if worried else (0.3, 0.1),
         brows="worried" if worried else "calm", mouth="o" if 1.6 < t < 3.0 else None)
    m.foreground(img, 0, dy)
    return img, lerp(1.14, 1.0, ease(t / dur)), 0.55 + 0.45 * lb


def scene2(t):
    m = metro(); dur = DUR[1]; tm = wt(1, "мигает")
    lb = 1.0
    if t > tm - 0.3:
        lb = flick(t - tm, [(0.0, 0.12), (0.25, 0.5), (0.7, 0.78)])
        if t > dur - 0.5: lb = 0.0
    pan = lerp(-40, 40, ease(t / dur))
    img, dy = m.background(t, lb, pan=pan)
    look = (math.sin(t * 0.7) * 0.6, 0.4) if t < tm else (0.2, -0.9)
    hero(img, 560 + pan, 1560 + dy, 1.32, t, look=look, arm="phone", phone_on=True,
         brows="worried" if t > tm else "calm", mouth="o" if t > tm + 0.2 else None)
    hp = (560 + pan + 27 * 1.32, 1560 + dy - 306 * 1.32)
    glow(img, hp[0], hp[1], 90, (190, 215, 255), 0.35)
    m.foreground(img, pan, dy)
    return img, lerp(1.0, 1.06, ease(t / dur)), (0.55 + 0.45 * lb) if t > tm - 0.3 else 1.0


def scene3(t):
    m = metro(); dur = DUR[2]; tl = wt(2, "фонарик")
    if m.dark_bg is None:
        bg, _ = m.background(0, 0.0, pan=0, sway=False, streaks=False)
        m.foreground(bg, 0, 0)
        m.dark_bg = walls_dark(bg, 0.26)
        # луч фонарика: мягкий конус влево-вниз
        beam = Image.new("RGBA", (W, H), (0, 0, 0, 0)); bd = ImageDraw.Draw(beam)
        ax, ay = 540, 1560 - 512 * 1.32
        bd.polygon([(ax, ay), (-160, 1050), (260, 1480)], fill=(255, 240, 200, 70))
        bd.ellipse([-80, 1180, 360, 1420], fill=(255, 240, 200, 60))
        m.beam = beam.filter(ImageFilter.GaussianBlur(28))
        m.motes = [(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 6.28)) for _ in range(26)]
    img = m.dark_bg.copy()
    blink = (t % 1.2) < 0.6
    glow(img, 940, 300, 160, RED, 0.45 if blink else 0.15)
    glow(img, 940, 300, 26, (255, 120, 110), 1.0 if blink else 0.3)
    on = t > tl + 0.25 and not (tl + 0.35 < t < tl + 0.45)
    if on:
        img.alpha_composite(m.beam)
        d = ImageDraw.Draw(img)
        ax, ay = 540, 1560 - 512 * 1.32
        for u, v, ph in m.motes:
            k = (u + t * 0.05) % 1.0
            x = lerp(ax, lerp(-100, 300, v), k) + 6 * math.sin(t + ph); y = lerp(ay, lerp(1060, 1460, v), k)
            d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(255, 240, 210, 140))
    pts = hero(img, 540, 1560, 1.32, t, look=(-0.6, 0.3) if on else (0.5, -0.3), lamp=t > tl,
               brows="worried", dark=0.95 if on else 0.42, mouth=None if on else "flat")
    lamp_glow(img, pts["lamp"], on, size=1.32)
    card(img, t, wt(2, "Так уже было") - 0.1, "", "ЧАГИНО · МАЙ 2005")
    return img, lerp(1.0, 1.12, ease(t / dur)), 1.0


# ======================================================================= УЛИЦА (сцена 4)
class Street:
    def __init__(s):
        WW = W + 700; s.WW = WW
        s.sky = vgrad(W, H, [(0, (5, 8, 20)), (0.45, (16, 24, 50)), (0.62, (34, 32, 62)), (1, (20, 24, 44))])
        rnd = random.Random(11)
        def far(p):
            for _ in range(60):
                x, y = rnd.uniform(0, WW), rnd.uniform(60, 700); p.circ(x, y, rnd.uniform(1, 2.6), (150, 160, 190))
            x = -40
            while x < WW:
                w = rnd.randint(150, 260); h = rnd.randint(420, 760); top = 1260 - h
                p.rr(x, top, x + w, 1300, 10, (14, 20, 40))
                for wy in range(top + 34, 1240, 52):
                    for wx in range(x + 20, x + w - 24, 40): p.rr(wx, wy, wx + 20, wy + 28, 4, (22, 30, 54))
                x += w + rnd.randint(14, 40)
        s.far = layer(WW, H, far)
        def mid(p):
            p.rect(-40, 1250, WW + 40, H, (58, 68, 100))
            p.rr(-40, 1236, WW + 40, 1270, 16, (196, 206, 226))                     # снег у дороги
            p.rect(-40, 1330, WW + 40, 1530, (30, 36, 58))                          # дорога
            p.rr(-40, 1518, WW + 40, 1548, 14, (176, 188, 212))
            for x in range(0, WW, 140): p.rr(x, 1424, x + 70, 1434, 4, (70, 78, 104))
            # светофор без света
            p.line([(1180, 1250), (1180, 760)], (60, 68, 94), 16, round_caps=False)
            p.rr(1146, 700, 1214, 900, 18, (28, 32, 48))
            for k, yy in enumerate((738, 800, 862)): p.circ(1180, yy, 22, (44, 46, 60))
            p.rr(1140, 690, 1220, 706, 8, SNOW)
            # знак метро без подсветки
            p.line([(260, 1250), (260, 860)], (60, 68, 94), 14, round_caps=False)
            p.circ(260, 820, 62, (52, 58, 82)); p.text(222, 776, "М", font(80), (96, 52, 60))
            # машины в пробке
            for cx, col in ((520, (40, 48, 74)), (930, (52, 46, 66)), (1480, (36, 52, 70))):
                p.rr(cx - 150, 1380, cx + 150, 1480, 34, col)
                p.rr(cx - 90, 1330, cx + 80, 1400, 30, mixc(col, (0, 0, 0), 0.2))
                p.rr(cx - 76, 1342, cx + 66, 1392, 18, (20, 26, 44))
                p.circ(cx - 96, 1486, 26, (16, 18, 26)); p.circ(cx + 96, 1486, 26, (16, 18, 26))
                p.rr(cx - 150, 1370, cx + 150, 1386, 8, SNOW)
        s.mid = layer(WW, H, mid)
        s.cars = (520, 930, 1480)
        def fg(p):
            p.el(-200, 1720, 420, 2100, (214, 222, 238)); p.el(760, 1760, 1500, 2160, (200, 210, 230))
            p.el(1500, 1700, 2000, 2140, (214, 222, 238))
        s.fg = layer(WW + 300, H, fg)
        s.snow_far = Snow(110, 3, (1.2, 2.6), (40, 90)); s.snow_near = Snow(36, 4, (4, 8), (140, 240))

STREET = None
def scene4(t):
    global STREET
    if STREET is None: STREET = Street()
    s = STREET; dur = DUR[3]
    hx = lerp(320, 900, t / dur)                   # мировая координата героя
    cam = (hx - 540) * 0.85
    img = s.sky.copy()
    s.snow_far.draw(img, t, 160)
    comp(img, s.far, -cam * 0.35 - 100, 0)
    comp(img, s.mid, -cam - 100, 0)
    blink = (t % 0.9) < 0.45
    for cx in s.cars:
        for dx in (-140, 140):
            x = cx - cam - 100 + dx
            glow(img, x, 1440, 60, AMBER, 0.55 if blink else 0.12)
            glow(img, x, 1440, 12, (255, 220, 150), 1.0 if blink else 0.4)
    sx = hx - cam
    tn = wt(3, "не находит")
    pts = hero(img, sx, 1590, 1.12, t, walk=t * 5.2, arm="phone", phone_on=True, look=(0.3, 0.6),
               brows="worried" if t > tn - 0.6 else "calm")
    glow(img, pts["phone"][0], pts["phone"][1], 120, (190, 215, 255), 0.45)
    steam(img, *pts["mouth"], t, scale=1.1)
    if tn - 0.6 < t < wt(3, "Терминалы") + 0.6:          # пузырь «нет сети»
        k = ease((t - tn + 0.6) / 0.3)
        bx, by = pts["head"][0] + 120, pts["head"][1] - 210
        d = P(img, 1.0)
        d.rr(bx, by, bx + 300 * k, by + 110 * k, 26 * k + 1, (12, 18, 34, 230))
        if k > 0.9:
            for i in range(4): d.rr(bx + 30 + i * 30, by + 80 - 14 * i, bx + 50 + i * 30, by + 90, 4, (70, 84, 120))
            d.line([(bx + 24, by + 30), (bx + 150, by + 96)], RED, 8)
            d.text(bx + 170, by + 36, "НЕТ\nСЕТИ", font(30), SNOW)
    s.snow_near.draw(img, t, 230)
    comp(img, s.fg, -cam * 1.3 - 200, 0)
    return img, 1.04, 1.0


# ======================================================================= ПОДЪЕЗД И КУХНЯ (сцена 5)
class Stairs:
    def __init__(s):
        s.bg = vgrad(W, H, [(0, (26, 34, 58)), (0.5, (22, 30, 52)), (1, (14, 20, 36))])
        def deco(p):
            p.rect(-20, 1000, W + 20, H, (34, 56, 70))                               # крашеная панель
            p.rect(-20, 990, W + 20, 1004, (60, 84, 98))
            p.rr(90, 300, 360, 620, 18, (10, 16, 32)); p.rr(84, 294, 366, 626, 20, None, (70, 84, 112), 10)
            p.line([(225, 300), (225, 620)], (70, 84, 112), 8); p.line([(90, 460), (360, 460)], (70, 84, 112), 8)
        s.bg.alpha_composite(layer(W, H, deco))
        s.snow = Snow(30, 9, (1.5, 3), (40, 90), w=270, h=320)

    def frame(s, t, floor):
        img = s.bg.copy()
        win = Image.new("RGBA", (270, 320), (0, 0, 0, 0)); s.snow.draw(win, t, 150)
        comp(img, win, 90, 300)
        d = P(img, 1.0)
        d.text(620, 360, str(floor), font(230), (64, 86, 120))
        # ступени, которые «едут» вниз: эффект подъёма
        step = 90; off = (t * 150) % step
        for i in range(-2, 14):
            y = 2000 - i * step + off; x = -200 + i * 80
            d.poly([(x, y), (x + 900, y), (x + 900 + 30, y - step), (x + 30, y - step)], (52, 62, 90))
            d.poly([(x, y), (x + 900, y), (x + 900, y + 18), (x, y + 18)], (34, 42, 66))
        for i in range(-2, 14):
            y = 2000 - i * step + off; x = 720 + i * 80
            d.line([(x, y - step), (x, y - step - 210)], (110, 120, 146), 8, round_caps=False)
        d.line([(520, 2160 + off), (1800, 560 + off)], (140, 104, 70), 18)          # деревянный поручень
        return img


class Kitchen:
    def __init__(s):
        s.bg = vgrad(W, H, [(0, (20, 30, 56)), (1, (14, 22, 42))])
        def deco(p):
            for y in range(560, 1420, 70): p.line([(0, y), (W, y)], (28, 40, 70), 3, round_caps=False)
            for x in range(0, W, 70): p.line([(x, 560), (x, 1420)], (28, 40, 70), 3, round_caps=False)
            p.rr(240, 180, 840, 760, 20, (8, 12, 26))
            for _ in range(0): pass
        s.bg.alpha_composite(layer(W, H, deco))
        rnd = random.Random(2)
        def city(p):
            for _ in range(8):
                x = rnd.uniform(240, 800); w = rnd.uniform(80, 150); h = rnd.uniform(160, 420)
                p.rect(x, 760 - h, x + w, 760, (16, 22, 40))
        s.bg.alpha_composite(layer(W, H, city))
        def frame_(p):
            p.rr(232, 172, 848, 768, 22, None, (200, 208, 226), 16)
            p.line([(540, 180), (540, 760)], (200, 208, 226), 12); p.line([(240, 470), (840, 470)], (200, 208, 226), 12)
            p.rr(200, 768, 880, 800, 10, (200, 208, 226))
            for k in range(7): p.rr(250 + k * 84, 840, 310 + k * 84, 1040, 22, (70, 84, 116))  # батарея
            p.rr(240, 870, 860, 900, 10, (70, 84, 116))
        s.winframe = layer(W, H, frame_)
        def counter(p):
            p.rr(-30, 1380, W + 30, 1440, 14, (150, 164, 192))
            p.rect(-30, 1440, W + 30, H, (40, 56, 92))
            for x in (40, 400, 760): p.rr(x, 1480, x + 300, H + 40, 16, (50, 68, 108))
            for x in (310, 670): p.rr(x - 6, 1520, x + 6, 1600, 6, (150, 164, 192))
            p.rr(380, 1386, 700, 1420, 12, (90, 100, 126))                          # мойка
            p.rr(620, 1220, 650, 1392, 10, (170, 180, 204))                         # кран
            p.rr(530, 1210, 650, 1240, 12, (170, 180, 204))
            p.rr(526, 1236, 556, 1270, 8, (150, 160, 186))
        s.counter = layer(W, H, counter)
        rnd = random.Random(8)
        s.frost = [(rnd.choice([(240, 172), (848, 172), (240, 768), (848, 768)]), rnd.uniform(0, 1), rnd.uniform(20, 70)) for _ in range(46)]

    def frame(s, t, dur, t0):
        img = s.bg.copy()
        img.alpha_composite(s.winframe)
        kk = ease(t / dur)
        for (cx, cy), u, r in s.frost:                                              # иней растёт
            a = clamp(kk * 1.6 - u * 0.6)
            if a <= 0: continue
            ang = u * 6.28; dist = u * 160 * kk
            x = cx + (1 if cx < 540 else -1) * abs(math.cos(ang)) * dist; y = cy + (1 if cy < 470 else -1) * abs(math.sin(ang)) * dist
            glow(img, x, y, r, (225, 236, 250), 0.55 * a, 1.2)
        heat = clamp(1 - (t - t0) / 3.5) if t > t0 else 1.0                         # тепло батареи гаснет
        if heat > 0.02:
            d = P(img, 1.0)
            for k in range(4):
                x = 330 + k * 140
                pts = [(x + 10 * math.sin(t * 3 + yy * 0.05 + k), yy) for yy in range(820, 640, -10)]
                d.line(pts, (255, 190, 120, int(120 * heat)), 4, round_caps=False)
        return img

STAIRS = KITCHEN = None
def scene5(t):
    global STAIRS, KITCHEN
    dur = DUR[4]; tc = wt(4, "В кране")
    if t < tc:
        if STAIRS is None: STAIRS = Stairs()
        floor = 1 + int(13 * ease(t / (tc - 0.3)))
        img = walls_dark(STAIRS.frame(t, floor), 0.5)
        glow(img, 820, 640, 520, (255, 236, 196), 0.2, 1.5)
        pts = hero(img, 520, 1580, 1.18, t, walk=t * 4.0, lamp=True, look=(0.7, -0.4), brows="calm", dark=0.85)
        lamp_glow(img, pts["lamp"], True, size=1.18)
        steam(img, *pts["mouth"], t, period=1.4, scale=1.0)
        return img, lerp(1.0, 1.05, t / tc), 1.0
    if KITCHEN is None: KITCHEN = Kitchen()
    tt = t - tc
    img = walls_dark(KITCHEN.frame(tt, dur - tc, wt(4, "Батареи") - tc), 0.62)
    pts = hero(img, 400, 1700, 1.3, t, look=(0.6, 0.9), lamp=True, brows="worried",
               mouth="flat" if tt > 1.2 else None, arm="reach" if tt < 1.6 else None)
    lamp_glow(img, pts["lamp"], True, size=1.3)
    glow(img, 640, 1300, 360, (255, 236, 196), 0.18, 1.6)
    img.alpha_composite(KITCHEN.counter)
    k = (tt - 0.9) / 0.6                                                            # одна капля и всё
    if 0 < k < 1:
        y = lerp(1270, 1400, k * k); d = P(img, 1.0)
        d.el(533, y - 16, 549, y + 6, (170, 210, 245))
    if tt > wt(4, "холоднее") - tc: steam(img, *pts["mouth"], t, period=2.2, scale=1.2)
    return img, lerp(1.0, 1.08, ease(tt / (dur - tc))), 1.0


# ======================================================================= БАЛКОН И ДВЕРЬ (сцена 6)
class Balcony:
    def __init__(s):
        s.bg = vgrad(W, H, [(0, (6, 10, 24)), (0.5, (16, 24, 50)), (1, (26, 34, 60))])
        rnd = random.Random(4)
        def city(p):
            for _ in range(50): p.circ(rnd.uniform(0, W), rnd.uniform(40, 600), rnd.uniform(1, 2.4), (150, 160, 190))
            x = -30
            while x < W:
                w = rnd.randint(140, 240); h = rnd.randint(500, 900); top = 1300 - h
                p.rr(x, top, x + w, 1400, 8, (14, 20, 40))
                for wy in range(top + 30, 1360, 48):
                    for wx in range(x + 18, x + w - 22, 36): p.rr(wx, wy, wx + 18, wy + 26, 3, (22, 30, 54))
                x += w + rnd.randint(20, 60)
        s.bg.alpha_composite(layer(W, H, city))
        def balc(p):
            p.rect(-20, 1460, W + 20, H, (44, 54, 84))                               # пол балкона
            p.rr(-20, 1440, W + 20, 1500, 20, SNOW)
            p.rect(-20, 1150, W + 20, 1176, (96, 108, 140))                          # перила
            p.rr(-20, 1128, W + 20, 1158, 15, SNOW)
            for x in range(20, W, 64): p.rect(x, 1176, x + 12, 1460, (80, 92, 124))
            p.rect(-20, 1500, 120, H, (30, 40, 66)); p.rect(960, 1500, W + 20, H, (30, 40, 66))
        s.balc = layer(W, H, balc)
        s.snow = Snow(80, 12, (2, 5), (60, 160))


class Door:
    def __init__(s):
        s.bg = vgrad(W, H, [(0, (18, 26, 48)), (1, (12, 18, 34))])
        def deco(p):
            p.rect(0, 1560, W, H, (30, 26, 34))                                      # пол
            for x in range(-200, W, 120): p.line([(x, 1560), (x + 260, H)], (38, 32, 42), 4, round_caps=False)
            p.rr(560, 360, 1000, 1570, 12, (52, 44, 50))                             # проём
            p.rr(586, 386, 974, 1570, 8, (6, 8, 16))                                 # тёмный подъезд
        s.bg.alpha_composite(layer(W, H, deco))
        s.door = layer(W, H, lambda p: (p.rr(586, 386, 974, 1570, 8, (92, 70, 58)),
                                       p.rr(616, 420, 944, 960, 10, (104, 80, 66)), p.rr(616, 1000, 944, 1530, 10, (104, 80, 66)),
                                       p.circ(920, 1000, 16, (200, 180, 120))))
        s.door_open = layer(W, H, lambda p: (p.poly([(974, 386), (1070, 330), (1070, 1640), (974, 1570)], (92, 70, 58)),
                                            p.circ(1040, 1000, 12, (200, 180, 120))))

BALC = DOOR = None
def card(img, t, t0, title, sub):
    """Карточка факта под заголовком."""
    if t < t0: return
    k = ease((t - t0) / 0.35)
    d = ImageDraw.Draw(img)
    f = font(40); tw = d.textlength(sub, font=f)
    x0 = W / 2 - tw / 2 - 34; y0 = 330 - 20 * (1 - k)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    od.rounded_rectangle([x0, y0, x0 + tw + 68, y0 + 84], radius=20, fill=(10, 14, 28, int(220 * k)), outline=(255, 178, 64, int(255 * k)), width=3)
    od.text((x0 + 34, y0 + 18), sub, font=f, fill=(255, 226, 170, int(255 * k)))
    img.alpha_composite(ov)


def scene6(t):
    global BALC, DOOR
    dur = DUR[5]; tk = wt(5, "Стук")
    if t < tk:
        if BALC is None: BALC = Balcony()
        img = BALC.bg.copy(); BALC.snow.draw(img, t, 170)
        img.alpha_composite(BALC.balc)
        nb = min(3, int((t - 0.6) / 0.9) + 1) if t > 0.6 else 0
        d = P(img, 1.0)
        for i, (bx, c) in enumerate(((180, (200, 190, 170)), (330, (176, 186, 200)), (460, (210, 196, 160)))):
            if i < nb:
                d.poly([(bx - 60, 1500), (bx + 60, 1500), (bx + 48, 1360), (bx - 48, 1360)], c)
                d.arc(bx - 30, 1300, bx + 30, 1380, 180, 360, c, 8)
                d.rr(bx - 50, 1354, bx + 50, 1366, 6, SNOW)
        pts = hero(img, 760, 1580, 1.2, t, look=(-0.8, 0.6), arm="reach" if t < 3.2 else None, brows="calm")
        steam(img, *pts["mouth"], t, scale=1.1)
        BALC.snow.draw(img, t + 50, 230)
        return img, lerp(1.0, 1.06, t / tk), 1.0
    if DOOR is None: DOOR = Door()
    tt = t - tk; to = wt(5, "Это сосед") - tk
    img = DOOR.bg.copy()
    if tt < to:
        shake = 4 * math.sin(tt * 60) if (tt % 0.5) < 0.12 and tt < 1.2 else 0
        comp(img, DOOR.door, shake, 0)
    else:
        img.alpha_composite(DOOR.door_open)
        glow(img, 780, 900, 340, (255, 240, 200), 0.22, 1.4)
        old_man(img, 790, 1560, 1.22, t, look=-0.6, bottle=True, dark=0.92)
    img = walls_dark(img, 0.72)
    pts = hero(img, 300, 1580, 1.2, t, look=(0.8, 0.0), lamp=True, brows="worried" if tt < to else "calm",
               mouth="o" if tt < to else ("smile" if tt > to + 1.5 else None))
    lamp_glow(img, pts["lamp"], True, size=1.3)
    card(img, t, wt(5, "Так было") - 0.1, "", "ТЕХАС · ФЕВРАЛЬ 2021")
    return img, 1.04, 1.0


# ======================================================================= ТРУБА И СВЕЧИ (сцена 7)
class Pipe:
    def __init__(s):
        st = Stairs(); s.base = walls_dark(st.frame(0, 9), 0.45)
        s.parts = [(random.uniform(-1, 1), random.uniform(0.3, 1.0), random.uniform(0.6, 1.4)) for _ in range(60)]
        rnd = random.Random(21)
        s.ice = [(rnd.uniform(80, 1000), rnd.uniform(1280, 1820), rnd.uniform(40, 110), rnd.uniform(0, 1)) for _ in range(26)]


class Candles:
    def __init__(s):
        s.bg = vgrad(W, H, [(0, (14, 18, 34)), (1, (22, 20, 30))])
        def deco(p):
            p.rr(300, 260, 780, 760, 20, (10, 16, 32)); p.rr(292, 252, 788, 768, 22, None, (180, 190, 210), 14)
            p.line([(540, 260), (540, 760)], (180, 190, 210), 10); p.line([(300, 510), (780, 510)], (180, 190, 210), 10)
        s.bg.alpha_composite(layer(W, H, deco))
        rnd = random.Random(6)
        for _ in range(40):
            cx = rnd.choice([300, 780]); cy = rnd.choice([260, 760]); u = rnd.random()
            glow(s.bg, cx + (1 if cx < 540 else -1) * u * 180, cy + (1 if cy < 510 else -1) * rnd.random() * 160, rnd.uniform(30, 80), (220, 232, 248), 0.5, 1.2)
        def table(p):
            p.rr(-60, 1380, W + 60, 1460, 30, (110, 80, 60)); p.rect(-60, 1440, W + 60, H, (78, 56, 44))
            p.rr(240, 1300, 290, 1392, 8, (150, 160, 180)); p.rr(236, 1290, 294, 1306, 6, (110, 120, 140))  # термос
            p.rr(340, 1336, 400, 1392, 10, (176, 140, 120)); p.arc(388, 1346, 420, 1380, 270, 90, (176, 140, 120), 8)  # кружка
            for x in (480, 610, 740): p.rr(x - 12, 1290, x + 12, 1392, 8, (238, 232, 216))  # свечи
            p.rr(820, 1330, 890, 1392, 8, (150, 156, 170)); p.rr(900, 1340, 960, 1392, 8, (150, 156, 170))  # консервы
        s.table = layer(W, H, table)

PIPE = CAND = None
def scene7(t):
    global PIPE, CAND
    dur = DUR[6]; ts = wt(6, "Соседи"); tb = wt(6, "лопается"); tf = wt(6, "замерзает")
    if t < ts:
        if PIPE is None: PIPE = Pipe()
        img = PIPE.base.copy(); d = P(img, 1.0)
        d.rr(-20, 860, W + 20, 920, 28, (96, 106, 130)); d.rr(-20, 864, W + 20, 878, 7, (140, 150, 172))
        for x in (200, 760): d.rr(x - 18, 846, x + 18, 934, 8, (70, 78, 100))
        if t > tb:
            k = clamp((t - tb) / 0.25)
            d.line([(540, 862), (520, 884), (556, 900), (532, 918)], RED if t < tb + 1.0 else (90, 60, 70), 8)
            for u, v, sp in PIPE.parts:
                tt = (t - tb) * sp
                if tt > 1.8: continue
                x = 540 + u * 400 * tt; y = 920 + 300 * tt * v + 260 * tt * tt
                d.circ(x, y, 6, (170, 210, 245))
            fr = ease((t - tf) / 2.0) if t > tf else 0
            for x, y, r, u in PIPE.ice:
                if u < fr: d.el(x - r, y - r * 0.35, x + r, y + r * 0.35, (190, 225, 250, 255))
            if t < tb + 0.15: img.alpha_composite(Image.new("RGBA", (W, H), (255, 60, 60, 70)))
        pts = hero(img, 860, 1580, 0.95, t, look=(-0.8, -0.2), lamp=True, brows="worried",
                   mouth="o" if t > tb else None, dark=0.85)
        lamp_glow(img, pts["lamp"], True, size=0.95)
        glow(img, 600, 900, 300, (255, 236, 196), 0.2, 1.4)
        return img, lerp(1.0, 1.1, ease(t / ts)), 1.0
    if CAND is None: CAND = Candles()
    tt = t - ts
    img = CAND.bg.copy()
    woman(img, 220, 1560, 1.12, t, dark=0.8)
    old_man(img, 870, 1560, 1.12, t, look=-0.8, dark=0.8)
    pts = hero(img, 560, 1620, 1.18, t, look=(0.6, 0.3), lamp=False, arm="reach", mouth="smile", dark=0.85)
    hx, hy = pts["hand"]
    P(img, 1.0).rr(hx - 30, hy - 40, hx + 30, hy + 20, 8, (150, 156, 170))
    img.alpha_composite(CAND.table)
    for i, x in enumerate((480, 610, 740)):
        fl = 0.85 + 0.15 * math.sin(t * 13 + i * 2) * math.sin(t * 7.3 + i)
        glow(img, x, 1270, 330 * fl, AMBER, 0.22, 1.7)
        glow(img, x, 1270, 40, (255, 220, 150), 0.9 * fl, 1.4)
        P(img, 1.0).el(x - 7, 1262 - 16 * fl, x + 7, 1290, (255, 236, 180))
    steam(img, 370, 1320, t, period=1.8, scale=0.6)
    return img, lerp(1.04, 1.0, ease(tt / (dur - ts))), 1.0


# ======================================================================= ОКНО (сцена 8)
class Window:
    def __init__(s):
        rnd = random.Random(31)
        s.sky = vgrad(W, H, [(0, (6, 10, 24)), (0.5, (16, 22, 46)), (1, (22, 24, 44))])
        def outside(p):
            p.rr(210, 330, 870, 1300, 6, (18, 24, 44))                               # дом напротив
            for x in (80, 920): p.rect(x - 200, 600, x + 120, 1300, (12, 18, 34))
        s.sky.alpha_composite(layer(W, H, outside))
        s.wins = [(x, y) for y in range(380, 1260, 74) for x in range(250, 820, 64)]
        rnd.shuffle(s.wins); s.order = {w: i for i, w in enumerate(s.wins)}
        s.horizon = [(rnd.uniform(0, W), rnd.uniform(560, 620)) for _ in range(70)]
        s.horizon.sort()
        def room(p):
            p.rect(0, 0, W, 300, (8, 12, 24)); p.rect(0, 1380, W, H, (8, 12, 24))
            p.rect(0, 0, 150, H, (8, 12, 24)); p.rect(930, 0, W, H, (8, 12, 24))
            p.rr(130, 280, 950, 1400, 18, None, (60, 70, 96), 26)
            p.line([(540, 300), (540, 1380)], (60, 70, 96), 18); p.line([(150, 800), (930, 800)], (60, 70, 96), 18)
            p.rr(110, 1380, 970, 1430, 12, (80, 90, 118))
        s.room = layer(W, H, room)
        s.snow = Snow(60, 7, (1.5, 3.5), (40, 110))

WIN = None
def scene8(t):
    global WIN
    if WIN is None: WIN = Window()
    s = WIN; dur = DUR[7]; tl = wt(7, "Дом напротив")
    img = s.sky.copy(); d = P(img, 1.0)
    kh = clamp(t / (tl - 0.5))
    for x, y in s.horizon:                                                          # свет возвращается по районам
        if x / W < kh: glow(img, x, y, 18, AMBER, 0.6, 1.3)
    nlit = int(len(s.wins) * ease((t - tl) / 1.6)) if t > tl else 0
    for (x, y) in s.wins:
        on = s.order[(x, y)] < nlit
        d.rr(x, y, x + 36, y + 48, 4, AMBER if on else (26, 32, 54))
    if nlit: glow(img, 540, 800, 520, AMBER, 0.18 * nlit / len(s.wins), 1.4)
    s.snow.draw(img, t, 180)
    img.alpha_composite(s.room)
    rim = 0.5 + 0.35 * (nlit / len(s.wins))
    hero(img, 540, 1580, 1.12, t, view="back", dark=rim)
    return img, lerp(1.0, 1.1, ease(t / dur)), 1.0


# ======================================================================= ДОМА (сцена 9)
class Home:
    def __init__(s):
        s.bg = vgrad(W, H, [(0, (40, 46, 70)), (0.6, (52, 54, 78)), (1, (34, 32, 46))])
        def deco(p):
            p.rect(0, 1560, W, H, (60, 48, 46))
            for x in range(-200, W, 110): p.line([(x, 1560), (x + 220, H)], (70, 56, 52), 4, round_caps=False)
            p.rr(700, 420, 1040, 1570, 10, (80, 62, 56)); p.rr(724, 444, 1016, 1570, 8, (110, 84, 68))
            p.circ(990, 1000, 14, (220, 196, 130))
            p.rr(640, 860, 668, 884, 6, (150, 156, 172))                              # крючок
            p.line([(654, 884), (654, 910)], (150, 156, 172), 6)
            p.rr(80, 380, 420, 800, 10, (66, 70, 96)); p.rr(96, 396, 404, 784, 6, (90, 96, 124))  # картина
            p.line([(540, 0), (540, 140)], (40, 40, 50), 6)
            p.chord(440, 120, 640, 260, 180, 360, (230, 210, 170))                      # абажур
        s.bg.alpha_composite(layer(W, H, deco))
        s.dark = walls_dark(s.bg, 0.25)

HOME = None
def scene9(t):
    global HOME
    if HOME is None: HOME = Home()
    s = HOME; dur = DUR[8]
    th = wt(8, "вешает"); tp = wt(8, "Телефон"); tm = wt(8, "Приходит")
    on = t > 0.2 and not (0.32 < t < 0.4)
    img = s.bg.copy() if on else s.dark.copy()
    if on:
        glow(img, 540, 200, 900, WARM, 0.35, 1.6); glow(img, 540, 210, 90, (255, 248, 220), 0.9, 1.3)
    hung = t > th + 0.5
    if hung:
        d = P(img, 1.0)
        d.el(626, 900, 682, 960, None, (20, 20, 26), 6); d.el(638, 940, 670, 972, (150, 156, 172))
    arm = "up" if th - 0.2 < t < th + 0.7 else ("phone" if t > tp - 0.2 else None)
    buzz = 3 * math.sin(t * 90) if tm < t < tm + 0.7 else 0
    pts = hero(img, 400 + buzz * 0.3, 1580, 1.25, t, look=(0.6, -0.3) if t < tp else (0.2, 0.6),
               lamp=not hung, arm=arm, phone_on=t > tp, mouth="smile" if on and t < tp + 0.5 else (None if t < tm else "o"),
               dark=1.0 if on else 0.4)
    if arm == "phone" and t > tp:
        ph = pts["phone"]; glow(img, ph[0], ph[1], 130, (190, 215, 255), 0.5)
        if t > tm:
            k = ease((t - tm) / 0.3); bx, by = ph[0] + 60, ph[1] - 330
            ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = P(ov, 1.0)
            od.rr(bx, by, bx + 380 * k + 1, by + 150 * k + 1, 28 * k + 1, (240, 244, 252, int(240 * k)))
            if k > 0.95:
                od.circ(bx + 50, by + 75, 30, (120, 140, 180))
                od.rr(bx + 100, by + 48, bx + 330, by + 64, 8, (180, 188, 204))
                od.rr(bx + 100, by + 86, bx + 280, by + 102, 8, (200, 206, 218))
            img.alpha_composite(ov)
    return img, lerp(1.06, 1.0, ease(t / dur)), 1.0


SCENE_FUNCS = [scene1, scene2, scene3, scene4, scene5, scene6, scene7, scene8, scene9]


# ======================================================================= субтитры
def captions(i):
    text = SCENES[i]["text"]; a = ALN[i]
    st = a["character_start_times_seconds"]; en = a["character_end_times_seconds"]
    words = [(m.start(), m.group()) for m in re.finditer(r"\S+", text)]
    for k_ in CAPTION_NUMS:                         # число из нескольких слов = одно «слово»
        p0 = text.find(k_)
        if p0 < 0: continue
        p1 = p0 + len(k_)
        inside = [w for w in words if p0 <= w[0] < p1]
        tail = text[p1:].split(" ")[0] if not text[p1:].startswith(" ") else ""
        merged = (p0, text[p0:p1] + tail)
        words = [w for w in words if not (p0 <= w[0] < p1)]
        words.append(merged); words.sort()
    sents, cur = [], []
    for w in words:
        cur.append(w)
        if w[1][-1] in ".?!": sents.append(cur); cur = []
    if cur: sents.append(cur)
    chunks = []
    for sent in sents:
        n = math.ceil(len(sent) / 6); per = math.ceil(len(sent) / n)
        for j in range(0, len(sent), per): chunks.append(sent[j:j + per])
    out = []
    for j, c in enumerate(chunks):
        a0 = st[c[0][0]] + LEAD; last = c[-1]; b0 = en[last[0] + len(last[1]) - 1] + LEAD + 0.25
        if j + 1 < len(chunks): b0 = min(b0 + 0.4, st[chunks[j + 1][0][0]] + LEAD)
        s_ = text[c[0][0]: last[0] + len(last[1])]
        for k_, v_ in CAPTION_NUMS.items(): s_ = s_.replace(k_, v_)
        out.append((a0, b0, s_))
    return out
