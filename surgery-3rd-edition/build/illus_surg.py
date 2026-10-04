"""Part-divider and cover illustrations for the Surgery Bank 3rd edition.
Same technique as build/illus.py (glowing white line-art on black, tone-mapped by build/art.py);
each drawing shows the subject of its part. Page 1300 x 1823; the lower third stays dark for the titles."""
import math, random
import numpy as np
from illus import Pen, path, tf, tree, glow_dots, ecg, W, H


def blob(cx, cy, rx, ry, rnd=None, k=0.0, n=160, rot=0.0):
    out = []
    for a in np.linspace(0, 2 * math.pi, n, endpoint=False):
        w = 1 + (k * math.sin(3 * a + 1) + 0.5 * k * math.sin(5 * a + 2) if k else 0)
        x, y = rx * math.cos(a) * w, ry * math.sin(a) * w
        out.append((cx + x * math.cos(rot) - y * math.sin(rot), cy + x * math.sin(rot) + y * math.cos(rot)))
    return out


def catmull(P, n=24):
    """smooth curve through the points (Catmull-Rom)."""
    P = [P[0]] + list(P) + [P[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for t in np.linspace(0, 1, n, endpoint=False):
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[k]) + (-p0[k] + p2[k]) * t + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t2 + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t3) for k in (0, 1)))
    out.append(P[-2])
    return out


