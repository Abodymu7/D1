"""Minimal IDML reader for the Bank books (generated IDMLs: paragraphs, character
style runs, inline image rectangles, simple frames on spreads)."""
import re
import zipfile
from lxml import etree

NS = {'idPkg': 'http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging'}


def fnum(v, d=0.0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return d


def parse_transform(s):
    a, b, c, d, e, f = [float(x) for x in (s or '1 0 0 1 0 0').split()]
    return (a, b, c, d, e, f)


def apply_t(t, x, y):
    a, b, c, d, e, f = t
    return (a * x + c * y + e, b * x + d * y + f)


def mul_t(t1, t2):
    """t1 then t2 (point -> t2(t1(p)))."""
    a1, b1, c1, d1, e1, f1 = t1
    a2, b2, c2, d2, e2, f2 = t2
    return (a1 * a2 + b1 * c2, a1 * b2 + b1 * d2,
            c1 * a2 + d1 * c2, c1 * b2 + d1 * d2,
            e1 * a2 + f1 * c2 + e2, e1 * b2 + f1 * d2 + f2)


def bounds_of(el, t):
    pts = []
    for p in el.iter('PathPointType'):
        x, y = [float(v) for v in p.get('Anchor').split()]
        pts.append(apply_t(t, x, y))
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


class Style(dict):
    pass


def _props(el):
    d = {}
    for k, v in el.attrib.items():
        if k in ('Self', 'Name', 'Imported', 'NextStyle', 'KeyboardShortcut'):
            continue
        d[k] = v
    pr = el.find('Properties')
    if pr is not None:
        for p in pr:
            if p.tag == 'BasedOn':
                d['BasedOn'] = p.text
            elif p.tag in ('AppliedFont', 'Leading'):
                d[p.tag] = p.text
            elif p.tag in ('RuleAboveColor', 'RuleBelowColor', 'UnderlineColor'):
                d[p.tag] = p.text
            elif p.tag == 'TabList':
                tabs = []
                for li in p.findall('ListItem'):
                    tabs.append((li.findtext('Alignment'), fnum(li.findtext('Position'))))
                d['TabList'] = tabs
    return d


class Doc:
    def __init__(self, path):
        self.path = path
        self.z = zipfile.ZipFile(path)
        self.names = self.z.namelist()
        self.designmap = self.z.read('designmap.xml')
        self._styles()
        self._colors()
        self._masters()
        self._spreads()
        self.story_cache = {}

    def read(self, n):
        return self.z.read(n)

    # ---------- styles
    def _styles(self):
        r = etree.fromstring(self.read('Resources/Styles.xml'))
        self.pstyles_raw = {}
        self.cstyles_raw = {}
        for el in r.iter('ParagraphStyle'):
            self.pstyles_raw[el.get('Self')] = _props(el)
        for el in r.iter('CharacterStyle'):
            self.cstyles_raw[el.get('Self')] = _props(el)
        self._pcache = {}

    def pstyle(self, name):
        if name in self._pcache:
            return self._pcache[name]
        raw = self.pstyles_raw.get(name, {})
        base = raw.get('BasedOn')
        d = {}
        if base and base not in ('$ID/[No paragraph style]',) and base != name:
            if not base.startswith('ParagraphStyle/'):
                base = 'ParagraphStyle/' + base
            d.update(self.pstyle(base))
        elif name != 'ParagraphStyle/$ID/[No paragraph style]':
            d.update(self.pstyles_raw.get('ParagraphStyle/$ID/[No paragraph style]', {}))
        d.update({k: v for k, v in raw.items() if k != 'BasedOn'})
        self._pcache[name] = d
        return d

    def cstyle(self, name):
        if not name or name.endswith('[No character style]'):
            return {}
        return {k: v for k, v in self.cstyles_raw.get(name, {}).items() if k != 'BasedOn'}

    # ---------- colours
    def _colors(self):
        r = etree.fromstring(self.read('Resources/Graphic.xml'))
        self.colors = {}
        for el in r.iter('Color'):
            sp = el.get('Space')
            v = [float(x) for x in el.get('ColorValue').split()]
            if sp == 'RGB':
                rgb = tuple(int(round(x)) for x in v)
            elif sp == 'CMYK':
                c, m, y, k = [x / 100 for x in v]
                rgb = tuple(int(round(255 * (1 - a) * (1 - k))) for a in (c, m, y))
            else:
                rgb = (0, 0, 0)
            self.colors[el.get('Self')] = rgb
        self.colors['Swatch/None'] = None
        self.colors['Color/Paper'] = (255, 255, 255)

    def rgb(self, name, tint=None):
        c = self.colors.get(name)
        if c is None:
            return None
        if tint is not None and 0 <= tint < 100:
            c = tuple(int(round(255 - (255 - x) * tint / 100)) for x in c)
        return c

    # ---------- spreads
    def _parse_spread(self, root, master=False):
        sp = root[0]
        st = parse_transform(sp.get('ItemTransform'))
        pages = []
        for p in sp.findall('Page'):
            pt = mul_t(parse_transform(p.get('ItemTransform')), st)
            gb = [float(x) for x in p.get('GeometricBounds').split()]
            mp = p.find('MarginPreference')
            pages.append(dict(self_=p.get('Self'), name=p.get('Name'), master=p.get('AppliedMaster'),
                              ox=pt[4] + gb[1], oy=pt[5] + gb[0], w=gb[3] - gb[1], h=gb[2] - gb[0],
                              margins={k: fnum(mp.get(k)) for k in ('Top', 'Bottom', 'Left', 'Right')} if mp is not None else {},
                              el=p))
        items = []
        for el in sp:
            if el.tag in ('Page', 'FlattenerPreference', 'Properties'):
                continue
            t = mul_t(parse_transform(el.get('ItemTransform')), st)
            x0, y0, x1, y1 = bounds_of(el.find('Properties'), t) if el.find('Properties') is not None else (0, 0, 0, 0)
            cx = (x0 + x1) / 2
            pg = None
            for p in pages:
                if p['ox'] - 1 <= cx <= p['ox'] + p['w'] + 1:
                    pg = p
            if pg is None:  # spans pages (bleed rect) -> nearest
                pg = min(pages, key=lambda p: abs(p['ox'] + p['w'] / 2 - cx))
            it = dict(tag=el.tag, el=el, x=x0 - pg['ox'], y=y0 - pg['oy'], w=x1 - x0, h=y1 - y0,
                      page=pg['self_'], t=t)
            if el.tag == 'TextFrame':
                tfp = el.find('TextFramePreference')
                it.update(story=el.get('ParentStory'), prev=el.get('PreviousTextFrame'),
                          next=el.get('NextTextFrame'), cols=int(tfp.get('TextColumnCount', '1')),
                          gutter=fnum(tfp.get('TextColumnGutter'), 12),
                          vj=tfp.get('VerticalJustification', 'TopAlign'))
            elif el.tag == 'Rectangle':
                img = el.find('Image')
                it.update(fill=el.get('FillColor'), tint=fnum(el.get('FillTint'), -1),
                          stroke=el.get('StrokeColor'), sw=fnum(el.get('StrokeWeight')))
                if img is not None:
                    link = img.find('Link').get('LinkResourceURI')
                    it.update(image=link.replace('file:', ''), imgt=mul_t(parse_transform(img.get('ItemTransform')), t),
                              gb={k: fnum(img.find('Properties/GraphicBounds').get(k)) for k in ('Left', 'Top', 'Right', 'Bottom')})
            elif el.tag == 'GraphicLine':
                it.update(stroke=el.get('StrokeColor'), sw=fnum(el.get('StrokeWeight')))
            items.append(it)
        return dict(self_=sp.get('Self'), pages=pages, items=items, el=sp)

    def _masters(self):
        dm = etree.fromstring(self.designmap)
        self.masters = {}
        for m in dm.findall('idPkg:MasterSpread', NS):
            r = etree.fromstring(self.read(m.get('src')))
            s = self._parse_spread(r, True)
            s['src'] = m.get('src')
            self.masters[s['self_']] = s

    def _spreads(self):
        dm = etree.fromstring(self.designmap)
        self.spreads = []
        for m in dm.findall('idPkg:Spread', NS):
            r = etree.fromstring(self.read(m.get('src')))
            s = self._parse_spread(r)
            s['src'] = m.get('src')
            self.spreads.append(s)

    # ---------- stories
    def story(self, sid):
        if sid in self.story_cache:
            return self.story_cache[sid]
        r = etree.fromstring(self.read(f'Stories/Story_{sid}.xml'))
        paras = []
        for psr in r.iter('ParagraphStyleRange'):
            cur = None
            for csr in psr.findall('CharacterStyleRange'):
                cs = csr.get('AppliedCharacterStyle')
                for node in csr:
                    if cur is None:
                        cur = dict(style=psr.get('AppliedParagraphStyle'), attrs=dict(psr.attrib), runs=[])
                    if node.tag == 'Content':
                        txt = node.text or ''
                        for pi in node:  # processing instruction e.g. page number
                            if isinstance(pi, etree._ProcessingInstruction):
                                if txt:
                                    cur['runs'].append((cs, ('text', txt)))
                                    txt = ''
                                code = (pi.text or '').strip()
                                kind = {'18': 'pagenum', '8': 'rtab', '7': 'indenthere'}.get(code, 'pi')
                                cur['runs'].append((cs, (kind, code)))
                            if pi.tail:
                                txt += pi.tail
                        if node.text or len(node) == 0:
                            pass
                        if txt:
                            cur['runs'].append((cs, ('text', txt)))
                    elif node.tag == 'Br':
                        paras.append(cur)
                        cur = None
                    elif node.tag == 'Rectangle':
                        cur['runs'].append((cs, ('rect', node)))
            if cur is not None and cur['runs']:
                paras.append(cur)
        self.story_cache[sid] = paras
        return paras
