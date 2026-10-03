import fitz, sys
from PIL import Image
pdf, out = sys.argv[1], sys.argv[2]
pages = sys.argv[3] if len(sys.argv) > 3 else None
cols = int(sys.argv[4]) if len(sys.argv) > 4 else 8
dpi = int(sys.argv[5]) if len(sys.argv) > 5 else 30
d = fitz.open(pdf)
if pages:
    a, b = pages.split('-'); idx = range(int(a) - 1, min(int(b), d.page_count))
else:
    idx = range(d.page_count)
ims = []
for i in idx:
    pm = d[i].get_pixmap(dpi=dpi)
    ims.append(Image.frombytes('RGB', (pm.width, pm.height), pm.samples))
w, h = ims[0].size
rows = (len(ims) + cols - 1) // cols
M = Image.new('RGB', (cols * (w + 6), rows * (h + 6)), (120, 120, 120))
for k, im in enumerate(ims):
    M.paste(im, ((k % cols) * (w + 6), (k // cols) * (h + 6)))
M.save(out, quality=85)
print(d.page_count, M.size)
