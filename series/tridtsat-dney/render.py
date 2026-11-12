import math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from multiprocessing import Pool
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
from scenes import *

F_HEAD = ImageFont.truetype(FB, 62); F_CAP = ImageFont.truetype(FB, 56); F_TAG = ImageFont.truetype(FB, 34)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIG = (1 - 0.55 * (((xx - W / 2) / (W / 2)) ** 2 * 0.6 + ((yy - H / 2) / (H / 2)) ** 2) / 1.6).clip(0, 1)[..., None]
rng = np.random.default_rng(1)
GRAIN = [rng.normal(0, 5.5, (H, W, 1)).astype(np.float32) for _ in range(6)]
CAPS = [captions(i) for i in range(9)]
HEADS = [s["head"] for s in SCENES]
RED_HEADS = {8}


def wrap(d, text, f, maxw):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur); return lines


def post(si, i, t, img, zoom, bright):
    if zoom != 1.0:
        cw, ch = W / zoom, H / zoom; ox, oy = (W - cw) / 2, (H - ch) / 2
        img = img.resize((W, H), Image.BILINEAR, box=(ox, oy, ox + cw, oy + ch))
    a = np.asarray(img.convert("RGB")).astype(np.float32)
    a = a * (VIG * bright) + GRAIN[i % 6]
    out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    head = HEADS[si]; tw = d.textlength(head, font=F_HEAD)
    d.rounded_rectangle([W / 2 - tw / 2 - 32, 160, W / 2 + tw / 2 + 32, 268], radius=20, fill=(6, 10, 20, 225))
    d.text((W / 2 - tw / 2, 178), head, font=F_HEAD, fill=RED if si in RED_HEADS else AMBER)
    if si == 8 and t > DUR[8] - 2.6:
        tag = "ТРИДЦАТЬ ДНЕЙ · СЕРИЯ 1"; tw2 = d.textlength(tag, font=F_TAG)
        d.text((W / 2 - tw2 / 2, 290), tag, font=F_TAG, fill=(220, 226, 240, 230))
    for a0, b0, txt in CAPS[si]:
        if a0 <= t < b0:
            y = 1600
            for ln in wrap(d, txt, F_CAP, 960):
                lw = d.textlength(ln, font=F_CAP)
                d.rounded_rectangle([W / 2 - lw / 2 - 24, y - 10, W / 2 + lw / 2 + 24, y + 76], radius=16, fill=(6, 10, 20, 215))
                d.text((W / 2 - lw / 2, y), ln, font=F_CAP, fill=(244, 246, 250)); y += 92
    out.alpha_composite(ov)
    return out.convert("RGB")


def render_scene(si):
    fn = SCENE_FUNCS[si]; path = f"{D}/seg{si + 1}.mp4"
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p",
           "-preset", "medium", "-crf", "19", "-threads", "1", path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(NFR[si]):
        t = i / FPS
        img, zoom, bright = fn(t)
        p.stdin.write(post(si, i, t, img, zoom, bright).tobytes())
    p.stdin.close(); p.wait()
    return si, p.returncode


def preview(fracs=(0.15, 0.5, 0.85)):
    tiles = []
    for si in range(9):
        for f in fracs:
            t = DUR[si] * f
            img, zoom, bright = SCENE_FUNCS[si](t)
            tiles.append(post(si, 0, t, img, zoom, bright).resize((270, 480)))
    sheet = Image.new("RGB", (270 * 9, 480 * len(fracs)))
    for k, tile in enumerate(tiles):
        si, j = divmod(k, len(fracs)); sheet.paste(tile, (si * 270, j * 480))
    sheet.save(f"{D}/preview.jpg", quality=85)


