"""Page-level HTML builders: absolutely positioned pages, story flow, master overlays."""
import collections
import os

from idml import Doc, fnum
from render import Renderer, rgbcss, esc

PAGE_W = 595.2756
PAGE_H = 841.8898


def font_faces(fontdir):
    """@font-face rules for the static instances made by mkfonts.py (fontdir/static)."""
    f = fontdir.rstrip('/') + '/static/'
    out = []
    for w in (300, 400, 500, 600, 700):
        for it in ('', '-Italic'):
            out.append(f"@font-face{{font-family:'Source Serif 4';src:url('{f}Serif-{w}{it}.ttf');font-weight:{w};"
                       f"font-style:{'italic' if it else 'normal'}}}")
    for w in (400, 600, 700):
        for it in ('', '-Italic'):
            out.append(f"@font-face{{font-family:'Source Sans 3';src:url('{f}Sans-{w}{it}.ttf');font-weight:{w};"
                       f"font-style:{'italic' if it else 'normal'}}}")
    for wd in (62, 75, 100):
        for w in (300, 400, 500, 600, 700, 800, 900):
            out.append(f"@font-face{{font-family:'Archivo';src:url('{f}Archivo-{wd}-{w}.ttf');font-weight:{w};"
                       f"font-stretch:{wd}%;font-style:normal}}")
        for w in (400, 700):
            out.append(f"@font-face{{font-family:'Archivo';src:url('{f}Archivo-{wd}-{w}-Italic.ttf');font-weight:{w};"
                       f"font-stretch:{wd}%;font-style:italic}}")
    return '\n'.join(out) + '\n'


