"""Chapter illustrations for the 3rd edition dividers.
Each motif is a recognisable drawing of the chapter's subject (heart, coronary plaque,
ECG, valves, lungs, clot, mass ...) in glowing white line-art on black; build/art.py
tone-maps it into the chapter colour.  Coordinates are in a 1300 x 1823 page; the
lower-left third stays dark for the chapter title."""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops

W, H = 1300, 1823
SS = 2


# ---------------------------------------------------------------- basics
class Pen:
    def __init__(self):
        self.im = Image.new('L', (W * SS, H * SS), 0)
        self.d = ImageDraw.Draw(self.im)

    def P(self, pts):
        return [(x * SS, y * SS) for x, y in pts]

    def line(self, pts, v=255, w=4, closed=False):
        pts = list(pts)
        if closed:
            pts = pts + pts[:1]
        self.d.line(self.P(pts), fill=int(v), width=max(1, int(w * SS)), joint='curve')
        r = w * SS / 2
        for x, y in (pts[0], pts[-1]):
            self.d.ellipse([x * SS - r, y * SS - r, x * SS + r, y * SS + r], fill=int(v))

    def fill(self, pts, v):
        self.d.polygon(self.P(pts), fill=int(v))

    def circle(self, cx, cy, r, v=255, w=3, fill=None):
        b = [(cx - r) * SS, (cy - r) * SS, (cx + r) * SS, (cy + r) * SS]
        if fill is not None:
            self.d.ellipse(b, fill=int(fill))
        if w:
            self.d.ellipse(b, outline=int(v), width=max(1, int(w * SS)))

    def layer(self):
        """a blank layer with the same API, merged later with max()"""
        return Pen()

    def merge(self, other, k=1.0, mask=None):
        a = np.asarray(self.im, dtype=np.float32)
        b = np.asarray(other.im, dtype=np.float32) * k
        if mask is not None:
            b = b * (np.asarray(mask.im, dtype=np.float32) / 255)
        self.im = Image.fromarray(np.clip(np.maximum(a, b), 0, 255).astype(np.uint8))
        self.d = ImageDraw.Draw(self.im)

    def out(self):
        return self.im.resize((W, H), Image.LANCZOS)


def bez(p0, p1, p2, p3, n=40):
    out = []
    for t in np.linspace(0, 1, n):
        u = 1 - t
        out.append((u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
                    u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1]))
    return out


def path(segs):
    """segs: [p0, (c1, c2, p1), (c1, c2, p2), ...] cubic chain"""
    pts = []
    cur = segs[0]
    for c1, c2, p in segs[1:]:
        pts += bez(cur, c1, c2, p)[(1 if pts else 0):]
        cur = p
    return pts


def tf(pts, ox, oy, sx, sy=None, flip=False):
    sy = sx if sy is None else sy
    return [(ox + ((1 - x) if flip else x) * sx, oy + y * sy) for x, y in pts]


def offset(pts, k):
    """shrink/grow a closed outline towards its centroid"""
    cx = sum(p[0] for p in pts) / len(pts); cy = sum(p[1] for p in pts) / len(pts)
    return [(cx + (x - cx) * k, cy + (y - cy) * k) for x, y in pts]


def tree(pen, x, y, ang, length, width, depth, rnd, spread=0.45, shrink=0.78, curl=0.25, v=255, tips=0):
    if depth == 0 or width < 0.9:
        if tips:
            r = tips * rnd.uniform(0.7, 1.3)
            pen.circle(x, y, r, v=v, w=max(1, r / 5))
        return
    steps = 7
    a = ang
    for i in range(steps):
        a += rnd.uniform(-curl, curl) / steps * 3
        nx, ny = x + math.cos(a) * length / steps, y + math.sin(a) * length / steps
        pen.line([(x, y), (nx, ny)], v=v, w=max(0.8, width * (1 - 0.2 * i / steps)))
        x, y = nx, ny
    n = 2 if rnd.random() > 0.15 else 3
    for k in range(n):
        da = (k - (n - 1) / 2) * spread * 2 / max(1, n - 1) + rnd.uniform(-0.12, 0.12)
        tree(pen, x, y, a + da, length * rnd.uniform(shrink - 0.08, shrink + 0.05), width * rnd.uniform(0.62, 0.76),
             depth - 1, rnd, spread, shrink, curl, max(110, v - 14), tips)


# ---------------------------------------------------------------- anatomy outlines (unit boxes)
# heart, anterior view: apex towards the viewer's right
HEART = path([(0.30, 0.20), ((0.16, 0.24), (0.06, 0.42), (0.10, 0.62)), ((0.16, 0.80), (0.48, 0.90), (0.80, 0.97)),
              ((0.90, 0.99), (0.95, 0.95), (0.96, 0.86)), ((0.99, 0.66), (0.96, 0.46), (0.84, 0.32)),
              ((0.76, 0.20), (0.62, 0.15), (0.52, 0.18)), ((0.44, 0.20), (0.38, 0.17), (0.30, 0.20))])
