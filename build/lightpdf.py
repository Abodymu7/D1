"""Smaller copy of a book PDF for sharing: full-page scans/photos re-encoded at ~200 dpi.
usage: python lightpdf.py in.pdf out.pdf"""
import io
import sys

import pymupdf
from PIL import Image

src, dst = sys.argv[1], sys.argv[2]
d = pymupdf.open(src)
done = {}
for p in d:
    for img in p.get_images(full=True):
        x, w, h = img[0], img[2], img[3]
        if x in done or w < int(__import__('os').environ.get('MINW', '1600')):
            continue
        info = d.extract_image(x)
        if img[1]:  # has soft mask (transparency) -> leave as is
            done[x] = 0
            continue
        im = Image.open(io.BytesIO(info['image'])).convert('RGB')
        s = 1654 / max(im.width, im.height) * (im.height / im.width if im.height > im.width else 1)
        tw = 1654 if im.height <= im.width else int(im.width * 2340 / im.height)
        th = int(im.height * tw / im.width)
        im = im.resize((tw, th), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, 'JPEG', quality=int(__import__('os').environ.get('Q', '84')), optimize=True)
        p.replace_image(x, stream=buf.getvalue())
        done[x] = 1
d.save(dst, garbage=4, deflate=True)
print(dst, sum(done.values()), 'images re-encoded')
