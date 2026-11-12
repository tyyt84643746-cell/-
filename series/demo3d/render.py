"""Тест 3D-стиля «Тридцать дней». Запуск: LIBGL_ALWAYS_SOFTWARE=1 xvfb-run -a python3 render.py [preview]"""
import json, math, os, random, re, subprocess, sys
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(D, "..", "engine3d")); sys.path.insert(0, D)
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from models import *
from script import SCENES, CAPTION_NUMS

W, H, FPS = 1080, 1920, 30
LEAD, TAILS = 0.3, [0.7, 0.8, 2.6]
N = len(SCENES)
ALN = [json.load(open(f"{D}/v{i}.json")) for i in range(1, N + 1)]
NFR = [round((a["character_end_times_seconds"][-1] + LEAD + TAILS[i]) * FPS) for i, a in enumerate(ALN)]
DUR = [n / FPS for n in NFR]; STARTS = [sum(DUR[:i]) for i in range(N)]
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
_F = {}
def font(sz):
    if sz not in _F: _F[sz] = ImageFont.truetype(FB, sz)
    return _F[sz]
YEL = (255, 214, 64); RED = (240, 70, 60); WHITE = (255, 255, 255)
KEY = {"30", "дней.", "удар.", "смеются.", "бункер.", "Воздух.", "Вода.", "Еда.", "всё.", "половину.", "первым?", "комментариях."}

def lerp(a, b, k): return a + (b - a) * k
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(k): k = clamp(k); return k * k * (3 - 2 * k)
def wt(i, sub):
    text = SCENES[i]["text"]; k = text.find(sub); assert k >= 0, sub
    return ALN[i]["character_start_times_seconds"][k] + LEAD

# ---------------------------------------------------------------- мир
def world(t):
    it = [box(T(0, -0.25, 0) @ S(80, 0.5, 80), C["snow"])]
    it += house(T(-3.5, 0, -6))
    for x, z, h in ((-10, -10, 5), (-7, -14, 6), (3, -13, 5.5), (7, -9, 4.5), (10, -15, 6), (-13, -7, 5), (13, -6, 5), (-2, -18, 7)):
        it += pine(T(x, 0, z), h)
    it += fence(-9, 9, -1.6)
    it.append(box(T(1.6, 0.012, 1.4) @ S(2.4, 0.02, 1.8), C["dark"], cast=False))
    it.append(ball(T(3.7, 0.0, 1.0) @ S(1.8, 0.9, 1.3), C["dirt"]))
    it.append(ball(T(3.2, 0.25, 2.0) @ S(0.9, 0.5, 0.8), C["dirt"]))
    return it

LAMPS = [((-5.0, 1.5, -4.0), (1.0, 0.55, 0.22), 7.0), ((-2.0, 1.5, -4.0), (1.0, 0.55, 0.22), 7.0)]
NB_COL = [dict(body=rgb((84, 92, 62)), body_d=rgb((64, 70, 46)), hat=rgb((140, 62, 58)), hat_b=rgb((160, 76, 70)), pack=None),
          dict(body=rgb((86, 70, 100)), body_d=rgb((70, 56, 84)), hat=rgb((70, 110, 104)), hat_b=rgb((84, 128, 120)), pack=None),
          dict(body=rgb((70, 78, 92)), body_d=rgb((54, 60, 72)), hat=rgb((30, 30, 36)), hat_b=rgb((44, 44, 52)), pack=None)]

def neighbors(t, laugh=True):
    it = []
    for j, x in enumerate((-6.0, -4.6, -3.2)):
        bounce = 0.05 * abs(math.sin(t * 9 + j)) if laugh else 0
        p, _ = person(T(x, bounce, -2.3) @ Ry(0.35), t + j, colors=NB_COL[j], mouth="smile", blink_seed=j, look=0.3)
        it += p
    return it

def artyom_dig(t, lamp=True):
    root = T(1.0, 0, 2.6) @ Ry(0.5)
    p, head = person(root, t, arm="dig", look=0.15 * math.sin(t), lamp=lamp, blink_seed=0.7)
    dig = math.sin(t * 4.5)
    p += shovel(root @ T(0.1, 1.2 + 0.15 * dig, 0.55) @ Rx(0.5 + 0.2 * dig))
    hl = (root @ np.array([0, 2.16, 0.34, 1], "f4"))[:3]
    return p, [(tuple(hl), (1.0, 0.95, 0.8), 4.5)]