def audio():
    SR = 44100; TOTAL = sum(DUR); n = int(round(TOTAL * SR)); tt = np.arange(n) / SR
    rnd = np.random.default_rng(3)
    music = (0.08 * np.sin(2 * np.pi * 49 * tt) + 0.05 * np.sin(2 * np.pi * 51.8 * tt)
             + 0.03 * np.sin(2 * np.pi * 73.4 * tt) + 0.018 * np.sin(2 * np.pi * 98 * tt + np.sin(tt * 0.3)))
    music *= 0.65 + 0.35 * np.sin(2 * np.pi * 0.06 * tt)
    gain = np.full(n, 0.5); gain[tt < STARTS[1]] = 0.8; gain[tt > STARTS[8]] = 0.9
    music *= gain * np.clip(tt / 1.5, 0, 1) * np.clip((TOTAL - tt) / 2.5, 0, 1)
    sfx = np.zeros(n)
    def add(sig, at):
        s0 = int(at * SR)
        if s0 >= n or s0 < 0: return
        sig = sig[: n - s0]; sfx[s0:s0 + len(sig)] += sig
    def T(d): return np.arange(int(d * SR)) / SR
    def noise(d): return rnd.uniform(-1, 1, int(d * SR))
    def lp(x, a):
        y = np.zeros_like(x); acc = 0.0
        for k in range(len(x)): acc += a * (x[k] - acc); y[k] = acc
        return y
    tick = 0.25 * np.sin(2 * np.pi * 2400 * T(0.02)) * np.exp(-T(0.02) * 300)
    for i in range(9):
        for j in range(3): add(tick * (1.0 if j % 2 == 0 else 0.7), STARTS[i] + 0.05 + j * 0.5)
    t_ = T(0.9); add(0.6 * np.sin(2 * np.pi * 42 * t_) * np.exp(-t_ * 5), 0.05)
    blip = 0.2 * np.sin(2 * np.pi * 1320 * T(0.09)) * np.exp(-T(0.09) * 30)
    tv_noise = lp(noise(4.0), 0.05) * 0.18
    add(tv_noise * np.clip(np.sin(np.pi * T(4.0) / 4.0) * 3, 0, 1), STARTS[1] + 0.2)
    tf = wt(1, "Друзья")
    for d in (0, 0.9, 1.8): add(blip, STARTS[1] + tf + d)
    purr = 0.12 * lp(noise(3.0), 0.04) * (0.5 + 0.5 * np.sin(2 * np.pi * 24 * T(3.0)))
    add(purr, STARTS[1] + tf + 2.2)
    click = 0.12 * noise(0.025) * np.exp(-T(0.025) * 200)
    k = 0.6
    while k < wt(2, "Утром") - 0.3: add(click, STARTS[2] + k + rnd.uniform(0, 0.08)); k += rnd.uniform(0.12, 0.3)
    add(0.3 * np.sin(2 * np.pi * 900 * T(0.06)) * np.exp(-T(0.06) * 50), STARTS[2] + wt(2, "Утром") + 1.2)
    crunch = lp(noise(0.16), 0.25) * np.exp(-T(0.16) * 18) * 0.9
    k = 0.1
    while k < 3.6: add(crunch, STARTS[3] + k); k += math.pi / 5
    wind = lp(noise(DUR[3] + DUR[4]), 0.02) * 0.25
    add(wind, STARTS[3])
    thud = 0.45 * np.sin(2 * np.pi * 70 * T(0.2)) * np.exp(-T(0.2) * 18) + 0.25 * lp(noise(0.2), 0.3) * np.exp(-T(0.2) * 25)
    k = (math.pi / 2) / 4.5
    while k < DUR[4] - 0.3: add(thud, STARTS[4] + k); k += 2 * math.pi / 4.5
    tv_ = wt(4, "Видео")
    for d in (0.0, 0.6, 1.1, 1.5, 1.8, 2.1, 2.35, 2.6): add(blip * 0.7, STARTS[4] + tv_ + d)
    pop = 0.35 * np.sin(2 * np.pi * 180 * T(0.15)) * np.exp(-T(0.15) * 22) + 0.15 * lp(noise(0.15), 0.4) * np.exp(-T(0.15) * 30)
    for w in ("Фильтры", "Вода", "Консервы", "корма"): add(pop, STARTS[5] + wt(5, w))
    rl = DUR[6] + wt(7, "Твой дед")
    rain = lp(noise(rl), 0.35) * 0.22 + lp(noise(rl), 0.05) * 0.2
    rain *= np.clip(T(rl) / 0.8, 0, 1) * np.clip((rl - T(rl)) / 0.4, 0, 1)
    add(rain, STARTS[6])
    fl = DUR[7] - wt(7, "Твой дед")
    crackle = np.zeros(int(fl * SR)); idx = rnd.integers(0, len(crackle), 300); crackle[idx] = rnd.uniform(-0.5, 0.5, 300)
    add(crackle + 0.06 * np.sin(2 * np.pi * 110 * T(fl)) * np.clip(T(fl) / 1.0, 0, 1), STARTS[7] + wt(7, "Твой дед"))
    add(0.15 * noise(0.5) * np.exp(-T(0.5) * 6), STARTS[8])
    t_ = T(1.6); add(0.7 * np.sin(2 * np.pi * 38 * t_) * np.exp(-t_ * 2.5) + 0.2 * lp(noise(1.6), 0.1) * np.exp(-t_ * 3), STARTS[8] + 1.2)
    voice = np.zeros(n)
    for i in range(9):
        raw = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", f"{D}/v{i + 1}.mp3", "-f", "f32le",
                              "-ac", "1", "-ar", str(SR), "-"], capture_output=True).stdout
        v = np.frombuffer(raw, np.float32); v = v / max(1e-6, np.abs(v).max()) * 0.8
        s0 = int((STARTS[i] + LEAD) * SR); v = v[: n - s0]; voice[s0:s0 + len(v)] += v
    mix = np.clip(voice + music + sfx, -1, 1)
    (np.stack([mix, mix], 1) * 32767).astype(np.int16).tofile(f"{D}/audio.raw")
    return SR


if __name__ == "__main__":
    print("durations", [round(d, 2) for d in DUR], "total", round(sum(DUR), 2), flush=True)
    if sys.argv[1:] == ["preview"]:
        preview(); sys.exit()
    SR = audio(); print("audio ok", flush=True)
    with Pool(4) as pool:
        for si, rc in pool.imap_unordered(render_scene, range(9)): print("scene", si + 1, "rc", rc, flush=True)
    open(f"{D}/list.txt", "w").write("".join(f"file 'seg{i}.mp4'\n" for i in range(1, 10)))
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{D}/list.txt",
                    "-f", "s16le", "-ar", str(SR), "-ac", "2", "-i", f"{D}/audio.raw",
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
                    f"{D}/tridtsat_ep1_raw.mp4"], check=True)
    print("done")
