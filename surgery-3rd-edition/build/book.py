"""Whole-book PDF build (WeasyPrint, no InDesign): front matter, 19 chapters (divider + opener +
Essentials at a glance + question banks with answers after every set), index, back cover.

  python build/book.py [--only cad,hf] [--html]
Output: output/<file_name>.pdf  (+ output/book.html, output/pagemap.json)

One HTML document so that every cross-reference (contents, opener lists, question<->answer, index) is a
live link and page numbers come from target-counter().
"""
import collections, html, json, math, os, re, sys, time
import weasyprint

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import gen

book = gen.book
Q = gen.questions
BYID = {q['id']: q for q in Q}
ESS = json.load(open(os.path.join(ROOT, 'data', 'essentials.json'), encoding='utf-8'))
OUT = os.path.join(ROOT, 'output')
TMP = os.path.join(HERE, 'out')
os.makedirs(OUT, exist_ok=True); os.makedirs(TMP, exist_ok=True)
args = sys.argv[1:]
ONLY = args[args.index('--only') + 1].split(',') if '--only' in args else None

INK, INK2, MUTED, LINE, MIST, GOLD, HL = '#0E1726', '#1B2A41', '#667085', '#D0D5DD', '#F2F4F7', '#E8B64C', '#FFF3CD'
F = '/home/claude/fonts'
B39 = '39 Blocks Questions'
CH = [c for c in book['chapters'] if not ONLY or c['id'] in ONLY]
PARTS = list(dict.fromkeys(c['part'] for c in book['chapters']))
BANK_SHORT = {B39: '39 Blocks', 'Formative & Previous Years': 'Formative & Previous', 'End-Block Exams': 'End-Block 2025'}


# ------------------------------------------------------------------ helpers
def t(s):
    s = html.escape(s or '', quote=False)
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    s = s.replace('⁺', '<sup>+</sup>').replace('⁻', '<sup>−</sup>')
    s = re.sub(r'\b(SpO|PaO|PaCO|FiO|SaO|PAO|PvO|CO|O|PO|PCO|ScvO|pCO|pO)2\b', r'\1<sub>2</sub>', s)
    s = re.sub(r'\b(FEV)1\b', r'\1<sub>1</sub>', s)
    s = re.sub(r'\bHCO3(−|-)?', lambda m: 'HCO<sub>3</sub>' + ('<sup>−</sup>' if m.group(1) else ''), s)
    s = re.sub(r'10\^?(\d+)/L', r'10<sup>\1</sup>/L', s)
    return s


def tint(hexc, a):
    hexc = hexc.lstrip('#')
    r, g, b = int(hexc[0:2], 16), int(hexc[2:4], 16), int(hexc[4:6], 16)
    mix = lambda c: round(255 - (255 - c) * a)
    return '#%02X%02X%02X' % (mix(r), mix(g), mix(b))


def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


def fontcss():
    fs = []
    def ff(fam, path, w, st='normal'):
        fs.append("@font-face{font-family:'%s';src:url('file://%s');font-weight:%s;font-style:%s}" % (fam, path, w, st))
    SER = F + '/full/source-serif-4.5.1/OTF/SourceSerif4-%s.otf'
    SAN = F + '/full/source-sans-3.52.0/OTF/SourceSans3-%s.otf'
    for w, n in ((400, 'Regular'), (600, 'Semibold'), (700, 'Bold')):
        ff('SSerif', SER % n, w); ff('SSerif', SER % ({'Regular': 'It'}.get(n, n + 'It')), w, 'italic')
        ff('SSans', SAN % n, w); ff('SSans', SAN % ({'Regular': 'It'}.get(n, n + 'It')), w, 'italic')
    for w in (500, 600, 700, 800, 900):
        ff('Disp', '%s/fontsource-barlow-condensed-5.3.0/files/barlow-condensed-latin-%d-normal.woff2' % (F, w), w)
    for w in (500, 600, 700):
        ff('DispS', '%s/fontsource-barlow-semi-condensed-5.3.0/files/barlow-semi-condensed-latin-%d-normal.woff2' % (F, w), w)
    return '\n'.join(fs)


# ------------------------------------------------------------------ repeat captions (user rule)
LOCAL_BANKS = ['39th Batch Exams', 'Ministerial Exam', 'Formative', 'Previous Years']
LOCAL_LABEL = 'Local Exams'
LOCAL_BLURB = '39th-batch block, induction & final papers · ministerial · formative & previous-years exams — one numbering'


def src_label(q):
    """where a question was asked, as shown in the 'repeated' note."""
    b = q['bank']
    if b == '39th Batch Exams':
        p = (q.get('src') or {}).get('paper', '')
        return '39th batch ' + ({'Paper 1': 'final Paper 1', 'Paper 2': 'final Paper 2', 'Block 2': 'Block 2 exam', 'Block 3': 'Block 3 exam',
                                 'End-induction Block A': 'end-induction exam'}.get(p, 'exam'))
    if b == 'Ministerial Exam':
        return 'Ministerial exam'
    if b == 'Formative':
        return 'Formative exam'
    if b == 'Previous Years':
        return 'Previous-years exam'
    return b