AORTA = path([(0.40, 0.20), ((0.38, 0.02), (0.42, -0.14), (0.56, -0.15)), ((0.68, -0.16), (0.74, -0.08), (0.74, 0.04))])
AORTA_IN = path([(0.50, 0.20), ((0.48, 0.05), (0.50, -0.06), (0.57, -0.06)), ((0.64, -0.06), (0.66, -0.02), (0.66, 0.06))])
SVC = [(0.26, 0.22), (0.25, -0.12)]
SVC2 = [(0.36, 0.20), (0.35, -0.12)]
PT = path([(0.52, 0.22), ((0.54, 0.12), (0.60, 0.06), (0.70, 0.08))])
PT2 = path([(0.64, 0.24), ((0.66, 0.18), (0.72, 0.14), (0.80, 0.16))])
LAD = path([(0.60, 0.24), ((0.62, 0.45), (0.70, 0.70), (0.88, 0.94))])
RCA = path([(0.40, 0.26), ((0.26, 0.32), (0.18, 0.52), (0.24, 0.70)), ((0.30, 0.80), (0.44, 0.86), (0.60, 0.90))])
CX = path([(0.60, 0.24), ((0.74, 0.26), (0.86, 0.36), (0.93, 0.52))])

# lung, right lung (viewer's left) in a unit box; mirrored for the left lung
LUNG = path([(0.66, 0.0), ((0.36, 0.0), (0.02, 0.42), (0.02, 0.97)), ((0.30, 0.84), (0.66, 0.82), (0.98, 0.92)),
             ((0.88, 0.70), (0.98, 0.50), (0.86, 0.34)), ((0.80, 0.22), (0.80, 0.04), (0.66, 0.0))])
LUNG_L = path([(0.66, 0.0), ((0.36, 0.0), (0.02, 0.42), (0.02, 0.97)), ((0.30, 0.86), (0.60, 0.86), (0.82, 0.93)),
               ((0.64, 0.78), (0.60, 0.56), (0.80, 0.42)), ((0.84, 0.26), (0.80, 0.04), (0.66, 0.0))])


def heart(pen, ox, oy, s, v=255, w=5, fill=38, coronaries=True, vessels=True, glow_fill=True):
    out = tf(HEART, ox, oy, s)
    if glow_fill:
        pen.fill(out, fill)
    if vessels:
        a, b = tf(AORTA, ox, oy, s), tf(AORTA_IN, ox, oy, s)
        pen.fill(a + b[::-1], fill + 10)
        pen.line(a, v, w); pen.line(b, v, w * 0.8)
        for x0, x1 in ((0.47, 0.47), (0.55, 0.56), (0.62, 0.64)):   # arch branches
            pen.line(tf([(x0, -0.12 if x0 < 0.5 else -0.14), (x1, -0.30)], ox, oy, s), v, w * 0.7)
        pen.line(tf(SVC, ox, oy, s), v * 0.85, w * 0.8); pen.line(tf(SVC2, ox, oy, s), v * 0.85, w * 0.8)
        pen.line(tf(PT, ox, oy, s), v * 0.9, w * 0.8); pen.line(tf(PT2, ox, oy, s), v * 0.9, w * 0.8)
    pen.line(out, v, w, closed=True)
    if coronaries:
        for c, k in ((LAD, 1), (RCA, 0.9), (CX, 0.85)):
            pen.line(tf(c, ox, oy, s), v * k, w * 0.75)
    return out


def lungs(pen, ox, oy, s, gap=0.30, v=255, w=5, fill=30, trachea=True, notch=True, hy=1.25):
    """two lungs side by side; returns (right_outline, left_outline)"""
    r = tf(LUNG, ox, oy, s, s * hy)
    l = tf(LUNG_L if notch else LUNG, ox + s * (1 + gap), oy, s, s * hy, flip=True)
    for o in (r, l):
        if fill:
            pen.fill(o, fill)
        pen.line(o, v, w, closed=True)
    if trachea:
        cx = ox + s * (1 + gap / 2)
        tw = s * 0.07
        top = oy - s * 0.28
        car = oy + s * 0.42
        for sg in (-1, 1):
            pen.line([(cx + sg * tw, top), (cx + sg * tw, car - tw * 0.6)], v, w * 0.9)
        for k in range(9):
            yy = top + (car - top) * (k + 0.5) / 9.5
            pen.line([(cx - tw * 0.9, yy), (cx + tw * 0.9, yy)], v * 0.55, w * 0.5)
        pen.line([(cx - tw, car - tw * 0.6), (ox + s * 0.80, oy + s * 0.50)], v, w * 0.9)
        pen.line([(cx + tw, car - tw * 0.6), (ox + s * (1 + gap) + s * 0.20, oy + s * 0.54)], v, w * 0.9)
    return r, l


def mask_of(*outlines):
    m = Pen()
    for o in outlines:
        m.fill(o, 255)
    return m


def bronchi_inside(pen, ox, oy, s, gap, rnd, v=230, depth=8, tips=0, width=None):
    """bronchial trees clipped to the lung outlines"""
    r, l = tf(LUNG, ox, oy, s, s * 1.25), tf(LUNG_L, ox + s * (1 + gap), oy, s, s * 1.25, flip=True)
    t = Pen()
    w0 = width or s * 0.05
    tree(t, ox + s * 0.80, oy + s * 0.50, math.pi * 0.62, s * 0.22, w0, depth, rnd, spread=0.5, shrink=0.8, curl=0.3, v=v, tips=tips)
    tree(t, ox + s * 0.80, oy + s * 0.50, math.pi * 1.25, s * 0.18, w0 * 0.8, depth - 1, rnd, spread=0.5, shrink=0.8, curl=0.3, v=v, tips=tips)
    lx = ox + s * (1 + gap) + s * 0.20
    tree(t, lx, oy + s * 0.54, math.pi * 0.38, s * 0.22, w0, depth, rnd, spread=0.5, shrink=0.8, curl=0.3, v=v, tips=tips)
    tree(t, lx, oy + s * 0.54, -math.pi * 0.25, s * 0.18, w0 * 0.8, depth - 1, rnd, spread=0.5, shrink=0.8, curl=0.3, v=v, tips=tips)
    pen.merge(t, mask=mask_of(r, l))
    return r, l