# ---------------------------------------------------------------- сцены (3D)
def scene_3d(si, t):
    if si == 0:
        k = ease(t / DUR[0])
        a = lerp(0.9, 0.25, k); r = lerp(15, 7.0, k)
        eye = (1.0 + r * math.sin(a), lerp(6.5, 2.6, k), 1.0 + r * math.cos(a)); tgt = (lerp(-2, 0.8, k), lerp(1.5, 1.4, k), lerp(-2, 1.5, k))
        it = world(t) + neighbors(t, laugh=t > wt(0, "Все")); a_, l_ = artyom_dig(t)
        return it + a_, eye, tgt, LAMPS + l_
    if si == 1:
        it = world(t) + neighbors(t, laugh=False); a_, l_ = artyom_dig(t)
        drops = [wt(1, "Воздух"), wt(1, "Вода"), wt(1, "Еда")]
        cols = [rgb((176, 180, 190)), rgb((80, 140, 200)), rgb((150, 116, 80))]
        for j, t0 in enumerate(drops):
            if t < t0: continue
            for k in range(3):
                tt = t - t0 - k * 0.12
                if tt < 0: continue
                y = max(0.3 + k * 0.62, 6 - 18 * tt * tt) if True else 0
                if y > 0.3 + k * 0.62: pass
                yy = max(0.3 + k * 0.62, 6 - 18 * tt * tt)
                it.append(box(T(-3.3 + j * 0.85, yy, 1.6) @ Ry(0.3 * j) @ S(0.7, 0.55, 0.6), cols[j]))
        eye = (2.0 + 0.6 * math.sin(t * 0.4), 3.0, 10.5); tgt = (-0.6, 1.3, 2.4)
        return it + a_, eye, tgt, LAMPS + l_
    k = ease(t / 1.5)
    root = T(0.6, 0, 3.6) @ Ry(0.0)
    it = world(t) + neighbors(t, laugh=False)
    p, head = person(root, t, look=0.0, lamp=True, mouth="o" if t < 1.0 else None, blink_seed=0.3)
    it += p + cat(T(1.6, 0, 3.9) @ Ry(-0.4), t, look=-0.4)
    hl = (root @ np.array([0, 2.16, 0.34, 1], "f4"))[:3]
    eye = (0.9, 2.4, lerp(11.0, 9.2, k)); tgt = (0.9, 1.5, 3.6)
    return it, eye, tgt, LAMPS + [(tuple(hl), (1.0, 0.95, 0.8), 4.5)]

# ---------------------------------------------------------------- 2D поверх
def stroke_text(d, xy, s, f, fill, sw=7, anchor="mm"):
    d.text(xy, s, font=f, fill=fill, stroke_width=sw, stroke_fill=(0, 0, 0), anchor=anchor)

def captions(i):
    text = SCENES[i]["text"]; a = ALN[i]; st = a["character_start_times_seconds"]; en = a["character_end_times_seconds"]
    words = [(m.start(), m.group()) for m in re.finditer(r"\S+", text) if m.group() != "—"]
    for k_ in CAPTION_NUMS:
        p0 = text.find(k_)
        if p0 >= 0:
            p1 = p0 + len(k_); tail = text[p1:].split(" ")[0] if not text[p1:].startswith(" ") else ""
            words = [w for w in words if not (p0 <= w[0] < p1)] + [(p0, text[p0:p1] + tail)]; words.sort()
    chunks, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) == 3 or w[1][-1] in ".?!": chunks.append(cur); cur = []
    if cur: chunks.append(cur)
    out = []
    for j, c in enumerate(chunks):
        a0 = st[c[0][0]] + LEAD; last = c[-1]; b0 = en[last[0] + len(last[1]) - 1] + LEAD + 0.15
        if j + 1 < len(chunks): b0 = max(b0, st[chunks[j + 1][0][0]] + LEAD)
        ws = []
        for p0, w in c:
            s_ = w
            for k_, v_ in CAPTION_NUMS.items(): s_ = s_.replace(k_, v_)
            ws.append((st[p0] + LEAD, s_))
        out.append((a0, b0, ws))
    return out
CAPS = [captions(i) for i in range(N)]

