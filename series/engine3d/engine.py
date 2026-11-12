"""Мини-движок 3D на moderngl: low-poly примитивы, солнце с тенями, точечные огни, туман, небо-градиент.
Запуск только под виртуальным экраном: xvfb-run -a python3 ...  (LIBGL_ALWAYS_SOFTWARE=1)."""
import math
import numpy as np
import moderngl

# ------------------------------------------------------------------ матрицы
def persp(fovy, aspect, near, far):
    f = 1 / math.tan(math.radians(fovy) / 2)
    m = np.zeros((4, 4), "f4"); m[0, 0] = f / aspect; m[1, 1] = f
    m[2, 2] = (far + near) / (near - far); m[2, 3] = 2 * far * near / (near - far); m[3, 2] = -1
    return m

def ortho(l, r, b, t, n, f):
    m = np.eye(4, dtype="f4"); m[0, 0] = 2 / (r - l); m[1, 1] = 2 / (t - b); m[2, 2] = -2 / (f - n)
    m[0, 3] = -(r + l) / (r - l); m[1, 3] = -(t + b) / (t - b); m[2, 3] = -(f + n) / (f - n)
    return m

def look_at(eye, target, up=(0, 1, 0)):
    eye, target, up = map(lambda v: np.array(v, "f4"), (eye, target, up))
    f = target - eye; f /= np.linalg.norm(f); s = np.cross(f, up); s /= np.linalg.norm(s); u = np.cross(s, f)
    m = np.eye(4, dtype="f4"); m[0, :3] = s; m[1, :3] = u; m[2, :3] = -f
    m[0, 3] = -s @ eye; m[1, 3] = -u @ eye; m[2, 3] = f @ eye
    return m

def T(x, y, z):
    m = np.eye(4, dtype="f4"); m[:3, 3] = (x, y, z); return m

def S(x, y=None, z=None):
    y = x if y is None else y; z = x if z is None else z
    return np.diag(np.array((x, y, z, 1), "f4"))

def Rx(a):
    c, s = math.cos(a), math.sin(a); m = np.eye(4, dtype="f4"); m[1, 1] = c; m[1, 2] = -s; m[2, 1] = s; m[2, 2] = c; return m

def Ry(a):
    c, s = math.cos(a), math.sin(a); m = np.eye(4, dtype="f4"); m[0, 0] = c; m[0, 2] = s; m[2, 0] = -s; m[2, 2] = c; return m

def Rz(a):
    c, s = math.cos(a), math.sin(a); m = np.eye(4, dtype="f4"); m[0, 0] = c; m[0, 1] = -s; m[1, 0] = s; m[1, 1] = c; return m

def M(*ms):
    out = np.eye(4, dtype="f4")
    for m in ms: out = out @ m
    return out

def rgb(c):
    """(r,g,b) 0..255 -> 0..1 в линейном пространстве (грубо)."""
    return tuple((v / 255.0) ** 2.2 for v in c)

# ------------------------------------------------------------------ сетки
def _cube():
    v = []
    faces = [((1, 0, 0), [(1, -1, -1), (1, 1, -1), (1, 1, 1), (1, -1, 1)]), ((-1, 0, 0), [(-1, -1, 1), (-1, 1, 1), (-1, 1, -1), (-1, -1, -1)]),
             ((0, 1, 0), [(-1, 1, -1), (-1, 1, 1), (1, 1, 1), (1, 1, -1)]), ((0, -1, 0), [(-1, -1, 1), (-1, -1, -1), (1, -1, -1), (1, -1, 1)]),
             ((0, 0, 1), [(-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)]), ((0, 0, -1), [(1, -1, -1), (-1, -1, -1), (-1, 1, -1), (1, 1, -1)])]
    for n, q in faces:
        for i in (0, 1, 2, 0, 2, 3): v += [c * 0.5 for c in q[i]] + list(n)
    return np.array(v, "f4")