def captions():
    """survivor id -> (times asked, [(label, n), ...] for the OTHER places it was asked), following dup chains."""
    cap = collections.defaultdict(collections.Counter)
    for q in Q:
        if q.get('status') != 'deleted' or not q.get('dup_of') or q.get('dup_silent'):
            continue
        tgt = q['dup_of']; seen = set()
        while BYID[tgt].get('status') == 'deleted' and BYID[tgt].get('dup_of') and tgt not in seen:
            seen.add(tgt); tgt = BYID[tgt]['dup_of']
        if BYID[tgt].get('status') == 'deleted':
            continue
        cap[tgt][(q['bank'], src_label(q))] += 1
    out = {}
    for sid, cnt in cap.items():
        order = sorted(cnt.items(), key=lambda kv: (gen.BANK_ORDER.index(kv[0][0]) if kv[0][0] in gen.BANK_ORDER else 99, kv[0][1]))
        out[sid] = (sum(cnt.values()) + 1, [(lab, k) for (bk, lab), k in order])
    return out


CAP = captions()


def cap_html(qid):
    if qid not in CAP:
        return ''
    n, order = CAP[qid]
    src = ' · '.join('%s%s' % (t(b), ' ×%d' % k if k > 1 else '') for b, k in order)
    return ('<p class="rep"><span class="repk">REPEATED %d× · ALSO ASKED IN</span><span class="reps">%s</span></p>' % (n, src))


# ------------------------------------------------------------------ page chrome
def tab_pos(c):
    same = [x for x in book['chapters'] if x['part'] == c['part']]
    return same.index(c)


def bg_svg(c, side):
    acc = '#' + c['color']
    y = 24 + tab_pos(c) * 25
    if side == 'left':
        tab = '<rect x="0" y="%d" width="6" height="23" fill="%s"/>' % (y, acc)
        head = '<line x1="17" y1="14.2" x2="191" y2="14.2" stroke="%s" stroke-width="0.18"/>' % LINE
    else:
        tab = '<rect x="204" y="%d" width="6" height="23" fill="%s"/>' % (y, acc)
        head = '<line x1="19" y1="14.2" x2="193" y2="14.2" stroke="%s" stroke-width="0.18"/>' % LINE
    svg = '<svg xmlns="http://www.w3.org/2000/svg" width="210mm" height="297mm" viewBox="0 0 210 297">%s%s</svg>' % (head, tab)
    p = os.path.join(TMP, 'bg-%s-%s.svg' % (c['id'], side))
    open(p, 'w').write(svg)
    return p


def opener_svg(c, side='right'):
    """opener: thumb tab on the outer edge."""
    acc = '#' + c['color']
    y = 24 + tab_pos(c) * 25
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="210mm" height="297mm" viewBox="0 0 210 297">'
           '<rect x="%d" y="%d" width="6" height="23" fill="%s"/></svg>') % (204 if side == 'right' else 0, y, acc)
    p = os.path.join(TMP, 'op-%s-%s.svg' % (c['id'], side))
    open(p, 'w').write(svg)
    return p


def page_css(c):
    cid, acc = c['id'], '#' + c['color']
    L, R = bg_svg(c, 'left'), bg_svg(c, 'right')
    part = c['part'].upper()
    title = c['title'].upper().replace('"', '')
    div = os.path.join(ROOT, 'assets', 'dividers', 'part-%d.jpg' % (PARTS.index(c['part']) + 1))
    return '''
@page ch-%(cid)s:left { margin: 21mm 19mm 20mm 17mm; background: url('file://%(L)s') no-repeat -17mm -21mm / 210mm 297mm;
  @top-left { content: "%(part)s  /  %(title)s"; }
  @bottom-left { content: counter(page); background: %(acc)s; } }
@page ch-%(cid)s:right { margin: 21mm 17mm 20mm 19mm; background: url('file://%(R)s') no-repeat -19mm -21mm / 210mm 297mm;
  @top-right { content: string(bank); }
  @bottom-right { content: counter(page); background: %(acc)s; } }
@page div-%(cid)s { margin: 0; background: %(ink)s url('file://%(div)s') no-repeat center / cover; }
@page op-%(cid)s:right { margin: 21mm 17mm 20mm 19mm; background: url('file://%(op)s') no-repeat -19mm -21mm / 210mm 297mm; }
@page op-%(cid)s:left { margin: 21mm 19mm 20mm 17mm; background: url('file://%(opl)s') no-repeat -17mm -21mm / 210mm 297mm; }
@page ch-%(cid)s:blank { background: none; @top-left { content: none } @top-right { content: none } @bottom-left { content: none; background: none } @bottom-right { content: none; background: none } }
@page div-%(cid)s:blank { background: none }
.c-%(cid)s { --acc: %(acc)s; --acc9: %(acc9)s; --acc18: %(acc18)s; }
''' % dict(cid=cid, L=L, R=R, part=part, title=title, acc=acc, div=div, ink=INK, op=opener_svg(c), opl=opener_svg(c, 'left'),
           acc9=tint(c['color'], 0.08), acc18=tint(c['color'], 0.16))


