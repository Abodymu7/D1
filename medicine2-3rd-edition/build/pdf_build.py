"""Cloud PDF build (no InDesign): renders a chapter part with WeasyPrint using the engine's
design (A4, 2 columns, opener spread, answers after each set, linked Q<->A, running heads, thumb tab).

  python build/pdf_build.py git [--start 8]
Output: output/parts/NN-<ch>.pdf + output/parts/<ch>.json (page map, same keys as the InDesign build)
"""
import json, math, os, re, sys, html, random
import weasyprint

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import gen  # engine generator: ordering, bank labels, index entries

FONTS = '/home/claude/fonts'
book = gen.book
args = sys.argv[1:]
cid = args[0] if args and not args[0].startswith('--') else book['chapters'][0]['id']
START = int(args[args.index('--start') + 1]) if '--start' in args else 8
ch = next(c for c in book['chapters'] if c['id'] == cid)
ACC = '#' + ch['color']
INK, INK2, MUTED, LINE, MIST, GOLD = '#0E1726', '#1B2A41', '#667085', '#D0D5DD', '#F2F4F7', '#E8B64C'
PARTS = os.path.join(ROOT, 'output', 'parts')
os.makedirs(PARTS, exist_ok=True)
NAME = '%02d-%s' % (ch['order'], cid)


def ff(family, path_glob, weight, style='normal'):
    return "@font-face{font-family:'%s';src:url('file://%s');font-weight:%s;font-style:%s}" % (family, path_glob, weight, style)


def fontcss():
    out = []
    for w in (400, 600, 700):
        for st in ('normal', 'italic'):
            out.append(ff('SSerif', '%s/fontsource-source-serif-4-5.3.0/files/source-serif-4-latin-%d-%s.woff2' % (FONTS, w, st), w, st))
    for w in (400, 600, 700):
        for st in ('normal', 'italic'):
            out.append(ff('SSans', '%s/fontsource-source-sans-3-5.3.0/files/source-sans-3-latin-%d-%s.woff2' % (FONTS, w, st), w, st))
    for w in (500, 600, 700, 800, 900):
        out.append(ff('Disp', '%s/fontsource-barlow-condensed-5.3.0/files/barlow-condensed-latin-%d-normal.woff2' % (FONTS, w), w))
    for w in (500, 600, 700):
        out.append(ff('DispS', '%s/fontsource-barlow-semi-condensed-5.3.0/files/barlow-semi-condensed-latin-%d-normal.woff2' % (FONTS, w), w))
    return '\n'.join(out)


def t(s):
    """escape + typographic fixes; superscript powers."""
    s = html.escape(s or '')
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    s = s.replace('10⁹', '10<sup>9</sup>').replace('10¹²', '10<sup>12</sup>')
    return s


# ------------------------------------------------------------------ page chrome (SVG backgrounds)
def svg_bg(side):
    W, H = 210, 297
    tab_h, tab_y = 27, 30 + (ch['order'] - 1) * 29
    if side == 'left':
        hl = (17, 191)
        tab = '<rect x="0" y="%d" width="7" height="%d" fill="%s"/>' % (tab_y, tab_h, ACC)
        chip = '<rect x="17" y="282.2" width="12" height="6.2" fill="%s"/>' % ACC
    else:
        hl = (19, 193)
        tab = '<rect x="203" y="%d" width="7" height="%d" fill="%s"/>' % (tab_y, tab_h, ACC)
        chip = '<rect x="181" y="282.2" width="12" height="6.2" fill="%s"/>' % ACC
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="210mm" height="297mm" viewBox="0 0 210 297">'
           '<line x1="%s" y1="14.2" x2="%s" y2="14.2" stroke="%s" stroke-width="0.18"/>%s</svg>') % (hl[0], hl[1], LINE, tab)
    p = os.path.join(HERE, 'out', 'bg-%s-%s.svg' % (cid, side))
    open(p, 'w').write(svg)
    return p