def ecg_beat(u, kind='n'):
    y = 0.12 * math.exp(-((u - 0.18) / 0.035) ** 2) if kind != 'af' else 0
    y -= 0.10 * math.exp(-((u - 0.34) / 0.012) ** 2)
    y += 1.00 * math.exp(-((u - 0.37) / 0.014) ** 2)
    y -= 0.25 * math.exp(-((u - 0.40) / 0.014) ** 2)
    y += 0.28 * math.exp(-((u - 0.62) / 0.055) ** 2)
    return y


def ecg(pen, x0, x1, y0, amp, period, v=255, w=5, kind='n', rnd=None, grid=False):
    if grid:
        for gx in np.arange(x0, x1, period / 8):
            pen.line([(gx, y0 - amp * 1.4), (gx, y0 + amp * 0.6)], 60, 1)
    pts = []; x = x0
    while x < x1:
        p = period * (rnd.uniform(0.55, 1.35) if kind == 'af' else 1)
        for i in range(70):
            u = i / 70
            yy = ecg_beat(u, kind)
            if kind == 'af':
                yy += 0.05 * math.sin(u * p / 9) + 0.03 * math.sin(u * p / 5.3)
            if x + u * p <= x1:
                pts.append((x + u * p, y0 - amp * yy))
        x += p
    pen.line(pts, v, w)


def glow_dots(pen, rnd, n, box, rmin, rmax, v=(120, 240)):
    x0, y0, x1, y1 = box
    for _ in range(n):
        r = rnd.uniform(rmin, rmax)
        pen.circle(rnd.uniform(x0, x1), rnd.uniform(y0, y1), r, v=rnd.uniform(*v), w=0, fill=rnd.uniform(*v) * 0.6)


def capsule(pen, cx, cy, L, R, ang, v=255, w=4, half=True):
    ca, sa = math.cos(ang), math.sin(ang)
    def rot(x, y):
        return (cx + x * ca - y * sa, cy + x * sa + y * ca)
    pts = []
    for t in np.linspace(-math.pi / 2, math.pi / 2, 30):
        pts.append(rot(L / 2 + R * math.cos(t), R * math.sin(t)))
    for t in np.linspace(math.pi / 2, 3 * math.pi / 2, 30):
        pts.append(rot(-L / 2 + R * math.cos(t), R * math.sin(t)))
    pen.fill(pts, 70 if half else 40)
    if half:
        pen.fill([p for p in pts[:30]] + [rot(0, R), rot(0, -R)], 150)
        pen.line([rot(0, -R), rot(0, R)], v, w * 0.8)
    pen.line(pts, v, w, closed=True)


def tablet(pen, cx, cy, r, v=255, w=4):
    pen.circle(cx, cy, r, v=v, w=w, fill=60)
    pen.circle(cx, cy, r * 0.78, v=v * 0.5, w=w * 0.5)
    pen.line([(cx - r * 0.6, cy), (cx + r * 0.6, cy)], v * 0.8, w * 0.8)


def stethoscope(pen, x, y, s, v=255, w=7):
    # earpieces -> binaurals -> Y -> tubing -> chest piece at (x, y)
    ex1, ex2 = (x - s * 0.55, y - s * 1.9), (x - s * 0.05, y - s * 1.95)
    yj = (x - s * 0.32, y - s * 1.15)
    pen.line(path([ex1, ((ex1[0] - s * 0.08, ex1[1] + s * 0.35), (yj[0] - s * 0.18, yj[1] - s * 0.15), yj)]), v, w)
    pen.line(path([ex2, ((ex2[0] + s * 0.08, ex2[1] + s * 0.35), (yj[0] + s * 0.2, yj[1] - s * 0.2), yj)]), v, w)
    for e in (ex1, ex2):
        pen.circle(e[0], e[1], s * 0.04, v=v, w=0, fill=v)
    pen.line(path([yj, ((yj[0] - s * 0.1, yj[1] + s * 0.6), (x - s * 0.9, y + s * 0.2), (x - s * 0.45, y + s * 0.45)),
                   ((x - s * 0.15, y + s * 0.62), (x + s * 0.05, y + s * 0.3), (x, y + s * 0.02))]), v, w * 1.2)
    pen.circle(x, y - s * 0.12, s * 0.17, v=v, w=w, fill=70)
    pen.circle(x, y - s * 0.12, s * 0.10, v=v * 0.8, w=w * 0.6)


def artery_section(pen, cx, cy, r, plaque=0.55, v=255, w=5):
    """cross-section of a coronary artery with an eccentric atheromatous plaque"""
    pen.circle(cx, cy, r, v=v, w=w, fill=55)          # adventitia
    pen.circle(cx, cy, r * 0.86, v=v * 0.7, w=w * 0.6)  # media
    # plaque crescent
    pts = []
    for t in np.linspace(math.pi * 0.05, math.pi * 1.25, 60):
        pts.append((cx + math.cos(t) * r * 0.82, cy + math.sin(t) * r * 0.82))
    lum_c = (cx - r * 0.18, cy - r * 0.22)
    lr = r * (0.82 - plaque * 0.55)
    inner = [(lum_c[0] + math.cos(t) * lr * 1.15, lum_c[1] + math.sin(t) * lr) for t in np.linspace(math.pi * 1.25, math.pi * 0.05, 60)]
    pen.fill(pts + inner, 150)
    for k in range(18):          # lipid core speckle
        a = math.pi * (0.25 + 0.8 * k / 18)
        rr = r * (0.62 + 0.08 * math.sin(k * 3))
        pen.circle(cx + math.cos(a) * rr, cy + math.sin(a) * rr, r * 0.03, v=230, w=0, fill=230)
    pen.line(inner, v, w * 0.8)