def overlay(si, t, img):
    im = Image.fromarray(img).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    gt = STARTS[si] + t
    # постоянный крючок сверху
    stroke_text(d, (W / 2, 250), "ТЕБЕ ДАЛИ", font(70), WHITE, 6)
    stroke_text(d, (W / 2, 345), "30 ДНЕЙ", font(118), RED if gt > 1.0 and int(gt * 2) % 2 == 0 and gt < 2.6 else YEL, 8)
    # «ха-ха» над соседями
    if si == 0 and t > wt(0, "Все"):
        for j, (x, y) in enumerate(((180, 820), (330, 760), (120, 700))):
            k = ease((t - wt(0, "Все") - j * 0.15) / 0.25)
            if k > 0: stroke_text(d, (x, y - 30 * k + 6 * math.sin(t * 9 + j)), "ХА-ХА", font(46), WHITE, 5)
    # чек-лист и деньги
    if si == 1:
        items = [("ВОЗДУХ", wt(1, "Воздух")), ("ВОДА", wt(1, "Вода")), ("ЕДА", wt(1, "Еда"))]
        d.rounded_rectangle([60, 470, 470, 760], radius=28, fill=(8, 12, 26, 210))
        for j, (name, t0) in enumerate(items):
            y = 510 + j * 82; ok = t > t0 + 0.3
            d.rounded_rectangle([90, y, 140, y + 50], radius=10, outline=WHITE, width=5, fill=(60, 200, 110) if ok else None)
            if ok: d.line([(100, y + 26), (113, y + 39), (132, y + 12)], fill=WHITE, width=7)
            d.text((165, y + 25), name, font=font(46), fill=WHITE if ok else (170, 176, 196), anchor="lm")
        money = int(lerp(9_900_000, 4_950_000, ease((t - wt(1, "А денег")) / 1.0))) if t > wt(1, "А денег") else 9_900_000
        stroke_text(d, (780, 610), f"{money:,} ₽".replace(",", " "), font(54), RED if money < 9_000_000 else WHITE, 6)
    # CTA
    if si == 2 and t > wt(2, "Пиши") - 0.2:
        k = ease((t - wt(2, "Пиши") + 0.2) / 0.4)
        a = int(235 * k)
        for j, (x, label, c) in enumerate(((290, "ВОЗДУХ", (230, 60, 80)), (790, "ЕДА", (60, 130, 230)))):
            d.rounded_rectangle([x - 220, 1420, x + 220, 1700], radius=40, fill=(8, 12, 26, a))
            if j == 0:
                cx, cy = x, 1510
                d.ellipse([cx - 62, cy - 50, cx + 2, cy + 14], fill=c + (int(255 * k),)); d.ellipse([cx - 2, cy - 50, cx + 62, cy + 14], fill=c + (int(255 * k),))
                d.polygon([(cx - 60, cy - 6), (cx + 60, cy - 6), (cx, cy + 62)], fill=c + (int(255 * k),))
            else:
                cx, cy = x, 1505
                d.rounded_rectangle([cx - 66, cy - 52, cx + 66, cy + 34], radius=24, fill=c + (int(255 * k),)); d.polygon([(cx - 30, cy + 30), (cx - 6, cy + 30), (cx - 34, cy + 62)], fill=c + (int(255 * k),))
                for dx in (-30, 0, 30): d.ellipse([cx + dx - 9, cy - 18, cx + dx + 9, cy], fill=(255, 255, 255, int(255 * k)))
            d.text((x, 1630), ("ЛАЙК — " if j == 0 else "КОММЕНТ — ") + label, font=font(38), fill=(255, 255, 255, a), anchor="mm")
    # караоке-субтитры по центру
    for a0, b0, ws in CAPS[si]:
        if a0 <= t < b0:
            parts = []
            for ts_, w in ws:
                col = YEL if w in KEY or w.isdigit() or w.startswith("30") else WHITE
                if t < ts_: col = (200, 200, 200)
                parts.append((w, col))
            sz = 92
            while sz > 50 and sum(d.textlength(w + " ", font=font(sz)) for w, _ in parts) > 940: sz -= 4
            fs = font(sz)
            widths = [d.textlength(w + " ", font=fs) for w, _ in parts]; x = W / 2 - sum(widths) / 2
            pop = 1.0
            for (w, col), wd in zip(parts, widths):
                d.text((x, 1240), w, font=fs, fill=col, stroke_width=8, stroke_fill=(0, 0, 0), anchor="lm"); x += wd
    im.alpha_composite(ov)
    return np.asarray(im.convert("RGB"))

SNOW = [(random.random(), random.random(), random.uniform(60, 160), random.uniform(2, 6)) for _ in range(140)]
def snow(img, gt):
    im = Image.fromarray(img); d = ImageDraw.Draw(im)
    for x, y, v, r in SNOW:
        yy = (y * H + v * gt) % H; xx = (x * W + 20 * math.sin(gt + y * 9)) % W
        d.ellipse([xx - r, yy - r, xx + r, yy + r], fill=(235, 240, 250))
    return np.asarray(im)

R_ = None
def frame(si, t):
    global R_
    if R_ is None: R_ = Renderer(W, H)
    it, eye, tgt, lights = scene_3d(si, t)
    img = R_.render(it, eye, tgt, fov=42, lights=lights, sun_dir=(-0.5, -1.0, -0.35), sun_col=(0.32, 0.38, 0.6),
                    amb_top=(0.12, 0.14, 0.24), amb_bot=(0.05, 0.05, 0.09), fog=0.022, shadow_center=(0, 0, 0), shadow_size=14)
    img = snow(img, STARTS[si] + t)
    return overlay(si, t, img)

def render_scene(si):
    path = f"{D}/seg{si + 1}.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "18", "-threads", "1", path], stdin=subprocess.PIPE)
    for i in range(NFR[si]): p.stdin.write(frame(si, i / FPS).tobytes())
    p.stdin.close(); p.wait(); return si, p.returncode

