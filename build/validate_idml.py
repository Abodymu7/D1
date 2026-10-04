"""Structural checks for a generated IDML package (no InDesign available).
usage: python validate_idml.py book.idml"""
import collections
import os
import re
import sys
import zipfile

from lxml import etree

path = sys.argv[1]
z = zipfile.ZipFile(path)
names = z.namelist()
errors = []
assert names[0] == 'mimetype' and z.getinfo('mimetype').compress_type == zipfile.ZIP_STORED, 'mimetype must be first+stored'
assert z.read('mimetype') == b'application/vnd.adobe.indesign-idml-package'

trees = {}
for n in names:
    if n.endswith('.xml'):
        try:
            trees[n] = etree.fromstring(z.read(n))
        except Exception as e:  # noqa
            errors.append(f'XML error in {n}: {e}')

dm = trees['designmap.xml']
NS = '{http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging}'
listed = [e.get('src') for e in dm if e.tag.startswith(NS) and e.get('src')]
for s in listed:
    if s not in names:
        errors.append(f'designmap lists missing file {s}')
for n in names:
    if n.startswith(('Stories/', 'Spreads/', 'MasterSpreads/')) and n not in listed:
        errors.append(f'file not listed in designmap: {n}')

# ids
selfs = collections.Counter()
for n, t in trees.items():
    for e in t.iter():
        v = e.get('Self')
        if v:
            selfs[v] += 1
dups = [k for k, c in selfs.items() if c > 1]
if dups:
    errors.append(f'{len(dups)} duplicate Self ids e.g. {dups[:5]}')

story_ids = set()
for n in names:
    if n.startswith('Stories/'):
        story_ids.add(trees[n][0].get('Self'))
storylist = set(dm.get('StoryList').split())
missing_sl = story_ids - storylist
if missing_sl:
    errors.append(f'stories missing from StoryList: {list(missing_sl)[:5]}')

frames = {}
placed = set()
masters = set()
for n in names:
    if n.startswith('MasterSpreads/'):
        masters.add(trees[n][0].get('Self'))
for n in names:
    if n.startswith(('Spreads/', 'MasterSpreads/')):
        for tf in trees[n].iter('TextFrame'):
            frames[tf.get('Self')] = tf
            ps = tf.get('ParentStory')
            if ps not in story_ids:
                errors.append(f'{n}: frame {tf.get("Self")} -> missing story {ps}')
            placed.add(ps)
        for pg in trees[n].iter('Page'):
            am = pg.get('AppliedMaster')
            if am not in ('n', None) and am not in masters:
                errors.append(f'{n}: page {pg.get("Name")} -> missing master {am}')
unplaced = story_ids - placed
# stories anchored inside other stories (none expected) would be fine; report unplaced
if unplaced:
    errors.append(f'{len(unplaced)} stories not placed in any frame: {list(unplaced)[:5]}')
for fid, tf in frames.items():
    for a in ('PreviousTextFrame', 'NextTextFrame'):
        v = tf.get(a)
        if v != 'n' and v not in frames:
            errors.append(f'frame {fid} {a} -> missing {v}')
        elif v != 'n':
            other = frames[v]
            back = 'NextTextFrame' if a == 'PreviousTextFrame' else 'PreviousTextFrame'
            if other.get(back) != fid:
                errors.append(f'frame chain mismatch {fid} {a} {v}')
            if other.get('ParentStory') != tf.get('ParentStory'):
                errors.append(f'frame chain crosses stories {fid}->{v}')

# styles and colours
st = trees['Resources/Styles.xml']
pst = {e.get('Self') for e in st.iter('ParagraphStyle')}
cst = {e.get('Self') for e in st.iter('CharacterStyle')}
gr = trees['Resources/Graphic.xml']
cols = {e.get('Self') for e in gr}
used_p, used_c, used_col = set(), set(), set()
for n, t in trees.items():
    for e in t.iter():
        if e.get('AppliedParagraphStyle'):
            used_p.add(e.get('AppliedParagraphStyle'))
        if e.get('AppliedCharacterStyle'):
            used_c.add(e.get('AppliedCharacterStyle'))
        for a in ('FillColor', 'StrokeColor'):
            v = e.get(a)
            if v:
                used_col.add(v)
    for e in t.iter('RuleAboveColor', 'RuleBelowColor', 'UnderlineColor', 'BasedOn'):
        if e.text and e.text.startswith(('Color/', 'Swatch/')):
            used_col.add(e.text)
for p in used_p - pst:
    errors.append(f'missing paragraph style {p}')
for c in used_c - cst - {'n'}:
    errors.append(f'missing character style {c}')
for c in used_col - cols:
    if c not in ('Swatch/None',) and not c.startswith('Gradient/'):
        errors.append(f'missing colour {c}')
for e in st.iter('ParagraphStyle'):
    b = e.find('Properties/BasedOn')
    if b is not None and b.text and b.text.startswith('ParagraphStyle/') and b.text not in pst:
        errors.append(f'style {e.get("Self")} based on missing {b.text}')

# links
links_dir = os.path.join(os.path.dirname(path), 'Links')
nlinks = 0
for n, t in trees.items():
    for l in t.iter('Link'):
        nlinks += 1
        uri = l.get('LinkResourceURI').replace('file:', '')
        if not os.path.exists(os.path.join(os.path.dirname(path), uri)):
            errors.append(f'missing linked file {uri}')

# anchored objects
anch = collections.Counter(e.get('AnchoredPosition') for t in trees.values() for e in t.iter('AnchoredObjectSetting'))
upd = sum(len(re.findall(rb'UPDATED', z.read(n))) for n in names if n.startswith('Stories/'))
pages = sum(1 for n in names if n.startswith('Spreads/') for _ in trees[n].iter('Page'))
sec = re.search(r'<Section [^>]*>', z.read('designmap.xml').decode()).group(0)
print(f'pages={pages} stories={len(story_ids)} frames={len(frames)} masters={len(masters)} links={nlinks} '
      f'anchored={dict(anch)} UPDATED={upd}')
print(sec)
if errors:
    print(f'{len(errors)} ERRORS')
    for e in errors[:40]:
        print('  ', e)
    sys.exit(1)
print('OK')