def chambers(pen, ox, oy, s, v=255, w=5, dilated=False, vsd=False, asd=False):
    """four-chamber section (apex down) used for heart failure and congenital disease"""
    # outline
    k = 1.18 if dilated else 1.0
    out = path([(0.50, 0.04), ((0.20, 0.00), (0.02, 0.18), (0.04, 0.40)), ((0.06, 0.66), (0.30, 0.94), (0.50, 1.0)),
                ((0.70, 0.94 + 0.06 * (k - 1)), (0.98 * k, 0.70), (0.97 * k, 0.40)), ((0.96, 0.16), (0.80, 0.00), (0.50, 0.04))])
    out = tf(out, ox, oy, s)
    pen.fill(out, 40); pen.line(out, v, w * 1.3, closed=True)
    wall = 0.06 if not dilated else 0.035
    # cavities
    def cav(pts, val=95):
        p = tf(path(pts), ox, oy, s)
        pen.fill(p, val); pen.line(p, v * 0.9, w * 0.8, closed=True)
        return p
    cav([(0.14, 0.12), ((0.14, 0.06), (0.44, 0.06), (0.45, 0.12)), ((0.46, 0.22), (0.46, 0.34), (0.44, 0.36)),
         ((0.30, 0.36), (0.16, 0.36), (0.12, 0.34)), ((0.10, 0.26), (0.12, 0.16), (0.14, 0.12))])            # RA
    cav([(0.55, 0.12), ((0.56, 0.06), (0.84, 0.06), (0.86, 0.12)), ((0.90, 0.20), (0.90, 0.32), (0.88, 0.36)),
         ((0.72, 0.36), (0.58, 0.36), (0.55, 0.34)), ((0.53, 0.24), (0.54, 0.16), (0.55, 0.12))])            # LA
    cav([(0.12 + wall, 0.42), ((0.12, 0.62), (0.30, 0.84), (0.46, 0.90)), ((0.47, 0.76), (0.46, 0.56), (0.45, 0.42)),
         ((0.36, 0.41), (0.22, 0.41), (0.12 + wall, 0.42))])                                                 # RV
    lx = 0.88 * k - wall
    cav([(0.55, 0.42), ((0.55, 0.60), (0.53, 0.80), (0.52, 0.92 if not dilated else 0.94)), ((0.70, 0.86 + 0.06 * (k - 1)), (lx, 0.66), (lx, 0.42)),
         ((0.78, 0.41), (0.62, 0.41), (0.55, 0.42))])                                                        # LV
    # AV valves
    for x0 in (0.16, 0.30, 0.58, 0.74):
        pen.line(tf([(x0, 0.38), (x0 + 0.05, 0.46)], ox, oy, s), v, w * 0.7)
    if vsd:
        hole = tf([(0.455, 0.50), (0.545, 0.50), (0.545, 0.58), (0.455, 0.58)], ox, oy, s)
        pen.fill(hole, 95)
        a = tf([(0.66, 0.54), (0.36, 0.54)], ox, oy, s)
        pen.line(a, 255, w * 1.1)
        tip = a[1]; pen.fill([tip, (tip[0] + s * 0.05, tip[1] - s * 0.03), (tip[0] + s * 0.05, tip[1] + s * 0.03)], 255)
    if asd:
        hole = tf([(0.45, 0.20), (0.56, 0.20), (0.56, 0.27), (0.45, 0.27)], ox, oy, s)
        pen.fill(hole, 95)
        a = tf([(0.74, 0.24), (0.28, 0.24)], ox, oy, s)
        pen.line(a, 255, w * 1.1)
        tip = a[1]; pen.fill([tip, (tip[0] + s * 0.05, tip[1] - s * 0.03), (tip[0] + s * 0.05, tip[1] + s * 0.03)], 255)
    return out


def valve_en_face(pen, cx, cy, R, n=3, v=255, w=4, stenosed=False):
    for ring in range(14):
        rr = R * (1 - ring / 22)
        pen.circle(cx, cy, rr, v=60 + ring * 9, w=1.6)
    pen.circle(cx, cy, R, v=v, w=w * 1.2)
    for k in range(n):
        a0 = 2 * math.pi * k / n - math.pi / 2
        for j in range(10):
            pts = []
            for t in np.linspace(0, 1, 50):
                ang = a0 + (t - 0.5) * (2 * math.pi / n) * 0.95
                rad = R * (0.97 - (0.97 - (0.25 if stenosed else 0.03)) * math.sin(math.pi * t) ** (0.55 + j * 0.06)) * (1 - j * 0.012)
                pts.append((cx + math.cos(ang) * rad, cy + math.sin(ang) * rad))
            pen.line(pts, 150 + j * 10, w * 0.8)
        # commissure line to centre
        pen.line([(cx + math.cos(a0 + math.pi / n) * R, cy + math.sin(a0 + math.pi / n) * R), (cx, cy)], v * 0.9, w * 0.7)
    if stenosed:
        rnd = random.Random(int(cx))
        for _ in range(26):
            a = rnd.uniform(0, 2 * math.pi); rr = R * rnd.uniform(0.3, 0.8)
            pen.circle(cx + math.cos(a) * rr, cy + math.sin(a) * rr, R * rnd.uniform(0.02, 0.05), v=250, w=0, fill=250)


