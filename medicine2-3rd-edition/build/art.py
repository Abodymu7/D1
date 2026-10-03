"""Duotone divider / cover art drawn for the 3rd edition (see build/illus.py).
Each chapter gets a motif rendered as glowing white structure on black, then mapped
ink -> chapter colour -> warm highlight, with film grain and a vignette.

  python build/art.py            -> assets/dividers/<ch>.jpg  + assets/dividers/cover.jpg
"""
import json, math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
OUT = os.path.join(ROOT, 'assets', 'dividers')
os.makedirs(OUT, exist_ok=True)
book = json.load(open(os.path.join(ROOT, 'data', 'book.json'), encoding='utf-8'))
W, H = 1300, 1823            # 216 x 303 mm at ~153 dpi
SS = 2                        # supersampling
TIPS = [0]


def canvas():
    im = Image.new('L', (W * SS, H * SS), 0)
    return im, ImageDraw.Draw(im)


def fin(im):
    return im.resize((W, H), Image.LANCZOS)


# ---------------------------------------------------------------- motifs (draw white on black)
def tree(d, x, y, ang, length, width, depth, rnd, spread=0.42, shrink=0.78, curl=0.18, bright=255, min_w=1.2):
    if depth == 0 or width < min_w:
        if TIPS[0]:
            rr = TIPS[0] * rnd.uniform(0.6, 1.3)
            d.ellipse([x - rr, y - rr, x + rr, y + rr], outline=bright, width=max(1, int(rr / 5)))
        return
    steps = 9
    px, py = x, y
    a = ang
    for i in range(steps):
        a += rnd.uniform(-curl, curl) / steps * 3
        nx = px + math.cos(a) * length / steps
        ny = py + math.sin(a) * length / steps
        w = max(1, width * (1 - 0.25 * i / steps))
        d.line([(px, py), (nx, ny)], fill=bright, width=int(w))
        d.ellipse([nx - w / 2, ny - w / 2, nx + w / 2, ny + w / 2], fill=bright)
        px, py = nx, ny
    n = 2 if rnd.random() > 0.15 else 3
    for k in range(n):
        da = (k - (n - 1) / 2) * spread * 2 / max(1, n - 1) + rnd.uniform(-0.15, 0.15)
        tree(d, px, py, a + da, length * rnd.uniform(shrink - 0.08, shrink + 0.05), width * rnd.uniform(0.62, 0.78),
             depth - 1, rnd, spread, shrink, curl, max(90, bright - 12), min_w)


def m_bronchi(seed):
    im, d = canvas(); r = random.Random(seed)
    s = SS
    # trachea + two main bronchi -> lungs
    tree(d, 700 * s, -40 * s, math.pi / 2, 380 * s, 70 * s, 1, r)
    for side, ang in ((-1, math.pi / 2 + 0.62), (1, math.pi / 2 - 0.55)):
        tree(d, 700 * s, 330 * s, ang, 250 * s, 48 * s, 9, r, spread=0.5, shrink=0.8, curl=0.25)
    return fin(im)


def m_alveoli(seed):
    im, d = canvas(); r = random.Random(seed); s = SS
    TIPS[0] = 16 * s
    tree(d, 650 * s, -60 * s, math.pi / 2 + 0.1, 300 * s, 46 * s, 8, r, spread=0.55, shrink=0.8, curl=0.4)
    TIPS[0] = 0
    return fin(im)


def m_coronary(seed):
    im, d = canvas(); r = random.Random(seed)
    s = SS
    heart_glow(d, 760, 760, 1100, 45)
    tree(d, 690 * s, 300 * s, math.pi * 0.62, 260 * s, 28 * s, 8, r, spread=0.38, shrink=0.82, curl=0.35)
    tree(d, 760 * s, 290 * s, math.pi * 0.22, 300 * s, 30 * s, 8, r, spread=0.4, shrink=0.8, curl=0.35)
    tree(d, 820 * s, 320 * s, math.pi * 0.45, 360 * s, 22 * s, 7, r, spread=0.35, shrink=0.8, curl=0.3)
    return fin(im)


def heart_glow(d, cx, cy, size, val):
    s = SS
    pts = []
    for t in np.linspace(0, 2 * math.pi, 240):
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        pts.append(((cx + x * size / 34) * s, (cy + y * size / 34) * s))
    d.polygon(pts, fill=val)


