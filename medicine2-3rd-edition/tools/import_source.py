"""Import questions from any source into data/questions.json (or into a staging file first).

  python tools/import_source.py SOURCE [--chapter ID] [--bank NAME] [--source LABEL]
                                [--status original|new] [--stage] [--dry]

SOURCE can be
  .xlsx / .xls / .csv   a spreadsheet: headers are matched loosely (see COLS below); our own
                        questions.csv export round-trips exactly (use tools/csvio.py import for that)
  .pdf                  text is extracted page by page, then parsed (numbered questions, A–H options,
                        "Answer: X" lines or a separate answers section "12. C  explanation…")
  .txt / .md            parsed like PDF text
  .docx                 paragraphs are extracted, then parsed like text
  .indd                 exported to text through InDesign (work/extract_text.jsx), then parsed
  folder                every supported file inside it

Chapter assignment:  --chapter wins; else a "chapter" column; else keyword match against
book.json chapters[].keywords (and title); unmatched rows go to the chapter "inbox" so nothing is lost.

--stage   write data/import/<name>.json for review instead of touching questions.json
--dry     parse and print a report only
Every run prints a report: parsed / with key / with explanation / EMQs / per chapter, plus the ids
created, so the review step (patches) can start straight away.
"""
import csv, json, os, re, subprocess, sys, time, collections

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
QF = os.path.join(ROOT, 'data', 'questions.json')
BF = os.path.join(ROOT, 'data', 'book.json')

args = sys.argv[1:]
if not args or args[0].startswith('--'):
    sys.exit(__doc__)


def opt(name, default=None):
    return args[args.index(name) + 1] if name in args else default


SRC = os.path.abspath(args[0])
CHAPTER, BANK, SOURCE = opt('--chapter'), opt('--bank'), opt('--source')
STATUS = opt('--status', 'original')
STAGE, DRY = '--stage' in args, '--dry' in args

book = json.load(open(BF, encoding='utf-8'))
Q = json.load(open(QF, encoding='utf-8')) if os.path.exists(QF) else []

# ------------------------------------------------------------------ text helpers
LET = 'ABCDEFGHIJKLMNOP'


def clean(s):
    s = (s or '').replace('\r\n', '\n').replace('\r', '\n').replace('­', '').replace('ﬁ', 'fi').replace('ﬂ', 'fl')
    s = re.sub(r'[ \t ]+', ' ', s)
    return s.strip()


def join_lines(lines):
    out = ' '.join(l.strip() for l in lines if l.strip())
    out = re.sub(r'(\w)- (\w)', r'\1\2', out)          # hyphenated line breaks
    return re.sub(r'\s{2,}', ' ', out).strip()


# ------------------------------------------------------------------ spreadsheet
COLS = {
    'id': ['id', 'qid', 'question id'],
    'chapter': ['chapter', 'chapter id', 'system', 'section'],
    'bank': ['bank', 'source bank', 'set', 'paper'],
    'source': ['source', 'reference', 'book'],
    'type': ['type', 'question type', 'format'],
    'theme': ['emq_theme', 'theme', 'emq theme'],
    'emq_options': ['emq_options'],
    'item_no': ['item_no', 'item', 'item number'],
    'stem': ['stem', 'question', 'question text', 'scenario', 'vignette', 'q'],
    'answer': ['answer', 'key', 'correct', 'correct answer', 'answer key', 'ans'],
    'explanation': ['explanation', 'rationale', 'explain', 'feedback', 'comment', 'discussion'],
    'topics': ['topics', 'topic', 'tags', 'keywords'],
    'images': ['images', 'image', 'figure', 'picture'],
    'notes': ['notes', 'note', 'remarks'],
    'options': ['options', 'choices', 'answers list'],
}


def norm_header(h):
    return re.sub(r'\s+', ' ', str(h or '').strip().lower().replace('_', ' '))


def map_headers(headers):
    m = {}
    for i, h in enumerate(headers):
        n = norm_header(h)
        for key, names in COLS.items():
            if n in [x.replace('_', ' ') for x in names] and key not in m:
                m[key] = i
        mo = re.match(r'^(?:option|opt|choice)?\s*([a-p])$', n) or re.match(r'^(?:option|opt|choice)\s*([a-p])\b', n)
        if mo:
            m['opt_' + mo.group(1).upper()] = i
    return m