def _sphere(nu=24, nv=16):
    v = []
    def P(i, j):
        th = math.pi * j / nv; ph = 2 * math.pi * i / nu
        x, y, z = math.sin(th) * math.cos(ph), math.cos(th), math.sin(th) * math.sin(ph)
        return [x * 0.5, y * 0.5, z * 0.5, x, y, z]
    for j in range(nv):
        for i in range(nu):
            a, b, c, d = P(i, j), P(i + 1, j), P(i + 1, j + 1), P(i, j + 1)
            v += a + c + b + a + d + c
    return np.array(v, "f4")

def _cyl(n=20, cone=False):
    v = []
    for i in range(n):
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        c0, s0, c1, s1 = math.cos(a0), math.sin(a0), math.cos(a1), math.sin(a1)
        rt = 0.0 if cone else 0.5
        ny = 0.5 if cone else 0.0
        n0 = [c0, ny, s0]; n1 = [c1, ny, s1]
        b0 = [0.5 * c0, -0.5, 0.5 * s0]; b1 = [0.5 * c1, -0.5, 0.5 * s1]; t0 = [rt * c0, 0.5, rt * s0]; t1 = [rt * c1, 0.5, rt * s1]
        v += b0 + n0 + t1 + n1 + b1 + n1 + b0 + n0 + t0 + n0 + t1 + n1
        v += [0, -0.5, 0, 0, -1, 0] + b1 + [0, -1, 0] + b0 + [0, -1, 0]
        if not cone: v += [0, 0.5, 0, 0, 1, 0] + t0 + [0, 1, 0] + t1 + [0, 1, 0]
    return np.array(v, "f4")

def _prism():
    """Треугольная призма (крыша) вдоль оси X: основание y=-0.5 (z от -0.5 до 0.5), конёк y=0.5, z=0."""
    A, B, C = (-0.5, 0.5), (0.5, -0.5), (0.0, 0.5)  # (z,y): A=(-.5,-.5) B=(.5,-.5) C=(0,.5)
    A, B, C = (-0.5, -0.5), (0.5, -0.5), (0.0, 0.5)
    v = []
    def tri(p, q, r, n):
        nonlocal v
        for pt in (p, q, r): v += list(pt) + list(n)
    for x in (-0.5, 0.5):
        sgn = 1 if x > 0 else -1
        p = [(x, A[1], A[0]), (x, B[1], B[0]), (x, C[1], C[0])]
        tri(*(p if sgn > 0 else p[::-1]), (sgn, 0, 0))
    for (z0, y0), (z1, y1) in ((A, C), (C, B), (B, A)):
        nz, ny = (y1 - y0), -(z1 - z0); L = math.hypot(nz, ny); nz, ny = nz / L, ny / L
        if (z0, y0) == B: nz, ny = 0, -1
        q = [(-0.5, y0, z0), (0.5, y0, z0), (0.5, y1, z1), (-0.5, y1, z1)]
        n = (0, ny, nz)
        tri(q[0], q[2], q[1], n); tri(q[0], q[3], q[2], n)
    return np.array(v, "f4")

