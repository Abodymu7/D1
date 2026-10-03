"""Parse 'Real_med2version3.0' (Internal Medicine Bank, Cardiorespiratory 2025) PDF into raw records.

Output: data/raw_questions.json + work/parse_report.txt + assets/q/*.png (question figures)
"""
import json, os, re, collections
import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
PDF = '/home/claude/med2/Real_med2version3.0 - Copy.pdf'
QDIR = os.path.join(ROOT, 'assets', 'q')
os.makedirs(QDIR, exist_ok=True)

RANGES = [  # (first, last, chapter) original page numbers
    (24, 50, 'cad'), (52, 73, 'hf'), (75, 80, 'chd'), (82, 105, 'arr'), (106, 116, 'valv'),
    (118, 125, 'peri'), (126, 134, 'peri'), (136, 141, 'cad'), (142, 148, 'htn'), (150, 153, 'cpharm'),
    (154, 176, 'cvsx'), (177, 233, 'cvsemq'),
    (248, 254, 'airway'), (255, 263, 'airway'), (264, 281, 'resinf'), (282, 285, 'crit'), (286, 294, 'pleura'),
    (296, 307, 'ild'), (308, 311, 'pvasc'), (312, 321, 'lca'), (322, 345, 'resx'), (346, 377, 'resemq')]
ORIG_CH = [  # original chapter titles (for provenance)
    (24, 50, 'Vascular Diseases'), (52, 73, 'Heart Failure'), (75, 80, 'Congenital Heart Disease'), (82, 105, 'Arrhythmia'),
    (106, 116, 'Valvular Disease'), (118, 125, 'Pericardial Diseases'), (126, 134, 'CVS Inflammatory Diseases'),
    (136, 141, 'Aortic Diseases'), (142, 148, 'Hypertension'), (150, 153, 'CVS Pharma'), (154, 176, "Other CVS MCQ's"),
    (177, 233, "EMQ's of CVS"), (248, 254, 'Asthma'), (255, 263, 'COPD'), (264, 281, 'Respiratory Inflammations'),
    (282, 283, 'ARDS'), (284, 285, 'Respiratory Failure'), (286, 294, 'Pleural Diseases'), (296, 307, 'Interstitial Lung Disease'),
    (308, 311, 'Pulmonary HTN'), (312, 321, 'Lung Cancer'), (322, 345, "Other Respiratory MCQ's"), (346, 377, "EMQ's of Respiratory system")]


def chap(pg, table=RANGES):
    for a, b, c in table:
        if a <= pg <= b:
            return c
    return None


BANK_MAP = [  # (regex on heading, bank)
    (r'end ?blocks?', 'End-Block Exams'), (r'formative', 'Formative & Previous Years'), (r'previous', 'Formative & Previous Years'),
    (r'log ?book', 'Log Book'), (r'davidson', 'Davidson'), (r'harrison', 'Harrison'), (r'crash', 'Crash Course'),
    (r'pre-?test', 'PreTest'), (r'passmedicine', 'Passmedicine'), (r'pastest', 'PasTest'), (r'irfan', 'Irfan'),
    (r'get a ?head', 'Get Ahead'), (r'2016|2019', 'Previous Years EMQs'), (r'other', 'Other Sources'), (r'^mcq', 'Other Sources')]


def bank_of(h):
    hl = h.lower()
    for rx, b in BANK_MAP:
        if re.search(rx, hl):
            return b
    return None


def clean(t):
    t = t.replace('­\n', '').replace('­', '').replace('‑', '-').replace(' ', ' ')
    t = t.replace('﻿', '').replace('‏', '').replace('‎', '')
    return t