def divider_svg():
    """Abstract duotone divider: ink -> chapter colour with looping 'bowel' curves."""
    random.seed(7)
    W, H = 216, 303
    paths = []
    for k in range(34):
        y0 = 20 + k * 8.2
        amp = 6 + 10 * math.sin(k / 5.0) ** 2
        freq = 0.035 + 0.012 * math.sin(k / 3.0)
        ph = k * 0.55
        pts = []
        for i in range(0, 221, 3):
            x = i - 2
            y = y0 + amp * math.sin(freq * x * 2 * math.pi / 1.0 * 0.16 + ph) + 3 * math.sin(x / 11.0 + k)
            pts.append('%.1f,%.1f' % (x, y))
        op = 0.10 + 0.22 * (k / 34.0)
        paths.append('<polyline points="%s" fill="none" stroke="#FFFFFF" stroke-opacity="%.2f" stroke-width="%.2f"/>' % (' '.join(pts), op, 0.35 + 0.5 * (k % 3 == 0)))
    circles = []
    for _ in range(26):
        cx, cy, r = random.uniform(10, 206), random.uniform(150, 290), random.uniform(1.5, 9)
        circles.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" stroke-opacity="0.45" stroke-width="0.4"/>' % (cx, cy, r, GOLD))
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="216mm" height="303mm" viewBox="0 0 216 303">'
           '<defs><linearGradient id="g" x1="0" y1="0" x2="0.35" y2="1"><stop offset="0" stop-color="%s"/><stop offset="0.55" stop-color="%s"/>'
           '<stop offset="1" stop-color="%s"/></linearGradient>'
           '<linearGradient id="f" x1="0" y1="0" x2="0" y2="1"><stop offset="0.55" stop-color="%s" stop-opacity="0"/><stop offset="1" stop-color="%s" stop-opacity="0.85"/></linearGradient></defs>'
           '<rect width="216" height="303" fill="url(#g)"/>%s%s<rect width="216" height="303" fill="url(#f)"/></svg>') % (
        INK, INK2, ACC, INK, INK, ''.join(paths), ''.join(circles))
    p = os.path.join(ROOT, 'assets', 'dividers', '%s.svg' % cid)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w').write(svg)
    return p