def m_fibres(seed):
    """myocardial helix inside a heart outline"""
    im, d = canvas(); r = random.Random(seed); s = SS
    cx, cy, size = 720, 700, 1150
    for k in range(70):
        ph = r.uniform(0, 2 * math.pi); tilt = r.uniform(0.5, 1.1)
        pts = []
        for t in np.linspace(0, 2 * math.pi, 300):
            x = 16 * math.sin(t) ** 3
            y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
            f = 0.35 + 0.65 * (k / 70)
            x *= f; y *= f
            x += 1.6 * math.sin(tilt * t * 3 + ph); y += 1.6 * math.cos(tilt * t * 2 + ph)
            pts.append(((cx + x * size / 34) * s, (cy + y * size / 34) * s))
        d.line(pts, fill=int(110 + 140 * (k / 70)), width=int(r.uniform(1.5, 4.5) * s))
    return fin(im)


def ecg_wave(x):
    """one PQRST beat on [0,1)"""
    y = 0.0
    y += 0.12 * math.exp(-((x - 0.18) / 0.035) ** 2)
    y -= 0.10 * math.exp(-((x - 0.34) / 0.012) ** 2)
    y += 1.00 * math.exp(-((x - 0.37) / 0.014) ** 2)
    y -= 0.25 * math.exp(-((x - 0.40) / 0.014) ** 2)
    y += 0.28 * math.exp(-((x - 0.62) / 0.055) ** 2)
    return y


def m_ecg(seed, irregular=False):
    im, d = canvas(); r = random.Random(seed); s = SS
    # grid
    for gx in range(0, W, 26):
        d.line([(gx * s, 0), (gx * s, H * s)], fill=55 if gx % 130 else 105, width=s)
    for gy in range(0, H, 26):
        d.line([(0, gy * s), (W * s, gy * s)], fill=55 if gy % 130 else 105, width=s)
    for row in range(7):
        y0 = 200 + row * 200
        amp = 150 - row * 8
        pts = []; x = -50.0; beat = r.uniform(0.2, 0.9)
        period = 230
        while x < W + 60:
            p = period * (r.uniform(0.6, 1.4) if irregular else 1)
            for i in range(60):
                u = i / 60
                pts.append(((x + u * p) * s, (y0 - amp * ecg_wave(u) + (r.uniform(-3, 3) if irregular else 0)) * s))
            x += p
        d.line(pts, fill=255 - row * 10, width=int((7 - row * 0.4) * s))
    return fin(im)


def m_cells(seed, n=170, big=False):
    im, d = canvas(); r = random.Random(seed); s = SS
    for k in range(n):
        cx, cy = r.uniform(80, W - 40), r.uniform(60, H * 0.72)
        rad = r.uniform(30, 110 if big else 80) * (1.3 if k < 10 else 1)
        v = int(r.uniform(120, 250))
        d.ellipse([(cx - rad) * s, (cy - rad) * s, (cx + rad) * s, (cy + rad) * s], outline=v, width=int(r.uniform(2, 6) * s))
        if big or r.random() < 0.35:
            nr = rad * r.uniform(0.2, 0.35)
            ox, oy = r.uniform(-rad / 3, rad / 3), r.uniform(-rad / 3, rad / 3)
            d.ellipse([(cx + ox - nr) * s, (cy + oy - nr) * s, (cx + ox + nr) * s, (cy + oy + nr) * s], fill=int(v * 0.8))
    return fin(im)


def m_honeycomb(seed):
    from scipy.spatial import Voronoi
    im, d = canvas(); r = random.Random(seed); s = SS
    pts = np.array([[r.uniform(-100, W + 100), r.uniform(-100, H * 0.85)] for _ in range(420)])
    # denser at bottom right (subpleural basal)
    pts = np.vstack([pts, [[r.uniform(500, W + 100), r.uniform(700, H * 0.85)] for _ in range(300)]])
    vor = Voronoi(pts)
    for (a_, b_) in vor.ridge_vertices:
        if a_ < 0 or b_ < 0:
            continue
        p, q = vor.vertices[a_], vor.vertices[b_]
        if not (-200 < p[0] < W + 200 and -200 < p[1] < H + 200):
            continue
        v = int(90 + 160 * min(1, max(0, (p[1]) / (H * 0.8))))
        d.line([(p[0] * s, p[1] * s), (q[0] * s, q[1] * s)], fill=v, width=int(r.uniform(2, 5) * s))
    return fin(im)


def m_rosette(seed):
    """valve leaflets seen en face, several valves"""
    im, d = canvas(); r = random.Random(seed); s = SS
    for (cx, cy, R, n) in ((740, 620, 520, 3), (230, 230, 230, 3), (1150, 1250, 300, 2), (330, 1080, 170, 3)):
        for ring in range(26):
            rr = R * (1 - ring / 30)
            d.ellipse([(cx - rr) * s, (cy - rr) * s, (cx + rr) * s, (cy + rr) * s], outline=int(60 + ring * 6), width=int(2 * s))
        for k in range(n):
            a0 = 2 * math.pi * k / n + 0.3
            for j in range(18):
                pts = []
                for t in np.linspace(0, 1, 60):
                    ang = a0 + (t - 0.5) * (2 * math.pi / n) * 0.92
                    rad = R * (0.98 - 0.98 * math.sin(math.pi * t) ** (0.6 + j * 0.05)) * (1 - j * 0.01)
                    pts.append(((cx + math.cos(ang) * rad) * s, (cy + math.sin(ang) * rad) * s))
                d.line(pts, fill=int(150 + j * 6), width=int(3.2 * s))
    return fin(im)