# ------------------------------------------------------------------ question rendering
# 3rd edition numbering: the local exams of each chapter share ONE sequence (1, 2, 3 ...), every other source
# restarts at 1; EMQs are numbered Theme 1, Theme 2 ... with scenarios 1, 2, 3 ... inside each theme and options A, B, C ...
INDEX = collections.defaultdict(lambda: collections.defaultdict(list))   # l1 -> l2 -> [anchor ids]
PAGE = {}                                                                  # anchor id -> page (filled after pass 1)
SUBLAB = {'39th Batch Exams': ('39th Batch Exams', 'Block 2, Block 3, end-induction and final Papers 1 & 2 of the 39th batch (recalled)'),
          'Ministerial Exam': ('Ministerial Exam', 'Ministerial evaluation examinations'),
          'Formative': ('Formative', 'College formative examinations'),
          'Previous Years': ('Previous Years', 'Previous-years college examinations')}


def imgs(lst):
    out = []
    for x in lst or []:
        p = os.path.join(ROOT, 'assets', x)
        if os.path.exists(p):
            out.append('<img class="qimg" src="file://%s">' % p)
        else:   # original picture not supplied yet: keep a labelled frame so it can be dropped in later
            out.append('<div class="qimgph"><span>FIGURE</span>%s</div>' % t(os.path.basename(x)))
    return ''.join(out)


def add_index(topics, anchor):
    for l1, l2 in gen.index_entries(topics):
        INDEX[l1][l2].append(anchor)


def case_prefix(a, b):
    """shared opening sentences of two stems (a clinical case reused by several questions)."""
    k = 0
    while k < min(len(a), len(b)) and a[k] == b[k]:
        k += 1
    cut = a.rfind('. ', 0, k + 1)
    return a[:cut + 1] if cut >= 90 else ''


def case_groups(s):
    """-> {index_of_first: (prefix, count)} for runs of consecutive MCQs sharing a case."""
    def pref(stems):
        cp = os.path.commonprefix(stems)
        cut = cp.rfind('. ')
        return cp[:cut + 1] if cut >= 90 else ''
    out, i = {}, 0
    while i < len(s):
        if s[i]['type'] != 'MCQ':
            i += 1; continue
        j, best = i + 1, ''
        while j < len(s) and s[j]['type'] == 'MCQ':
            p = pref([x['stem'] for x in s[i:j + 1]])
            if not p:
                break
            best = p; j += 1
        if best and j - i >= 2:
            out[i] = (best, j - i); i = j
        else:
            i += 1
    return out


def chapter_plan(cid):
    """ordered sections of a chapter, each numbered from 1; shared by the PDF and the IDML builders."""
    qs = gen.chapter_questions(cid)
    secs = collections.OrderedDict()
    for q in qs:
        grp = LOCAL_LABEL if q['bank'] in LOCAL_BANKS else q['bank']
        secs.setdefault((grp, q['type']), []).append(q)
    plan = []
    for (grp, typ), items in secs.items():
        n, prev = 0, None
        for q in items:
            q['_sub'] = q['bank'] if (grp == LOCAL_LABEL and q['bank'] != prev) else None
            prev = q['bank']
            n += 1
            q['_num'] = n
            for k, it in enumerate(q.get('items') or []):
                it['_num'] = k + 1
        sets, cur, count = [], [], 0
        for q in items:
            size = 1 if typ == 'MCQ' else len(q['items'])
            if cur and count + size > gen.SET_SIZE:
                sets.append(cur); cur, count = [], 0
            cur.append(q); count += size
        if cur:
            sets.append(cur)
        plan.append(dict(group=grp, type=typ, label='%s %s' % (grp, 'EMQs' if typ == 'EMQ' else 'MCQs'),
                         blurb=LOCAL_BLURB if grp == LOCAL_LABEL else gen.BANK_BLURB.get(grp, ''),
                         bid='bank-%s-%s-%s' % (cid, slug(grp), typ.lower()),
                         units=sum(1 if typ == 'MCQ' else len(q['items']) for q in items), sets=sets, items=items))
    return plan