doc = pymupdf.open(PDF)
lines = []          # (page, text)  ; images as [[IMG:file]]
img_seen = {}
for pno in range(len(doc)):
    pg = pno + 1
    if not chap(pg):
        continue
    page = doc[pno]
    blocks = []
    for b in page.get_text('dict')['blocks']:
        x0, y0, x1, y1 = b['bbox']
        if b['type'] == 1:
            if b['width'] >= 2400:      # page background
                continue
            key = (b['width'], b['height'], len(b['image']))
            fn = img_seen.get(key)
            if not fn:
                fn = 'o%03d_%d.%s' % (pg, len(img_seen), b.get('ext', 'png'))
                open(os.path.join(QDIR, fn), 'wb').write(b['image'])
                img_seen[key] = fn
            blocks.append((x0, y0, x1, y1, '[[IMG:q/%s]]' % fn))
            continue
        if y0 > 800 and re.fullmatch(r'\s*\d+\s*', ''.join(s['text'] for l in b['lines'] for s in l['spans'])):
            continue        # folio
        txt = '\n'.join(''.join(s['text'] for s in l['spans']) for l in b['lines'])
        blocks.append((x0, y0, x1, y1, txt))
    spanning = any(b[0] < 290 and b[2] > 320 for b in blocks if not b[4].startswith('[[IMG'))
    if spanning:
        blocks.sort(key=lambda b: (round(b[1] / 4), b[0]))
    else:
        blocks.sort(key=lambda b: (0 if b[0] < 298 else 1, b[1]))
    for b in blocks:
        for ln in clean(b[4]).split('\n'):
            if ln.strip():
                lines.append((pg, ln.strip()))

open(os.path.join(HERE, 'stream.txt'), 'w').write('\n'.join('%d\t%s' % l for l in lines))

# ---------------------------------------------------------------- MCQ parse (non-EMQ chapters)
Q_RE = re.compile(r'^(\d{1,3})[\.\)]\s*(.*)')
OPT_RE = re.compile(r'^([A-Ja-j])[\.\)]\s*(.*)')
ANS_RE = re.compile(r'^(\d{1,3})[\.\)]\s*(?:\d{1,3}[\.\)]\s*)?([A-Ja-j])\s*[\.\)\-:]\s*(.*)')

records, report = [], []
bank, heading = None, None
mode = 'q'
cur = None
answers = {}   # (chapter, bank-block id, num) -> (letter, text)
block_id = 0
pending_bank_line = None


def flush():
    global cur
    if cur:
        records.append(cur)
    cur = None


def looks_like_question(i):
    # a numbered line followed (before the next numbered line) by an A. option line
    for k in range(i + 1, min(i + 25, len(L))):
        tt = L[k][1]
        if re.match(r'^[Aa][\.\)]\s', tt):
            return True
        if Q_RE.match(tt) or tt.startswith('-----'):
            return False
    return False


i = 0
L0 = [l for l in lines if chap(l[0]) not in ('cvsemq', 'resemq')]
L = []
for pg_, t_ in L0:
    if re.fullmatch(r"MCQ[’']s:?", t_) and L and len(L[-1][1]) < 40:
        L[-1] = (L[-1][0], L[-1][1] + ' ' + t_)
    else:
        L.append((pg_, t_))
while i < len(L):
    pg, t = L[i]
    nxt = L[i + 1][1] if i + 1 < len(L) else ''
    if t.startswith('-----'):
        i += 1
        continue
    if re.match(r'^answers? of mcq', t, re.I) or t.lower().startswith('answers of'):
        flush(); mode = 'a'; i += 1; continue
    if (nxt.startswith('-----') or (len(t) < 48 and re.search(r"mcq|emq", t, re.I))) and not Q_RE.match(t) and not OPT_RE.match(t):
        b = bank_of(t)
        if b:
            flush(); bank, heading, mode = b, t, 'q'; block_id += 1
            i += 1
            continue
    if mode == 'q':
        m = Q_RE.match(t)
        opt = OPT_RE.match(t)
        if m and not (cur and cur['_opts'] and not cur['_closed'] and False):
            flush()
            cur = dict(num=int(m.group(1)), page=pg, chapter=chap(pg), orig_chapter=chap(pg, ORIG_CH), bank=bank, heading=heading,
                       block=block_id, stem=m.group(2), _opts=[], images=[], _closed=False)
        elif cur is not None and t.startswith('[[IMG:'):
            cur['images'].append(t[6:-2])
        elif cur is not None and opt and (not cur['_opts'] and opt.group(1).upper() == 'A' or cur['_opts'] and ord(opt.group(1).upper()) == 65 + len(cur['_opts'])):
            cur['_opts'].append(opt.group(2))
        elif cur is not None:
            if cur['_opts']:
                cur['_opts'][-1] += ' ' + t
            else:
                cur['stem'] += ' ' + t
        else:
            report.append('orphan q-line p%d: %s' % (pg, t[:80]))
    else:
        t = re.sub(r'^(\d{1,3})\.\s*\1\.\s*', r'\1. ', t)
        m = ANS_RE.match(t)
        if m:
            answers[(block_id, int(m.group(1)))] = [m.group(2).upper(), m.group(3), pg]
            last = (block_id, int(m.group(1)))
        elif re.fullmatch(r'\d{1,3}\.', t) and i + 1 < len(L) and re.match(r'^[A-Ja-j][\.\)]', L[i + 1][1]):
            n0 = int(t[:-1]); m3 = re.match(r'^([A-Ja-j])[\.\)]\s*(.*)', L[i + 1][1])
            answers[(block_id, n0)] = [m3.group(1).upper(), m3.group(2), pg]; last = (block_id, n0); i += 2; continue
        elif Q_RE.match(t) and looks_like_question(i):
            mode = 'q'; block_id += 1; continue
        elif Q_RE.match(t) and not ANS_RE.match(t):
            # a numbered line in answer mode without a letter -> maybe a new question block without heading
            m2 = Q_RE.match(t)
            report.append('answer-mode numbered line without letter p%d: %s' % (pg, t[:90]))
            answers[(block_id, int(m2.group(1)))] = ['?', m2.group(2), pg]
            last = (block_id, int(m2.group(1)))
        elif t.startswith('[[IMG:'):
            report.append('image in answers p%d %s' % (pg, t))
        else:
            try:
                answers[last][1] += ' ' + t
            except NameError:
                report.append('orphan a-line p%d: %s' % (pg, t[:80]))
    i += 1