def m_layers(seed, n=34):
    """concentric sac / pleural membranes around a blob"""
    im, d = canvas(); r = random.Random(seed); s = SS
    cx, cy = 760, 650
    base = [r.uniform(0.9, 1.1) for _ in range(7)]
    for k in range(n):
        R = 170 + k * 16
        pts = []
        for t in np.linspace(0, 2 * math.pi, 400):
            f = 1 + 0.08 * sum(math.sin(t * (j + 2) + base[j] * 3 + k * 0.03) / (j + 1) for j in range(7))
            pts.append(((cx + math.cos(t) * R * f * 1.05) * s, (cy + math.sin(t) * R * f * 0.95) * s))
        d.line(pts + pts[:1], fill=int(250 - k * 5), width=int((3.5 if k % 5 == 0 else 1.6) * s))
    return fin(im)


def m_lungs(seed, n=26):
    im, d = canvas(); r = random.Random(seed); s = SS
    for cx, sgn in ((430, -1), (1000, 1)):
        for k in range(n):
            pts = []
            for t in np.linspace(0, 2 * math.pi, 400):
                # lung-like: flat medial border, rounded apex, broad base
                x = math.cos(t); y = math.sin(t)
                sx = 250 * (1 + 0.25 * y) * (0.75 if x * sgn < 0 else 1.0)
                sy = 520 * (1 + 0.1 * math.sin(3 * t))
                g = 1 + k * 0.035
                pts.append(((cx + sgn * 0 + x * sx * g) * s, (700 + y * sy * g) * s))
            d.line(pts + pts[:1], fill=int(255 - k * 7), width=int((4 if k in (0, 1) else 1.6) * s))
    return fin(im)


def m_waves(seed):
    """arterial pressure waveforms stacked in perspective"""
    im, d = canvas(); r = random.Random(seed); s = SS
    def art(u):
        return (math.exp(-((u - 0.18) / 0.08) ** 2) * 1.0 + 0.35 * math.exp(-((u - 0.42) / 0.06) ** 2)
                - 0.12 * math.exp(-((u - 0.34) / 0.02) ** 2) + 0.2 * (1 - u))
    for row in range(40):
        y0 = 120 + row * 30
        amp = 40 + row * 6
        pts = []
        per = 260 - row * 2
        x = -per * r.random()
        while x < W + per:
            for i in range(50):
                u = i / 50
                pts.append(((x + u * per) * s, (y0 - amp * art(u)) * s))
            x += per
        d.line(pts, fill=int(80 + row * 4), width=int((1.5 + row * 0.06) * s))
    return fin(im)


def m_lattice(seed):
    """molecular ball-and-stick lattice"""
    im, d = canvas(); r = random.Random(seed); s = SS
    nodes = []
    for i in range(-1, 12):
        for j in range(-1, 16):
            x = i * 120 + (60 if j % 2 else 0) + r.uniform(-18, 18)
            y = j * 104 + r.uniform(-18, 18)
            if r.random() < 0.72:
                nodes.append((x, y))
    for (x, y) in nodes:
        for (u, v) in nodes:
            dd = math.hypot(u - x, v - y)
            if 0 < dd < 140 and r.random() < 0.7:
                d.line([(x * s, y * s), (u * s, v * s)], fill=int(90 + 60 * (y / H)), width=int(3 * s))
    for (x, y) in nodes:
        rad = r.uniform(10, 26)
        d.ellipse([(x - rad) * s, (y - rad) * s, (x + rad) * s, (y + rad) * s], fill=int(r.uniform(150, 250)))
    return fin(im)


def m_chambers(seed):
    """two circulations: looping flow lines crossing (shunts)"""
    im, d = canvas(); r = random.Random(seed); s = SS
    for k in range(60):
        pts = []
        ph = r.uniform(0, 6.28)
        for t in np.linspace(0, 2 * math.pi, 400):
            x = 720 + (430 + k * 4) * math.sin(2 * t) * 0.9 + 30 * math.sin(3 * t + ph)
            y = 720 + (560 + k * 3) * math.cos(t) + 25 * math.sin(5 * t + ph)
            pts.append((x * s, y * s))
        d.line(pts, fill=int(90 + k * 2.6), width=int(r.uniform(1.4, 3.8) * s))
    return fin(im)