BASE_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
html,body{-webkit-print-color-adjust:exact;print-color-adjust:exact}
body{font-family:'Source Serif 4';font-optical-sizing:auto;font-kerning:normal;text-rendering:geometricPrecision}
.pp{position:relative;white-space:pre-wrap;overflow-wrap:break-word;z-index:0}
.hang{display:inline-block;text-indent:0;white-space:nowrap;vertical-align:baseline}
.tabrow{display:flex;align-items:baseline;width:100%}
.tc{display:inline-block;white-space:pre-wrap;flex:none}
.tc.grow{flex:1 1 auto;min-width:0}
.tc.r{text-align:right}
.qimg{display:block}
.anchorline{display:inline}
.page{position:relative;width:595.2756pt;height:841.8898pt;overflow:hidden;break-after:page;page-break-after:always}
.page:last-child{break-after:auto}
.it{position:absolute}
.frame{position:absolute;display:flex;flex-direction:column}
.frame.vj-TopAlign{justify-content:flex-start}
.frame.vj-BottomAlign{justify-content:flex-end}
.frame.vj-CenterAlign{justify-content:center}
.frame>.inner{width:100%}
"""


class Section:
    def __init__(self, path, img_map=None):
        self.doc = Doc(path)
        self.key = os.path.basename(path).split('.')[0]
        self.short = self.key.split('-', 1)[1]
        self.r = Renderer(self.doc, img_map=img_map)
        d = self.doc
        cnt = collections.Counter(it['story'] for sp in d.spreads for it in sp['items'] if it['tag'] == 'TextFrame')
        self.main = cnt.most_common(1)[0][0]
        self.pre_pages = []  # (page, items)
        self.story_pages = []
        for sp in d.spreads:
            for p in sp['pages']:
                its = [it for it in sp['items'] if it['page'] == p['self_']]
                if any(it['tag'] == 'TextFrame' and it['story'] == self.main for it in its):
                    self.story_pages.append((p, its))
                else:
                    self.pre_pages.append((p, its))
        # normalise generator quirks: items placed for the facing page
        for p, its in self.pre_pages + self.story_pages:
            for it in its:
                if it['x'] + it['w'] <= 1:
                    it['x'] += p['w']
                elif it['x'] >= p['w'] - 1:
                    it['x'] -= p['w']
        sp0, its0 = self.story_pages[0]
        stray = [it for it in its0 if not (it['tag'] == 'TextFrame' and it['story'] == self.main)]
        if stray:
            empty = [i for i, (p, its) in enumerate(self.pre_pages) if not its]
            if empty:
                p, _ = self.pre_pages[empty[-1]]
                self.pre_pages[empty[-1]] = (p, stray)
                self.story_pages[0] = (sp0, [it for it in its0 if it not in stray])
        # main-story master
        self.story_master = self.story_pages[0][0]['master']

    # ---------------------------------------------------------------- items
    def item_html(self, it, pagenum=None):
        d = self.doc
        x, y, w, h = it['x'], it['y'], it['w'], it['h']
        box = f'left:{x:.2f}pt;top:{y:.2f}pt;width:{w:.2f}pt;height:{h:.2f}pt'
        if it['tag'] == 'Rectangle':
            fill = d.rgb(it.get('fill', 'Swatch/None'), it.get('tint') if it.get('tint', -1) >= 0 else None)
            st = [box]
            if fill:
                st.append('background:' + rgbcss(fill))
            if it.get('sw') and d.rgb(it.get('stroke', 'Swatch/None')):
                st.append(f"outline:{it['sw']}pt solid {rgbcss(d.rgb(it['stroke']))};outline-offset:-{it['sw'] / 2}pt")
            inner = ''
            if it.get('image'):
                a, b, c, dd, e, f = it['imgt']
                gb = it['gb']
                iw = (gb['Right'] - gb['Left']) * a
                ih = (gb['Bottom'] - gb['Top']) * dd
                ix = e + gb['Left'] * a
                iy = f + gb['Top'] * dd
                # image position relative to the rectangle's spread bounds
                rx0 = it['x'] + 0  # page-relative
                # spread->page offset is the same for rect & image: use difference in spread space
                sx0 = it['t'][4]
                sy0 = it['t'][5]
                # rect spread bounds
                from idml import bounds_of
                bx0, by0, _, _ = bounds_of(it['el'].find('Properties'), it['t'])
                name = it['image'].split('/')[-1]
                src = self.r.img_map.get(name, 'Links/' + name)
                inner = (f'<img src="{esc(src)}" style="position:absolute;left:{ix - bx0:.2f}pt;top:{iy - by0:.2f}pt;'
                         f'width:{iw:.2f}pt;height:{ih:.2f}pt">')
                st.append('overflow:hidden')
            return f'<div class="it" style="{";".join(st)}">{inner}</div>'
        if it['tag'] == 'GraphicLine':
            col = d.rgb(it.get('stroke', 'Swatch/None'))
            if not col:
                return ''
            sw = it.get('sw') or 1
            if h < 0.01:
                return f'<div class="it" style="left:{x:.2f}pt;top:{y - sw / 2:.2f}pt;width:{w:.2f}pt;height:{sw}pt;background:{rgbcss(col)}"></div>'
            return f'<div class="it" style="left:{x - sw / 2:.2f}pt;top:{y:.2f}pt;width:{sw}pt;height:{h:.2f}pt;background:{rgbcss(col)}"></div>'
        if it['tag'] == 'TextFrame':
            fill = d.rgb(it['el'].get('FillColor', 'Swatch/None'))
            self.r.cur_width = w
            body = self.r.story_html(it['story'], pagenum=pagenum)
            bg = f';background:{rgbcss(fill)}' if fill else ''
            return f'<div class="frame vj-{it["vj"]}" style="{box}{bg}"><div class="inner">{body}</div></div>'
        return ''

    def master_items(self, master_id, side):
        """side: 0 = left page, 1 = right page."""
        if not master_id or master_id == 'n' or master_id not in self.doc.masters:
            return []
        m = self.doc.masters[master_id]
        pages = m['pages']
        pg = pages[side] if len(pages) > 1 else pages[0]
        return [it for it in m['items'] if it['page'] == pg['self_']]

    def abs_page(self, page, items, pagenum, side, master=None, extra=''):
        mid = master if master is not None else page['master']
        out = [self.item_html(it, pagenum) for it in self.master_items(mid, side)]
        out += [self.item_html(it, pagenum) for it in items]
        return f'<div class="page">{"".join(out)}{extra}</div>'

    def overlay_page(self, pagenum, side, master=None):
        mid = master or self.story_master
        out = [self.item_html(it, pagenum) for it in self.master_items(mid, side)]
        return f'<div class="page">{"".join(out)}</div>'


def story_document(sec, fontdir, first_side, anchor_fn=None, extra_css=''):
    """HTML for the main story flow. first_side: 0 = story starts on a left page, 1 = right.
    Returns (html, anchors) where anchors is a list of element ids (for page lookup)."""
    pages = sec.story_pages
    geo = {}
    for p, its in pages:
        for it in its:
            if it['tag'] == 'TextFrame' and it['story'] == sec.main:
                side = 0 if it['x'] < 50.5 else 1
                geo[side] = it
    g0 = geo.get(0) or geo.get(1)
    g1 = geo.get(1) or geo.get(0)
    top = g0['y']
    bottom = PAGE_H - g0['y'] - g0['h']
    cols = g0['cols']
    gutter = g0['gutter']
    anchors = []

    def anchor(p, i):
        if anchor_fn:
            a = anchor_fn(p, i)
            if a:
                anchors.append(a)
                return a
        return None

    sec.r.cur_width = (g0['w'] - gutter) / 2
    body = sec.r.story_html(sec.main, anchor=anchor)
    css = f"""
@page{{size:{PAGE_W}pt {PAGE_H}pt;margin:{top}pt 0 {bottom}pt 0}}
@page :left{{margin-left:{g0['x']}pt;margin-right:{PAGE_W - g0['x'] - g0['w']}pt}}
@page :right{{margin-left:{g1['x']}pt;margin-right:{PAGE_W - g1['x'] - g1['w']}pt}}
.flow{{column-count:{cols};column-gap:{gutter}pt;column-fill:auto}}
.dummy{{break-after:page;height:10pt}}
.linkpage{{break-before:page;font-size:2pt;line-height:2.4pt;column-span:all}}
{extra_css}
"""
    dummy = '<div class="dummy"></div>' if first_side == 0 else ''
    links = ''.join(f'<a href="#{a}">.</a> ' for a in anchors)
    html = (f'<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><style>{font_faces(fontdir)}{BASE_CSS}{css}'
            f'{"".join(sec.r.css)}</style></head><body>{dummy}<div class="flow">{body}</div>'
            f'<div class="linkpage">{links}</div></body></html>')
    return html, anchors
