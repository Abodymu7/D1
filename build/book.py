"""Build one IDML + one PDF per book.

usage: python book.py <scratch> <book-key> [--skip-flow]
  <scratch>/work/<book>/fixed/*.idml   cleaned sections (fixpass.py)
  <scratch>/img/...                    divider/cover images, credits
Outputs to <scratch>/work/<book>/out/
"""
import copy
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile

import pymupdf
from lxml import etree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import idmlw as W  # noqa: E402
from idml import Doc, bounds_of, parse_transform  # noqa: E402
from pages import BASE_CSS, PAGE_H, PAGE_W, Section, font_faces, story_document  # noqa: E402
from render import Renderer  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SCR = sys.argv[1]
BOOK = sys.argv[2]
FONTS = os.path.join(SCR, 'fonts')
NODE = ['node', os.path.join(HERE, 'print.js')]
NODE_ENV = dict(os.environ, NODE_PATH='/opt/node22/lib/node_modules')

TEAM = ['Ruqaya Mohammed Kadhim', 'Abdullah Musab Jefferz']
BOOKS = {
    'med1': dict(
        out='Internal-Medicine-Bank-Medicine-1-3rd-Edition', title='Internal Medicine Bank — Medicine 1',
        keys=['01-pit', '02-thy', '03-adr', '04-dm', '05-neph', '06-elec', '07-git', '08-rheum', '09-gen'],
        kicker='MEDICINE 1', big=['MEDICINE', 'BANK'], sub='Internal Medicine', cover='cover-med1.jpg',
        accent=(8, 102, 170), running='INTERNAL MEDICINE BANK  /  MEDICINE 1',
        scope='Endocrinology, nephrology and electrolytes, gastroenterology and hepatology, rheumatology and general medicine'),
    'med2': dict(
        out='Internal-Medicine-Bank-Medicine-2-3rd-Edition', title='Internal Medicine Bank — Medicine 2',
        keys=['01-cad', '02-hf', '03-chd', '04-arr', '05-valv', '06-peri', '07-htn', '08-cpharm', '09-cvsx',
              '10-cvsemq', '11-airway', '12-resinf', '13-crit', '14-pleura', '15-ild', '16-pvasc', '17-lca',
              '18-resx', '19-resemq'],
        kicker='MEDICINE 2', big=['MEDICINE', 'BANK'], sub='Internal Medicine', cover='cover-med2.jpg',
        accent=(150, 12, 24), running='INTERNAL MEDICINE BANK  /  MEDICINE 2',
        scope='Cardiovascular and respiratory medicine'),
    'surg2': dict(
        out='118-Surgery-Bank-General-Surgery-2-3rd-Edition', title='118 Surgery Bank — General Surgery 2',
        keys=['01-ul', '02-ll', '03-bone', '04-thor', '05-vasc', '06-neuro', '07-plas', '08-anaes'],
        kicker='SURGERY 2', big=['SURGERY', 'BANK'], sub='General Surgery', cover='cover-surg2.jpg',
        accent=(0, 140, 134), running='118 SURGERY BANK  /  GENERAL SURGERY 2',
        scope='Orthopaedics, thoracic, vascular, neurosurgery, plastic surgery and anaesthesia'),
}
CFG = BOOKS[BOOK]
EDITION = '3RD EDITION  /  2026'
WORK = os.path.join(SCR, 'work', BOOK)
OUT = os.path.join(WORK, 'out')
FLOW = os.path.join(WORK, 'flow')
os.makedirs(OUT, exist_ok=True)
os.makedirs(FLOW, exist_ok=True)
LINKS_SRC = os.path.join(WORK, 'fixed', 'Links')
FRONT_PAGES = 5  # cover, blank, title, how-to-use + credits, contents

HEAD_RE = re.compile(r'(EssHead|BankHead)-')


def log(*a):
    print(*a, flush=True)


# ===================================================================== metadata
def text_of(p):
    return ''.join(v for _, (k, v) in p['runs'] if k == 'text')


def section_meta(sec):
    d = sec.doc
    meta = dict(stats=[], toc=[])
    for p, its in sec.pre_pages[:2]:
        for it in its:
            if it['tag'] != 'TextFrame':
                continue
            for q in d.story(it['story']):
                st = q['style'].split('/')[-1].rsplit('-', 1)[0]
                t = text_of(q)
                if st == 'DivNum':
                    meta['num'] = t.strip()
                elif st == 'DivTitle':
                    meta['title'] = t.strip()
                elif st == 'OpKicker':
                    meta['part'] = t.strip()
                elif st == 'OpIntro':
                    meta['intro'] = t.strip()
                elif st == 'StatNum':
                    meta['stats'].append([t.strip(), None])
                elif st == 'StatLbl':
                    meta['stats'][-1][1] = t.strip()
                elif st == 'OpToc':
                    parts = t.split('\t')
                    meta['toc'].append(parts[1].strip() if len(parts) > 1 else t)
    return meta


# ===================================================================== pass B: story flows
GROUP_START = re.compile(r'(BankKicker|BankKickerFirst|EssKicker|EmqSecKicker|AnsHead)-')
ORPHAN_LIMIT = PAGE_H - 56.6929 - 105  # a heading group starting below this line moves to the next page


