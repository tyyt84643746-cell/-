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
CAPS = [captions(i) for i in range(N)]
HEADS = [s["head"] for s in SCENES]
RED_HEADS = {N - 1}


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
    if si == N - 1 and t > DUR[N - 1] - 2.6:
        from script import SERIES_TAG
        tag = SERIES_TAG; tw2 = d.textlength(tag, font=F_TAG)
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
    for si in range(N):
        for f in fracs:
            t = DUR[si] * f
            img, zoom, bright = SCENE_FUNCS[si](t)
            tiles.append(post(si, 0, t, img, zoom, bright).resize((270, 480)))
    sheet = Image.new("RGB", (270 * N, 480 * len(fracs)))
    for k, tile in enumerate(tiles):
        si, j = divmod(k, len(fracs)); sheet.paste(tile, (si * 270, j * 480))
    sheet.save(f"{D}/preview.jpg", quality=85)


def audio():
    SR = 44100; TOTAL = sum(DUR); n = int(round(TOTAL * SR)); tt = np.arange(n) / SR
    rnd = np.random.default_rng(9)
    music = (0.08 * np.sin(2 * np.pi * 49 * tt) + 0.05 * np.sin(2 * np.pi * 51.8 * tt)
             + 0.03 * np.sin(2 * np.pi * 73.4 * tt) + 0.018 * np.sin(2 * np.pi * 98 * tt + np.sin(tt * 0.3)))
    music *= 0.65 + 0.35 * np.sin(2 * np.pi * 0.06 * tt)
    gain = np.full(n, 0.5); gain[tt > STARTS[N - 1] + wt(N - 1, "Осталось")] = 0.9
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
    def sweep(f0, f1, d):
        t = T(d); return t, np.sin(2 * np.pi * np.cumsum(f0 + (f1 - f0) * t / d) / SR)
    def thump(f, d, a): return a * np.sin(2 * np.pi * f * T(d)) * np.exp(-T(d) * (4 / d))
    def clang(at, a=0.22):
        for f in (310, 470, 820): add(a * np.sin(2 * np.pi * f * T(1.2)) * np.exp(-T(1.2) * 4), at)
    def chime(at):
        for f in (2100, 2600, 3200): add(0.16 * np.sin(2 * np.pi * f * T(0.5)) * np.exp(-T(0.5) * 7), at + (f - 2100) / 9000)
    def pencil(at, d=0.9): add(lp(noise(d), 0.6) * 0.1 * (0.5 + 0.5 * np.sin(2 * np.pi * 9 * T(d))), at)
    def click(at):
        add(0.5 * noise(0.05) * np.exp(-T(0.05) * 120), at); add(0.3 * np.sin(2 * np.pi * 900 * T(0.08)) * np.exp(-T(0.08) * 40), at)
    tick = 0.25 * np.sin(2 * np.pi * 2400 * T(0.02)) * np.exp(-T(0.02) * 300)
    blip = 0.2 * np.sin(2 * np.pi * 1320 * T(0.09)) * np.exp(-T(0.09) * 30)
    for i in range(N):
        for j in range(3): add(tick * (1.0 if j % 2 == 0 else 0.7), STARTS[i] + 0.05 + j * 0.5)
    S = STARTS
    crunch = lp(noise(0.16), 0.25) * np.exp(-T(0.16) * 18) * 0.9
    def steps(a, b):
        k = a
        while k < b: add(crunch, k); k += math.pi / 5
    def creak(at, d=0.8):
        t_, s_ = sweep(240, 600, d); add(0.09 * s_ * np.sin(np.pi * t_ / d) * rnd.uniform(0.5, 1, len(t_)), at)
    def murmur(at, d, a=0.3):
        m = lp(noise(d), 0.06) * a * (0.6 + 0.4 * np.sin(2 * np.pi * 3.1 * T(d))) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.9 * T(d)))
        add(m * np.clip(T(d) / 0.5, 0, 1) * np.clip((d - T(d)) / 0.6, 0, 1), at)
    def wind(at, d): add(lp(noise(d), 0.02) * 0.3 * np.clip(T(d) / 0.5, 0, 1) * np.clip((d - T(d)) / 0.5, 0, 1), at)
    def boom(at, a=0.5): add(thump(46, 1.3, a), at)
    clang(S[0] + 0.1, 0.12); tm = wt(0, "В убежище"); murmur(S[0] + tm, DUR[0] - tm); boom(S[0] + wt(0, "Желающих")); boom(S[0] + wt(0, "Нужен"), 0.35)
    for w_ in ("Сначала", "Потом старики", "Потом те"): pencil(S[1] + wt(1, w_))
    pencil(S[1] + wt(1, "Потом те") + 0.7); boom(S[1] + wt(1, "Мест остаётся"), 0.4)
    chime(S[2] + 0.4); add(thump(60, 0.8, 0.3), S[2] + wt(2, "Ей шесть"))
    for f in (523, 659): add(0.07 * np.sin(2 * np.pi * f * T(1.6)) * np.exp(-T(1.6) * 2.5), S[2] + wt(2, "Её мама"))
    add(0.2 * lp(noise(0.35), 0.5) * np.sin(np.pi * T(0.35) / 0.35), S[3] + wt(3, "Находит"))
    pencil(S[3] + wt(3, "И зачёркивает"), 0.7); boom(S[3] + wt(3, "И зачёркивает"), 0.45); pencil(S[3] + wt(3, "На это место"), 1.1)
    for f in (523, 659, 784): add(0.07 * np.sin(2 * np.pi * f * T(1.8)) * np.exp(-T(1.8) * 2.2), S[3] + wt(3, "На это место") + 0.6)
    add(thump(90, 0.4, 0.4), S[4] + 0.5); add(blip, S[4] + wt(4, "Артём отвечает") + 0.6); chime(S[4] + wt(4, "Он на четверых"))
    wind(S[5], DUR[5]); steps(S[5] + 0.1, S[5] + wt(5, "Четвёртое")); add(thump(60, 0.9, 0.35), S[5] + wt(5, "Четвёртое"))
    chime(S[6] + wt(6, "Потом берёт") + 0.2); to = wt(6, "И открывает"); click(S[6] + to); creak(S[6] + to + 0.5, 1.0); clang(S[6] + to + 0.6, 0.12)
    for f in (392, 523, 659): add(0.08 * np.sin(2 * np.pi * f * T(2.0)) * np.exp(-T(2.0) * 2.0), S[6] + to + 1.0)
    st = lp(noise(1.2), 0.8) - lp(noise(1.2), 0.2); add(0.25 * st * np.clip(1 - T(1.2) / 1.2, 0, 1), S[7] + 0.5)
    t_, s_ = sweep(900, 300, 0.5); add(0.1 * s_ * np.sin(np.pi * t_ / 0.5), S[7] + 0.6)
    boom(S[7] + wt(7, "Переговоры"), 0.55)
    t_ = T(1.6); add(0.7 * np.sin(2 * np.pi * 38 * t_) * np.exp(-t_ * 2.5) + 0.2 * lp(noise(1.6), 0.1) * np.exp(-t_ * 3), S[7] + wt(7, "Осталось"))
    voice = np.zeros(n)
    for i in range(N):
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
        for si, rc in pool.imap_unordered(render_scene, range(N)): print("scene", si + 1, "rc", rc, flush=True)
    open(f"{D}/list.txt", "w").write("".join(f"file 'seg{i}.mp4'\n" for i in range(1, N + 1)))
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{D}/list.txt",
                    "-f", "s16le", "-ar", str(SR), "-ac", "2", "-i", f"{D}/audio.raw",
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
                    f"{D}/tridtsat_ep6_raw.mp4"], check=True)
    print("done")