def render_set(sec, s):
    typ, label = sec['type'], sec['label']
    body = ['<div class="flow">']
    groups = case_groups(s) if typ == 'MCQ' else {}
    strip = {}
    for gi, (pre, cnt) in groups.items():
        for k in range(gi, gi + cnt):
            strip[k] = len(pre)
    for qi, q in enumerate(s):
        if q.get('_sub'):
            a_, b_ = SUBLAB.get(q['_sub'], (q['_sub'], ''))
            body.append('<p class="subsrc">%s<small>%s</small></p>' % (t(a_), t(b_)))
        qa = 'q-' + q['id']
        if qi in groups:
            pre, cnt = groups[qi]
            body.append('<div class="case"><p class="csk">CASE &nbsp;·&nbsp; QUESTIONS %d–%d</p><p>%s</p></div>' % (q['_num'], s[qi + cnt - 1]['_num'], t(pre)))
        if typ == 'MCQ':
            add_index(q.get('topics'), qa)
            stem = q['stem'][strip[qi]:].strip() if qi in strip else q['stem']
            stem = stem[:1].upper() + stem[1:]
            opts = ''.join('<li><span class="ol">%s</span>%s</li>' % (chr(65 + i), t(o)) for i, o in enumerate(q['options']))
            body.append('<div class="q" id="%s"><p class="qs"><a class="qn" href="#a-%s">%d</a>%s</p>%s<ul class="opts">%s</ul>%s</div>'
                        % (qa, q['id'], q['_num'], t(stem), imgs(q.get('images')), opts, cap_html(q['id'])))
        else:
            opts = ''.join('<li><span class="ol">%s</span>%s</li>' % (chr(65 + i), t(o)) for i, o in enumerate(q['options']))
            blk = ['<div class="emq" id="%s"><p class="et"><span>THEME %d</span>%s</p>%s<ul class="eo">%s</ul>' % (qa, q['_num'], t(q['theme']), imgs(q.get('images')), opts),
                   '<p class="el">For each scenario, choose the single most appropriate option. Each option may be used once, more than once or not at all.</p>']
            for it in q['items']:
                ia = '%s-%d' % (qa, it['_num'])
                add_index(q.get('topics'), ia)
                blk.append('<div class="ei"><p class="qs" id="%s"><a class="qn" href="#a-%s-%d">%d</a>%s</p>%s</div>' % (ia, q['id'], it['_num'], it['_num'], t(it['stem']), imgs(it.get('images'))))
            blk.append(cap_html(q['id']))
            blk.append('</div>')
            body.append(''.join(blk))
    body.append('</div>')
    if typ == 'MCQ':
        head = 'Answers&nbsp; %d–%d' % (s[0]['_num'], s[-1]['_num']) if len(s) > 1 else 'Answer&nbsp; %d' % s[0]['_num']
    else:
        head = 'Answers&nbsp; · Themes %d–%d' % (s[0]['_num'], s[-1]['_num']) if len(s) > 1 else 'Answers&nbsp; · Theme %d' % s[0]['_num']
    body.append('<h3 class="ah"><span>%s</span><span class="ahb">%s</span></h3><div class="flow ans">' % (head, t(label)))
    for q in s:
        if typ == 'MCQ':
            upd = '<span class="upd">UPDATED</span> ' if q.get('status') == 'corrected' else ''
            if len(q['answer']) == 1:
                aopt = t(q['options'][ord(q['answer']) - 65])
            else:
                aopt = 'True: ' + ', '.join(q['answer'])
            body.append('<p class="an" id="a-%s"><a class="anum" href="#q-%s">%d</a><span class="chip">%s</span> <span class="aopt">%s</span> — %s%s</p>'
                        % (q['id'], q['id'], q['_num'], ' '.join(q['answer']), aopt, upd, t(q['explanation'])))
        else:
            body.append('<p class="ath">Theme %d · %s</p>' % (q['_num'], t(q['theme'])))
            L = q['option_letters']
            for it in q['items']:
                k = L.index(it['answer'])
                body.append('<p class="an" id="a-%s-%d"><a class="anum" href="#q-%s-%d">%d</a><span class="chip">%s</span> <span class="aopt">%s</span> — %s</p>'
                            % (q['id'], it['_num'], q['id'], it['_num'], it['_num'], chr(65 + k), t(q['options'][k]), t(it['explanation'])))
    body.append('</div>')
    return body