def gauge(pen, cx, cy, R, v=255, w=5, needle=0.68):
    pen.circle(cx, cy, R, v=v, w=w * 1.4, fill=45)
    pen.circle(cx, cy, R * 0.9, v=v * 0.6, w=w * 0.5)
    for k in range(31):
        a = math.pi * (0.75 + 1.5 * k / 30)
        r1 = R * (0.72 if k % 5 == 0 else 0.79)
        pen.line([(cx + math.cos(a) * r1, cy + math.sin(a) * r1), (cx + math.cos(a) * R * 0.86, cy + math.sin(a) * R * 0.86)],
                 v, w * (0.9 if k % 5 == 0 else 0.5))
    a = math.pi * (0.75 + 1.5 * needle)
    pen.line([(cx - math.cos(a) * R * 0.12, cy - math.sin(a) * R * 0.12), (cx + math.cos(a) * R * 0.7, cy + math.sin(a) * R * 0.7)], 255, w * 1.2)
    pen.circle(cx, cy, R * 0.06, v=255, w=0, fill=255)


def bacteria(pen, rnd, n, box, v=230, w=3):
    x0, y0, x1, y1 = box
    for i in range(n):
        cx, cy = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        if i % 3 == 0:           # diplococci chain
            a = rnd.uniform(0, math.pi); r = rnd.uniform(9, 14)
            for k in range(rnd.choice((2, 2, 4))):
                pen.circle(cx + math.cos(a) * k * r * 2.1, cy + math.sin(a) * k * r * 2.1, r, v=v, w=w, fill=v * 0.45)
        else:                    # rods
            capsule(pen, cx, cy, rnd.uniform(26, 46), rnd.uniform(8, 11), rnd.uniform(0, math.pi), v=v, w=w, half=False)


def alveoli(pen, cx, cy, R, rnd, v=230, w=3, n=11):
    """grape-like cluster at the end of a bronchiole"""
    pen.line([(cx, cy - R * 2.2), (cx, cy - R * 0.6)], v, w * 2.2)
    for k in range(n):
        a = 2 * math.pi * k / n + rnd.uniform(-0.2, 0.2)
        rr = R * rnd.uniform(0.55, 0.9)
        r = R * rnd.uniform(0.32, 0.42)
        pen.circle(cx + math.cos(a) * rr, cy + math.sin(a) * rr, r, v=v, w=w, fill=50)
    pen.circle(cx, cy, R * 0.38, v=v, w=w, fill=60)
    # capillary net
    for _ in range(30):
        a = rnd.uniform(0, 2 * math.pi); rr = R * rnd.uniform(0.3, 1.1)
        b = a + rnd.uniform(0.2, 0.6)
        pen.line([(cx + math.cos(a) * rr, cy + math.sin(a) * rr), (cx + math.cos(b) * rr * 0.95, cy + math.sin(b) * rr * 0.95)], v * 0.6, 1.5)


def wave_box(pen, x0, y0, wdt, ht, fn, cycles, v=255, w=5, axis=True):
    if axis:
        pen.line([(x0, y0), (x0 + wdt, y0)], v * 0.45, 2)
        pen.line([(x0, y0 + ht * 0.2), (x0, y0 - ht * 1.1)], v * 0.45, 2)
    pts = []
    for i in range(cycles * 120):
        u = i / 120
        pts.append((x0 + u / cycles * wdt, y0 - ht * fn(u % 1)))
    pen.line(pts, v, w)


def spiculated(pen, cx, cy, R, rnd, v=255, w=4):
    pts = []
    for t in np.linspace(0, 2 * math.pi, 220):
        rr = R * (1 + 0.12 * math.sin(5 * t) + 0.06 * math.sin(11 * t + 1))
        pts.append((cx + math.cos(t) * rr, cy + math.sin(t) * rr))
    pen.fill(pts, 200)
    pen.line(pts, 255, w, closed=True)
    for k in range(34):
        a = 2 * math.pi * k / 34 + rnd.uniform(-0.06, 0.06)
        L = R * rnd.uniform(0.4, 1.0)
        r0 = R * 1.02
        pen.line([(cx + math.cos(a) * r0, cy + math.sin(a) * r0), (cx + math.cos(a) * (r0 + L), cy + math.sin(a) * (r0 + L))], v * 0.85, w * 0.6)


def honeycomb_in(pen, outline, rnd, dens=230, lower=0.45):
    from scipy.spatial import Voronoi
    xs = [p[0] for p in outline]; ys = [p[1] for p in outline]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    pts = []
    for _ in range(dens):
        y = y0 + (y1 - y0) * (1 - rnd.random() ** 1.8)     # denser at the base
        pts.append((rnd.uniform(x0, x1), y))
    vor = Voronoi(np.array(pts))
    t = Pen()
    for a, b in vor.ridge_vertices:
        if a < 0 or b < 0:
            continue
        p, q = vor.vertices[a], vor.vertices[b]
        f = min(1, max(0, ((p[1] - y0) / (y1 - y0) - lower) / (1 - lower)))
        if f <= 0:
            continue
        t.line([tuple(p), tuple(q)], 80 + 170 * f, 2 + 2 * f)
    pen.merge(t, mask=mask_of(outline))


