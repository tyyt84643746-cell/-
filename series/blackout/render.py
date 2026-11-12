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
RED_HEADS = {2, 6}


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
        tag = "СЕРИЯ 1 · БЛЭКАУТ"; tw2 = d.textlength(tag, font=F_TAG)
        d.text((W / 2 - tw2 / 2, 290), tag, font=F_TAG, fill=(220, 226, 240, 230))
    for a0, b0, txt in CAPS[si]:
        if a0 <= t < b0:
            y = 1600
            for ln in wrap(d, txt, F_CAP, 960):
                lw = d.textlength(ln, font=F_CAP)
                d.rounded_rectangle([W / 2 - lw / 2 - 24, y - 10, W / 2 + lw / 2 + 24, y + 76], radius=16, fill=(6, 10, 20, 215))
                d.text((W / 2 - lw / 2, y), ln, font=F_CAP, fill=(244, 246, 250)); y += 92
    out.alpha_composite(ov)
    if si == 2 and t < 0.25:
        out = Image.blend(out, Image.new("RGBA", (W, H), (255, 255, 255, 255)), 0.85 * (1 - t / 0.25))
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
    music = (0.085 * np.sin(2 * np.pi * 55 * tt) + 0.055 * np.sin(2 * np.pi * 58.2 * tt)
             + 0.03 * np.sin(2 * np.pi * 82.4 * tt) + 0.02 * np.sin(2 * np.pi * 110.3 * tt + np.sin(tt * 0.3)))
    music *= 0.65 + 0.35 * np.sin(2 * np.pi * 0.07 * tt)
    gain = np.full(n, 0.5); gain[tt < STARTS[1]] = 0.85; gain[tt > STARTS[8]] = 0.85
    music *= gain * np.clip(tt / 1.5, 0, 1) * np.clip((TOTAL - tt) / 2.5, 0, 1)
    sfx = np.zeros(n)
    def add(sig, at):
        s0 = int(at * SR)
        if s0 >= n: return
        sig = sig[: n - s0]; sfx[s0:s0 + len(sig)] += sig
    def T(d): return np.arange(int(d * SR)) / SR
    def noise(d): return rnd.uniform(-1, 1, int(d * SR))
    def lowpass(x, a=0.08):
        y = np.zeros_like(x); acc = 0.0
        for k in range(len(x)): acc += a * (x[k] - acc); y[k] = acc
        return y
    # 1: треск ламп
    for a_ in (1.5, 1.75, 3.1):
        t_ = T(0.25); add(0.12 * np.sign(np.sin(2 * np.pi * 100 * t_)) * rnd.uniform(0.3, 1, len(t_)) * np.exp(-t_ * 8), STARTS[0] + a_)
    # 2: отключение
    t_ = T(2.4); ph = 2 * np.pi * np.cumsum(170 * np.exp(-t_ * 1.4) + 28) / SR
    add(0.32 * np.sin(ph) * np.clip(1 - t_ / 2.4, 0, 1), STARTS[2] - 0.8)
    # 3: тормоза + удар, щелчок фонарика
    t_ = T(1.6); ph = 2 * np.pi * np.cumsum(2300 - 800 * t_ / 1.6) / SR
    add(0.06 * np.sin(ph) * rnd.uniform(0.6, 1, len(t_)) * np.sin(np.pi * t_ / 1.6), STARTS[2])
    t_ = T(0.6); add(0.3 * noise(0.6) * np.exp(-t_ * 10) + 0.3 * np.sin(2 * np.pi * 45 * t_) * np.exp(-t_ * 6), STARTS[2] + 0.1)
    t_ = T(0.04); add(0.4 * noise(0.04) * np.exp(-t_ * 120), STARTS[2] + wt(2, "фонарик") + 0.25)
    # 4: шаги по снегу
    crunch = lowpass(noise(0.16), 0.25) * np.exp(-T(0.16) * 18) * 0.9
    k = 0.15
    while k < DUR[3] - 0.3: add(crunch, STARTS[3] + k); k += math.pi / 5.2
    # 5: шаги по лестнице, капля
    step = 0.5 * np.sin(2 * np.pi * 90 * T(0.12)) * np.exp(-T(0.12) * 30) + 0.15 * noise(0.12) * np.exp(-T(0.12) * 40)
    k = 0.2; tc = wt(4, "В кране")
    while k < tc - 0.3: add(step, STARTS[4] + k); k += math.pi / 4.0
    t_ = T(0.12); ph = 2 * np.pi * np.cumsum(900 + 1400 * t_ / 0.12) / SR
    add(0.22 * np.sin(ph) * np.exp(-t_ * 25), STARTS[4] + tc + 1.45)
    # 6: стук в дверь, скрип
    tk = wt(5, "Стук")
    for j in range(3):
        t_ = T(0.18); add(0.55 * np.sin(2 * np.pi * 110 * t_) * np.exp(-t_ * 28) + 0.2 * lowpass(noise(0.18), 0.3) * np.exp(-t_ * 30), STARTS[5] + tk + 0.05 + j * 0.22)
    t_ = T(0.8); ph = 2 * np.pi * np.cumsum(260 + 360 * t_ / 0.8) / SR
    add(0.07 * np.sin(ph) * np.sin(np.pi * t_ / 0.8) * rnd.uniform(0.5, 1, len(t_)), STARTS[5] + wt(5, "Это сосед") - 0.2)
    # 7: труба лопается, лёд трещит
    tb = wt(6, "лопается"); t_ = T(1.2)
    add(0.7 * noise(1.2) * np.exp(-t_ * 7) + 0.4 * np.sin(2 * np.pi * 50 * t_) * np.exp(-t_ * 5), STARTS[6] + tb)
    add(0.12 * lowpass(noise(1.8), 0.6) * np.exp(-T(1.8) * 1.2), STARTS[6] + tb + 0.2)
    for dt in (0, 0.13, 0.31, 0.45, 0.7):
        t_ = T(0.2); add(0.35 * noise(0.2) * np.exp(-t_ * 45), STARTS[6] + wt(6, "замерзает") + dt)
    # 8: свет в доме напротив — мягкий подъём
    t_ = T(1.8); ph = 2 * np.pi * np.cumsum(60 + 80 * t_ / 1.8) / SR
    add(0.12 * np.sin(ph) * np.sin(np.pi * t_ / 1.8), STARTS[7] + wt(7, "Дом напротив"))
    # 9: щелчок выключателя, вибрация телефона
    t_ = T(0.05); add(0.6 * noise(0.05) * np.exp(-t_ * 140), STARTS[8] + 0.18)
    for j in range(2):
        t_ = T(0.28); add(0.25 * np.sin(2 * np.pi * 160 * t_) * (np.sin(2 * np.pi * 30 * t_) > 0), STARTS[8] + wt(8, "Приходит") + j * 0.4)
    voice = np.zeros(n)
    for i in range(9):
        raw = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", f"{D}/v{i + 1}.mp3", "-f", "f32le",
                              "-ac", "1", "-ar", str(SR), "-"], capture_output=True).stdout
        v = np.frombuffer(raw, np.float32); v = v / max(1e-6, np.abs(v).max()) * 0.85
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
                    f"{D}/blackout_ep1.mp4"], check=True)
    print("done")