def chapter_html(c):
    cid = c['id']
    plan = chapter_plan(cid)
    qs = [q for sec in plan for q in sec['items']]
    body, bank_list = [], []
    n_sets = 0
    for sec in plan:
        bank_list.append((sec['bid'], sec['label'], sec['units']))
        n_sets += len(sec['sets'])
        kind = 'THEMES · %d SCENARIOS' % sec['units'] if sec['type'] == 'EMQ' else 'QUESTIONS'
        cnt = len(sec['items']) if sec['type'] == 'EMQ' else sec['units']
        body.append('<div class="bankhead"><p class="bk">%d %s &nbsp;•&nbsp; %s</p>' % (cnt, kind, t(sec['blurb']).upper()))
        body.append('<h2 class="bh" id="%s">%s</h2></div>' % (sec['bid'], t(sec['label'])))
        for si, s in enumerate(sec['sets']):
            if len(sec['sets']) > 1:
                body.append('<p class="sh">Set %d of %d</p>' % (si + 1, len(sec['sets'])))
            body += render_set(sec, s)
    n_mcq = sum(1 for q in qs if q['type'] == 'MCQ')
    n_emq = sum(len(q['items']) for q in qs if q['type'] == 'EMQ')
    n_rep = sum(1 for q in qs if q['id'] in CAP)
    ess = ESS.get(cid, [])
    stats = [(n_mcq, 'MCQs'), (n_emq, 'EMQ scenarios'), (len(plan), 'sources'), (n_rep, 'repeated ideas')]
    rows = []
    k = 0
    if ess:
        k += 1
        rows.append('<li><span class="k">%02d</span><a href="#ess-%s">Management flowcharts</a><span class="c">%d charts</span><a class="p" href="#ess-%s"></a></li>' % (k, cid, len(ess), cid))
    for b, l, n in bank_list:
        k += 1
        rows.append('<li><span class="k">%02d</span><a href="#%s">%s</a><span class="c">%d Q</span><a class="p" href="#%s"></a></li>' % (k, b, t(l), n, b))
    part = t(c['part']).upper()
    pk = PARTS.index(c['part']) + 1
    first = [x for x in book['chapters'] if x['part'] == c['part']][0]['id'] == cid
    pch = [x for x in book['chapters'] if x['part'] == c['part']]
    div = ('<section class="divider" style="page: div-%(cid)s" id="part-%(pk)d"><div class="dk">PART %(pk)02d &nbsp;/&nbsp; %(np)d CHAPTERS</div>'
           '<div class="dnum">%(pk)02d</div><div class="dt">%(part)s</div><ul class="dch">%(chs)s</ul>'
           '<div class="cr">Artwork drawn for this edition</div></section>') % dict(
        cid=cid, pk=pk, np=len(pch), part=part, chs=''.join('<li><b>%02d</b>%s</li>' % (x['order'], t(x['title'])) for x in pch)) if first else ''
    op = ('<section class="opener%(ofirst)s" style="page: op-%(cid)s" id="ch-%(cid)s"><div class="ghost">%(o)02d</div><p class="kick">%(part)s</p><h1>%(title)s</h1><div class="rule"></div>'
          '<p class="intro">%(intro)s</p><div class="stats">%(stats)s</div><p class="oh">In this chapter</p><ul class="toc">%(rows)s</ul></section>') % dict(
        cid=cid, o=c['order'], part=part, title=t(c['title']), intro=t(c.get('intro', '')), ofirst=' ofirst' if first else '',
        stats=''.join('<div><b>%d</b><span>%s</span></div>' % s for s in stats), rows=''.join(rows))
    esshtml = essentials_html(cid, ess) if ess else ''
    return ('<div class="chapter c-%s" style="page: ch-%s">%s%s%s<section class="content">%s</section></div>'
            % (cid, cid, div, op, esshtml, '\n'.join(body))), dict(id=cid, mcq=n_mcq, emq=n_emq, rep=n_rep, banks=bank_list)


# ------------------------------------------------------------------ management flowcharts
def fc_box(n):
    return '<div class="fcn %s">%s</div>' % (n['k'], t(n['t']))


def flowchart_html(b):
    out = ['<div class="fc"><h4>%s</h4><p class="fcsrc">%s</p>' % (t(b['title']), t(b.get('source', '')))]
    for i, n in enumerate(b['nodes']):
        if i:
            out.append('<div class="fca"></div>')
        if n['k'] == 'split':
            out.append('<div class="fcq">%s</div><div class="fcstem"></div>' % t(n['q']))
            cols = []
            for br in n['br']:
                inner = []
                for j, m in enumerate(br['n']):
                    if j:
                        inner.append('<div class="fca"></div>')
                    inner.append(fc_box(m))
                cols.append('<td class="fcc"><div class="fct"></div><span class="fcl">%s</span>%s</td>' % (t(br['l']), ''.join(inner)))
            out.append('<table class="fcb n%d"><tr>%s</tr></table>' % (len(n['br']), ''.join(cols)))
        else:
            out.append(fc_box(n))
    out.append('</div>')
    return ''.join(out)


def essentials_html(cid, blocks):
    out = ['<section class="ess" id="ess-%s"><p class="bk">MANAGEMENT FLOWCHARTS &nbsp;•&nbsp; UPDATED TO CURRENT GUIDELINES</p><h2 class="bh eh">Step by step</h2>' % cid]
    for b in blocks:
        out.append(flowchart_html(b))
    out.append('</section>')
    return ''.join(out)


