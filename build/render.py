"""IDML -> HTML renderer for the Bank books (Chromium prints the HTML to PDF)."""
import html
import os
import re

from idml import Doc, fnum

PT = 'pt'
FONTDIR = os.environ.get('BANK_FONTS', '')

# font metrics (ascent, descent) in em, typo metrics (USE_TYPO_METRICS set)
METRICS = {
    'Source Serif 4': (1.036, 0.335),
    'Source Sans 3': (1.024, 0.400),
    'Archivo': (0.878, 0.210),
}

WEIGHTS = [('ExtraBlack', 950), ('Black', 900), ('Heavy', 900), ('ExtraBold', 800), ('Bold', 700),
           ('Semibold', 600), ('SemiBold', 600), ('Medium', 500), ('ExtraLight', 200), ('Light', 300),
           ('Thin', 100)]


def font_css(font, style):
    """Map an InDesign font + style to CSS family/weight/stretch/italic."""
    style = style or 'Regular'
    font = font or 'Source Serif Variable'
    if 'Acumin' in font:
        fam = 'Archivo'
    elif 'Sans' in font or 'Myriad' in font:
        fam = 'Source Sans 3'
    else:
        fam = 'Source Serif 4'
    w = 400
    for k, v in WEIGHTS:
        if k in style:
            w = v
            break
    if style.strip() in ('B',):
        w = 700
    stretch = 100
    if 'ExtraCondensed' in style or 'Extra Condensed' in style:
        stretch = 62
    elif 'SemiCondensed' in style:
        stretch = 87.5
    elif 'Condensed' in style or 'Cond' in style:
        stretch = 75
    italic = 'Italic' in style or style.endswith(' It')
    return fam, w, stretch, italic


def rgbcss(c, alpha=None):
    if c is None:
        return 'transparent'
    if alpha is not None:
        return f'rgba({c[0]},{c[1]},{c[2]},{alpha:.3f})'
    return '#%02x%02x%02x' % c


def esc(t):
    return html.escape(t, quote=False)