# ------------------------------------------------------------------ content
def build_html():
    qs = gen.chapter_questions(cid)
    banks = {}
    for q in qs:
        banks.setdefault((q['bank'], q['type']), []).append(q)
    body, bank_list, topics = [], [], []
    qn = 0
    for (bank, typ), items in banks.items():
        n_units = sum(1 if q['type'] == 'MCQ' else len(q['items']) for q in items)
        label = '%s %s' % (bank, 'EMQs' if typ == 'EMQ' else 'MCQs')
        bid = 'bank-%s-%s' % (re.sub(r'[^a-z]+', '-', bank.lower()).strip('-'), typ.lower())
        bank_list.append((bid, label, n_units))
        sets, cur, count = [], [], 0
        for q in items:
            size = 1 if q['type'] == 'MCQ' else len(q['items'])
            if cur and count + size > gen.SET_SIZE and typ == 'MCQ':
                sets.append(cur); cur, count = [], 0
            cur.append(q); count += size
        if cur:
            sets.append(cur)
        body.append('<p class="bk">%d %s &nbsp;•&nbsp; %s</p>' % (n_units, 'EMQ ITEMS' if typ == 'EMQ' else 'QUESTIONS', t(gen.BANK_BLURB.get(bank, '')).upper()))
        body.append('<h2 class="bh" id="%s">%s</h2>' % (bid, t(label)))
        for si, s in enumerate(sets):
            first = qn + 1
            body.append('<div class="flow">')
            if len(sets) > 1:
                body.append('<p class="sh">Set %d of %d</p>' % (si + 1, len(sets)))
            for q in s:
                for tp in q.get('topics', []):
                    if tp not in topics:
                        topics.append(tp)
                if q['type'] == 'MCQ':
                    qn += 1; q['_n'] = qn
                    opts = ''.join('<li%s><span class="ol">%s</span>%s</li>' % (' class="last"' if i == len(q['options']) - 1 else '', chr(65 + i), t(o))
                                   for i, o in enumerate(q['options']))
                    body.append('<div class="q"><p class="qs" id="q-%d"><a class="qn" href="#a-%d">%d</a>%s</p><ul class="opts">%s</ul></div>' % (qn, qn, qn, t(q['stem']), opts))
                else:
                    letters = q['option_letters']
                    opts = ''.join('<li><span class="ol">%s</span>%s</li>' % (letters[i], t(o)) for i, o in enumerate(q['options']))
                    blk = ['<div class="emq"><p class="et"><span>THEME</span>%s</p><ul class="eo">%s</ul>' % (t(q['theme']), opts),
                           '<p class="el">For each scenario, choose the single most appropriate option. Each option may be used once, more than once or not at all.</p>']
                    for it in q['items']:
                        qn += 1; it['_n'] = qn
                        blk.append('<p class="qs ei" id="q-%d"><a class="qn" href="#a-%d">%d</a>%s</p>' % (qn, qn, qn, t(it['stem'])))
                    blk.append('</div>')
                    body.append(''.join(blk))
            body.append('</div>')
            last = qn
            head = 'Answers&nbsp; %d–%d' % (first, last) if last > first else 'Answer&nbsp; %d' % first
            body.append('<h3 class="ah"><span>%s</span><span class="ahb">%s</span></h3><div class="flow ans">' % (head, t(label)))
            for q in s:
                if q['type'] == 'MCQ':
                    recs = [(q['_n'], q['answer'], q['options'][ord(q['answer']) - 65], q['explanation'])]
                else:
                    L = q['option_letters']
                    recs = [(it['_n'], it['answer'], q['options'][L.index(it['answer'])], it['explanation']) for it in q['items']]
                for n, L, opt, ex in recs:
                    body.append('<p class="an" id="a-%d"><a class="anum" href="#q-%d">%d</a><span class="chip">%s</span> <span class="aopt">%s</span> — %s</p>' % (n, n, n, L, t(opt), t(ex)))
            body.append('</div>')
    return body, bank_list, topics, qn, qs


