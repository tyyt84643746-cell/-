"""Общий каркас 3D-серии: тайминг по озвучке, караоке-субтитры, свечения, снег, рендер по кускам, сведение.
Серия передаёт сюда свой модуль (ep) с SCENES, CAPTION_NUMS, KEY, LEADS, TAILS, ENV, scene_3d(), overlay(), sound()."""
import json, math, os, random, re, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from engine import Renderer, persp, look_at

W, H, FPS = 1080, 1920, 30
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
YEL = (255, 214, 64); RED = (240, 70, 60); WHITE = (255, 255, 255); GREEN = (60, 200, 110); PANEL = (8, 12, 26)
_F = {}
def font(sz):
    if sz not in _F: _F[sz] = ImageFont.truetype(FB, sz)
    return _F[sz]
def lerp(a, b, k): return a + (b - a) * k
def lerp3(a, b, k): return tuple(a[i] + (b[i] - a[i]) * k for i in range(3))
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(k): k = clamp(k); return k * k * (3 - 2 * k)
def stroke_text(d, xy, s, f, fill, sw=7, anchor="mm"):
    d.text(xy, s, font=f, fill=fill, stroke_width=sw, stroke_fill=(0, 0, 0) + ((fill[3],) if len(fill) == 4 else ()), anchor=anchor)
def project(pt, eye, tgt, fov):
    """Мировая точка -> (x, y) экрана и флаг «перед камерой»."""
    v = persp(fov, W / H, 0.1, 200) @ look_at(eye, tgt) @ np.array([pt[0], pt[1], pt[2], 1.0], "f4")
    if v[3] <= 0.01: return 0, 0, False
    return (v[0] / v[3] * 0.5 + 0.5) * W, (1 - (v[1] / v[3] * 0.5 + 0.5)) * H, True


_SHOW = None
def _job(args): return _SHOW._chunk(args)


