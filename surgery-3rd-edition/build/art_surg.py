"""Render the Surgery Bank part dividers and cover (build/illus_surg.py) with the duotone of build/art.py.
  python build/art_surg.py [part-1 ... cover]   -> assets/dividers/part-N.jpg, cover.jpg"""
import os, sys
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import art, illus_surg

book = art.book
PARTS = list(dict.fromkeys(c['part'] for c in book['chapters']))
# a bright, saturated tone per part (the first chapter colour of the part, lifted)
COL = {}
for k, part in enumerate(PARTS):
    c = [x for x in book['chapters'] if x['part'] == part][0]['color']
    COL['part-%d' % (k + 1)] = c
COL['cover'] = '1F7A8C'


def render(key):
    L = np.asarray(illus_surg.MOTIFS[key](), dtype=np.float32) / 255
    rgb = art.duotone(L, COL[key], seed=sum(map(ord, key)) % 1000)
    p = os.path.join(art.OUT, key + '.jpg')
    Image.fromarray(rgb).save(p, quality=86, optimize=True, progressive=True)
    return p


if __name__ == '__main__':
    for k in (sys.argv[1:] or list(illus_surg.MOTIFS)):
        print(render(k))
