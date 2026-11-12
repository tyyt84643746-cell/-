import time
from models import *
from PIL import Image
r = Renderer(540, 960)
t = 0.5
items = [box(T(0, -0.25, 0) @ S(60, 0.5, 60), C["snow"])]
items += house(T(-3, 0, -6))
for x, z in ((-9, -10), (-6, -13), (2, -12), (6, -9), (9, -14), (-12, -8)): items += pine(T(x, 0, z), 5)
items += fence(-8, 8, -1.5)
items.append(box(T(1.5, 0.01, 1.2) @ S(2.2, 0.02, 1.6), C["dark"], cast=False))
items.append(ball(T(3.4, 0.0, 1.0) @ S(1.6, 0.8, 1.2), C["dirt"]))
p, head = person(T(0.5, 0, 2.5) @ Ry(0.4), t, arm="dig", look=0.2, lamp=True)
items += p
items += cat(T(-0.8, 0, 3.0) @ Ry(0.5), t)
nb, _ = person(T(-4, 0, -2.4), t, colors=dict(body=rgb((84, 92, 62)), body_d=rgb((64, 70, 46)), hat=rgb((140, 62, 58)), hat_b=rgb((160, 76, 70)), pack=None), mouth="smile")
items += nb
lights = [((-4.5, 1.5, -3.8), (1.0, 0.6, 0.25), 6.0), ((-1.5, 1.5, -3.8), (1.0, 0.6, 0.25), 6.0), ((0.6, 2.2, 2.9), (0.9, 0.85, 0.7), 5.0)]
t0 = time.time()
img = r.render(items, (5.5, 3.2, 9.5), (-0.5, 1.2, 0), fov=45, lights=lights, shadow_center=(0, 0, 0), sun_dir=(-0.5, -1.0, -0.35), sun_col=(0.30, 0.35, 0.55), fog=0.025)
print("frame", round(time.time() - t0, 3), "s")
Image.fromarray(img).save("/tmp/claude-0/-home-user--/61d10885-b2e8-5620-8f48-9e12bf360b91/scratchpad/test3d.jpg")