VS = """
#version 330
in vec3 in_pos; in vec3 in_norm;
uniform mat4 u_model, u_vp, u_light;
out vec3 v_w; out vec3 v_n; out vec4 v_l;
void main(){ vec4 w = u_model * vec4(in_pos,1.0); v_w = w.xyz; v_n = mat3(transpose(inverse(u_model))) * in_norm;
  v_l = u_light * w; gl_Position = u_vp * w; }
"""
FS = """
#version 330
in vec3 v_w; in vec3 v_n; in vec4 v_l;
uniform vec3 u_color; uniform float u_emit;
uniform vec3 u_sun_dir, u_sun_col, u_amb_top, u_amb_bot, u_fog_col, u_cam; uniform float u_fog;
uniform int u_npl; uniform vec3 u_pl_pos[8]; uniform vec3 u_pl_col[8]; uniform float u_pl_rad[8];
uniform sampler2DShadow u_shadow; uniform float u_use_shadow;
out vec4 f;
float shadow(){
  vec3 p = v_l.xyz / v_l.w * 0.5 + 0.5;
  if (p.x<0.0||p.x>1.0||p.y<0.0||p.y>1.0||p.z>1.0) return 1.0;
  float s = 0.0; vec2 tx = 1.0 / vec2(textureSize(u_shadow,0));
  for (int i=-1;i<=1;i++) for (int j=-1;j<=1;j++) s += texture(u_shadow, vec3(p.xy + vec2(i,j)*tx, p.z - 0.0015));
  return s/9.0;
}
void main(){
  vec3 n = normalize(v_n); vec3 V = normalize(u_cam - v_w);
  vec3 amb = mix(u_amb_bot, u_amb_top, n.y*0.5+0.5);
  float sh = u_use_shadow > 0.5 ? shadow() : 1.0;
  vec3 lit = amb + u_sun_col * max(dot(n, -u_sun_dir), 0.0) * sh;
  for (int i=0;i<u_npl;i++){
    vec3 L = u_pl_pos[i] - v_w; float d = length(L); L /= d;
    float a = clamp(1.0 - d/u_pl_rad[i], 0.0, 1.0); a *= a;
    lit += u_pl_col[i] * a * (0.35 + 0.65*max(dot(n,L),0.0));
  }
  float rim = pow(1.0 - max(dot(n,V),0.0), 3.0) * 0.18;
  vec3 c = u_color * lit + u_color * u_emit + rim * u_sun_col;
  float d = length(u_cam - v_w); float fg = 1.0 - exp(-pow(d*u_fog, 2.0));
  c = mix(c, u_fog_col, clamp(fg,0.0,1.0));
  f = vec4(pow(max(c,0.0), vec3(1.0/2.2)), 1.0);
}
"""
SVS = """
#version 330
in vec3 in_pos; uniform mat4 u_model, u_light;
void main(){ gl_Position = u_light * u_model * vec4(in_pos,1.0); }
"""
SFS = "#version 330\nvoid main(){}"
SKY_VS = """
#version 330
out vec2 uv; void main(){ vec2 p = vec2((gl_VertexID<<1)&2, gl_VertexID&2); uv = p; gl_Position = vec4(p*2.0-1.0, 0.0, 1.0); }
"""
SKY_FS = """
#version 330
in vec2 uv; uniform vec3 u_top, u_mid, u_bot; uniform float u_hz; out vec4 f;
void main(){ float y = uv.y; vec3 c = y > u_hz ? mix(u_mid, u_top, (y-u_hz)/(1.0-u_hz)) : mix(u_bot, u_mid, y/u_hz);
  f = vec4(pow(c, vec3(1.0/2.2)), 1.0); }
"""