def flow_pass(sections):
    for key, sec in sections:
        nflow = len(sec.pre_pages) - 2
        sec.first_side = 0 if (2 + nflow) % 2 == 0 else 1  # sections start on a left (even) page
        sec.nflow = nflow
        sec.breaks = set()
    todo = [k for k, _ in sections]
    secd = dict(sections)
    for it in range(6):
        jobs = []
        for key in todo:
            sec = secd[key]
            anchors = []

            def anc(p, i, anchors=anchors):
                if HEAD_RE.search(p['style']) or GROUP_START.search(p['style']):
                    anchors.append((f'h{i}', p['style'], text_of(p).strip()))
                    return f'h{i}'
                return None
            extra = ''.join(f'#{b}{{break-before:page}}' for b in sorted(sec.breaks))
            html, _ = story_document(sec, FONTS, sec.first_side, anc, extra_css=extra)
            hp = os.path.join(FLOW, key + '.html')
            open(hp, 'w').write(html)
            sec.anchors = anchors
            jobs += [hp, os.path.join(FLOW, key + '.pdf')]
        if '--skip-flow' not in sys.argv or it > 0:
            subprocess.run(NODE + jobs, check=True, env=NODE_ENV, cwd=FLOW, stdout=subprocess.DEVNULL)
        nxt = []
        for key in todo:
            sec = secd[key]
            pdf = pymupdf.open(os.path.join(FLOW, key + '.pdf'))
            dummy = 1 if sec.first_side == 0 else 0
            links = [l for l in pdf[-1].get_links() if l.get('page', -1) >= 0]
            assert len(links) == len(sec.anchors), (key, len(links), len(sec.anchors))
            pos = {}
            for (aid, st, t), l in zip(sec.anchors, links):
                pos[aid] = (l['page'] - dummy, PAGE_H - l['to'].y)
            sec.head_pages = [(t, pos[aid][0]) for aid, st, t in sec.anchors if HEAD_RE.search(st)]
            sec.n_story = len(pdf) - 1 - dummy
            sec.flow_dummy = dummy
            new = {aid for aid, st, t in sec.anchors
                   if GROUP_START.search(st) and pos[aid][1] > ORPHAN_LIMIT and aid not in sec.breaks}
            if new:
                sec.breaks |= new
                nxt.append(key)
            else:
                log(key, 'story pages', sec.n_story, '(source had', len(sec.story_pages), ') breaks', len(sec.breaks))
        if not nxt:
            break
        todo = nxt


# ===================================================================== numbering
def number(sections):
    plan = []  # (kind, payload)
    for i in range(FRONT_PAGES):
        plan.append(('front', i))
    for key, sec in sections:
        sec.start = len(plan) + 1
        assert sec.start % 2 == 0
        for j, (p, its) in enumerate(sec.pre_pages):
            plan.append(('pre', (key, j)))
        sec.story_start = len(plan) + 1
        for j in range(sec.n_story):
            plan.append(('story', (key, j)))
        sec.end = len(plan)
        if sec.end % 2 == 0 and key != sections[-1][0]:
            plan.append(('notes', None))
    if len(plan) % 2 == 0:
        plan.append(('notes', None))
    plan.append(('back', None))
    return plan


# ===================================================================== IDML merge
RENAME_ATTRS = ('Self', 'ParentStory', 'PreviousTextFrame', 'NextTextFrame', 'AppliedMaster')


class Renamer:
    def __init__(self, prefix, ids):
        self.p = prefix
        self.ids = ids

    def __call__(self, v):
        return self.p + v if v in self.ids else v

    def tree(self, el):
        for e in el.iter():
            for a in RENAME_ATTRS:
                v = e.get(a)
                if v is not None and v in self.ids:
                    e.set(a, self.p + v)
            if e.get('ItemLayer') is not None:
                e.set('ItemLayer', W.LAYER)
        return el


def collect_ids(doc):
    ids = set()
    for n in doc.names:
        if n.startswith(('Stories/', 'Spreads/', 'MasterSpreads/')):
            for m in re.finditer(rb'\bSelf="([^"]+)"', doc.read(n)):
                ids.add(m.group(1).decode())
    return ids


def moved(el, it, side):
    """Copy of a page item, retranslated to page `side` of a new spread."""
    e = copy.deepcopy(el)
    t = it['t']
    bx0, by0, _, _ = bounds_of(el.find('Properties'), t)
    ox, oy = W.page_origin(side)
    dx = ox + it['x'] - bx0
    dy = oy + it['y'] - by0
    own = parse_transform(el.get('ItemTransform'))
    # it['t'] already includes the old spread transform: new = own + (spread + delta)
    st_dx = t[4] - own[4]
    st_dy = t[5] - own[5]
    e.set('ItemTransform', f'{own[0]:g} {own[1]:g} {own[2]:g} {own[3]:g} {W.f(own[4] + st_dx + dx)} {W.f(own[5] + st_dy + dy)}')
    return e


def xml(e):
    return etree.tostring(e, encoding='unicode')


