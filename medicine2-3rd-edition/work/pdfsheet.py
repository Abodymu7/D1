"""python3 work/pdfsheet.py file.pdf first last out.png [dpi] [cols]"""
import sys, subprocess, glob, os
from PIL import Image
f, a, b, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
dpi = sys.argv[5] if len(sys.argv) > 5 else '30'; cols = int(sys.argv[6]) if len(sys.argv) > 6 else 8
tmp = '/tmp/claude-0/sheet'; os.makedirs(tmp, exist_ok=True)
for x in glob.glob(tmp + '/*'): os.remove(x)
subprocess.run(['pdftoppm', '-f', str(a), '-l', str(b), '-r', dpi, '-png', f, tmp + '/p'], check=True)
fs = sorted(glob.glob(tmp + '/p*.png'))
ims = [Image.open(x) for x in fs]
w, h = ims[0].size
# pair as spreads: page 1 alone on the right
S = Image.new('RGB', (cols * w + (cols // 2) * 6, ((len(ims) + cols) // cols) * (h + 6)), '#888')
for k, im in enumerate(ims):
    pos = k + (a % 2 == 1)   # odd first page sits in the right slot
    r, c = divmod(pos, cols)
    S.paste(im, (c * w + (c // 2) * 6, r * (h + 6)))
S.save(out); print(len(ims), S.size)
