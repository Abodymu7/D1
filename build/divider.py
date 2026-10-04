"""Section-divider artwork: a real photograph / scan, colour-graded as a duotone in the
chapter colour on the book's ink background (style of Surgery Bank 1, Part 05)."""
import numpy as np
from PIL import Image, ImageFilter, ImageOps

INK = (14, 23, 38)
W, H = 1300, 1823  # matches the divider rectangle (603.8 x 858.9 pt incl. bleed)


def _lerp(a, b, t):
    return a + (b - a) * t


def gradient_map(gray, color, ink=INK, hi_mix=0.80, mid=0.62):
    """gray: float array 0..1 -> RGB float array, ink -> colour -> light tint."""
    c = np.array(color, float)
    k = np.array(ink, float)
    dark = k + (c - k) * 0.28
    light = c + (255 - c) * hi_mix
    stops = [(0.0, k), (0.30, dark), (mid, c), (1.0, light)]
    out = np.zeros(gray.shape + (3,), float)
    for (p0, c0), (p1, c1) in zip(stops[:-1], stops[1:]):
        m = (gray >= p0) & (gray <= p1)
        t = ((gray - p0) / (p1 - p0))[m][:, None]
        out[m] = c0 + (c1 - c0) * t
    return out


def prepare(img, crop=None, invert=False, gamma=1.0, autocontrast=1.0, blur=0, equalize=False):
    g = img.convert('L')
    if crop:
        w, h = g.size
        g = g.crop((int(crop[0] * w), int(crop[1] * h), int(crop[2] * w), int(crop[3] * h)))
    if invert:
        g = ImageOps.invert(g)
    if equalize:
        g = ImageOps.equalize(g)
    if autocontrast:
        g = ImageOps.autocontrast(g, cutoff=autocontrast)
    if blur:
        g = g.filter(ImageFilter.GaussianBlur(blur))
    a = np.asarray(g, float) / 255.0
    if gamma != 1.0:
        a = a ** gamma
    return a


def compose(gray, color, box=(0.0, 0.02, 1.0, 0.86), fade=(0.18, 0.26, 0.18, 0.16), strength=1.0,
            glow=0.0, mid=0.62, hi_mix=0.80, bottom_shade=0.45):
    """Place `gray` (0..1 array) inside box (fractions of the page), cover-fit, fade the edges
    (left, bottom, right, top fractions of the box) into the ink background."""
    bx0, by0, bx1, by1 = int(box[0] * W), int(box[1] * H), int(box[2] * W), int(box[3] * H)
    bw, bh = bx1 - bx0, by1 - by0
    im = Image.fromarray((np.clip(gray, 0, 1) * 255).astype(np.uint8))
    s = max(bw / im.width, bh / im.height)
    im = im.resize((max(bw, int(im.width * s + 0.5)), max(bh, int(im.height * s + 0.5))), Image.LANCZOS)
    ox, oy = (im.width - bw) // 2, (im.height - bh) // 2
    im = im.crop((ox, oy, ox + bw, oy + bh))
    g = np.asarray(im, float) / 255.0 * strength
    # edge fades
    yy, xx = np.mgrid[0:bh, 0:bw]
    fx = xx / max(1, bw - 1)
    fy = yy / max(1, bh - 1)
    m = np.ones((bh, bw))
    l, b, r, t = fade
    if l:
        m *= np.clip(fx / l, 0, 1) ** 1.4
    if r:
        m *= np.clip((1 - fx) / r, 0, 1) ** 1.4
    if t:
        m *= np.clip(fy / t, 0, 1) ** 1.4
    if b:
        m *= np.clip((1 - fy) / b, 0, 1) ** 1.6
    m = m * m * (3 - 2 * m)  # smoothstep
    # elliptical vignette so photos never show a hard rectangle
    ex = (fx - 0.5) / 0.62
    ey = (fy - 0.48) / 0.66
    m *= np.clip(1.25 - (ex ** 2 + ey ** 2), 0, 1) ** 0.9
    g = g * m
    page = np.zeros((H, W))
    page[by0:by1, bx0:bx1] = g
    if glow:
        gl = Image.fromarray((np.clip(page, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(28))
        page = np.clip(page + glow * np.asarray(gl, float) / 255.0, 0, 1)
    rgb = gradient_map(page, color, mid=mid, hi_mix=hi_mix)
    # gentle shade at the bottom for the chapter number / title
    if bottom_shade:
        sy = np.clip((np.arange(H) / H - 0.55) / 0.45, 0, 1)[:, None, None]
        k = np.array(INK, float)
        rgb = rgb + (k - rgb) * (sy ** 1.5) * bottom_shade
    return Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8))