def tube(p, pts, width, v=255, w=4, fill=40, rings=0):
    """a hollow tube along a polyline: two parallel walls (+ optional cartilage rings)."""
    pts = list(pts)
    L, R = [], []
    for i, (x, y) in enumerate(pts):
        x0, y0 = pts[max(0, i - 1)]; x1, y1 = pts[min(len(pts) - 1, i + 1)]
        dx, dy = x1 - x0, y1 - y0; d = math.hypot(dx, dy) or 1
        nx, ny = -dy / d, dx / d
        L.append((x + nx * width / 2, y + ny * width / 2)); R.append((x - nx * width / 2, y - ny * width / 2))
    if fill:
        p.fill(L + R[::-1], fill)
    p.line(L, v, w); p.line(R, v, w)
    if rings:
        step = max(1, len(pts) // rings)
        for i in range(step // 2, len(pts), step):
            p.line([L[i], R[i]], v * 0.55, w * 0.6)
    return L, R


# ---------------------------------------------------------------- part 1: neck & endocrine
def m_neck(seed=1):
    p = Pen(); r = random.Random(seed)
    cx = 650
    # carotid sheaths and jugular node chains
    for sg in (-1, 1):
        x = cx + sg * 330
        p.line(path([(x + sg * 30, 150), ((x + sg * 10, 500), (x - sg * 10, 800), (x + sg * 20, 1150))]), 190, 9)
        p.line(path([(x + sg * 75, 150), ((x + sg * 60, 500), (x + sg * 45, 800), (x + sg * 70, 1150))]), 140, 14)
        for k in range(7):
            p.circle(x + sg * (100 + r.uniform(-12, 12)), 260 + k * 125 + r.uniform(-20, 20), r.uniform(11, 20), v=200, w=3, fill=90)
    # larynx: thyroid cartilage shield + cricoid
    shield = path([(cx - 170, 170), ((cx - 160, 300), (cx - 60, 400), (cx, 430)), ((cx + 60, 400), (cx + 160, 300), (cx + 170, 170)),
                   ((cx + 80, 205), (cx + 20, 160), (cx, 200)), ((cx - 20, 160), (cx - 80, 205), (cx - 170, 170))])
    p.fill(shield, 40); p.line(shield, 255, 6, closed=True)
    p.line([(cx, 210), (cx, 420)], 150, 3)
    cric = blob(cx, 470, 120, 34)
    p.fill(cric, 50); p.line(cric, 235, 5, closed=True)
    # trachea with rings
    tube(p, [(cx, 500 + k * 10) for k in range(80)], 210, v=230, w=5, fill=26, rings=16)
    # thyroid: two lobes and the isthmus, with a nodule in the right lobe
    for sg in (-1, 1):
        lobe = path([(cx + sg * 70, 520), ((cx + sg * 230, 470), (cx + sg * 290, 720), (cx + sg * 250, 900)),
                     ((cx + sg * 210, 1000), (cx + sg * 90, 990), (cx + sg * 80, 860)), ((cx + sg * 60, 760), (cx + sg * 50, 620), (cx + sg * 70, 520))])
        p.fill(lobe, 85); p.line(lobe, 255, 7, closed=True)
        for yy in (640, 830):   # parathyroids peeking behind
            p.circle(cx + sg * 255, yy, 22, v=255, w=3, fill=200)
        for _ in range(26):     # follicles
            a, rr = r.uniform(0, 2 * math.pi), r.uniform(0, 1)
            fx = cx + sg * (165 + 70 * rr * math.cos(a)); fy = 750 + 170 * rr * math.sin(a)
            p.circle(fx, fy, r.uniform(7, 14), v=170, w=2)
    isth = path([(cx - 90, 760), ((cx - 40, 730), (cx + 40, 730), (cx + 90, 760)), ((cx + 40, 820), (cx - 40, 820), (cx - 90, 760))])
    p.fill(isth, 90); p.line(isth, 255, 6, closed=True)
    p.circle(cx - 175, 720, 50, v=255, w=5, fill=230)
    return p.out()


# ---------------------------------------------------------------- part 2: breast
def m_breast(seed=2):
    p = Pen(); r = random.Random(seed)
    cx, cy, R = 600, 720, 430
    outline = blob(cx, cy, R, R * 0.98, k=0.02)
    p.fill(outline, 26); p.line(outline, 255, 6, closed=True)
    # axillary tail with level I-III nodes
    tail = path([(cx + R * 0.62, cy - R * 0.78), ((cx + R * 0.95, cy - R * 1.15), (cx + R * 1.25, cy - R * 1.25), (cx + R * 1.45, cy - R * 1.32))])
    p.line(tail, 200, 5)
    for k in range(9):
        p.circle(cx + R * (0.95 + 0.06 * k) + r.uniform(-15, 15), cy - R * (1.0 + 0.04 * k) + r.uniform(-25, 25), r.uniform(14, 24), v=220, w=3, fill=120)
    # nipple–areola and ductal tree branching to lobules
    nx, ny = cx + 40, cy + 30
    p.circle(nx, ny, 95, v=200, w=3, fill=60)
    p.circle(nx, ny, 34, v=255, w=4, fill=200)
    t = Pen()
    for k in range(13):
        ang = 2 * math.pi * k / 13 + r.uniform(-0.1, 0.1)
        tree(t, nx + 30 * math.cos(ang), ny + 30 * math.sin(ang), ang, R * 0.27, 7, 5, r, spread=0.5, shrink=0.72, curl=0.3, v=230, tips=11)
    p.merge(t)
    # a stellate lesion in the upper outer quadrant
    sx, sy = cx + 230, cy - 230
    for k in range(18):
        a = 2 * math.pi * k / 18
        p.line([(sx, sy), (sx + math.cos(a) * r.uniform(50, 85), sy + math.sin(a) * r.uniform(50, 85))], 255, 3)
    p.circle(sx, sy, 34, v=255, w=4, fill=240)
    return p.out()


# ---------------------------------------------------------------- part 3: gastrointestinal tract
def gut(p, r, ox=0, oy=0, s=1.0, v=255):
    X = lambda x: ox + x * s
    Y = lambda y: oy + y * s
    oes = [(X(560), Y(60 + k * 6)) for k in range(45)]
    tube(p, oes, 60 * s, v=v, w=5, fill=40, rings=0)
    stomach = path([(X(545), Y(330)), ((X(470), Y(380)), (X(430), Y(520)), (X(520), Y(640))), ((X(600), Y(720)), (X(760), Y(700)), (X(830), Y(610))),
                    ((X(870), Y(560)), (X(900), Y(520)), (X(940), Y(530))), ((X(950), Y(480)), (X(900), Y(450)), (X(840), Y(500))),
                    ((X(760), Y(600)), (X(660), Y(560)), (X(640), Y(470))), ((X(630), Y(400)), (X(640), Y(340)), (X(590), Y(330)))])
    p.fill(stomach, 60); p.line(stomach, v, 7, closed=True)
    rug = Pen()
    for k in range(6):
        rug.line(path([(X(500 + 30 * k), Y(420 + 20 * k)), ((X(560 + 30 * k), Y(480 + 20 * k)), (X(600 + 30 * k), Y(560)), (X(660 + 30 * k), Y(600)))]), 120, 3)
    p.merge(rug)
    duo = path([(X(940), Y(505)), ((X(1010), Y(520)), (X(1030), Y(620)), (X(1000), Y(700))), ((X(960), Y(790)), (X(860), Y(800)), (X(820), Y(760)))])
    tube(p, duo, 50 * s, v=v, w=5, fill=40)
    # colon frame: caecum → ascending → transverse → descending → sigmoid → rectum (smooth spline)
    colon = catmull([(X(x), Y(y)) for x, y in [(330, 1270), (305, 1060), (318, 870), (390, 755), (540, 725), (700, 795), (870, 765), (1000, 745),
                                                (1052, 870), (1050, 1080), (1012, 1225), (900, 1290), (780, 1300), (722, 1385), (700, 1500)]])
    L, R_ = tube(p, colon, 92 * s, v=v, w=6, fill=48)
    for i in range(6, len(colon) - 4, 9):    # haustra
        p.line([L[i], R_[i]], v * 0.5, 3)
    p.line(path([(X(330), Y(1250)), ((X(300), Y(1300)), (X(320), Y(1340)), (X(345), Y(1320)))]), v * 0.9, 5)   # appendix
    # small bowel coils
    pts, x, y, a = [], X(820), Y(800), math.pi
    for k in range(420):
        a += r.uniform(-0.35, 0.35) + 0.06 * math.sin(k / 9)
        x += 9 * s * math.cos(a); y += 9 * s * math.sin(a)
        if not (X(420) < x < X(930)): a = math.pi - a
        if not (Y(860) < y < Y(1230)): a = -a
        x = min(max(x, X(420)), X(930)); y = min(max(y, Y(860)), Y(1230))
        pts.append((x, y))
    tube(p, pts, 34 * s, v=v * 0.85, w=3, fill=30)
    return colon


def m_git(seed=3):
    p = Pen(); r = random.Random(seed)
    gut(p, r, ox=-20, oy=40)
    return p.out()


# ---------------------------------------------------------------- part 4: paediatric surgery
def m_paed(seed=4):
    """a teddy bear with a sutured tummy, and a stethoscope"""
    p = Pen(); r = random.Random(seed)
    def part(cx, cy, rx, ry, v=255, w=7, fill=60, rot=0.0):
        o = blob(cx, cy, rx, ry, rot=rot); p.fill(o, fill); p.line(o, v, w, closed=True); return o
    cx = 640
    for sg in (-1, 1):                                   # legs and feet pads
        part(cx + sg * 175, 1110, 120, 135, fill=55)
        part(cx + sg * 190, 1175, 62, 55, v=220, w=5, fill=110)
    part(cx, 870, 255, 300, fill=50)                    # body
    part(cx, 900, 165, 195, v=200, w=4, fill=80)        # tummy patch
    for sg in (-1, 1):                                   # arms
        part(cx + sg * 270, 780, 85, 175, fill=55, rot=-sg * 0.55)
    for sg in (-1, 1):                                   # ears
        part(cx + sg * 175, 330, 82, 82, fill=55)
        part(cx + sg * 175, 330, 42, 42, v=200, w=4, fill=110)
    part(cx, 470, 215, 195, fill=60)                    # head
    part(cx, 545, 92, 70, v=230, w=5, fill=110)         # muzzle
    p.circle(cx, 515, 26, v=255, w=0, fill=255)         # nose
    p.line(path([(cx, 540), ((cx, 570), (cx - 30, 590), (cx - 50, 575))]), 230, 5)
    p.line(path([(cx, 540), ((cx, 570), (cx + 30, 590), (cx + 50, 575))]), 230, 5)
    for sg in (-1, 1):
        p.circle(cx + sg * 80, 430, 20, v=255, w=0, fill=255)
    # sutured incision on the tummy
    inc = path([(cx - 110, 960), ((cx - 50, 930), (cx + 50, 930), (cx + 110, 960))])
    p.line(inc, 255, 5)
    for i in range(4, len(inc) - 3, 6):
        x, y = inc[i]
        p.line([(x - 10, y - 30), (x + 10, y + 30)], 255, 4)
    # stethoscope draped over the shoulder
    p.line(path([(cx - 120, 650), ((cx - 260, 600), (cx - 400, 760), (cx - 330, 1000))]), 230, 9)
    p.line(path([(cx + 120, 650), ((cx + 30, 760), (cx - 120, 860), (cx - 300, 1000))]), 230, 9)
    p.line(path([(cx - 315, 1000), ((cx - 340, 1120), (cx - 250, 1260), (cx - 120, 1250))]), 230, 9)
    p.circle(cx - 90, 1250, 52, v=255, w=8, fill=150)
    p.circle(cx - 90, 1250, 24, v=255, w=4, fill=230)
    return p.out()


# ---------------------------------------------------------------- part 5: abdomen (hepatobiliary, pancreas, spleen)
def m_abd(seed=5):
    p = Pen(); r = random.Random(seed)
    liver = path([(170, 520), ((180, 330), (420, 230), (700, 260)), ((900, 280), (1050, 320), (1080, 380)), ((980, 470), (820, 560), (700, 640)),
                  ((560, 730), (380, 780), (260, 760)), ((160, 720), (150, 620), (170, 520))])
    p.fill(liver, 50); p.line(liver, 255, 7, closed=True)
    p.line(path([(640, 270), ((620, 400), (600, 500), (590, 680))]), 140, 3)        # falciform
    # biliary tree in the liver, converging on the hilum
    hx, hy = 560, 650
    t = Pen()
    for ang in (-2.3, -1.9, -1.4, -1.0, -0.6):
        tree(t, hx, hy, ang, 120, 9, 6, r, spread=0.5, curl=0.25, v=220)
    p.merge(t)
    # gallbladder, cystic duct, CBD to the duodenum
    gb = path([(500, 720), ((420, 760), (360, 880), (420, 930)), ((480, 960), (540, 880), (540, 760)), ((535, 720), (520, 705), (500, 720))])
    p.fill(gb, 110); p.line(gb, 255, 6, closed=True)
    for _ in range(5):
        p.circle(r.uniform(430, 500), r.uniform(840, 910), r.uniform(10, 16), v=255, w=2, fill=230)
    p.line(path([(530, 730), ((560, 700), (570, 690), (575, 680))]), 255, 8)
    cbd = path([(hx, hy), ((575, 760), (590, 880), (620, 990))])
    p.line(cbd, 255, 12)
    duo = path([(560, 900), ((470, 950), (450, 1120), (560, 1180)), ((680, 1240), (800, 1160), (820, 1100))])
    tube(p, duo, 70, v=240, w=5, fill=40)
    # pancreas across to the spleen
    panc = path([(560, 1060), ((560, 980), (640, 940), (720, 960)), ((860, 1000), (1000, 940), (1080, 860)), ((1110, 830), (1130, 880), (1100, 920)),
                 ((1000, 1030), (860, 1080), (720, 1070)), ((640, 1140), (570, 1130), (560, 1060))])
    p.fill(panc, 80); p.line(panc, 255, 6, closed=True)
    p.line(path([(600, 1050), ((760, 1020), (920, 990), (1080, 880))]), 180, 4)       # main duct
    for _ in range(60):
        x, y = r.uniform(620, 1060), r.uniform(950, 1060)
        p.circle(x, y, r.uniform(4, 8), v=120, w=1.5)
    spleen = blob(1120, 720, 95, 175, k=0.03, rot=0.35)
    p.fill(spleen, 90); p.line(spleen, 255, 7, closed=True)
    return p.out()


# ---------------------------------------------------------------- part 6: urology
def kidney(p, cx, cy, s, flip=1, r=None):
    out = path([(cx, cy - 1.0 * s), ((cx + flip * 0.75 * s, cy - 1.05 * s), (cx + flip * 0.85 * s, cy + 1.0 * s), (cx, cy + 1.0 * s)),
                ((cx - flip * 0.35 * s, cy + 1.0 * s), (cx - flip * 0.45 * s, cy + 0.6 * s), (cx - flip * 0.25 * s, cy + 0.25 * s)),
                ((cx - flip * 0.15 * s, cy + 0.1 * s), (cx - flip * 0.15 * s, cy - 0.15 * s), (cx - flip * 0.25 * s, cy - 0.3 * s)),
                ((cx - flip * 0.45 * s, cy - 0.6 * s), (cx - flip * 0.4 * s, cy - 1.0 * s), (cx, cy - 1.0 * s))])
    p.fill(out, 60); p.line(out, 255, 7, closed=True)
    # pelvis and calyces
    px, py = cx - flip * 0.05 * s, cy
    for a in (-0.9, -0.35, 0.2, 0.75):
        ex, ey = cx + flip * 0.38 * s * math.cos(a), cy + 0.62 * s * math.sin(a)
        p.line([(px, py), (ex, ey)], 220, 9)
        p.circle(ex, ey, 0.08 * s, v=230, w=4, fill=120)
    # adrenal cap
    adr = path([(cx - flip * 0.25 * s, cy - 0.95 * s), ((cx - flip * 0.1 * s, cy - 1.45 * s), (cx + flip * 0.3 * s, cy - 1.4 * s), (cx + flip * 0.45 * s, cy - 1.05 * s))])
    p.line(adr, 230, 9)
    return (px - flip * 0.25 * s, py + 0.25 * s)


def m_uro(seed=6):
    p = Pen(); r = random.Random(seed)
    # aorta and IVC
    p.line([(620, 150), (620, 1250)], 150, 26); p.line([(700, 150), (700, 1250)], 110, 30)
    s = 210
    hl = kidney(p, 330, 520, s, flip=-1)
    hr = kidney(p, 990, 540, s, flip=1)
    bx, by = 660, 1230
    for (x, y), sg in ((hl, -1), (hr, 1)):
        u = path([(x, y), ((x + sg * 20, y + 300), (bx + sg * 250, by - 380), (bx + sg * 150, by - 80))])
        p.line(u, 255, 10)
    bladder = path([(bx - 210, by - 60), ((bx - 230, by - 230), (bx + 230, by - 230), (bx + 210, by - 60)), ((bx + 190, by + 90), (bx + 60, by + 150), (bx, by + 150)),
                    ((bx - 60, by + 150), (bx - 190, by + 90), (bx - 210, by - 60))])
    p.fill(bladder, 70); p.line(bladder, 255, 7, closed=True)
    prost = blob(bx, by + 215, 95, 70)
    p.fill(prost, 110); p.line(prost, 255, 6, closed=True)
    p.line([(bx, by + 150), (bx, by + 420)], 230, 8)
    # a stone in the right ureter and one in the left lower calyx
    p.circle(bx + 205, by - 330, 20, v=255, w=3, fill=255)
    p.circle(300, 680, 22, v=255, w=3, fill=255)
    return p.out()


# ---------------------------------------------------------------- part 7: trauma & critical care
def scalpel(p, x, y, L, ang, v=255):
    ca, sa = math.cos(ang), math.sin(ang)
    P_ = lambda u, w: (x + ca * u - sa * w, y + sa * u + ca * w)
    handle = [P_(0, -22), P_(L * 0.62, -26), P_(L * 0.66, -18), P_(L * 0.66, 18), P_(L * 0.62, 26), P_(0, 22)]
    p.fill(handle, 70); p.line(handle, v, 6, closed=True)
    for k in range(10):
        u = L * (0.08 + 0.045 * k)
        p.line([P_(u, -14), P_(u, 14)], v * 0.45, 2.5)
    blade = [P_(L * 0.66, -12), P_(L * 0.78, -30), P_(L * 0.93, -34), P_(L * 1.0, -10), P_(L * 0.92, 6), P_(L * 0.66, 12)]
    p.fill(blade, 200); p.line(blade, v, 5, closed=True)


def m_trauma(seed=7):
    p = Pen(); r = random.Random(seed)
    # sutured incision with interrupted stitches
    inc = path([(170, 900), ((420, 760), (820, 760), (1130, 620))])
    p.line(inc, 255, 7)
    for i in range(4, len(inc) - 3, 4):
        x0, y0 = inc[i - 1]; x1, y1 = inc[i + 1]
        dx, dy = x1 - x0, y1 - y0; d = math.hypot(dx, dy) or 1
        nx, ny = -dy / d * 48, dx / d * 48
        x, y = inc[i]
        p.line([(x - nx, y - ny), (x + nx, y + ny)], 235, 5)
        p.circle(x - nx, y - ny, 6, v=255, w=0, fill=255); p.circle(x + nx, y + ny, 6, v=255, w=0, fill=255)
    scalpel(p, 260, 300, 880, 0.18)
    # needle holder with a curved needle
    p.line(path([(820, 1180), ((900, 1050), (980, 960), (1050, 900))]), 230, 10)
    p.line(path([(900, 1210), ((960, 1080), (1020, 990), (1065, 915))]), 230, 10)
    p.circle(800, 1210, 46, v=230, w=8); p.circle(915, 1245, 46, v=230, w=8)
    needle = [(1060 + 70 * math.cos(a), 880 + 70 * math.sin(a)) for a in np.linspace(math.pi * 1.05, math.pi * 2.0, 50)]
    p.line(needle, 255, 5)
    # monitor trace
    ecg(p, -20, 1320, 1140, 80, 300, v=200, w=4)
    return p.out()


def m_cover(seed=8):
    p = Pen(); r = random.Random(seed)
    gut(p, r, ox=60, oy=-10, s=0.92, v=235)
    scalpel(p, 180, 1430, 760, -0.42)
    return p.out()


MOTIFS = {'part-1': m_neck, 'part-2': m_breast, 'part-3': m_git, 'part-4': m_paed, 'part-5': m_abd, 'part-6': m_uro, 'part-7': m_trauma,
          'cover': m_cover}