def main():
    body, bank_list, topics, total, qs = build_html()
    n_mcq = sum(1 for q in qs if q['type'] == 'MCQ')
    n_emq = sum(len(q['items']) for q in qs if q['type'] == 'EMQ')
    n_th = sum(1 for q in qs if q['type'] == 'EMQ')
    bgL, bgR = svg_bg('left'), svg_bg('right')
    div = divider_svg()
    part = t(ch['part']).upper()
    title = t(ch['title'])
    hy = list(dict.fromkeys(q['topics'][0] for q in qs if q.get('topics')))[:24]
    stats = [(total, 'questions'), (n_mcq, 'single best answers'), (n_emq, 'EMQ items'), (n_th, 'EMQ themes')]
    css = fontcss() + '''
@page { size: 210mm 297mm; margin: 21mm 17mm 20mm 19mm; }
@page :left  { margin: 21mm 19mm 20mm 17mm; background: url('file://%(bgL)s') no-repeat -17mm -21mm / 210mm 297mm;
  @top-left { content: "%(part)s  /  %(titleU)s"; font: 600 6.8pt DispS; letter-spacing: 0.12em; color: %(muted)s; vertical-align: bottom; padding-bottom: 2.3mm; width: 150mm }
  @bottom-left { content: counter(page); font: 700 9pt Disp; color: #fff; width: 12mm; height: 6.2mm; text-align: center; vertical-align: middle; margin: 5.2mm 0 8.6mm; background: %(acc)s } }
@page :right { background: url('file://%(bgR)s') no-repeat -19mm -21mm / 210mm 297mm;
  @top-right { content: string(bank); font: 600 6.8pt DispS; letter-spacing: 0.12em; text-transform: uppercase; color: %(muted)s; vertical-align: bottom; padding-bottom: 2.3mm; width: 150mm; text-align: right }
  @bottom-right { content: counter(page); font: 700 9pt Disp; color: #fff; width: 12mm; height: 6.2mm; text-align: center; vertical-align: middle; margin: 5.2mm 0 8.6mm; background: %(acc)s } }
@page divider { margin: 0; counter-reset: page %(start)d; background: url('file://%(div)s') no-repeat -3mm -3mm / 216mm 303mm;
  @top-left { content: none } @bottom-left { content: none } @top-right { content: none } @bottom-right { content: none } }
@page opener { background: none; @top-right { content: none } @bottom-right { content: none } @top-left { content: none } @bottom-left { content: none } }
@page notes { @top-right { content: "NOTES" } }
html { break-before: left; }
body { margin: 0; font: 8.9pt/11.8pt SSerif; color: %(ink)s; hyphens: auto; }
a { color: inherit; text-decoration: none; }
.divider { page: divider; height: 297mm; position: relative; color: #fff; }
.divider .num { position: absolute; left: 17mm; top: 26mm; font: 900 150pt/1 Disp; color: #fff; opacity: .93; letter-spacing: -2pt }
.divider .dk { position: absolute; left: 18mm; top: 22mm; font: 600 8pt DispS; letter-spacing: .2em; color: %(gold)s }
.divider .dt { position: absolute; left: 17mm; right: 22mm; bottom: 34mm; font: 800 40pt/40pt Disp; text-transform: uppercase; color: #fff }
.divider .dr { position: absolute; left: 17mm; width: 38mm; bottom: 28mm; height: 1.6mm; background: %(acc)s }
.divider .cr { position: absolute; left: 17mm; bottom: 14mm; font: 400 6.5pt SSans; color: rgba(255,255,255,.65) }
.opener { page: opener; break-before: right; height: 250mm; position: relative }
.opener .kick { font: 600 8pt DispS; letter-spacing: .2em; color: %(acc)s; margin: 6mm 0 3mm }
.opener h1 { font: 800 44pt/42pt Disp; text-transform: uppercase; margin: 0 0 6mm; color: %(ink)s; bookmark-level: 1; bookmark-label: "%(order)02d  %(title_plain)s" }
.opener .rule { width: 38mm; height: 1.6mm; background: %(acc)s; margin-bottom: 7mm }
.opener .intro { font: 400 11pt/15pt SSerif; color: %(ink2)s; margin: 0 0 9mm; width: 150mm }
.stats { display: flex; border-top: .6pt solid %(line)s; border-bottom: .6pt solid %(line)s; padding: 4mm 0; margin-bottom: 9mm }
.stats div { flex: 1; } .stats b { display: block; font: 800 28pt/1 Disp; color: %(acc)s } .stats span { font: 600 7pt DispS; letter-spacing: .12em; text-transform: uppercase; color: %(muted)s }
.oh { font: 600 7.5pt DispS; letter-spacing: .16em; color: %(acc)s; margin: 0 0 2.5mm; text-transform: uppercase }
.toc { margin: 0 0 9mm; padding: 0; list-style: none }
.toc li { font: 700 13pt/1.25 Disp; border-bottom: .5pt solid %(line)s; padding: 2mm 0; display: flex }
.toc li a { flex: 1 } .toc li .c { font: 400 9pt SSans; color: %(muted)s; margin-right: 6mm } .toc li .p::after { content: target-counter(attr(href), page); font: 700 13pt Disp; color: %(acc)s }
.hy { columns: 2; column-gap: 8mm; margin: 0; padding: 0; list-style: none }
.hy li { font: 400 9pt/1.35 SSans; color: %(ink2)s; padding: .7mm 0 .7mm 4mm; position: relative }
.hy li::before { content: ""; position: absolute; left: 0; top: 2.4mm; width: 1.6mm; height: 1.6mm; background: %(acc)s }
.bk { font: 600 7pt/9pt DispS; letter-spacing: .14em; color: %(acc)s; margin: 9mm 0 1mm; break-after: avoid }
.content > .bk:first-child { margin-top: 0 }
.bh { font: 700 24pt/25pt Disp; color: %(ink)s; margin: 0 0 5.5mm; padding-bottom: 2.4mm; break-after: avoid; string-set: bank content(); bookmark-level: 2;
      position: relative }
.bh::after { content: ""; position: absolute; left: 0; bottom: 0; width: 24mm; height: .8mm; background: %(acc)s }
.flow { columns: 2; column-gap: 6mm; column-fill: auto }
.content { break-before: left }
.sh { font: 600 7.5pt DispS; letter-spacing: .12em; text-transform: uppercase; color: %(acc)s; margin: 3mm 0 1mm }
.q { break-inside: avoid; margin: 0 0 3mm }
.qs { margin: 3.4mm 0 1mm; padding-left: 7.5mm; text-indent: -7.5mm; orphans: 2; widows: 2 }
.q .qs { margin-top: 0 }
.qn { display: inline-block; width: 7.5mm; text-indent: 0; font: 700 10.5pt Disp; color: %(acc)s }
.opts, .eo { list-style: none; margin: 0; padding: 0 }
.opts li { font: 400 8.5pt/10.6pt SSans; color: %(ink2)s; padding-left: 12.5mm; text-indent: -5mm; margin-bottom: .35mm; hyphens: manual }
.opts li.last { margin-bottom: 1.2mm }
.ol { display: inline-block; width: 5mm; text-indent: 0; font: 600 8.2pt DispS; color: %(acc)s }
.emq { margin: 0 0 3mm }
.et { break-after: avoid; background: %(acc)s; color: #fff; font: 700 10pt/12pt Disp; padding: 1.6mm 2mm 1.4mm; margin: 6mm 0 2.2mm; }
.emq:first-child .et { margin-top: 0 }
.et span { display: inline-block; width: 13mm; font: 600 7pt DispS; letter-spacing: .14em; opacity: .85 }
.eo { background: %(acc9)s; padding: 1.4mm 2mm; margin-bottom: 2.6mm; break-inside: avoid }
.eo li { font: 400 8.4pt/10.8pt SSans; padding-left: 6mm; text-indent: -6mm; hyphens: manual }
.eo .ol { width: 6mm }
.el { font: italic 400 8pt/10pt SSerif; color: %(muted)s; margin: 0 0 .5mm; break-after: avoid }
.ei { break-inside: avoid }
.ah { column-span: all; display: flex; justify-content: space-between; align-items: baseline; font: 700 14pt/16pt Disp; color: %(acc)s;
      border-top: .8pt solid %(acc)s; padding-top: 3.2mm; margin: 8mm 0 3mm; break-after: avoid }
.ah { bookmark-level: none } .ah > span:first-child { bookmark-level: 3; bookmark-label: content(text) }
.ahb { font: 600 7.5pt DispS; letter-spacing: .1em; text-transform: uppercase; color: %(muted)s }
.an { font: 400 8.3pt/10.7pt SSans; padding-left: 7.5mm; text-indent: -7.5mm; margin: 0 0 1.9mm; orphans: 2; widows: 2 }
.anum { display: inline-block; width: 7.5mm; text-indent: 0; font: 700 9.5pt Disp; color: %(ink)s }
.chip { display: inline-block; text-indent: 0; background: %(acc)s; color: #fff; font: 700 8pt/1 Disp; padding: .5mm 1.1mm .4mm; border-radius: .4mm }
.aopt { font-weight: 600; color: %(acc)s }
sup { font-size: 70%%; line-height: 0 }
.notes { page: notes; break-before: page; }
.notes h4 { font: 700 24pt Disp; color: %(ink)s; margin: 0 0 6mm }
.notes .ln { height: 9mm; border-bottom: .5pt solid %(line)s }
''' % dict(bgL=bgL, bgR=bgR, div=div, part=part, titleU=title.upper().replace('&AMP;', '&'), muted=MUTED, ink=INK, ink2=INK2, line=LINE, gold=GOLD,
           acc=ACC, acc9=tint(ch['color'], 0.09), start0=START - 1, start=START, order=ch['order'], title_plain=ch['title'])

    toc = ''.join('<li><a href="#%s">%s</a><span class="c">%d</span><a class="p" href="#%s"></a></li>' % (b, t(l), n, b) for b, l, n in bank_list)
    hyl = ''.join('<li>%s</li>' % t(x) for x in hy)
    statsh = ''.join('<div><b>%d</b><span>%s</span></div>' % s for s in stats)
    doc = '''<!doctype html><html><head><meta charset="utf-8"><title>%(ttl)s</title><style>%(css)s</style></head><body>
<section class="divider"><div class="dk">%(part)s</div><div class="num">%(order)02d</div><div class="dt">%(title)s</div><div class="dr"></div>
<div class="cr">Artwork: generated for this edition</div></section>
<section class="opener"><p class="kick">CHAPTER %(order)02d &nbsp;/&nbsp; %(part)s</p><h1>%(title)s</h1><div class="rule"></div>
<p class="intro">%(intro)s</p><div class="stats">%(stats)s</div>
<p class="oh">In this chapter</p><ul class="toc">%(toc)s</ul>
<p class="oh">High-yield topics</p><ul class="hy">%(hy)s</ul></section>
<section class="content">%(body)s</section>
%%(notes)s
</body></html>''' % dict(ttl=t(book['title'] + ' — ' + ch['title']), css=css, part=part, order=ch['order'], title=title, intro=t(ch.get('intro', '')),
                         stats=statsh, toc=toc, hy=hyl, body='\n'.join(body))
    notes = '<section class="notes"><h4>Notes</h4>' + '<div class="ln"></div>' * 26 + '</section>'
    out_pdf = os.path.join(PARTS, NAME + '.pdf')
    rendered = weasyprint.HTML(string=doc.replace('%(notes)s', ''), base_url=ROOT).render()
    if len(rendered.pages) % 2:          # parts end on a right-hand page
        rendered = weasyprint.HTML(string=doc.replace('%(notes)s', notes), base_url=ROOT).render()
    rendered.metadata.title = '%s — %s' % (book['title'], ch['title'])
    rendered.metadata.authors = book.get('authors', [])
    rendered.write_pdf(out_pdf)
    open(os.path.join(HERE, 'out', NAME + '.html'), 'w', encoding='utf-8').write(doc.replace('%(notes)s', ''))
    print('pdf', out_pdf, 'pages', len(rendered.pages), 'start', START, 'end', START + len(rendered.pages) - 1)
    where = {}
    for i, pg in enumerate(rendered.pages):
        for k in pg.anchors:
            where.setdefault(k, START + i)
    json.dump(dict(part=cid, start=START, end=START + len(rendered.pages) - 1, pages=len(rendered.pages),
                   banks=[dict(key=b, title=l, count=n, page=where.get(b)) for b, l, n in bank_list], questions=total,
                   anchors=where),
              open(os.path.join(PARTS, cid + '.json'), 'w'), indent=1)


def tint(hexc, a):
    r, g, b = int(hexc[0:2], 16), int(hexc[2:4], 16), int(hexc[4:6], 16)
    mix = lambda c: round(255 - (255 - c) * a)
    return '#%02X%02X%02X' % (mix(r), mix(g), mix(b))


if __name__ == '__main__':
    main()
