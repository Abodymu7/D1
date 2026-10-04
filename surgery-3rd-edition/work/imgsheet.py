import json, sys
from PIL import Image, ImageDraw
Q = json.load(open('data/questions.json'))
pairs = []
pref = sys.argv[1].split(',')
for q in Q:
    for im in q.get('images', []):
        if any(im.startswith('q/' + p) for p in pref):
            pairs.append((q['id'], im))
W = 900; rows = []
for qid, im in pairs:
    i = Image.open('assets/' + im).convert('RGB')
    r = W / i.width; i = i.resize((W, int(i.height * r)))
    lab = Image.new('RGB', (W, 26), '#ffe'); ImageDraw.Draw(lab).text((6, 6), qid + '  ' + im, fill='black')
    rows += [lab, i]
H = sum(x.height for x in rows)
s = Image.new('RGB', (W, H), 'white'); y = 0
for x in rows: s.paste(x, (0, y)); y += x.height
s.save(sys.argv[2]); print(len(pairs), H)