class Merger:
    def __init__(self):
        self.files = {}        # path -> bytes
        self.stories = []      # story ids in order
        self.masters = []      # master ids
        self.spreads = []
        self.pstyles = {}      # Self -> xml
        self.cstyles = {}
        self.colors = {}       # Self -> xml (Color/Gradient/...)
        self.fonts = {}
        self.uid = 0
        self.master_prefix = iter([c for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'] + [a + b for a in 'ABC' for b in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'])

    def nid(self, p='bk'):
        self.uid += 1
        return f'{p}{self.uid:x}'

    # ------------------------------------------------ resources
    def add_resources(self, doc):
        st = etree.fromstring(doc.read('Resources/Styles.xml'))
        for el in st.iter('ParagraphStyle'):
            self.pstyles.setdefault(el.get('Self'), el)
        for el in st.iter('CharacterStyle'):
            self.cstyles.setdefault(el.get('Self'), el)
        gr = etree.fromstring(doc.read('Resources/Graphic.xml'))
        for el in gr:
            if el.get('Self'):
                self.colors.setdefault(el.get('Self'), el)
        fo = etree.fromstring(doc.read('Resources/Fonts.xml'))
        for el in fo:
            if el.get('Self'):
                self.fonts.setdefault(el.get('Self'), el)

    def write_resources(self, base):
        st = etree.fromstring(base.read('Resources/Styles.xml'))
        pg = st.find('RootParagraphStyleGroup')
        have = {e.get('Self') for e in pg.iter('ParagraphStyle')}
        for k, el in self.pstyles.items():
            if k not in have:
                pg.append(copy.deepcopy(el))
        cg = st.find('RootCharacterStyleGroup')
        have = {e.get('Self') for e in cg.iter('CharacterStyle')}
        for k, el in self.cstyles.items():
            if k not in have:
                cg.append(copy.deepcopy(el))
        self.files['Resources/Styles.xml'] = etree.tostring(st, xml_declaration=True, encoding='UTF-8', standalone=True).replace(
            b'AnchoredPosition="InlinePosition"', b'AnchoredPosition="AboveLine"')
        gr = etree.fromstring(base.read('Resources/Graphic.xml'))
        have = {e.get('Self') for e in gr}
        # colours must come before swatches/gradients that use them: insert after last Color
        last_color = max(i for i, e in enumerate(gr) if e.tag == 'Color')
        ins = last_color + 1
        for k, el in self.colors.items():
            if k not in have:
                if el.tag == 'Color':
                    gr.insert(ins, copy.deepcopy(el))
                    ins += 1
                else:
                    gr.append(copy.deepcopy(el))
        self.files['Resources/Graphic.xml'] = etree.tostring(gr, xml_declaration=True, encoding='UTF-8', standalone=True)
        fo = etree.fromstring(base.read('Resources/Fonts.xml'))
        have = {e.get('Self') for e in fo}
        for k, el in self.fonts.items():
            if k not in have:
                fo.append(copy.deepcopy(el))
        self.files['Resources/Fonts.xml'] = etree.tostring(fo, xml_declaration=True, encoding='UTF-8', standalone=True)

    # ------------------------------------------------ stories / masters
    def add_story_xml(self, sid, text):
        self.files[f'Stories/Story_{sid}.xml'] = text.encode('utf-8') if isinstance(text, str) else text
        self.stories.append(sid)

    def add_master(self, doc, mid, ren, base_name):
        root = etree.fromstring(doc.read(doc.masters[mid]['src']))
        ren.tree(root)
        ms = root[0]
        pfx = next(self.master_prefix)
        ms.set('NamePrefix', pfx)
        ms.set('BaseName', base_name)
        ms.set('Name', f'{pfx}-{base_name}')
        for pgel in ms.findall('Page'):
            pgel.set('Name', pfx)
        new = ms.get('Self')
        self.files[f'MasterSpreads/MasterSpread_{new}.xml'] = etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
        self.masters.append(new)
        return new

    # ------------------------------------------------ spreads
    def write_spreads(self, pages):
        """pages: list of dict(side, name, master, items[xml strings], self)."""
        i = 0
        spreads = []
        while i < len(pages):
            p = pages[i]
            if p['side'] == 1:
                group = [p]
                i += 1
            else:
                group = [p]
                if i + 1 < len(pages):
                    group.append(pages[i + 1])
                i += len(group)
            spreads.append(group)
        for g in spreads:
            sid = self.nid('sp')
            pxml = [W.page_xml(p['self'], p['name'], p['side'], p['master']) for p in g]
            items = [x for p in g for x in p['items']]
            binding = 0 if g[0]['side'] == 1 else 1
            self.files[f'Spreads/Spread_{sid}.xml'] = W.spread_xml(sid, pxml, items, len(g), binding).encode('utf-8')
            self.spreads.append(sid)

    def write(self, base, path, first_page_id, npages, links_dir):
        dm = base.designmap.decode('utf-8')
        dm = re.sub(r'\s*<idPkg:(MasterSpread|Spread|Story) src="[^"]+"/>', '', dm)
        dm = re.sub(r'StoryList="[^"]*"', 'StoryList="' + ' '.join(self.stories + ['ubackx']) + '"', dm)
        sec = re.search(r'<Section [^>]*>', dm).group(0)
        nsec = re.sub(r'Length="\d+"', f'Length="{npages}"', sec)
        nsec = re.sub(r'PageNumberStart="\d+"', 'PageNumberStart="1"', nsec)
        nsec = re.sub(r'PageStart="[^"]+"', f'PageStart="{first_page_id}"', nsec)
        lst = ''.join(f'\n\t<idPkg:MasterSpread src="MasterSpreads/MasterSpread_{m}.xml"/>' for m in self.masters)
        lst += ''.join(f'\n\t<idPkg:Spread src="Spreads/Spread_{s}.xml"/>' for s in self.spreads)
        dm = dm.replace(sec, lst.lstrip('\n') + '\n\t' + nsec, 1)
        # stories go right before </Document>-level BackingStory reference
        sl = ''.join(f'\n\t<idPkg:Story src="Stories/Story_{s}.xml"/>' for s in self.stories)
        dm = dm.replace('<idPkg:BackingStory', sl.lstrip('\n') + '\n\t<idPkg:BackingStory', 1)
        self.files['designmap.xml'] = dm.encode('utf-8')
        for n in ('META-INF/container.xml', 'META-INF/metadata.xml', 'Resources/Preferences.xml',
                  'XML/BackingStory.xml', 'XML/Tags.xml'):
            self.files[n] = base.read(n)
        self.files['Resources/Preferences.xml'] = self.files['Resources/Preferences.xml'].replace(
            b'AnchoredPosition="InlinePosition"', b'AnchoredPosition="AboveLine"')
        z = zipfile.ZipFile(path, 'w')
        z.writestr(zipfile.ZipInfo('mimetype'), b'application/vnd.adobe.indesign-idml-package',
                   compress_type=zipfile.ZIP_STORED)
        for n, data in self.files.items():
            z.writestr(n, data, compress_type=zipfile.ZIP_DEFLATED)
        z.close()