# ------------------------------------------------------------------ front & back matter
def front_html(meta, totals):
    T = book['texts']
    cover = os.path.join(ROOT, 'assets', 'dividers', 'cover.jpg')
    lines = ''.join('<span>%s</span>' % t(x) for x in T['cover_lines'])
    tot = totals['units']
    fmt = {'total': '{:,}'.format(tot), 'corrected': totals['corrected'], 'chapters': len(book['chapters'])}
    s = []
    s.append('''<section class="cover" style="page: cover"><div class="ck">%s</div><h1 class="ct">%s</h1><div class="crule"></div>
<p class="cv">%s</p><p class="ctag">%s</p>
<div class="cfoot"><p class="ced">%s</p><p class="cau">%s</p><p class="cteam">%s</p></div></section>''' % (
        t(book['volume']).upper(), lines, t(book['volume']), t(T['tagline']), t(book['edition']),
        ' &nbsp;·&nbsp; '.join(t(a) for a in book['authors']), t(book['team'])))
    s.append('<section class="blankp" style="page: plain"></section>')
    s.append('''<section class="titlep" style="page: plain"><p class="tk">%s</p><h1>%s</h1><p class="tv">%s</p><div class="trule"></div>
<p class="tau">%s</p><p class="ted">%s</p><p class="tteam">%s · <a href="%s">%s</a></p></section>''' % (
        t(book['edition']).upper(), t(book['title']), t(book['volume']), '<br>'.join(t(a) for a in book['authors']), t(book['edition']),
        t(book['team']), book['telegram'], book['telegram'].replace('https://', '')))
    # colophon
    col = [('This edition', 'The %s of the Surgery Bank for Surgery 1 (general surgery and urology). %s questions — %d MCQs and %d EMQ items in %d chapters — with answers and explanations.' % (
        book['edition'].split('/')[0].strip(), fmt['total'], totals['mcq'], totals['emq'], len(book['chapters'])))]
    col.append(('What changed in the 3rd edition', 'Every key was checked against current guidance and standard texts (Bailey & Love 28th edition, NICE, ATLS 10th edition, EAU, ESMO, WSES); %d questions were corrected, and every explanation was rewritten and then cut to two or three lines that say why the answer is right. %d questions whose idea had already been asked were removed: the question kept is the one from the earliest source in the chapter, and a highlighted note under it says how many times the idea was asked and in which exams or books. Numbering now restarts for each source: the local exams of a chapter (39th batch block, end-induction and final papers, ministerial, formative and previous-years exams) share one sequence, and each international book has its own; EMQs are numbered by theme. The 39th batch papers were added to the chapters they belong to; their recalled questions were completed and keyed, and their short-answer tasks recast as single-best-answer questions. All changes are logged in the corrections file that accompanies this book.' % (totals['corrected'], totals['merged'])))
    col.append(('Management flowcharts', 'The old summary tables were removed. Each chapter now opens with step-by-step flowcharts that combine the summaries of the source books with current guidelines, so that the next step in management can be read at a glance.'))
    col.append(('Artwork', 'Part and cover artwork was drawn for this edition; each illustration shows the subject of its part.'))
    col.append(('Contributors', 'Data: %s. Participants: %s.' % (', '.join(book['contributors']['data']), ', '.join(book['contributors']['participants']))))
    col.append(('Important', 'This book is a revision aid. Guidelines change: always check current local and national guidance before applying anything to patient care.'))
    s.append('<section class="colophon" style="page: plain"><h2 class="fh">Colophon</h2>%s<p class="cpy">© %s %s. Prepared by %s.</p></section>' % (
        ''.join('<div class="cb"><h5>%s</h5><p>%s</p></div>' % (t(a), t(b)) for a, b in col), '2026', ' & '.join(book['authors']), t(book['team'])))
    # contents
    rows = []
    for part in PARTS:
        chs = [c for c in book['chapters'] if c['part'] == part and (not ONLY or c['id'] in ONLY)]
        if not chs:
            continue
        rows.append('<h3 class="cpart">%s</h3>' % t(part))
        for c in chs:
            m = meta[c['id']]
            rows.append('<div class="crow" style="--acc:#%s"><span class="cnum">%02d</span><span class="ctitle"><a href="#ch-%s">%s</a><small>%s</small></span>'
                        '<span class="ccount">%d Q</span><span class="cpg" data-h="#ch-%s"></span></div>' % (
                            c['color'], c['order'], c['id'], t(c['title']), t(c.get('intro', '')), m['mcq'] + m['emq'], c['id']))
    rows.append('<h3 class="cpart">Back matter</h3><div class="crow" style="--acc:%s"><span class="cnum">—</span><span class="ctitle"><a href="#index">Index</a></span><span class="ccount"></span><span class="cpg" data-h="#index"></span></div>' % INK)
    s.append('<section class="contents" style="page: plain"><h2 class="fh">Contents</h2>%s</section>' % ''.join(rows))
    # how to use
    ex_cap = '<p class="rep"><span class="repk">REPEATED 3× · ALSO ASKED IN</span><span class="reps">Previous-years exam · Bailey &amp; Love</span></p>'
    s.append('''<section class="howto" style="page: plain"><h2 class="fh">How to use this book</h2>
<div class="hgrid">
<div><h5>Flowcharts first</h5><p>Each chapter opens with management flowcharts updated to current guidelines: follow the arrows from the presenting problem, answer the <b>?</b> decision boxes, and read the next step.</p></div>
<div><h5>Local exams first, then the books</h5><p>Questions come grouped by source. <b>Local Exams</b> — the 39th-batch block, end-induction and final papers, ministerial, formative and previous-years exams — come first and share one numbering. The essay questions converted to MCQs and each international book (Bailey &amp; Love, Lange, SBA, Oxford, PreTest, Get Ahead, Crash Course, Irfan) follow, each with its own numbering from 1.</p></div>
<div><h5>MCQs and EMQs</h5><p>MCQs are numbered 1, 2, 3 … within their source. EMQs are numbered <b>Theme 1, Theme 2 …</b>; each theme lists its options A, B, C … and its scenarios are numbered 1, 2, 3 ….</p></div>
<div><h5>Answers after every set</h5><p>Answers follow each set of up to 25 questions, each with a two- or three-line explanation. Tap a question number to jump to its answer and the answer number to jump back.</p></div>
<div><h5>Repeated questions</h5><p>When an idea was asked more than once, one question is kept — the one from the earliest source — and a highlighted note under it says how many times and where else it was asked. Repeats are a strong signal of a high-yield topic.</p>%s</div>
<div><h5>True/false questions</h5><p>Questions that ask <i>which statements are true</i> may have several correct options; the answer chip lists all of them (for example <b>A C E</b>) and the explanation names the false ones.</p></div>
<div><h5>Updated answers and index</h5><p>Answers marked <span class="upd">UPDATED</span> were corrected in this edition. The index lists diseases, drugs, tests and signs with the <b>page numbers</b> of the questions that test them.</p></div>
</div>
</section><section class="glancep" style="page: plain"><h2 class="fh">At a glance</h2><table class="glance"><thead><tr><th>Chapter</th><th>MCQs</th><th>EMQ scenarios</th><th>Repeated ideas</th></tr></thead><tbody>%s</tbody>
<tfoot><tr><td>Total</td><td>%d</td><td>%d</td><td>%d</td></tr></tfoot></table></section>''' % (
        ex_cap,
        ''.join('<tr><td><span class="sw" style="background:#%s"></span>%02d&nbsp; %s</td><td>%d</td><td>%d</td><td>%d</td></tr>' % (
            c['color'], c['order'], t(c['title']), meta[c['id']]['mcq'], meta[c['id']]['emq'], meta[c['id']]['rep']) for c in CH),
        totals['mcq'], totals['emq'], totals['rep']))
    # question sources
    bc = collections.Counter(); bt = collections.Counter()
    for q in Q:
        if q.get('status') != 'deleted' and (not ONLY or q['chapter'] in ONLY):
            bc[q['bank']] += 1 if q['type'] == 'MCQ' else len(q['items'])
    for q in Q:
        if q.get('status') == 'deleted' and q.get('dup_of') and not q.get('dup_silent'):
            bt[q['bank']] += 1
    rows = ''.join('<tr><td><b>%s</b><small>%s</small></td><td>%d</td><td>%s</td></tr>' % (t(b['name']), t(b.get('blurb', '')), bc[b['name']], bt[b['name']] or '—')
                   for b in book['banks'] if bc[b['name']])
    s.append('<section class="sources" style="page: plain"><h2 class="fh">Question sources</h2><p class="snote">In every chapter the banks appear in this order. '
             '“Merged” counts questions removed because their idea was already asked in an earlier or better question; each is credited in the repeat caption of the question that was kept.</p>'
             '<table class="glance srcs"><thead><tr><th>Source</th><th>Questions</th><th>Merged</th></tr></thead><tbody>%s</tbody>'
             '<tfoot><tr><td>Total</td><td>%d</td><td>%d</td></tr></tfoot></table></section>' % (rows, sum(bc.values()), sum(bt.values())))
    return '\n'.join(s)