class Show:
    def __init__(s, ep):
        s.ep = ep; s.D = os.path.dirname(os.path.abspath(ep.__file__)); s.N = len(ep.SCENES)
        s.ALN = [json.load(open(f"{s.D}/v{i}.json")) for i in range(1, s.N + 1)]
        s.NFR = [round((a["character_end_times_seconds"][-1] + ep.LEADS[i] + ep.TAILS[i]) * FPS) for i, a in enumerate(s.ALN)]
        s.DUR = [n / FPS for n in s.NFR]; s.STARTS = [sum(s.DUR[:i]) for i in range(s.N)]; s.TOTAL = sum(s.DUR)
        s.CAPS = [s._captions(i) for i in range(s.N)]
        s.R = None; s.q = float(os.environ.get("Q", "1"))
        rnd = random.Random(5)
        s.SNOW = [(rnd.random(), rnd.random(), rnd.uniform(30, 80), rnd.uniform(2, 5)) for _ in range(70)]
        yy, xx = np.mgrid[0:H, 0:W].astype("f4")
        s.VIG = (1 - 0.32 * np.clip((((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2), 0, 1))[..., None]
        s._gl = {}

    def wt(s, i, sub):
        text = s.ep.SCENES[i]["text"]; k = text.find(sub); assert k >= 0, sub
        return s.ALN[i]["character_start_times_seconds"][k] + s.ep.LEADS[i]

    def _captions(s, i):
        text = s.ep.SCENES[i]["text"]; a = s.ALN[i]; st = a["character_start_times_seconds"]; en = a["character_end_times_seconds"]; LEAD = s.ep.LEADS[i]
        words = [(m.start(), m.group()) for m in re.finditer(r"\S+", text) if m.group() != "—"]
        for k_, v_ in s.ep.CAPTION_NUMS.items():
            p0 = text.find(k_)
            if p0 < 0: continue
            p1 = p0 + len(k_)
            while p1 < len(text) and text[p1] != " ": p1 += 1
            words = [w for w in words if not (p0 <= w[0] < p1)] + [(p0, text[p0:p1].replace(k_, v_))]; words.sort()
        chunks, cur = [], []
        for w in words:
            cur.append(w)
            if len(cur) == 3 or w[1][-1] in ".?!": chunks.append(cur); cur = []
        if cur: chunks.append(cur)
        out = []
        for j, c in enumerate(chunks):
            a0 = st[c[0][0]] + LEAD
            b0 = (st[chunks[j + 1][0][0]] + LEAD) if j + 1 < len(chunks) else en[-1] + LEAD + 0.5
            out.append((a0, b0, [(st[p0] + LEAD, w) for p0, w in c]))
        return out

    def draw_captions(s, d, si, t, y=1180):
        for a0, b0, ws in s.CAPS[si]:
            if not (a0 <= t < b0): continue
            parts = []
            for ts_, w in ws:
                key = w.strip(".,?!—").lower() in s.ep.KEY or w[0].isdigit()
                parts.append((w, (205, 205, 205) if t < ts_ else (YEL if key else WHITE)))
            sz = 96
            while sz > 50 and sum(d.textlength(w + " ", font=font(sz)) for w, _ in parts) - d.textlength(" ", font=font(sz)) > 960: sz -= 4
            fs = font(sz); sp = d.textlength(" ", font=fs)
            widths = [d.textlength(w, font=fs) for w, _ in parts]; x = W / 2 - (sum(widths) + sp * (len(parts) - 1)) / 2
            k = ease((t - a0) / 0.1); yy = y + 14 * (1 - k)
            for (w, col), wd in zip(parts, widths):
                d.text((x, yy), w, font=fs, fill=col, stroke_width=9, stroke_fill=(0, 0, 0), anchor="lm"); x += wd + sp

    def checklist(s, d, t, items, x=60, y=470, w=440):
        """items: [(текст, время, ok: bool)] — панель с галочками/крестиками."""
        d.rounded_rectangle([x, y, x + w, y + 44 + 82 * len(items)], radius=28, fill=PANEL + (215,))
        for j, (name, t0, ok) in enumerate(items):
            yy = y + 40 + j * 82; on = t > t0
            pop = 1 + 0.25 * (1 - ease((t - t0) / 0.25)) if on else 1
            r = 25 * pop; cx, cy = x + 55, yy + 25
            d.rounded_rectangle([cx - r, cy - r, cx + r, cy + r], radius=10, outline=WHITE, width=5, fill=((GREEN if ok else RED) if on else None))
            if on and ok: d.line([(cx - 15, cy + 1), (cx - 3, cy + 13), (cx + 16, cy - 13)], fill=WHITE, width=7)
            if on and not ok: d.line([(cx - 13, cy - 13), (cx + 13, cy + 13)], fill=WHITE, width=7); d.line([(cx - 13, cy + 13), (cx + 13, cy - 13)], fill=WHITE, width=7)
            d.text((x + 105, yy + 25), name, font=font(46), fill=WHITE if on else (170, 176, 196), anchor="lm")

    def cta(s, d, t, t0, left, right, y=1330):
        """Две плашки: лайк = left, коммент = right."""
        k = ease((t - t0) / 0.35)
        if k <= 0: return
        a = int(235 * k); A = int(255 * k); dy = 40 * (1 - k)
        for j, (x, label, c) in enumerate(((290, left, (230, 60, 80)), (790, right, (60, 130, 230)))):
            pulse = 1 + 0.06 * math.sin(t * 7 + j * 1.5)
            d.rounded_rectangle([x - 225, y + dy, x + 225, y + 250 + dy], radius=40, fill=PANEL + (a,), outline=c + (A,), width=5)
            cx, cy = x, y + 85 + dy; r = pulse
            if j == 0:
                d.ellipse([cx - 62 * r, cy - 50 * r, cx + 2, cy + 14 * r], fill=c + (A,)); d.ellipse([cx - 2, cy - 50 * r, cx + 62 * r, cy + 14 * r], fill=c + (A,))
                d.polygon([(cx - 59 * r, cy - 4), (cx + 59 * r, cy - 4), (cx, cy + 62 * r)], fill=c + (A,))
            else:
                d.rounded_rectangle([cx - 66 * r, cy - 52 * r, cx + 66 * r, cy + 34 * r], radius=24, fill=c + (A,)); d.polygon([(cx - 30, cy + 30 * r), (cx - 6, cy + 30 * r), (cx - 34, cy + 62 * r)], fill=c + (A,))
                for dx in (-30, 0, 30): d.ellipse([cx + dx - 9, cy - 18, cx + dx + 9, cy], fill=(255, 255, 255, A))
            txt = ("ЛАЙК — " if j == 0 else "КОММЕНТ — ") + label
            d.text((x, y + 205 + dy), txt, font=font(36 if len(txt) <= 16 else 30), fill=(255, 255, 255, A), anchor="mm")

    def _glow(s, img, x, y, r, col, k):
        r = int(r)
        if r not in s._gl:
            g = np.mgrid[-r:r, -r:r].astype("f4"); dd = np.sqrt(g[0] ** 2 + g[1] ** 2) / r; s._gl[r] = (np.clip(1 - dd, 0, 1) ** 2)[..., None]
        x0, y0 = int(x) - r, int(y) - r; a0, b0 = max(0, x0), max(0, y0); a1, b1 = min(W, x0 + 2 * r), min(H, y0 + 2 * r)
        if a1 <= a0 or b1 <= b0: return
        sp = s._gl[r][b0 - y0:b1 - y0, a0 - x0:a1 - x0] * (np.array(col, "f4") * k)
        img[b0:b1, a0:a1] = np.clip(img[b0:b1, a0:a1] + sp, 0, 255)

    def frame(s, si, t):
        ep = s.ep
        if s.R is None: s.R = Renderer(int(W * s.q), int(H * s.q))
        sp = ep.scene_3d(si, t)
        env = dict(ep.ENV); env.update(sp.get("env", {}))
        img = s.R.render(sp["items"], sp["eye"], sp["tgt"], fov=sp.get("fov", 42), lights=sp.get("lights", ()), **env)
        if s.q != 1: img = np.asarray(Image.fromarray(img).resize((W, H), Image.BILINEAR))
        img = img.astype("f4")
        for pt, col, r, k in sp.get("glows", ()):
            x, y, ok = project(pt, sp["eye"], sp["tgt"], sp.get("fov", 42))
            if ok: s._glow(img, x, y, r, col, k)
        if sp.get("sepia"):
            g = img @ np.array([0.3, 0.59, 0.11], "f4"); k = sp["sepia"]
            img = img * (1 - k) + np.clip(g[..., None] * np.array([1.12, 0.96, 0.74], "f4") + 8, 0, 255) * k
        img = (img * s.VIG).astype("u1")
        gt = s.STARTS[si] + t
        im = Image.fromarray(img).convert("RGBA"); ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        for x, y, v, r in s.SNOW:
            yy = (y * H + v * gt) % H; xx = (x * W + 24 * math.sin(gt * 0.7 + y * 9)) % W
            d.ellipse([xx - r, yy - r, xx + r, yy + r], fill=(240, 244, 252, 200))
        ep.overlay(s, si, t, d)
        s.draw_captions(d, si, t)
        im.alpha_composite(ov)
        return np.asarray(im.convert("RGB"))

    # ------------------------------------------------------------ звук
    def mix(s):
        SR = 44100; n = int(round(s.TOTAL * SR)); tt = np.arange(n) / SR
        sfx = np.zeros(n)
        def add(sig, at):
            s0 = int(at * SR)
            if 0 <= s0 < n: sig = sig[: n - s0]; sfx[s0:s0 + len(sig)] += sig
        music = s.ep.sound(s, add, SR, n, tt)
        voice = np.zeros(n)
        for i in range(s.N):
            raw = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", f"{s.D}/v{i + 1}.mp3", "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True).stdout
            v = np.frombuffer(raw, np.float32); v = v / max(1e-6, np.abs(v).max()) * 0.95
            s0 = int((s.STARTS[i] + s.ep.LEADS[i]) * SR); v = v[: n - s0]; voice[s0:s0 + len(v)] += v
        m = np.clip(voice + music + sfx, -1, 1)
        (np.stack([m, m], 1) * 32767).astype(np.int16).tofile(f"{s.D}/audio.raw"); return SR

    def _chunk(s, args):
        si, a, b = args; path = f"{s.D}/seg{si + 1}_{a:04d}.mp4"
        p = subprocess.Popen(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "16", "-threads", "1", path], stdin=subprocess.PIPE)
        for i in range(a, b): p.stdin.write(s.frame(si, i / FPS).tobytes())
        p.stdin.close(); p.wait(); return path

    def sheet(s, frames, path, tw=270):
        th = tw * H // W; cols = min(len(frames), 8); rows = (len(frames) + cols - 1) // cols
        im = Image.new("RGB", (tw * cols, th * rows))
        for k, (si, t) in enumerate(frames): im.paste(Image.fromarray(s.frame(si, t)).resize((tw, th), Image.LANCZOS), ((k % cols) * tw, (k // cols) * th))
        im.save(path, quality=88)

    def run(s, name):
        print("durations", [round(x, 2) for x in s.DUR], "total", round(s.TOTAL, 2), flush=True)
        a = sys.argv[1:]
        if a[:1] == ["preview"]:
            s.sheet([(si, s.DUR[si] * f) for si in range(s.N) for f in (0.15, 0.5, 0.9)], f"{s.D}/preview.jpg", 216); return
        if a[:1] == ["sheet"]:                                    # sheet <сцена> <кадров> [ширина]
            si = int(a[1]); k = int(a[2]); tw = int(a[3]) if len(a) > 3 else 270
            s.sheet([(si, s.DUR[si] * (j + 0.5) / k) for j in range(k)], f"{s.D}/sheet{si + 1}.jpg", tw); return
        if a[:1] == ["at"]:                                       # at <сцена> <сек>
            Image.fromarray(s.frame(int(a[1]), float(a[2]))).save(f"{s.D}/frame.jpg", quality=90); return
        from multiprocessing import Pool
        SR = s.mix(); print("audio ok", flush=True)
        jobs = [(si, x, min(s.NFR[si], x + 45)) for si in range(s.N) for x in range(0, s.NFR[si], 45)]
        global _SHOW; _SHOW = s; s.R = None
        with Pool(4) as pool: parts = pool.map(_job, jobs)
        open(f"{s.D}/list.txt", "w").write("".join(f"file '{os.path.basename(x)}'\n" for x in parts))
        subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{s.D}/list.txt", "-f", "s16le", "-ar", str(SR), "-ac", "2", "-i", f"{s.D}/audio.raw",
                        "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-maxrate", "6M", "-bufsize", "12M", "-pix_fmt", "yuv420p",
                        "-af", "volume=2dB,alimiter=limit=0.8:level=disabled", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", f"{s.D}/{name}.mp4"], check=True)
        for x in parts: os.remove(x)
        print("done", flush=True)