# ===================================================================== front / back matter
FM_STYLES = None


def fm_styles(acc):
    ink = 'Color/IMB Ink'
    A = 'Color/BK Accent'
    AF = 'Acumin Variable Concept'
    SS = 'Source Serif Variable'
    SA = 'Source Sans Variable'
    s = [
        W.pstyle_xml('FM-Kicker', AF, 'Semibold', 7.5, 9, 'Color/IMB White', tracking=300, caps=True),
        W.pstyle_xml('FM-CoverTitle', AF, 'Condensed Bold', 66, 58, 'Color/IMB White', tracking=-5, caps=True),
        W.pstyle_xml('FM-CoverSub', AF, 'Semibold', 17, 20, 'Color/IMB White', sb=12,
                     rule_above=(2.6, 28, ink, 0, 235)),
        W.pstyle_xml('FM-CoverEd', AF, 'Semibold', 7, 9, 'Color/IMB White', tracking=300, caps=True, sb=6),
        W.pstyle_xml('FM-CoverName', AF, 'Condensed Bold', 10.5, 13, ink),
        W.pstyle_xml('FM-CoverNameFirst', AF, 'Condensed Bold', 10.5, 13, ink, rule_above=(1.2, 13, ink, 0, 205)),
        W.pstyle_xml('FM-CoverTeam', AF, 'Semibold', 8, 10, A, tracking=300, caps=True, sb=6),
        W.pstyle_xml('FM-TKicker', AF, 'Semibold', 8, 10, A, tracking=300, caps=True),
        W.pstyle_xml('FM-TTitle', AF, 'Condensed Bold', 60, 54, ink, tracking=-5, caps=True, sb=8),
        W.pstyle_xml('FM-TSub', AF, 'Semibold', 18, 22, ink, sb=14, rule_above=(2.6, 30, A, 0, 380)),
        W.pstyle_xml('FM-TScope', SS, 'Regular', 10.5, 15, 'Color/IMB Muted', sb=10, ri=120),
        W.pstyle_xml('FM-TEd', AF, 'Semibold', 7.5, 9, 'Color/IMB Muted', tracking=300, caps=True, sb=16),
        W.pstyle_xml('FM-TName', AF, 'Condensed Bold', 12, 15, ink),
        W.pstyle_xml('FM-TTeam', AF, 'Semibold', 8, 10, A, tracking=300, caps=True, sb=6),
        W.pstyle_xml('FM-H1', AF, 'Condensed Bold', 24, 26, ink, sa=4, keep_next=2),
        W.pstyle_xml('FM-HKick', AF, 'Semibold', 7, 9, A, tracking=200, caps=True, sa=3, keep_next=2),
        W.pstyle_xml('FM-Body', SS, 'Regular', 8.6, 12, ink, sa=4, hyph=True),
        W.pstyle_xml('FM-Bullet', SS, 'Regular', 8.6, 12, ink, sa=3, li=14, fi=-14, tabs=[('LeftAlign', 14)], hyph=True),
        W.pstyle_xml('FM-H2', AF, 'Condensed Bold', 12, 14, A, sb=12, sa=4, keep_next=2,
                     rule_above=(0.6, 15, 'Color/IMB Line', 0, 0)),
        W.pstyle_xml('FM-Credit', SA, 'Regular', 6.8, 8.8, 'Color/IMB Muted', li=26, fi=-26, tabs=[('LeftAlign', 26)], sa=1.2),
        W.pstyle_xml('FM-Small', SA, 'Regular', 7, 9.4, 'Color/IMB Muted', sa=3),
        W.pstyle_xml('FM-TocPart', AF, 'Semibold', 7.5, 9, A, tracking=250, caps=True, sb=16, sa=6, keep_next=2,
                     rule_below=(0.6, 4, 'Color/IMB Line', 0, 0)),
        W.pstyle_xml('FM-Toc', AF, 'Regular', 11, 14, ink, sa=7.5,
                     tabs=[('LeftAlign', 34), ('RightAlign', 420), ('RightAlign', 493.2283)]),
        W.pstyle_xml('FM-NotesH', AF, 'Condensed Bold', 24, 26, 'Color/IMB Line'),
        W.pstyle_xml('FM-BackTitle', AF, 'Condensed Bold', 34, 34, ink, caps=True, tracking=-5),
        W.pstyle_xml('FM-BackBody', SS, 'Regular', 10.5, 15, ink, sb=12, ri=40),
        W.pstyle_xml('FM-BackStat', AF, 'Condensed Bold', 30, 30, A, sb=0),
        W.pstyle_xml('FM-BackStatL', AF, 'Semibold', 7, 9, 'Color/IMB Muted', tracking=250, caps=True, sb=2),
    ]
    c = [
        W.cstyle_xml('FM-TocNum', 'Acumin Variable Concept', 'Condensed Bold', 12, 'Color/BK Accent'),
        W.cstyle_xml('FM-TocCount', 'Acumin Variable Concept', 'Semibold', 7.5, 'Color/IMB Muted', 120, True),
        W.cstyle_xml('FM-TocPage', 'Acumin Variable Concept', 'Condensed Bold', 11, 'Color/BK Accent'),
        W.cstyle_xml('FM-Bold', 'Source Serif Variable', 'Semibold', None, None),
        W.cstyle_xml('FM-Bul', 'Acumin Variable Concept', 'Bold', None, 'Color/BK Accent'),
        W.cstyle_xml('FM-CreditNum', 'Acumin Variable Concept', 'Semibold', None, 'Color/BK Accent'),
    ]
    col = [W.color_xml('BK Accent', acc), W.color_xml('BK Paper', (246, 244, 240))]
    return s, c, col