def index_html():
    ents = sorted(INDEX.items(), key=lambda kv: re.sub(r'[^a-z0-9 ]', '', kv[0].lower()))
    out = ['<section class="index" id="index" style="page: plain"><h2 class="fh">Index</h2><p class="inote">Numbers refer to pages; tap one to open the question.</p><div class="icols">']

    def refs(anchors):
        pages = {}
        for a_ in anchors:
            pg = PAGE.get(a_)
            if pg and pg not in pages:
                pages[pg] = a_
        if not pages:                       # first pass: placeholders of realistic length
            return ', '.join('<a href="#%s">000</a>' % a_ for a_ in list(dict.fromkeys(anchors))[:6])
        return ', '.join('<a class="ipg" href="#%s">%d</a>' % (pages[pg], pg) for pg in sorted(pages))
    letter = None
    for l1, subs in ents:
        L0 = (re.sub(r'[^A-Za-z0-9]', '', l1)[:1] or '#').upper()
        if L0.isdigit():
            L0 = '#'
        if L0 != letter:
            letter = L0
            out.append('<p class="il">%s</p>' % letter)
        out.append('<p class="ie">%s %s</p>' % (t(l1), refs(subs.get('', []))))
        for l2 in sorted(k for k in subs if k):
            out.append('<p class="ie2">%s %s</p>' % (t(l2), refs(subs[l2])))
    out.append('</div></section>')
    return ''.join(out)