class Renderer:
    def __init__(s, w=1080, h=1920, samples=4, shadow=2048):
        s.ctx = moderngl.create_standalone_context()
        s.w, s.h = w, h
        s.prog = s.ctx.program(vertex_shader=VS, fragment_shader=FS)
        s.sprog = s.ctx.program(vertex_shader=SVS, fragment_shader=SFS)
        s.sky = s.ctx.program(vertex_shader=SKY_VS, fragment_shader=SKY_FS)
        s.sky_vao = s.ctx.vertex_array(s.sky, [])
        s.meshes = {}
        for name, data in (("cube", _cube()), ("sphere", _sphere()), ("cyl", _cyl()), ("cone", _cyl(cone=True)), ("prism", _prism())):
            buf = s.ctx.buffer(data.tobytes())
            s.meshes[name] = (s.ctx.vertex_array(s.prog, [(buf, "3f 3f", "in_pos", "in_norm")]),
                              s.ctx.vertex_array(s.sprog, [(buf, "3f 12x", "in_pos")]), len(data) // 6)
        s.fbo = s.ctx.framebuffer(color_attachments=[s.ctx.renderbuffer((w, h), samples=samples)],
                                  depth_attachment=s.ctx.depth_renderbuffer((w, h), samples=samples))
        s.out = s.ctx.simple_framebuffer((w, h))
        s.sdepth = s.ctx.depth_texture((shadow, shadow)); s.sdepth.compare_func = "<="; s.sdepth.repeat_x = False; s.sdepth.repeat_y = False
        s.sfbo = s.ctx.framebuffer(depth_attachment=s.sdepth)

    def render(s, items, cam_eye, cam_target, fov=40, sun_dir=(-0.4, -1.0, -0.5), sun_col=(0.25, 0.3, 0.45),
               amb_top=(0.10, 0.12, 0.2), amb_bot=(0.04, 0.04, 0.07), fog_col=(0.05, 0.06, 0.12), fog=0.02,
               lights=(), sky=((0.01, 0.015, 0.05), (0.05, 0.06, 0.14), (0.08, 0.08, 0.15)), hz=0.45, shadow_center=(0, 0, 0), shadow_size=16):
        """items: [(mesh, model4x4, color_linear, emit, cast_shadow)]"""
        ctx = s.ctx
        sd = np.array(sun_dir, "f4"); sd /= np.linalg.norm(sd)
        c = np.array(shadow_center, "f4")
        lv = look_at(c - sd * 30, c, (0, 1, 0) if abs(sd[1]) < 0.99 else (0, 0, 1))
        lmat = ortho(-shadow_size, shadow_size, -shadow_size, shadow_size, 1, 80) @ lv
        s.sfbo.use(); s.sfbo.clear(depth=1.0); ctx.enable(moderngl.DEPTH_TEST); ctx.disable(moderngl.CULL_FACE)
        s.sprog["u_light"].write(lmat.T.copy().tobytes())
        for mesh, m, col, emit, cast in items:
            if not cast: continue
            s.sprog["u_model"].write(m.T.copy().tobytes()); s.meshes[mesh][1].render()
        s.fbo.use(); s.fbo.clear(0, 0, 0, 1)
        ctx.disable(moderngl.DEPTH_TEST)
        s.sky["u_top"].value, s.sky["u_mid"].value, s.sky["u_bot"].value = sky; s.sky["u_hz"].value = hz
        s.sky_vao.render(moderngl.TRIANGLES, vertices=3)
        ctx.enable(moderngl.DEPTH_TEST)
        vp = persp(fov, s.w / s.h, 0.1, 200) @ look_at(cam_eye, cam_target)
        p = s.prog
        p["u_vp"].write(vp.T.copy().tobytes()); p["u_light"].write(lmat.T.copy().tobytes())
        p["u_sun_dir"].value = tuple(sd); p["u_sun_col"].value = sun_col; p["u_amb_top"].value = amb_top; p["u_amb_bot"].value = amb_bot
        p["u_fog_col"].value = fog_col; p["u_fog"].value = fog; p["u_cam"].value = tuple(cam_eye)
        L = list(lights)[:8]
        p["u_npl"].value = len(L)
        if L:
            pos = [l[0] for l in L] + [(0, 0, 0)] * (8 - len(L)); col = [l[1] for l in L] + [(0, 0, 0)] * (8 - len(L)); rad = [l[2] for l in L] + [1.0] * (8 - len(L))
            p["u_pl_pos"].value = pos; p["u_pl_col"].value = col; p["u_pl_rad"].value = rad
        s.sdepth.use(0); p["u_shadow"].value = 0; p["u_use_shadow"].value = 1.0
        for mesh, m, col, emit, cast in items:
            p["u_model"].write(m.T.copy().tobytes()); p["u_color"].value = col; p["u_emit"].value = emit
            s.meshes[mesh][0].render()
        ctx.copy_framebuffer(s.out, s.fbo)
        img = np.frombuffer(s.out.read(components=3), "u1").reshape(s.h, s.w, 3)[::-1]
        return img