def add_fm_resources(m, acc):
    s, c, col = fm_styles(acc)
    for x in s:
        e = etree.fromstring(x)
        m.pstyles[e.get('Self')] = e
    for x in c:
        e = etree.fromstring(x)
        m.cstyles[e.get('Self')] = e
    for x in col:
        e = etree.fromstring(x)
        m.colors[e.get('Self')] = e


class Synth:
    """Collects items for synthetic pages (front/back matter)."""

    def __init__(self, m, side):
        self.m = m
        self.side = side
        self.items = []
        self.ox, self.oy = W.page_origin(side)

    def rect(self, x, y, w, h, fill='Swatch/None', image=None, stroke='Swatch/None', sw=0):
        img = None
        if image:
            fname, pw, ph = image
            sc = max(w / pw, h / ph)
            img = (self.m.nid('im'), fname, pw, ph, sc, (w - pw * sc) / 2, (h - ph * sc) / 2)
        self.items.append(W.rect_xml(self.m.nid('r'), self.ox + x, self.oy + y, w, h, fill, stroke, sw, img))

    def frame(self, x, y, w, h, paras, vj='TopAlign', cols=1):
        sid = self.m.nid('st')
        self.m.add_story_xml(sid, W.story_xml(sid, paras))
        self.items.append(W.frame_xml(self.m.nid('tf'), sid, self.ox + x, self.oy + y, w, h, cols=cols, vj=vj))
        return sid

    def line(self, x0, y0, x1, y1, color, sw):
        self.items.append(W.line_xml(self.m.nid('ln'), self.ox + x0, self.oy + y0, self.ox + x1, self.oy + y1, color, sw))


def img_size(path):
    from PIL import Image
    with Image.open(path) as im:
        return im.size


