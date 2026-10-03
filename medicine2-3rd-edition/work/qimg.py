"""Contact sheet of the images attached to given question ids (or asset file names).
usage: python3 work/qimg.py arr-0088,arr-0090,o100_3 out.png"""
import json, sys, os
from PIL import Image, ImageDraw
Image.MAX_IMAGE_PIXELS = None
Q = {q['id']: q for q in json.load(open('data/questions.json'))}
pairs = []
for t in sys.argv[1].split(','):
    if t in Q:
        q = Q[t]
        ims = list(q.get('images', []))
        for it in q.get('items', []) or []:
            ims += it.get('images', [])
        pairs += [(t, im) for im in ims] or [(t + ' (no image)', None)]
    else:
        for f in sorted(os.listdir('assets/q')):
            if f.startswith(t):
                pairs.append((f, 'q/' + f))
W = 900; rows = []
for lab_, im in pairs:
    lab = Image.new('RGB', (W, 26), '#ffe'); ImageDraw.Draw(lab).text((6, 6), '%s  %s' % (lab_, im), fill='black'); rows.append(lab)
    if im:
        i = Image.open('assets/' + im).convert('RGB'); r = W / i.width; rows.append(i.resize((W, max(1, int(i.height * r)))))
H = sum(x.height for x in rows)
s = Image.new('RGB', (W, max(H, 1)), 'white'); y = 0
for x in rows: s.paste(x, (0, y)); y += x.height
s.save(sys.argv[2]); print(len(pairs), 'images', H, 'px high')
