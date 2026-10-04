"""Contact sheet of PDF pages: python sheet.py in.pdf out.jpg first-last cols width"""
import sys
import pymupdf
from PIL import Image
pdf, out, rng, cols, w = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
a, b = [int(x) for x in rng.split('-')]
d = pymupdf.open(pdf)
b = min(b, len(d))
ims = []
for i in range(a - 1, b):
    pix = d[i].get_pixmap(matrix=pymupdf.Matrix(w / d[i].rect.width, w / d[i].rect.width))
    ims.append(Image.frombytes('RGB', (pix.width, pix.height), pix.samples))
h = ims[0].height
rows = (len(ims) + cols - 1) // cols
sh = Image.new('RGB', (cols * (w + 6), rows * (h + 6)), (120, 120, 120))
for k, im in enumerate(ims):
    sh.paste(im, ((k % cols) * (w + 6), (k // cols) * (h + 6)))
sh.save(out, quality=85)