def sac(pen, outline, grow, v=200, w=3, fill=None):
    o = offset(outline, grow)
    if fill is not None:
        pen.fill(o, fill)
    pen.line(o, v, w, closed=True)
    return o


def arrow(pen, a, b, v=255, w=6, head=24):
    pen.line([a, b], v, w)
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    p1 = (b[0] - head * math.cos(ang - 0.45), b[1] - head * math.sin(ang - 0.45))
    p2 = (b[0] - head * math.cos(ang + 0.45), b[1] - head * math.sin(ang + 0.45))
    pen.fill([b, p1, p2], v)


# ---------------------------------------------------------------- chapter motifs
def m_cad(seed=1):
    p = Pen(); r = random.Random(seed)
    heart(p, 170, 360, 820)
    # narrowing on the LAD + magnified cross-section
    lad = tf(LAD, 170, 360, 820)
    mx, my = lad[16]
    p.circle(mx, my, 30, v=255, w=4, fill=200)
    artery_section(p, 1040, 300, 165)
    p.line([(mx + 26, my - 18), (1040 - 150, 300 + 70)], 180, 2.5)
    # leg/limb artery hint: aorta continuing to iliac fork in background
    return p.out()


def m_hf(seed=2):
    p = Pen(); r = random.Random(seed)
    chambers(p, 200, 150, 900, dilated=True)
    return p.out()


def m_chd(seed=3):
    p = Pen()
    chambers(p, 200, 150, 900, vsd=True, asd=True)
    return p.out()


def m_arr(seed=4):
    p = Pen(); r = random.Random(seed)
    o = heart(p, 330, 230, 680, coronaries=False, fill=30)
    # conduction system: SA node, internodal paths, AV node, His, bundle branches, Purkinje
    T = lambda pts: tf(pts, 330, 230, 680)
    sa, av = T([(0.30, 0.26)])[0], T([(0.47, 0.50)])[0]
    p.circle(*sa, 22, v=255, w=0, fill=255); p.circle(*av, 18, v=255, w=0, fill=255)
    for c in (((0.30, 0.26), (0.30, 0.36), (0.40, 0.46), (0.47, 0.50)), ((0.30, 0.26), (0.40, 0.30), (0.46, 0.40), (0.47, 0.50))):
        p.line(T(bez(*c)), 230, 4)
    his = T(bez((0.47, 0.50), (0.52, 0.56), (0.54, 0.60), (0.55, 0.64)))
    p.line(his, 255, 7)
    p.line(T(bez((0.55, 0.64), (0.48, 0.74), (0.38, 0.84), (0.32, 0.86))), 240, 5)
    p.line(T(bez((0.55, 0.64), (0.64, 0.74), (0.74, 0.82), (0.86, 0.86))), 240, 5)
    t = Pen()
    for x, a in ((0.36, math.pi * 1.2), (0.84, -math.pi * 0.35), (0.6, math.pi * 0.45)):
        xy = T([(x, 0.84)])[0]
        tree(t, xy[0], xy[1], a, 70, 4, 5, r, spread=0.6, v=220)
    p.merge(t, mask=mask_of(o))
    # irregular rhythm strip underneath
    ecg(p, -20, 1320, 1070, 120, 190, kind='af', rnd=r, w=5)
    return p.out()


def m_valv(seed=5):
    p = Pen()
    o = heart(p, 120, 470, 560, fill=26, coronaries=False)
    valve_en_face(p, 920, 420, 300, 3, stenosed=True)
    # leader from aortic root to the magnified valve
    root = tf([(0.45, 0.20)], 120, 470, 560)[0]
    p.line([root, (920 - 290, 420 + 60)], 170, 2.5)
    valve_en_face(p, 1010, 1010, 150, 2)
    return p.out()


def m_peri(seed=6):
    p = Pen()
    o = heart(p, 260, 360, 780, fill=34)
    hb = tf(HEART, 260, 360, 780)
    sac(p, hb, 1.13, v=150, w=3, fill=None)
    big = sac(p, hb, 1.30, v=255, w=6)
    # effusion fill between the sac and the heart (drawn as a translucent band with ripples)
    t = Pen(); t.fill(big, 110); t.fill(offset(hb, 1.02), 0)
    for k in range(5):
        sac(t, hb, 1.16 + k * 0.03, v=150, w=1.5)
    p.merge(t, 0.9)
    heart(p, 260, 360, 780, fill=0, glow_fill=False)
    return p.out()


def m_htn(seed=7):
    p = Pen()
    gauge(p, 860, 400, 290, needle=0.82)
    # tubing + cuff
    p.line(path([(860, 690), ((860, 800), (600, 760), (520, 690))]), 220, 8)
    cuff = [(130, 560), (530, 520), (580, 780), (180, 830)]
    p.fill(cuff, 70); p.line(cuff, 255, 6, closed=True)
    for k in range(1, 5):
        p.line([(130 + 80 * k, 560 - 8 * k), (180 + 80 * k, 830 - 10 * k)], 120, 2)
    # arterial pressure waveform
    def art(u):
        return (math.exp(-((u - 0.18) / 0.08) ** 2) + 0.35 * math.exp(-((u - 0.42) / 0.06) ** 2)
                - 0.12 * math.exp(-((u - 0.34) / 0.02) ** 2) + 0.2 * (1 - u))
    wave_box(p, -40, 1090, 1380, 150, art, 5, axis=False)
    return p.out()