def front_pages(m, metas, sections, links):
    pages = []
    acc = CFG['accent']
    # 1 -- cover (right page)
    s = Synth(m, 1)
    cw, ch = img_size(os.path.join(links, CFG['cover']))
    s.rect(0, -W.BLEED, PAGE_W + W.BLEED, PAGE_H + 2 * W.BLEED, 'Color/IMB White', image=(CFG['cover'], cw, ch))
    lw, lh = img_size(os.path.join(links, 'logo-ar118.png'))
    s.rect(410, 66, 112, 112 * lh / lw, image=('logo-ar118.png', lw, lh))
    s.frame(40, 38, 330, 250, [
        ('FM-Kicker', [(None, CFG['kicker'])]),
        ('FM-CoverTitle', [(None, CFG['big'][0])]),
        ('FM-CoverTitle', [(None, CFG['big'][1])]),
        ('FM-CoverSub', [(None, CFG['sub'])]),
        ('FM-CoverEd', [(None, EDITION)]),
    ])
    s.frame(40, 712, 300, 90, [
        ('FM-CoverNameFirst', [(None, TEAM[0])]),
        ('FM-CoverName', [(None, TEAM[1])]),
        ('FM-CoverTeam', [(None, '118 Team')]),
    ], vj='BottomAlign')
    pages.append(dict(items=s.items, master='n', kind='cover'))
    # 2 -- blank
    pages.append(dict(items=[], master='n', kind='blank'))
    # 3 -- title page
    s = Synth(m, 1)
    s.rect(PAGE_W - 6, -W.BLEED, 6 + W.BLEED, PAGE_H + 2 * W.BLEED, 'Color/BK Accent')
    s.rect(440, 70, 90, 90 * lh / lw, image=('logo-ar118.png', lw, lh))
    s.frame(56.7, 180, 440, 330, [
        ('FM-TKicker', [(None, CFG['kicker'])]),
        ('FM-TTitle', [(None, CFG['big'][0])]),
        ('FM-TTitle', [(None, CFG['big'][1])]),
        ('FM-TSub', [(None, CFG['sub'])]),
        ('FM-TScope', [(None, CFG['scope'] + '.')]),
        ('FM-TEd', [(None, EDITION)]),
    ])
    s.frame(56.7, 690, 400, 90, [
        ('FM-TName', [(None, TEAM[0])]),
        ('FM-TName', [(None, TEAM[1])]),
        ('FM-TTeam', [(None, '118 Team')]),
    ], vj='BottomAlign')
    pages.append(dict(items=s.items, master='n', kind='title'))
    # 4 -- how to use + credits (left page)
    s = Synth(m, 0)
    nq = total_questions(metas)
    howto = [
        ('FM-HKick', [(None, 'Before you start')]),
        ('FM-H1', [(None, 'How to use this book')]),
        ('FM-Body', [(None, f'This bank collects {nq:,} exam-style questions in {len(sections)} sections. '
                           'Each section opens with a divider and a chapter page that lists its question banks '
                           'with page numbers, so you can jump straight to a source.')]),
        ('FM-Bullet', [('FM-Bul', '•'), (None, '\tQuestions come first, grouped by source bank; the answers for each '
                                              'bank follow straight after it, so you can test yourself before you look.')]),
        ('FM-Bullet', [('FM-Bul', '•'), (None, '\tEvery answer gives the key letter, the correct option and a short '
                                              'explanation of why it is right and why the tempting distractors are wrong.')]),
        ('FM-Bullet', [('FM-Bul', '•'), (None, '\tEMQs give a theme and an option list, then several stems; choose '
                                              'the single best option for each stem. Options can be used more than once.')]),
        ('FM-Bullet', [('FM-Bul', '•'), (None, '\tA gold “Repeated idea” box marks a concept that is examined again '
                                              'and again across papers and books. Learn these first.')]),
        ('FM-Bullet', [('FM-Bul', '•'), (None, '\tSummary boxes, approaches and flowcharts at the start of a section '
                                              'are for quick revision the night before the exam.')]),
        ('FM-H2', [(None, 'Image credits')]),
        ('FM-Small', [(None, 'Cover artwork: 118 Team. Section images are real photographs and scans, colour-graded '
                             'for this edition. They are used under the licences shown.')]),
    ]
    for key, sec in sections:
        mt = metas[key]
        cr = CREDITS.get(key.split('-', 1)[1], '')
        howto.append(('FM-Credit', [('FM-CreditNum', mt.get('num', '')), (None, '\t' + mt.get('title', '') + ': ' + cr)]))
    howto += [
        ('FM-H2', [(None, CFG['title'])]),
        ('FM-Small', [(None, f'{EDITION.title().replace("Rd", "rd")}. Prepared by {TEAM[0]} and {TEAM[1]}, 118 Team. '
                             'Typeset in Acumin, Source Serif and Source Sans.')]),
    ]
    s.frame(48.189, 59.5276, 493.2283, 725.669, howto)
    pages.append(dict(items=s.items, master='n', kind='howto'))
    # 5 -- contents (right page)
    s = Synth(m, 1)
    paras = [('FM-HKick', [(None, CFG['title'])]), ('FM-H1', [(None, 'Contents')])]
    part = None
    for key, sec in sections:
        mt = metas[key]
        if mt.get('part') and mt['part'] != part:
            part = mt['part']
            paras.append(('FM-TocPart', [(None, part)]))
        counts = '  /  '.join(f'{n} {lbl}' for n, lbl in mt['stats'][:2] if n and n != '0')
        paras.append(('FM-Toc', [('FM-TocNum', mt.get('num', '')), (None, '\t' + mt.get('title', '') + '\t'),
                                 ('FM-TocCount', counts), (None, '\t'), ('FM-TocPage', str(sec.start))]))
    s.frame(53.8583, 59.5276, 493.2283, 725.669, paras)
    pages.append(dict(items=s.items, master='n', kind='contents'))
    return pages


def notes_page(m, side):
    s = Synth(m, side)
    x0 = 48.189 if side == 0 else 53.8583
    s.frame(x0, 59.5276, 493.2283, 40, [('FM-NotesH', [(None, 'Notes')])])
    y = 120
    while y < 780:
        s.line(x0, y, x0 + 493.2283, y, 'Color/IMB Line', 0.5)
        y += 22.7
    return dict(items=s.items, master='n', kind='notes')


def back_page(m, metas, sections, links):
    s = Synth(m, 0)
    s.rect(-W.BLEED, -W.BLEED, PAGE_W + W.BLEED, PAGE_H + 2 * W.BLEED, 'Color/BK Paper')
    s.rect(-W.BLEED, -W.BLEED, PAGE_W + W.BLEED, 10 + W.BLEED, 'Color/BK Accent')
    lw, lh = img_size(os.path.join(links, 'logo-ar118.png'))
    s.rect(PAGE_W / 2 - 50, 80, 100, 100 * lh / lw, image=('logo-ar118.png', lw, lh))
    nq = total_questions(metas)
    mcq = sum(int(n) for mt in metas.values() for n, l in mt['stats'] if n.isdigit() and 'MCQ' in (l or ''))
    emq = sum(int(n) for mt in metas.values() for n, l in mt['stats'] if n.isdigit() and 'EMQ' in (l or ''))
    s.frame(70, 230, 455, 250, [
        ('FM-TKicker', [(None, CFG['kicker'] + '  /  ' + EDITION)]),
        ('FM-BackTitle', [(None, CFG['title'].replace(' — ', ' '))]),
        ('FM-BackBody', [(None, f'{CFG["scope"]}, in {len(sections)} sections. Local end-block and final papers, '
                                'formative and previous-years exams and the major review books, each answered with '
                                'a short explanation of why the key is right and the distractors are wrong.')]),
    ])
    stats = [(f'{nq:,}', 'questions'), (f'{mcq:,}', 'MCQs'), (f'{emq:,}', 'EMQ items'), (str(len(sections)), 'sections')]
    for i, (n, l) in enumerate(stats):
        s.frame(70 + i * 115, 520, 105, 50, [('FM-BackStat', [(None, n)]), ('FM-BackStatL', [(None, l)])])
    s.frame(70, 720, 455, 70, [
        ('FM-TName', [(None, TEAM[0] + '  /  ' + TEAM[1])]),
        ('FM-TTeam', [(None, '118 Team')]),
    ], vj='BottomAlign')
    return dict(items=s.items, master='n', kind='back')


