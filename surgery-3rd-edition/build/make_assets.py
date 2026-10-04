"""Chapter-divider & cover art: crop to a full-bleed A4 page and duotone in the chapter colour.

Light-background plates (pencil anatomy) are inverted first so every divider reads as a
glowing 'X-ray / blueprint' image on ink.  Output: assets/dividers/<id>.jpg
"""
import json, os, sys
from PIL import Image, ImageOps, ImageFilter, ImageEnhance

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
book = json.load(open(os.path.join(ROOT, 'data', 'book.json'), encoding='utf-8'))
INK = (14, 23, 38)
OUT = os.path.join(ROOT, 'assets', 'dividers')
os.makedirs(OUT, exist_ok=True)
PAGE = (216, 303)          # mm incl. bleed
DPI = 240


def hexrgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def duotone(gray, accent):
    hi = mix(accent, (255, 255, 255), 0.72)
    lut = []
    for c in range(3):
        for v in range(256):
            t = v / 255.0
            if t < 0.55:
                col = mix(INK, accent, (t / 0.55) ** 1.25)
            else:
                col = mix(accent, hi, (t - 0.55) / 0.45)
            lut.append(col[c])
    rgb = Image.merge('RGB', (gray, gray, gray))
    return rgb.point(lut)


def make(src, dst, accent, focus=0.5, invert=None, zoom=1.0, fy=0.5, black=0.0):
    im = Image.open(src).convert('RGB')
    g = ImageOps.grayscale(im)
    if invert is None:
        invert = sum(g.resize((64, 64)).tobytes()) / 4096 > 140
    if invert:
        g = ImageOps.invert(g)
    g = ImageOps.autocontrast(g, cutoff=0.5)
    if black:
        b = int(black * 255)
        g = g.point(lambda v: 0 if v <= b else int((v - b) * 255 / (255 - b)))
    # crop to page aspect
    ar = PAGE[0] / PAGE[1]
    w, h = g.size
    ch_ = h / zoom
    cw = ch_ * ar
    if cw > w:
        cw = w / zoom; ch_ = cw / ar
    x0 = max(0, min(w - cw, focus * w - cw / 2))
    y0 = max(0, min(h - ch_, fy * h - ch_ / 2))
    g = g.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch_)))
    tw = int(PAGE[0] / 25.4 * DPI)
    th = int(PAGE[1] / 25.4 * DPI)
    g = g.resize((tw, th), Image.LANCZOS) if g.size[0] < tw else g.resize((tw, th), Image.LANCZOS)
    out = duotone(g, accent)
    # bake ink fades: bottom 48% to solid ink, light top veil for the kicker text
    ov = Image.new('RGB', out.size, INK)
    mask = Image.new('L', out.size, 0)
    mh = out.size[1]
    px = []
    for y in range(mh):
        t = y / mh
        a = 0
        if t > 0.50:
            a = min(1.0, ((t - 0.50) / 0.40)) ** 1.6
        if t < 0.12:
            a = max(a, 0.55 * (1 - t / 0.12))
        px.append(int(a * 255))
    col = Image.new('L', (1, mh)); col.putdata(px)
    mask = col.resize(out.size)
    out = Image.composite(ov, out, mask)
    out.save(dst, quality=90, dpi=(DPI, DPI))
    return dst


if __name__ == '__main__':
    # per chapter: book.json chapters[].divider.art = {"source": "web file in assets/web", "focus": [x, y],
    #   "invert": true|false|null (null = auto), "zoom": 1.0, "black": 0..1}; default source assets/web/<id>.jpg
    cfg = {}
    for ch in book['chapters']:
        art = (ch.get('divider') or {}).get('art') or {}
        src = art.get('source', ch['id'] + '.jpg')
        if os.path.exists(os.path.join(ROOT, 'assets', 'web', src)):
            fx, fy = art.get('focus', [0.5, 0.5])
            cfg[ch['id']] = (src, fx, art.get('invert', None), art.get('zoom', 1.0), fy, art.get('black', 0))
    for ch in book['chapters']:
        if ch['id'] not in cfg:
            continue
        f, fx, inv, z, fy = cfg[ch['id']][:5]
        blk = cfg[ch['id']][5] if len(cfg[ch['id']]) > 5 else 0
        make(os.path.join(ROOT, 'assets', 'web', f), os.path.join(OUT, ch['id'] + '.jpg'), hexrgb(ch['color']), fx, inv, z, fy, blk)
        ch['divider']['image'] = 'dividers/%s.jpg' % ch['id']
        print('ok', ch['id'])
    # cover art: book.json cover.art = {"source": "cover1.jpg", "color": "2E90BE"}
    cart = (book.get('cover') or {}).get('art') or {'source': 'cover1.jpg', 'color': '2E90BE'}
    if os.path.exists(os.path.join(ROOT, 'assets', 'web', cart['source'])):
        make(os.path.join(ROOT, 'assets', 'web', cart['source']), os.path.join(OUT, 'cover.jpg'), hexrgb(cart.get('color', '2E90BE')), 0.5, False, 1.0, 0.5)
        book.setdefault('cover', {})['image'] = 'dividers/cover.jpg'
    json.dump(book, open(os.path.join(ROOT, 'data', 'book.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