def render_chunk(args):
    si, a, b = args
    path = f"{D}/seg{si + 1}_{a:04d}.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "18", "-threads", "1", path], stdin=subprocess.PIPE)
    for i in range(a, b): p.stdin.write(frame(si, i / FPS).tobytes())
    p.stdin.close(); p.wait(); return path

def audio():
    SR = 44100; TOTAL = sum(DUR); n = int(round(TOTAL * SR)); tt = np.arange(n) / SR; rnd = np.random.default_rng(1)
    def T_(d): return np.arange(int(d * SR)) / SR
    sfx = np.zeros(n)
    def add(sig, at):
        s0 = int(at * SR)
        if 0 <= s0 < n: sig = sig[: n - s0]; sfx[s0:s0 + len(sig)] += sig
    beat = np.zeros(n)                                                             # пульс 100 уд/мин
    k = 0.0
    while k < TOTAL - 0.5:
        t_ = T_(0.35); s0 = int(k * SR); sig = 0.35 * np.sin(2 * np.pi * 52 * t_) * np.exp(-t_ * 12); sig = sig[: n - s0]; beat[s0:s0 + len(sig)] += sig; k += 0.6
    drone = 0.06 * np.sin(2 * np.pi * 55 * tt) + 0.04 * np.sin(2 * np.pi * 82.4 * tt)
    music = (beat + drone) * np.clip(tt / 0.3, 0, 1) * np.clip((TOTAL - tt) / 1.5, 0, 1)
    t_ = T_(0.9); add(0.7 * np.sin(2 * np.pi * 40 * t_) * np.exp(-t_ * 4), 0.0)
    for j in range(3): add(0.15 * np.sin(2 * np.pi * (600 + 120 * j) * T_(0.1)) * np.exp(-T_(0.1) * 25), STARTS[0] + wt(0, "Все") + j * 0.15)
    for w in ("Воздух", "Вода", "Еда"):
        t0 = STARTS[1] + wt(1, w); add(0.5 * np.sin(2 * np.pi * 90 * T_(0.25)) * np.exp(-T_(0.25) * 18), t0 + 0.3)
        add(0.15 * np.sin(2 * np.pi * 1320 * T_(0.12)) * np.exp(-T_(0.12) * 25), t0 + 0.3)
    t_ = T_(0.5); add(0.25 * np.sin(2 * np.pi * np.cumsum(900 - 600 * t_ / 0.5) / SR) * np.exp(-t_ * 4), STARTS[1] + wt(1, "А денег"))
    for f in (523, 659, 784): add(0.08 * np.sin(2 * np.pi * f * T_(1.2)) * np.exp(-T_(1.2) * 3), STARTS[2] + wt(2, "Пиши"))
    voice = np.zeros(n)
    for i in range(N):
        raw = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", f"{D}/v{i + 1}.mp3", "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True).stdout
        v = np.frombuffer(raw, np.float32); v = v / max(1e-6, np.abs(v).max()) * 0.95
        s0 = int((STARTS[i] + LEAD) * SR); v = v[: n - s0]; voice[s0:s0 + len(v)] += v
    mix = np.clip(voice + music * 0.6 + sfx, -1, 1)
    (np.stack([mix, mix], 1) * 32767).astype(np.int16).tofile(f"{D}/audio.raw"); return SR

if __name__ == "__main__":
    print("durations", [round(x, 2) for x in DUR], "total", round(sum(DUR), 2), flush=True)
    if sys.argv[1:] == ["preview"]:
        tiles = []
        for si in range(N):
            for f in (0.2, 0.55, 0.9): tiles.append(Image.fromarray(frame(si, DUR[si] * f)).resize((270, 480)))
        sheet = Image.new("RGB", (270 * len(tiles), 480))
        for k, tl in enumerate(tiles): sheet.paste(tl, (k * 270, 0))
        sheet.save(f"{D}/preview.jpg", quality=85); sys.exit()
    from multiprocessing import Pool
    SR = audio(); print("audio ok", flush=True)
    jobs = []
    for si in range(N):
        for a in range(0, NFR[si], 60): jobs.append((si, a, min(NFR[si], a + 60)))
    with Pool(4) as pool: parts = pool.map(render_chunk, jobs)
    open(f"{D}/list.txt", "w").write("".join(f"file '{os.path.basename(x)}'\n" for x in parts))
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{D}/list.txt", "-f", "s16le", "-ar", str(SR), "-ac", "2", "-i", f"{D}/audio.raw",
                    "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-maxrate", "6M", "-bufsize", "12M", "-pix_fmt", "yuv420p",
                    "-af", "alimiter=limit=0.95", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", f"{D}/demo3d.mp4"], check=True)
    for x in parts: os.remove(x)
    print("done")