def m_cpharm(seed=8):
    p = Pen(); r = random.Random(seed)
    heart(p, 470, 300, 520, fill=26, coronaries=True, vessels=True)
    spots = [(260, 330, 0.5), (1100, 250, -0.4), (1150, 820, 0.9), (300, 960, -0.8), (1000, 1260, 0.3)]
    for (x, y, a) in spots:
        capsule(p, x, y, 120, 48, a)
    for (x, y) in ((180, 640), (1180, 560), (660, 1000), (1170, 1440)):
        tablet(p, x, y, 52)
    # a small ring molecule (e.g. aromatic core)
    cx, cy, R = 880, 1430, 70
    hexa = [(cx + R * math.cos(math.pi / 3 * k + math.pi / 6), cy + R * math.sin(math.pi / 3 * k + math.pi / 6)) for k in range(6)]
    p.line(hexa, 230, 4, closed=True)
    p.line(offset(hexa, 0.7)[0:2], 180, 3); p.line(offset(hexa, 0.7)[2:4], 180, 3); p.line(offset(hexa, 0.7)[4:6], 180, 3)
    for a, b in ((hexa[0], (hexa[0][0] + 70, hexa[0][1] + 40)), (hexa[3], (hexa[3][0] - 70, hexa[3][1] - 40))):
        p.line([a, b], 230, 4); p.circle(*b, 14, v=230, w=0, fill=230)
    return p.out()


def m_cvsx(seed=9):
    p = Pen()
    heart(p, 120, 360, 700, fill=30)
    stethoscope(p, 1000, 1180, 560)
    return p.out()


def m_cvsemq(seed=10):
    p = Pen(); r = random.Random(seed)
    heart(p, 330, 300, 640, fill=30)
    ecg(p, -20, 1320, 1070, 110, 230, w=5)
    valve_en_face(p, 1060, 1340, 150, 3)
    return p.out()


def lung_base(p, s=520, ox=None, oy=330, gap=0.30, fill=26, trachea=True, notch=True):
    ox = (W - s * (2 + gap)) / 2 if ox is None else ox
    return lungs(p, ox, oy, s, gap=gap, fill=fill, trachea=trachea, notch=notch), ox, oy, s, gap


def m_airway(seed=11):
    p = Pen(); r = random.Random(seed)
    (rl, ll), ox, oy, s, gap = lung_base(p)
    bronchi_inside(p, ox, oy, s, gap, r)
    # magnified asthmatic bronchus: thick inflamed wall, smooth muscle band, mucus plug
    cx, cy, R = 1010, 1180, 150
    p.circle(cx, cy, R, v=255, w=6, fill=60)
    p.circle(cx, cy, R * 0.80, v=200, w=3, fill=110)
    lumen = [(cx + math.cos(t) * R * (0.36 + 0.07 * math.sin(9 * t)), cy + math.sin(t) * R * (0.30 + 0.07 * math.sin(9 * t))) for t in np.linspace(0, 2 * math.pi, 200)]
    p.fill(lumen, 0); p.line(lumen, 255, 4, closed=True)
    p.circle(cx + 10, cy + 8, R * 0.12, v=230, w=0, fill=230)
    p.line([(ox + s * 0.6, oy + s * 0.95), (cx - R, cy - 40)], 160, 2.5)
    return p.out()


def m_resinf(seed=12):
    p = Pen(); r = random.Random(seed)
    (rl, ll), ox, oy, s, gap = lung_base(p)
    bronchi_inside(p, ox, oy, s, gap, r, v=150, depth=7)
    # lobar consolidation (right lower lobe) with air bronchogram
    t = Pen()
    blob = [(ox + s * (0.42 + 0.30 * math.cos(a)) + 18 * math.sin(5 * a), oy + s * 1.25 * (0.74 + 0.16 * math.sin(a))) for a in np.linspace(0, 2 * math.pi, 120)]
    t.fill(blob, 190)
    p.merge(t, mask=mask_of(rl))
    bacteria(p, r, 30, (780, 1150, 1250, 1480))
    return p.out()


def m_crit(seed=13):
    p = Pen(); r = random.Random(seed)
    (rl, ll), ox, oy, s, gap = lung_base(p, s=470, oy=260)
    # bilateral white-out (ARDS)
    t = Pen()
    for _ in range(260):
        x, y = r.uniform(ox, ox + s * (2 + gap)), r.uniform(oy + s * 0.2, oy + s * 1.2)
        t.circle(x, y, r.uniform(12, 34), v=0, w=0, fill=r.uniform(90, 200))
    p.merge(t, mask=mask_of(rl, ll))
    # ventilator: pressure and flow curves
    def press(u):
        return 0.15 + (0.85 * min(1, u / 0.05) if u < 0.35 else 0)
    def flow(u):
        return (0.8 - 1.4 * u) if u < 0.35 else -0.7 * math.exp(-(u - 0.35) / 0.12)
    wave_box(p, 760, 1260, 480, 140, press, 3)
    wave_box(p, 760, 1460, 480, 100, flow, 3)
    return p.out()