def total_questions(metas):
    t = 0
    for mt in metas.values():
        for n, l in mt['stats']:
            if n.isdigit() and l and ('MCQ' in l or 'EMQ' in l):
                t += int(n)
    return t


CREDITS = {}


# ===================================================================== main
def main():
    global CREDITS
    CREDITS = json.load(open(os.path.join(SCR, 'img', 'div', 'credits.json')))
    # links folder for the book
    links = os.path.join(OUT, 'Links')
    os.makedirs(links, exist_ok=True)
    for fn in os.listdir(LINKS_SRC):
        shutil.copy2(os.path.join(LINKS_SRC, fn), links)
    shutil.copy2(os.path.join(SCR, 'img', 'cover', CFG['cover']), links)
    shutil.copy2(os.path.join(SCR, 'img', 'cover', 'logo-ar118.png'), links)
    img_map = {n: 'file://' + os.path.join(links, n) for n in os.listdir(links)}

    sections = []
    for key in CFG['keys']:
        sec = Section(os.path.join(WORK, 'fixed', key + '.idml'), img_map=img_map)
        sections.append((key, sec))
    metas = {k: section_meta(s) for k, s in sections}
    flow_pass(sections)
    plan = number(sections)
    npages = len(plan)
    log('book pages', npages)

    # ---------------------------------------------------------------- IDML
    m = Merger()
    base = sections[0][1].doc
    for key, sec in sections:
        m.add_resources(sec.doc)
    add_fm_resources(m, CFG['accent'])
    m.write_resources(base)

    front = front_pages(m, metas, sections, links)
    secinfo = {}
    for idx, (key, sec) in enumerate(sections):
        d = sec.doc
        pfx = f'k{idx + 1:02d}'
        ren = Renamer(pfx, collect_ids(d))
        mt = metas[key]
        # masters used by this section
        mmap = {}
        used = {p['master'] for p, _ in sec.pre_pages + sec.story_pages if p['master'] not in ('n', None)}
        for mid in used:
            mmap[mid] = m.add_master(d, mid, ren, f'{mt.get("num", "")} {mt.get("title", key)}'[:60])
        # opener TOC page numbers
        toc_pages = []
        heads = dict()
        for t, pg in sec.head_pages:
            heads.setdefault(t, sec.story_start + pg)
        head_seq = [sec.story_start + pg for _, pg in sec.head_pages]
        hi = 0
        for row in mt['toc']:
            if 'flowchart' in row.lower() and sec.nflow:
                toc_pages.append(sec.start + 2)
            elif row in heads:
                toc_pages.append(heads[row])
                hi += 1
            else:
                toc_pages.append(head_seq[min(hi, len(head_seq) - 1)])
                hi += 1
        sec.toc_pages = toc_pages
        # stories (renamed + patched)
        for n in d.names:
            if not n.startswith('Stories/'):
                continue
            root = etree.fromstring(d.read(n))
            ren.tree(root)
            # TOC story: patch "page NN"
            k = 0
            for psr in root.iter('ParagraphStyleRange'):
                if 'OpToc' not in psr.get('AppliedParagraphStyle', ''):
                    continue
                for csr in psr.iter('CharacterStyleRange'):
                    c = csr.find('Content')
                    if 'TocPage' in csr.get('AppliedCharacterStyle', '') and c is not None and (c.text or '').startswith('page '):
                        if k < len(toc_pages):
                            c.text = f'page {toc_pages[k]}'
                        k += 1
            sid = root[0].get('Self')
            m.add_story_xml(sid, etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True))
        # pre pages
        pages = []
        for j, (p, its) in enumerate(sec.pre_pages):
            num = sec.start + j
            side = 0 if num % 2 == 0 else 1
            items = [xml(ren.tree(moved(it['el'], it, side))) for it in its]
            pages.append(dict(items=items, master=mmap.get(p['master'], 'n'), kind='pre'))
        # story pages with a fresh frame chain
        tmpl = next(it for p, its in sec.story_pages for it in its if it['tag'] == 'TextFrame' and it['story'] == sec.main)
        story_id = pfx + sec.main
        fids = [m.nid(pfx + 'f') for _ in range(sec.n_story)]
        for j in range(sec.n_story):
            num = sec.story_start + j
            side = 0 if num % 2 == 0 else 1
            x = 48.189 if side == 0 else 53.8583
            ox, oy = W.page_origin(side)
            prev = fids[j - 1] if j else 'n'
            nxt = fids[j + 1] if j + 1 < len(fids) else 'n'
            fr = W.frame_xml(fids[j], story_id, ox + x, oy + 59.5276, 493.2283, 725.669, cols=tmpl['cols'],
                             gutter=tmpl['gutter'], prev=prev, nxt=nxt)
            pages.append(dict(items=[fr], master=mmap.get(sec.story_master, 'n'), kind='story'))
        secinfo[key] = pages
        sec.main_story_id = story_id
    # assemble in plan order
    allpages = []
    fi = 0
    cursor = {k: 0 for k, _ in sections}
    for kind, payload in plan:
        if kind == 'front':
            allpages.append(front[payload])
        elif kind in ('pre', 'story'):
            key = payload[0]
            allpages.append(secinfo[key][cursor[key]])
            cursor[key] += 1
        elif kind == 'notes':
            allpages.append(None)
        elif kind == 'back':
            allpages.append(None)
    for i, p in enumerate(allpages):
        side = 0 if (i + 1) % 2 == 0 else 1
        if p is None:
            p = notes_page(m, side) if plan[i][0] == 'notes' else back_page(m, metas, sections, links)
            allpages[i] = p
        p['side'] = side
        p['name'] = str(i + 1)
        p['self'] = m.nid('pg')
    m.write_spreads(allpages)
    idml_path = os.path.join(OUT, CFG['out'] + '.idml')
    m.write(base, idml_path, allpages[0]['self'], len(allpages), links)
    log('IDML written', idml_path)
    json.dump(dict(plan=plan, sections={k: dict(start=s.start, story_start=s.story_start, n_story=s.n_story,
                                                    end=s.end, toc=metas[k]['toc'], toc_pages=s.toc_pages,
                                                    heads=s.head_pages, meta=metas[k], main=s.main_story_id,
                                                    dummy=s.flow_dummy)
                                        for k, s in sections}),
              open(os.path.join(OUT, 'layout.json'), 'w'), indent=1)
    build_pdf(idml_path, plan, sections, metas, img_map)