class Renderer:
    def __init__(self, doc: Doc, imgdir_url='Links/', img_map=None):
        self.doc = doc
        self.imgdir_url = imgdir_url
        self.img_map = img_map or {}
        self.pclass = {}
        self.cclass = {}
        self.css = []
        self.uid = re.sub(r'\W', '', os.path.basename(doc.path).split('.')[0])

    # ------------------------------------------------------------ styles
    def _font_decl(self, st):
        fam, w, stretch, it = font_css(st.get('AppliedFont'), st.get('FontStyle'))
        d = [f"font-family:'{fam}'", f'font-weight:{w}']
        if fam == 'Archivo':
            d.append(f'font-stretch:{stretch}%')
        d.append('font-style:' + ('italic' if it else 'normal'))
        return d, fam

    def pstyle_class(self, name):
        if name in self.pclass:
            return self.pclass[name]
        st = self.doc.pstyle(name)
        cls = 'p' + self.uid + str(len(self.pclass))
        d, fam = self._font_decl(st)
        size = fnum(st.get('PointSize'), 12)
        lead = st.get('Leading')
        lead = fnum(lead, size * 1.2) if lead not in (None, 'Auto') else size * fnum(st.get('AutoLeading'), 120) / 100
        d += [f'font-size:{size}pt', f'line-height:{lead}pt']
        col = self.doc.rgb(st.get('FillColor', 'Color/Black'), fnum(st.get('FillTint'), -1))
        d.append('color:' + rgbcss(col or (0, 0, 0)))
        j = st.get('Justification', 'LeftAlign')
        d.append('text-align:' + {'CenterAlign': 'center', 'RightAlign': 'right', 'LeftJustified': 'justify',
                                  'FullyJustified': 'justify'}.get(j, 'left'))
        li = fnum(st.get('LeftIndent'))
        ri = fnum(st.get('RightIndent'))
        fi = fnum(st.get('FirstLineIndent'))
        d += [f'padding-left:{li}pt', f'padding-right:{ri}pt', f'text-indent:{fi}pt']
        tr = fnum(st.get('Tracking'))
        if tr:
            d.append(f'letter-spacing:{tr / 1000:.3f}em')
        if st.get('Capitalization') == 'AllCaps':
            d.append('text-transform:uppercase')
        if st.get('Hyphenation') == 'true':
            d.append('hyphens:auto')
        else:
            d.append('hyphens:manual')
        # keeps
        if int(fnum(st.get('KeepWithNext'))) > 0:
            d.append('break-after:avoid')
        if st.get('KeepAllLinesTogether') == 'true' or (st.get('KeepLinesTogether') == 'true' and st.get('KeepAllLinesTogether') == 'true'):
            d.append('break-inside:avoid')
        if st.get('KeepLinesTogether') == 'true':
            d += [f"orphans:{int(fnum(st.get('KeepFirstLines'), 2))}", f"widows:{int(fnum(st.get('KeepLastLines'), 2))}"]
        else:
            d += ['orphans:1', 'widows:1']
        sp = st.get('StartParagraph', 'Anywhere')
        if sp == 'NextPage':
            d.append('break-before:page')
        elif sp == 'NextColumn':
            d.append('break-before:column')
        if st.get('SpanColumnType') == 'SpanColumns':
            d.append('column-span:all')
        self.css.append(f'.{cls}{{{";".join(d)}}}')
        # rules
        asc, desc = METRICS[fam]
        base1 = (lead - (asc + desc) * size) / 2 + asc * size  # first baseline from top of first line
        if st.get('RuleAbove') == 'true':
            w = fnum(st.get('RuleAboveLineWeight'), 1)
            off = fnum(st.get('RuleAboveOffset'))
            c = self.doc.rgb(st.get('RuleAboveColor', 'Color/Black'), fnum(st.get('RuleAboveTint'), -1))
            l = fnum(st.get('RuleAboveLeftIndent'))
            r = fnum(st.get('RuleAboveRightIndent'))
            top = base1 - off - w
            self.css.append(f'.{cls}::before{{content:"";position:absolute;z-index:-1;left:{l}pt;right:{r}pt;'
                            f'top:{top:.2f}pt;height:{w}pt;background:{rgbcss(c)}}}')
        if st.get('RuleBelow') == 'true':
            w = fnum(st.get('RuleBelowLineWeight'), 1)
            off = fnum(st.get('RuleBelowOffset'))
            c = self.doc.rgb(st.get('RuleBelowColor', 'Color/Black'), fnum(st.get('RuleBelowTint'), -1))
            l = fnum(st.get('RuleBelowLeftIndent'))
            r = fnum(st.get('RuleBelowRightIndent'))
            # bottom baseline = bottom of last line - (lead - base1)
            bot = (lead - base1) - off - w
            self.css.append(f'.{cls}::after{{content:"";position:absolute;z-index:-1;left:{l}pt;right:{r}pt;'
                            f'bottom:{bot:.2f}pt;height:{w}pt;background:{rgbcss(c)}}}')
        info = dict(cls=cls, st=st, size=size, lead=lead, fam=fam, li=li, fi=fi,
                    sb=fnum(st.get('SpaceBefore')), sa=fnum(st.get('SpaceAfter')),
                    tabs=st.get('TabList') or [])
        self.pclass[name] = info
        return info

    def cstyle_class(self, name, pinfo):
        key = (name, pinfo['cls'])
        if key in self.cclass:
            return self.cclass[key]
        cs = self.doc.cstyle(name)
        if not cs:
            self.cclass[key] = None
            return None
        cls = 'c' + self.uid + str(len(self.cclass))
        st = dict(pinfo['st'])
        st.update(cs)
        d = []
        fam = pinfo['fam']
        if any(k in cs for k in ('AppliedFont', 'FontStyle')):
            dd, fam = self._font_decl(st)
            d += dd
        size = fnum(st.get('PointSize'), 12)
        if 'PointSize' in cs:
            d.append(f'font-size:{size}pt')
        if 'FillColor' in cs or 'FillTint' in cs:
            d.append('color:' + rgbcss(self.doc.rgb(st.get('FillColor', 'Color/Black'), fnum(st.get('FillTint'), -1)) or (0, 0, 0)))
        if 'Tracking' in cs:
            d.append(f"letter-spacing:{fnum(cs['Tracking']) / 1000:.3f}em")
        if cs.get('Capitalization') == 'AllCaps':
            d.append('text-transform:uppercase')
        elif cs.get('Capitalization') == 'Normal':
            d.append('text-transform:none')
        if cs.get('Position') == 'Superscript':
            d += ['vertical-align:0.33em', 'font-size:58.3%']
        if cs.get('Underline') == 'true':
            w = fnum(cs.get('UnderlineWeight'), 1)
            off = fnum(cs.get('UnderlineOffset'))
            tint = fnum(cs.get('UnderlineTint'), 100)
            c = self.doc.rgb(cs.get('UnderlineColor', st.get('FillColor', 'Color/Black')))
            asc, desc = METRICS[fam]
            above = -off + w / 2  # band top above baseline
            below = w / 2 + off  # band bottom below baseline
            pt_ = max(0.0, above - asc * size)
            pb_ = max(0.0, below - desc * size)
            boxh = asc * size + desc * size + pt_ + pb_
            t0 = (asc * size + pt_) - above
            t1 = t0 + w
            bg = rgbcss(c, tint / 100 if tint < 100 else None)
            d += [f'padding:{pt_:.2f}pt 0 {pb_:.2f}pt 0',
                  f'background:linear-gradient(to bottom,transparent {t0:.2f}pt,{bg} {t0:.2f}pt,{bg} {t1:.2f}pt,transparent {t1:.2f}pt)',
                  '-webkit-box-decoration-break:clone', 'box-decoration-break:clone']
            _ = boxh
        self.css.append(f'.{cls}{{{";".join(d)}}}')
        self.cclass[key] = cls
        return cls

    # ------------------------------------------------------------ content
    def rect_html(self, node, extra=''):
        """Inline image rectangle from a story."""
        from idml import bounds_of, parse_transform
        x0, y0, x1, y1 = bounds_of(node.find('Properties'), parse_transform(node.get('ItemTransform')))
        w, h = x1 - x0, y1 - y0
        img = node.find('Image')
        src = ''
        if img is not None:
            src = img.find('Link').get('LinkResourceURI').replace('file:', '').split('/')[-1]
            src = self.img_map.get(src, self.imgdir_url + src)
        sw = fnum(node.get('StrokeWeight'))
        sc = self.doc.rgb(node.get('StrokeColor', 'Swatch/None'))
        border = f'outline:{sw}pt solid {rgbcss(sc)};outline-offset:-{sw / 2}pt;' if sw and sc else ''
        return (f'<img class="qimg" src="{esc(src)}" style="width:{w:.2f}pt;height:{h:.2f}pt;{border}{extra}">', w, h)

    def runs_html(self, runs, pinfo, pagenum=None):
        out = []
        for cs, (kind, val) in runs:
            if kind == 'text':
                t = esc(val)
                t = t.replace(' ', '<br>').replace('\t', '<span class="tab"> </span>')
            elif kind == 'pagenum':
                t = esc(str(pagenum if pagenum is not None else ''))
            elif kind == 'rect':
                t, _, _ = self.rect_html(val)
                t = '<span class="aboveline">' + t + '</span>'
            else:
                t = ''
            cls = self.cstyle_class(cs, pinfo)
            out.append(f'<span class="{cls}">{t}</span>' if cls else t)
        return ''.join(out)

    @staticmethod
    def split_tabs(runs):
        """Split runs into segments at tab characters."""
        segs = [[]]
        for cs, (kind, val) in runs:
            if kind == 'text' and '\t' in val:
                parts = val.split('\t')
                for i, p in enumerate(parts):
                    if i:
                        segs.append([])
                    if p:
                        segs[-1].append((cs, ('text', p)))
            else:
                segs[-1].append((cs, (kind, val)))
        return segs

    def para_html(self, para, prev_sa=0.0, first=False, pid=None, pagenum=None, tag='div'):
        pinfo = self.pstyle_class(para['style'])
        attrs = para.get('attrs', {})
        style = []
        mt = (0 if first else prev_sa) + pinfo['sb']
        style.append(f'margin-top:{mt:.3f}pt')
        if attrs.get('SpanColumnType') == 'SpanColumns' and 'column-span' not in ''.join(self.css[-1:]):
            style.append('column-span:all')
        runs = para['runs']
        has_rect = any(k == 'rect' for _, (k, _) in runs)
        segs = self.split_tabs(runs)
        tabs = pinfo['tabs']
        if has_rect:
            # Anchored object "Above Line": the object sits above the anchor line
            parts = []
            for cs, (k, v) in runs:
                if k == 'rect':
                    t, w, h = self.rect_html(v, 'display:block;')
                    parts.append(t)
            body = ''.join(parts) + '<span class="anchorline">​</span>'
            style.append('text-indent:0')
        elif any(k == 'rtab' for _, (k, _) in runs):
            i = next(i for i, (_, (k, _)) in enumerate(runs) if k == 'rtab')
            body = (f'<span style="float:right;text-indent:0">{self.runs_html(runs[i + 1:], pinfo, pagenum)}</span>'
                    + self.runs_html(runs[:i], pinfo, pagenum))
        elif len(segs) == 1:
            body = self.runs_html(runs, pinfo, pagenum)
        elif len(segs) == 2 and pinfo['fi'] < 0 and tabs:
            start = pinfo['li'] + pinfo['fi']
            stop = next((p for a, p in tabs if p > start + 0.1), pinfo['li'])
            w = stop - start
            body = (f'<span class="hang" style="width:{w:.2f}pt">{self.runs_html(segs[0], pinfo, pagenum)}</span>'
                    + self.runs_html(segs[1], pinfo, pagenum))
        elif len(segs) >= 3 and tabs and len(tabs) >= len(segs) - 1:
            # tabbed row -> flex with positioned cells
            cells = []
            start = pinfo['li'] + pinfo['fi']
            prev_kind = None
            for i, sg in enumerate(segs):
                content = self.runs_html(sg, pinfo, pagenum)
                if i == 0:
                    if tabs[0][0] == 'LeftAlign':
                        cells.append(f'<span class="tc" style="width:{tabs[0][1] - start:.2f}pt">{content}</span>')
                    else:
                        cells.append(f'<span class="tc">{content}</span>')
                    prev_kind = 'fixed'
                    continue
                a_, p = tabs[i - 1]
                nxt = tabs[i] if i < len(segs) - 1 else None
                if a_ == 'LeftAlign':
                    if nxt is not None and nxt[0] == 'LeftAlign':
                        cells.append(f'<span class="tc" style="width:{nxt[1] - p:.2f}pt">{content}</span>')
                        prev_kind = 'fixed'
                    else:
                        cells.append(f'<span class="tc grow">{content}</span>')
                        prev_kind = 'grow'
                else:
                    if prev_kind == 'grow':
                        cells.append(f'<span class="tc r">{content}</span>')
                    else:
                        cells.append(f'<span class="tc r" style="width:{p - tabs[i - 2][1]:.2f}pt">{content}</span>')
                    prev_kind = 'right'
            last = tabs[len(segs) - 2][1]
            W = getattr(self, 'cur_width', None)
            if W and tabs[len(segs) - 2][0] == 'RightAlign' and W - pinfo['li'] > last:
                cells.append(f'<span class="tc" style="width:{W - last - pinfo["li"]:.2f}pt"></span>')
            body = '<span class="tabrow">' + ''.join(cells) + '</span>'
            style.append('text-indent:0')
        else:
            body = self.runs_html(runs, pinfo, pagenum)
        idattr = f' id="{pid}"' if pid else ''
        if not body.strip() and not has_rect:
            body = '​'
        return f'<{tag} class="pp {pinfo["cls"]}"{idattr} style="{";".join(style)}">{body}</{tag}>', pinfo['sa']

    def story_html(self, sid, pagenum=None, anchor=None):
        out = []
        prev = 0.0
        for i, p in enumerate(self.doc.story(sid)):
            pid = anchor(p, i) if anchor else None
            h, prev = self.para_html(p, prev, first=(i == 0), pid=pid, pagenum=pagenum)
            out.append(h)
        return '\n'.join(out)