def read_table(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == '.csv':
        raw = open(path, encoding='utf-8-sig', errors='replace').read()
        rows = list(csv.reader(raw.splitlines()))
    else:
        import openpyxl
        wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
        rows = []
        for ws in wb.worksheets:
            sheet_rows = [[('' if c is None else str(c)) for c in r] for r in ws.iter_rows(values_only=True)]
            if sheet_rows:
                rows += sheet_rows if not rows else sheet_rows[1:]     # same headers assumed on later sheets
    return rows


def parse_table(path):
    rows = read_table(path)
    if not rows:
        return []
    hdr = map_headers(rows[0])
    if 'stem' not in hdr:
        raise SystemExit('No question column found in %s. Headers: %s' % (path, rows[0]))
    recs, emq = [], collections.OrderedDict()
    for r in rows[1:]:
        g = lambda k: clean(r[hdr[k]]) if k in hdr and hdr[k] < len(r) else ''
        stem = g('stem')
        if not stem:
            continue
        opts = [g('opt_' + L) for L in LET if 'opt_' + L in hdr]
        opts = [o for o in opts if o]
        if not opts and g('options'):
            opts = [re.sub(r'^\(?[A-Pa-p][\.\)]\s*', '', o).strip() for o in re.split(r'\n|\s\|\s|;\s*(?=\(?[A-Pa-p][\.\)])', g('options')) if o.strip()]
        ans = g('answer').strip()
        mo = re.match(r'^\(?([A-Pa-p])\b', ans)
        if mo:
            ans = mo.group(1).upper()
        elif ans and opts:                                  # answer given as text
            hit = [i for i, o in enumerate(opts) if o.lower() == ans.lower()]
            ans = LET[hit[0]] if hit else ans
        typ = (g('type') or ('EMQ' if g('theme') else 'MCQ')).upper()
        base = dict(chapter=g('chapter'), bank=g('bank'), source=g('source'), topics=[t.strip() for t in re.split(r'[;|,]', g('topics')) if t.strip()],
                    images=[t.strip() for t in re.split(r'[;|,]', g('images')) if t.strip()], notes=g('notes'), id=g('id'))
        if typ == 'EMQ' and g('theme'):
            key = (g('id') or g('theme'), g('chapter'))
            e = emq.setdefault(key, dict(base, type='EMQ', theme=g('theme'), options=opts or [o.strip() for o in g('emq_options').split('|') if o.strip()], items=[]))
            e['items'].append(dict(n=int(float(g('item_no'))) if g('item_no') else len(e['items']) + 1, stem=stem, answer=ans,
                                   explanation=g('explanation'), images=base['images']))
        else:
            recs.append(dict(base, type='MCQ', stem=stem, options=opts, answer=ans, explanation=g('explanation')))
    return recs + list(emq.values())


# ------------------------------------------------------------------ free text (PDF / DOCX / TXT / INDD export)
QSTART = re.compile(r'^(?:Q(?:uestion)?\s*)?(\d{1,4})\s*[\.\)\-:]\s*(.*)$', re.I)
OPT = re.compile(r'^\(?([A-Pa-p])(?:[\.\)]|\s(?=[A-Z0-9(]))\s*(.+)$')
ANSLINE = re.compile(r'^(?:correct\s+)?(?:answer|ans|key)\s*(?:is)?\s*[:\-–]?\s*\(?([A-P])\b[\.\)]?\s*(.*)$', re.I)
EXPL = re.compile(r'^(?:explanation|rationale|discussion)\s*[:\-–]\s*(.*)$', re.I)
ANS_HEAD = re.compile(r'^(answers?|answer key|key|solutions?)(\s+(to|for)\b.*)?\s*[:\-]?\s*$', re.I)
THEME = re.compile(r'^(?:theme|emq)\s*[:\-–]?\s*(.+)$', re.I)


def text_from(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == '.pdf':
        import fitz
        d = fitz.open(path)
        return '\n'.join(p.get_text() for p in d)
    if ext == '.docx':
        import zipfile
        x = zipfile.ZipFile(path).read('word/document.xml').decode('utf-8')
        paras = re.findall(r'<w:p[ >].*?</w:p>', x, re.S)
        return '\n'.join(re.sub(r'<[^>]+>', '', re.sub(r'<w:tab/>', '\t', p)) for p in paras)
    if ext == '.indd':
        out = os.path.join(ROOT, 'work', 'import_' + re.sub(r'\W+', '_', os.path.basename(path)) + '.txt')
        jsx = os.path.join(ROOT, 'work', 'extract_text.jsx')
        code = 'var SRC = %s; var OUT = %s;\n' % (json.dumps(path.replace('\\', '/')), json.dumps(out.replace('\\', '/'))) + open(jsx, encoding='utf-8').read()
        run = os.path.join(ROOT, 'work', '_extract_run.jsx')
        open(run, 'w', encoding='utf-8').write(code)
        ps = ('$app = New-Object -ComObject "InDesign.Application.2025"; '
              '$r = $app.DoScript(\'try { $.evalFile(File("%s")) } catch (e) { "ERR " + e.line + ": " + e.message }\', 1246973031); Write-Output $r') % run.replace('\\', '/')
        print('InDesign:', subprocess.run(['powershell', '-NoProfile', '-Command', ps], capture_output=True, text=True).stdout.strip())
        return open(out, encoding='utf-8').read()
    return open(path, encoding='utf-8', errors='replace').read()


SECTION = re.compile(r'\b(questions?|answers?|answer key|solutions?)\b', re.I)


def split_block(lines):
    """One question block -> stem lines, option list, answer letter, explanation lines.
    Options are the LAST run of lines starting A, B, C… in sequence (so a stem that begins
    'A 45-year-old…' is not mistaken for option A)."""
    ans, expl, body = '', [], []
    mode = 'body'
    for l in lines:
        a, e = ANSLINE.match(l), EXPL.match(l)
        if a:
            ans, mode = a.group(1).upper(), 'expl'
            if a.group(2):
                expl.append(a.group(2))
        elif e:
            mode = 'expl'; expl.append(e.group(1))
        elif mode == 'expl':
            expl.append(l)
        else:
            body.append(l)
    starts = [i for i, l in enumerate(body) if OPT.match(l) and OPT.match(l).group(1).upper() == 'A']
    best = None
    for i in starts:
        want, n = 1, 1
        for l in body[i + 1:]:
            o = OPT.match(l)
            if o and LET.index(o.group(1).upper()) == want:
                want += 1; n += 1
        if n >= 3:
            best = i
    opts = []
    if best is not None:
        stem, want = body[:best], 0
        for l in body[best:]:
            o = OPT.match(l)
            if o and LET.index(o.group(1).upper()) == want:
                opts.append(o.group(2)); want += 1
            elif opts:
                opts[-1] += ' ' + l
    else:
        stem = body
    return stem, [join_lines([o]) for o in opts], ans, expl


def parse_text(txt):
    lines = [clean(l) for l in clean(txt).split('\n')]
    lines = [l for l in lines if l and not re.fullmatch(r'\d{1,4}', l)]          # drop bare page numbers
    # walk the text; short heading lines mentioning "questions"/"answers" switch mode (running
    # headers repeat harmlessly). Answers attach to the questions of the most recent question section.
    mode, sec = 'q', 0
    qsecs = collections.defaultdict(list)          # sec -> [question dicts]
    asecs = collections.defaultdict(dict)          # sec -> {n: [letter, text...]}
    cur, theme, acur = None, None, None
    last_mode = 'q'
    for l in lines:
        if len(l) < 70 and SECTION.search(l) and not QSTART.match(l) and not ANSLINE.match(l):
            new_mode = 'a' if re.search(r'answer|solution|\bkey\b', l, re.I) else 'q'
            if new_mode == 'q' and last_mode == 'a':
                sec += 1
            mode = last_mode = new_mode
            cur = acur = None
            continue
        if mode == 'q':
            t, m = THEME.match(l), QSTART.match(l)
            if t and not m:
                theme = t.group(1); cur = None; continue
            if m and len(m.group(2)) != 1:
                cur = dict(n=int(m.group(1)), first=m.group(2), lines=[], theme=theme)
                qsecs[sec].append(cur)
            elif cur is not None:
                cur['lines'].append(l)
        else:
            m = re.match(r'^(\d{1,4})\s*[\.\)\-:]?\s*(?:\(?([A-P])\)?(?:[\.\):\s]|$))?\s*(.*)$', l)
            known = {q['n'] for q in qsecs[sec]}
            if m and (m.group(2) or int(m.group(1)) in known) and int(m.group(1)) in known | {int(m.group(1))} and (acur is None or int(m.group(1)) != acur):
                acur = int(m.group(1))
                asecs[sec][acur] = [m.group(2) or '', m.group(3)]
            elif acur is not None:
                buf = asecs[sec][acur]
                mm = re.match(r'^([A-P])\s*[\.\)]\s*(.*)$', l)
                if mm and not buf[0]:
                    asecs[sec][acur] = [mm.group(1), mm.group(2)]
                else:
                    buf.append(l)
    recs = []
    for s in sorted(qsecs):
        for q in qsecs[s]:
            stem, opts, ans, expl = split_block(q['lines'])
            if not ans and q['n'] in asecs.get(s, {}):
                b = asecs[s][q['n']]
                ans = (b[0] or '').upper()
                expl = b[1:]
            recs.append(dict(n=q['n'], stem=join_lines([q['first']] + stem), options=opts, answer=ans,
                             explanation=join_lines(expl), theme=q.get('theme')))
    # EMQs: items under a theme with no options of their own; the theme's option list is the
    # first block of that theme that does have options
    out, emqs, dropped = [], collections.OrderedDict(), 0
    for r in recs:
        if r['theme'] and len(r['options']) < 3:
            e = emqs.setdefault(r['theme'], dict(type='EMQ', theme=r['theme'], options=[], items=[]))
            e['items'].append(dict(n=len(e['items']) + 1, stem=r['stem'], answer=r['answer'], explanation=r['explanation'], images=[]))
        elif r['theme'] and r['theme'] in emqs and not emqs[r['theme']]['options']:
            emqs[r['theme']]['options'] = r['options']
        elif len(r['options']) >= 3:
            out.append(dict(type='MCQ', stem=r['stem'], options=r['options'], answer=r['answer'], explanation=r['explanation']))
        else:
            dropped += 1                  # numbered lines without options: contents lists, headings…
    if dropped:
        print('  (skipped %d numbered lines without options — contents entries, headings, notes)' % dropped)
    return out + [e for e in emqs.values() if e['items']]


# ------------------------------------------------------------------ chapter classification
def classify(rec):
    if CHAPTER:
        return CHAPTER
    c = (rec.get('chapter') or '').strip()
    ids = {ch['id'] for ch in book['chapters']}
    if c in ids:
        return c
    for ch in book['chapters']:
        if c and c.lower() in (ch['title'].lower(), ch.get('short', '').lower()):
            return ch['id']
    text = ' '.join([rec.get('stem', ''), rec.get('theme', '') or '', ' '.join(rec.get('options', []))]).lower()
    best, score = None, 0
    for ch in book['chapters']:
        kws = [k.lower() for k in ch.get('keywords', [])] + [ch.get('short', '').lower()]
        s = sum(text.count(k) for k in kws if k)
        if s > score:
            best, score = ch['id'], s
    return best or 'inbox'


# ------------------------------------------------------------------ run
files = []
if os.path.isdir(SRC):
    for f in sorted(os.listdir(SRC)):
        if os.path.splitext(f)[1].lower() in ('.xlsx', '.xls', '.csv', '.pdf', '.txt', '.md', '.docx', '.indd'):
            files.append(os.path.join(SRC, f))
else:
    files = [SRC]

new = []
if SRC.lower().endswith('.json'):                    # a staged file from data/import: merge as-is
    staged = json.load(open(SRC, encoding='utf-8'))
    ids = {q['id'] for q in Q}
    dup = [r['id'] for r in staged if r['id'] in ids]
    if dup:
        sys.exit('staged ids already exist: %s' % dup[:10])
    json.dump(Q + staged, open(QF, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    sys.exit('merged %d staged records' % len(staged))
for f in files:
    ext = os.path.splitext(f)[1].lower()
    recs = parse_table(f) if ext in ('.xlsx', '.xls', '.csv') else parse_text(text_from(f))
    for r in recs:
        r['bank'] = r.get('bank') or BANK or 'Other Sources'
        r['source'] = r.get('source') or SOURCE or os.path.basename(f)
        r['chapter'] = classify(r)
    new += recs
    print('%-40s %d records' % (os.path.basename(f)[:40], len(recs)))

# ids + order
maxn = collections.defaultdict(int)
maxo = collections.defaultdict(int)
for q in Q:
    m = re.match(r'^(\w+)-(\d+)$', q['id'])
    if m and int(m.group(2)) < 900:
        maxn[m.group(1)] = max(maxn[m.group(1)], int(m.group(2)))
    maxo[q['chapter']] = max(maxo[q['chapter']], q.get('order', 0))
existing = {q['id'] for q in Q}
created = []
for r in new:
    ch = r['chapter']
    if not r.get('id') or r['id'] in existing:
        maxn[ch] += 1
        r['id'] = '%s-%04d' % (ch, maxn[ch])
    maxo[ch] += 10
    rec = dict(id=r['id'], chapter=ch, order=maxo[ch], type=r['type'], bank=r['bank'], source=r['source'], status=STATUS,
               topics=r.get('topics', []), notes=r.get('notes', ''), images=r.get('images', []),
               imported=dict(file=os.path.basename(SRC), at=time.strftime('%Y-%m-%d %H:%M')))
    if r['type'] == 'EMQ':
        rec.update(theme=r['theme'], options=r['options'], option_letters=list(LET[:len(r['options'])]), items=r['items'], answer='', stem='', explanation='')
    else:
        rec.update(stem=r['stem'], options=r['options'], answer=r['answer'], explanation=r['explanation'])
    rec['orig'] = {k: rec.get(k) for k in ('stem', 'options', 'answer', 'explanation', 'theme', 'items') if k in rec}
    created.append(rec)
    existing.add(rec['id'])

# report
mcq = [r for r in created if r['type'] == 'MCQ']
emq = [r for r in created if r['type'] == 'EMQ']
print('\nparsed %d MCQs, %d EMQs (%d items)' % (len(mcq), len(emq), sum(len(e['items']) for e in emq)))
print('  MCQs with a key: %d   with explanation: %d   with <3 options: %d' % (
    sum(1 for r in mcq if r['answer']), sum(1 for r in mcq if r['explanation']), sum(1 for r in mcq if len(r['options']) < 3)))
print('  per chapter:', dict(collections.Counter(r['chapter'] for r in created)))
if any(r['chapter'] == 'inbox' for r in created):
    print('  NOTE: some records went to chapter "inbox"; move them with a patch ("set": {"chapter": ...}).')
if DRY:
    for r in created[:5]:
        print(json.dumps(r, ensure_ascii=False)[:400])
    sys.exit()
if STAGE:
    d = os.path.join(ROOT, 'data', 'import'); os.makedirs(d, exist_ok=True)
    out = os.path.join(d, re.sub(r'\W+', '_', os.path.basename(SRC)) + '.json')
    json.dump(created, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('staged ->', out, '(merge later with: python tools/import_source.py', out, ')')
    sys.exit()
if not any(ch['id'] == 'inbox' for ch in book['chapters']) and any(r['chapter'] == 'inbox' for r in created):
    book['chapters'].append(dict(id='inbox', order=99, part='Unsorted', title='Inbox (unsorted)', short='Inbox', color='98A2B3',
                                 intro='', divider=dict(image='', credit=''), summaries=[], appendix=True))
    json.dump(book, open(BF, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
os.makedirs(os.path.join(ROOT, 'data', 'backups'), exist_ok=True)
if os.path.exists(QF):
    json.dump(Q, open(os.path.join(ROOT, 'data', 'backups', 'questions-before-import-%s.json' % time.strftime('%Y%m%d-%H%M%S')), 'w', encoding='utf-8'), ensure_ascii=False)
json.dump(Q + created, open(QF, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('added %d records to questions.json: %s … %s' % (len(created), created[0]['id'] if created else '-', created[-1]['id'] if created else '-'))