def m_vessels(seed):
    """pulmonary arterial tree from hilum both sides"""
    im, d = canvas(); r = random.Random(seed); s = SS
    tree(d, 660 * s, 520 * s, math.pi * 0.95, 180 * s, 40 * s, 9, r, spread=0.5, shrink=0.8, curl=0.3)
    tree(d, 860 * s, 520 * s, -math.pi * 0.05, 180 * s, 40 * s, 9, r, spread=0.5, shrink=0.8, curl=0.3)
    tree(d, 760 * s, 400 * s, math.pi * 0.5, 260 * s, 28 * s, 8, r, spread=0.55, shrink=0.78, curl=0.3)
    return fin(im)


def m_mixed(seed, resp=False):
    a = m_bronchi(seed) if resp else m_coronary(seed)
    b = m_ecg(seed + 1) if not resp else m_cells(seed + 1, 90)
    return Image.fromarray(np.maximum(np.asarray(a), (np.asarray(b) * 0.45).astype(np.uint8)))


MOTIF = {
    'cad': lambda: m_coronary(11), 'hf': lambda: m_fibres(12), 'chd': lambda: m_chambers(13), 'arr': lambda: m_ecg(14, True),
    'valv': lambda: m_rosette(15), 'peri': lambda: m_layers(16), 'htn': lambda: m_waves(17), 'cpharm': lambda: m_lattice(18),
    'cvsx': lambda: m_mixed(19), 'cvsemq': lambda: m_ecg(20), 'airway': lambda: m_bronchi(21), 'resinf': lambda: m_cells(22, 150),
    'crit': lambda: m_cells(23, 80, True), 'pleura': lambda: m_lungs(24), 'ild': lambda: m_honeycomb(25), 'pvasc': lambda: m_vessels(26),
    'lca': lambda: m_cells(27, 60, True), 'resx': lambda: m_mixed(28, True), 'resemq': lambda: m_alveoli(29),
}


# ---------------------------------------------------------------- tone mapping
def hexrgb(h):
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float32)


def duotone(L, color, ink='0E1726', dark=True, seed=0):
    """L: float array 0..1 (structure). returns RGB uint8."""
    rng = np.random.default_rng(seed)
    Hh, Ww = L.shape
    # glow: combine sharp + blurred
    img = Image.fromarray((L * 255).astype(np.uint8))
    g1 = np.asarray(img.filter(ImageFilter.GaussianBlur(3)), dtype=np.float32) / 255
    g2 = np.asarray(img.filter(ImageFilter.GaussianBlur(18)), dtype=np.float32) / 255
    g3 = np.asarray(img.filter(ImageFilter.GaussianBlur(60)), dtype=np.float32) / 255
    v = np.clip(0.55 * L + 0.35 * g1 + 0.55 * g2 + 0.5 * g3, 0, 1.3)
    # vignette + darken the lower-left title zone
    yy, xx = np.mgrid[0:Hh, 0:Ww].astype(np.float32)
    vig = 1 - 0.55 * (((xx / Ww - 0.6) ** 2) * 1.2 + ((yy / Hh - 0.4) ** 2) * 1.4)
    title = 1 - 0.55 * np.clip((yy / Hh - 0.62) / 0.3, 0, 1) * np.clip((0.75 - xx / Ww) / 0.5, 0, 1)
    v = v * np.clip(vig, 0.25, 1) * title
    v = np.clip(v + rng.normal(0, 0.035, v.shape), 0, 1.25)
    c_ink, c_acc, c_hi = hexrgb(ink), hexrgb(color), np.array([255, 244, 226], dtype=np.float32)
    t = np.clip(v, 0, 1)[..., None]
    rgb = c_ink * (1 - t) ** 1.2 + c_acc * (1 - (1 - t) ** 1.2)
    hi = np.clip((v - 0.82) / 0.4, 0, 1)[..., None]
    rgb = rgb * (1 - hi) + c_hi * hi
    return np.clip(rgb, 0, 255).astype(np.uint8)


import illus


def render(cid, color):
    L = np.asarray(illus.MOTIFS[cid](), dtype=np.float32) / 255
    rgb = duotone(L, color, seed=hash(cid) % 1000)
    p = os.path.join(OUT, cid + '.jpg')
    Image.fromarray(rgb).save(p, quality=86, optimize=True, progressive=True)
    return p


def render_cover():
    L = np.asarray(illus.MOTIFS['cover'](), dtype=np.float32) / 255
    rgb = duotone(L, '2E90BE', seed=5)
    p = os.path.join(OUT, 'cover.jpg')
    Image.fromarray(rgb).save(p, quality=88, optimize=True, progressive=True)
    return p


if __name__ == '__main__':
    only = sys.argv[1:]
    for c in book['chapters']:
        if not only or c['id'] in only:
            print(render(c['id'], c['color']))
    if not only or 'cover' in only:
        print(render_cover())