flush()

# attach answers: by block + num; fall back to the nearest earlier block with same num
by_num = collections.defaultdict(list)
for (blk, n), v in answers.items():
    by_num[n].append((blk, v))
used = set()
out = []
norm = lambda x: re.sub(r'[^a-z0-9]', '', x.lower())
for r in records:
    key = None
    for blk, v in sorted(by_num.get(r['num'], []), key=lambda x: x[0]):
        if blk >= r['block'] and (blk, r['num']) not in used:
            key = (blk, r['num']); break
    opts = [re.sub(r'\s+', ' ', o).strip() for o in r['_opts']]
    rec = dict(num=r['num'], page=r['page'], chapter=r['chapter'], orig_chapter=r['orig_chapter'], bank=r['bank'], heading=r['heading'],
               stem=re.sub(r'\s+', ' ', r['stem']).strip(), options=opts, images=r['images'], answer='', answer_text='')
    if key:
        used.add(key)
        L_, txt, apg = answers[key]
        if L_ == '?':
            mm = re.match(r'^(?:answer:?\s*)?([A-Ja-j])(?:\s+|[\.\)]\s*)(?=[A-Z0-9])', txt, re.I)
            if mm and ord(mm.group(1).upper()) - 65 < max(len(opts), 1):
                L_ = mm.group(1).upper()
        if L_ == '?':
            nt = norm(txt)
            import difflib
            sc = [(difflib.SequenceMatcher(None, nt[:len(norm(o)) + 5], norm(o)).ratio(), k) for k, o in enumerate(opts)]
            if sc and max(sc)[0] > 0.72:
                L_ = chr(65 + max(sc)[1])
            best = None
            for k, o in enumerate(opts):
                no = norm(o)
                if no and (nt.startswith(no[:40]) or no.startswith(nt[:len(no)])):
                    if best is None or len(no) > len(norm(opts[best])):
                        best = k
            if best is not None:
                L_ = chr(65 + best)
                txt = txt  # keep
            else:
                report.append('letterless unmatched: p%d Q%d %s' % (r['page'], r['num'], txt[:60]))
        rec['answer'] = L_
        rec['answer_text'] = re.sub(r'\s+', ' ', txt).strip()
    else:
        report.append('no answer: p%d Q%d %s' % (r['page'], r['num'], rec['stem'][:60]))
    if len(opts) < 3:
        report.append('few options (%d): p%d Q%d %s' % (len(opts), r['page'], r['num'], rec['stem'][:60]))
    out.append(rec)
unused = [k for k in answers if k not in used]
for k in unused:
    report.append('unused answer block %s: %s' % (k, answers[k][1][:70]))
json.dump(out, open(os.path.join(ROOT, 'data', 'raw_mcq.json'), 'w'), ensure_ascii=False, indent=1)
open(os.path.join(HERE, 'parse_report.txt'), 'w').write('\n'.join(report))
print('MCQ records', len(out), 'with answer', sum(1 for r in out if r['answer'] and r['answer'] != '?'), 'report lines', len(report))
print(collections.Counter(r['chapter'] for r in out))
print(collections.Counter(r['bank'] for r in out))
print('images', len(img_seen))