def back_html(totals):
    T = book['texts']
    fmt = {'total': '{:,}'.format(totals['units']), 'corrected': totals['corrected'], 'chapters': len(book['chapters'])}
    pts = ''.join('<li>%s</li>' % t(p.format(**fmt)) for p in T['back_points'])
    return ('<section class="backc" style="page: backc"><p class="bkk">%s</p><h2>%s</h2><ul>%s</ul>'
            '<div class="bfoot"><p class="btitle">%s</p><p>%s · %s</p><p>%s · %s</p></div></section>') % (
        t(book['volume']).upper(), t(T['back_headline']), pts, t(book['title']), t(book['volume']), t(book['edition']),
        t(book['team']), book['telegram'].replace('https://', ''))


# ------------------------------------------------------------------ CSS
def css():
    return fontcss() + open(os.path.join(HERE, 'book.css'), encoding='utf-8').read().replace('%INK%', INK).replace('%INK2%', INK2) \
        .replace('%MUTED%', MUTED).replace('%LINE%', LINE).replace('%MIST%', MIST).replace('%GOLD%', GOLD).replace('%HL%', HL) \
        .replace('%COVER%', os.path.join(ROOT, 'assets', 'dividers', 'cover.jpg')) + ''.join(page_css(c) for c in CH)


def build_doc():
    INDEX.clear()
    chapters, meta = [], {}
    for c in CH:
        h, m = chapter_html(c)
        chapters.append(h); meta[c['id']] = m
    live = [q for q in Q if q.get('status') != 'deleted' and (not ONLY or q['chapter'] in ONLY)]
    totals = dict(mcq=sum(m['mcq'] for m in meta.values()), emq=sum(m['emq'] for m in meta.values()),
                  rep=sum(m['rep'] for m in meta.values()),
                  corrected=sum(1 for q in live if q.get('status') == 'corrected'),
                  merged=sum(1 for q in Q if q.get('status') == 'deleted' and q.get('dup_of') and not q.get('dup_silent')))
    totals['units'] = totals['mcq'] + totals['emq']
    doc = ('<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><title>%s — %s</title><style>%s</style></head><body>%s%s%s%s</body></html>'
           % (t(book['title']), t(book['volume']), css(), front_html(meta, totals), ''.join(chapters), index_html(), back_html(totals)))
    # contents page numbers: rewrite data-h spans into target-counter anchors
    doc = re.sub(r'<span class="cpg" data-h="(#[^"]+)"></span>', r'<span class="cpg"><a class="pg" href="\1"></a></span>', doc)
    return doc, meta, totals


def anchor_pages(r):
    where = {}
    for i, pg in enumerate(r.pages):
        for k in pg.anchors:
            where.setdefault(k, i + 1)
    return where


def main():
    t0 = time.time()
    doc, meta, totals = build_doc()
    open(os.path.join(OUT, 'book.html'), 'w', encoding='utf-8').write(doc)
    if '--html' in args:
        print('html only'); return
    print('rendering pass 1 (page numbers for the index)…', flush=True)
    r = weasyprint.HTML(string=doc, base_url=ROOT).render()
    PAGE.update(anchor_pages(r))
    doc, meta, totals = build_doc()
    open(os.path.join(OUT, 'book.html'), 'w', encoding='utf-8').write(doc)
    print('rendering pass 2…', flush=True)
    r = weasyprint.HTML(string=doc, base_url=ROOT).render()
    r.metadata.title = '%s — %s' % (book['title'], book['volume'])
    r.metadata.authors = book.get('authors', [])
    r.metadata.lang = 'en-GB'
    name = book.get('file_name', 'book') + ('' if not ONLY else '-' + '-'.join(ONLY))
    pdf = os.path.join(OUT, name + '.pdf')
    r.write_pdf(pdf)
    where = anchor_pages(r)
    json.dump(dict(pages=len(r.pages), totals=totals, meta=meta, anchors={k: v for k, v in where.items() if not k.startswith(('q-', 'a-'))},
                   q={k: v for k, v in where.items() if k.startswith('q-')}),
              open(os.path.join(OUT, 'pagemap.json'), 'w'), indent=1)
    print('pdf', pdf, 'pages', len(r.pages), 'in %.0fs' % (time.time() - t0))


if __name__ == '__main__':
    main()