def m_pleura(seed=14):
    p = Pen(); r = random.Random(seed)
    (rl, ll), ox, oy, s, gap = lung_base(p, fill=22)
    # pleural lining
    sac(p, rl, 1.04, v=170, w=2.5); sac(p, ll, 1.04, v=170, w=2.5)
    # effusion with a meniscus at the right base
    t = Pen()
    ys = oy + s * 1.25 * 0.62
    eff = [(ox - 20, ys - 70)] + [(ox + s * x, ys + 70 * x ** 2) for x in np.linspace(0, 1, 30)] + [(ox + s * 1.05, oy + s * 1.4), (ox - 20, oy + s * 1.4)]
    t.fill(eff, 210)
    p.merge(t, mask=mask_of(rl))
    p.line([(ox + s * x, ys + 70 * x ** 2) for x in np.linspace(0.02, 0.92, 30)], 255, 4)
    # pneumothorax on the left: collapsed lung edge
    lx = ox + s * (1 + gap)
    inner = offset(ll, 0.78)
    p.line(inner, 255, 4, closed=True)
    return p.out()


def m_ild(seed=15):
    p = Pen(); r = random.Random(seed)
    (rl, ll), ox, oy, s, gap = lung_base(p, fill=20)
    honeycomb_in(p, rl, r, 260); honeycomb_in(p, ll, r, 260)
    return p.out()


def m_pvasc(seed=16):
    p = Pen(); r = random.Random(seed)
    (rl, ll), ox, oy, s, gap = lung_base(p, fill=20, trachea=False)
    t = Pen()
    hx1, hx2, hy = ox + s * 0.84, ox + s * (1 + gap) + s * 0.16, oy + s * 0.62
    cx = ox + s * (1 + gap / 2)
    # pulmonary trunk and arteries
    top = (cx + s * 0.02, oy + s * 0.48)
    p.line(path([(cx - s * 0.06, oy + s * 0.95), ((cx - s * 0.04, oy + s * 0.75), (cx + s * 0.06, oy + s * 0.60), top)]), 255, 26)
    p.line(path([top, ((cx - s * 0.06, oy + s * 0.44), (hx1 + s * 0.08, hy - s * 0.04), (hx1, hy))]), 255, 17)
    p.line(path([top, ((cx + s * 0.08, oy + s * 0.46), (hx2 - s * 0.06, hy - s * 0.04), (hx2, hy))]), 255, 17)
    tree(t, hx1, hy, math.pi * 0.9, s * 0.2, 13, 8, r, spread=0.55, curl=0.3, v=240)
    tree(t, hx1, hy, math.pi * 0.55, s * 0.24, 13, 8, r, spread=0.55, curl=0.3, v=240)
    tree(t, hx2, hy, math.pi * 0.1, s * 0.2, 13, 8, r, spread=0.55, curl=0.3, v=240)
    tree(t, hx2, hy, math.pi * 0.45, s * 0.24, 13, 8, r, spread=0.55, curl=0.3, v=240)
    p.merge(t, mask=mask_of(rl, ll))
    # embolus wedged in the left lower branch, wedge-shaped infarct beyond it
    ex, ey = hx2 + s * 0.12, hy + s * 0.32
    clot = [(ex - 30, ey - 14), (ex + 34, ey - 6), (ex + 40, ey + 14), (ex - 24, ey + 16)]
    p.fill(clot, 255)
    wedge = [(ex + 30, ey + 20), (ox + s * (2 + gap) - 20, ey + 160), (ox + s * (2 + gap) - 30, ey + 330)]
    t2 = Pen(); t2.fill(wedge, 110); p.merge(t2, mask=mask_of(ll))
    return p.out()


def m_lca(seed=17):
    p = Pen(); r = random.Random(seed)
    (rl, ll), ox, oy, s, gap = lung_base(p, fill=22)
    bronchi_inside(p, ox, oy, s, gap, r, v=130, depth=7)
    spiculated(p, ox + s * 0.42, oy + s * 0.42, 70, r)
    # hilar nodes
    for dx, dy in ((0.86, 0.62), (0.80, 0.70), (1.42, 0.66)):
        p.circle(ox + s * dx, oy + s * dy, 20, v=230, w=3, fill=160)
    return p.out()


def m_resx(seed=18):
    p = Pen(); r = random.Random(seed)
    (rl, ll), ox, oy, s, gap = lung_base(p, s=470, oy=300, fill=22)
    bronchi_inside(p, ox, oy, s, gap, r, v=170, depth=7)
    stethoscope(p, 1110, 1430, 400)
    return p.out()


def m_resemq(seed=19):
    p = Pen(); r = random.Random(seed)
    (rl, ll), ox, oy, s, gap = lung_base(p, s=470, oy=280, fill=22)
    bronchi_inside(p, ox, oy, s, gap, r, v=170, depth=7)
    alveoli(p, 1060, 1320, 120, r)
    return p.out()


def m_cover(seed=20):
    p = Pen(); r = random.Random(seed)
    (rl, ll), ox, oy, s, gap = lung_base(p, s=520, oy=250, fill=18)
    bronchi_inside(p, ox, oy, s, gap, r, v=150, depth=8)
    heart(p, ox + s * 0.72, oy + s * 0.70, s * 0.85, fill=40)
    ecg(p, -20, 1320, 1250, 90, 260, w=4)
    return p.out()


MOTIFS = {'cad': m_cad, 'hf': m_hf, 'chd': m_chd, 'arr': m_arr, 'valv': m_valv, 'peri': m_peri, 'htn': m_htn,
          'cpharm': m_cpharm, 'cvsx': m_cvsx, 'cvsemq': m_cvsemq, 'airway': m_airway, 'resinf': m_resinf,
          'crit': m_crit, 'pleura': m_pleura, 'ild': m_ild, 'pvasc': m_pvasc, 'lca': m_lca, 'resx': m_resx,
          'resemq': m_resemq, 'cover': m_cover}