# ===================================================================== PDF
def build_pdf(idml_path, plan, sections, metas, img_map):
    doc = Doc(idml_path)
    pg = Section.__new__(Section)
    pg.doc = doc
    pg.r = Renderer(doc, img_map=img_map)
    main_ids = {s.main_story_id for _, s in sections}
    html_pages = []
    for sp in doc.spreads:
        for p in sp['pages']:
            its = [it for it in sp['items'] if it['page'] == p['self_']
                   and not (it['tag'] == 'TextFrame' and it['story'] in main_ids)]
            num = int(p['name'])
            side = 0 if num % 2 == 0 else 1
            html_pages.append(pg.abs_page(p, its, num, side))
    css = (f"{font_faces(FONTS)}{BASE_CSS}@page{{size:{PAGE_W}pt {PAGE_H}pt;margin:0}}"
           + ''.join(pg.r.css))
    html = f'<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><style>{css}</style></head><body>{"".join(html_pages)}</body></html>'
    hp = os.path.join(FLOW, 'chrome.html')
    open(hp, 'w').write(html)
    cp = os.path.join(FLOW, 'chrome.pdf')
    subprocess.run(NODE + [hp, cp], check=True, env=NODE_ENV, cwd=FLOW)
    chrome = pymupdf.open(cp)
    assert len(chrome) == len(plan), (len(chrome), len(plan))
    flows = {k: pymupdf.open(os.path.join(FLOW, k + '.pdf')) for k, _ in sections}
    secd = dict(sections)
    out = pymupdf.open()
    for i, (kind, payload) in enumerate(plan):
        out.insert_pdf(chrome, from_page=i, to_page=i)
        if kind == 'story':
            key, j = payload
            page = out[-1]
            page.show_pdf_page(page.rect, flows[key], j + secd[key].flow_dummy, overlay=False)
    # bookmarks + links
    toc = [[1, 'Cover', 1], [1, 'How to use this book', 4], [1, 'Contents', 5]]
    for key, sec in sections:
        mt = metas[key]
        toc.append([1, f'{mt.get("num", "")}  {mt.get("title", key)}', sec.start])
        for (t, _), p in zip([(r, 0) for r in mt['toc']], sec.toc_pages):
            toc.append([2, t, p])
    toc.append([1, 'Back cover', len(plan)])
    out.set_toc(toc)
    # contents page links
    cpage = out[4]
    for key, sec in sections:
        title = metas[key].get('title', '')
        for r in cpage.search_for(title)[:1]:
            rr = pymupdf.Rect(53, r.y0 - 3, 547, r.y1 + 3)
            cpage.insert_link(dict(kind=pymupdf.LINK_GOTO, **{'from': rr}, page=sec.start - 1, to=pymupdf.Point(0, 0)))
    # opener TOC links
    for key, sec in sections:
        op = out[sec.start]  # opener page (0-based index start)
        for row, p in zip(metas[key]['toc'], sec.toc_pages):
            hits = op.search_for(row)
            if hits:
                r = hits[0]
                rr = pymupdf.Rect(50, r.y0 - 2, 550, r.y1 + 2)
                op.insert_link(dict(kind=pymupdf.LINK_GOTO, **{'from': rr}, page=p - 1, to=pymupdf.Point(0, 0)))
    out.set_metadata(dict(title=CFG['title'], author='118 Team — ' + ', '.join(TEAM), subject=CFG['scope'],
                          creator='118 Team', producer='118 Team'))
    pdf_path = os.path.join(OUT, CFG['out'] + '.pdf')
    out.save(pdf_path, garbage=4, deflate=True)
    log('PDF written', pdf_path, len(out), 'pages')


if __name__ == '__main__':
    main()
