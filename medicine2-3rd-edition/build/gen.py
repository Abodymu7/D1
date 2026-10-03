"""Generate InDesign tagged text + a JSON manifest from data/book.json + data/questions.json.

Usage: python gen.py [chapter ids...]      (default: every chapter)
Output: build/out/<ch>.txt (UTF-16 tagged text), build/out/manifest.json
"""
import json, os, re, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
OUT = os.path.join(HERE, 'out')
os.makedirs(OUT, exist_ok=True)

book = json.load(open(os.path.join(ROOT, 'data', 'book.json'), encoding='utf-8'))
questions = json.load(open(os.path.join(ROOT, 'data', 'questions.json'), encoding='utf-8'))
cfg = book.get('layout', {})
SET_SIZE = cfg.get('answers_every', 25)          # answers block after at most N questions

DEFAULT_BANK_ORDER = ['Formative & Previous Years', 'End-Block Exams', 'Log Book', 'Davidson', 'Harrison',
              'Crash Course', 'Passmedicine', 'PasTest', 'PreTest', 'Irfan', 'Other Sources', 'Get Ahead SBAs']
DEFAULT_BANK_BLURB = {
    'Formative & Previous Years': 'College formative & previous-years exam questions',
    'End-Block Exams': 'End-block & induction exams 2025',
    'Log Book': 'Log-book questions 2025',
    'Davidson': "After Davidson's Principles & Practice of Medicine self-assessment",
    'Harrison': "After Harrison's Self-Assessment & Board Review",
    'Crash Course': 'After Crash Course SBAs & EMQs',
    'Passmedicine': 'After Passmedicine',
    'PasTest': 'After PasTest',
    'PreTest': 'After PreTest Medicine',
    'Irfan': 'Irfan EMQ collection',
    'Other Sources': 'Other colleges & sources',
    'Get Ahead SBAs': 'Finals-style SBAs written for this edition on the Get Ahead! Medicine topic map',
}


# ---- smart index: topic normalisation + generic facets that become sub-entries
NORM = {
    'Proton pump inhibitors': 'Proton-pump inhibitors', 'MEN 1': 'MEN1', 'ADPKD': 'Autosomal dominant polycystic kidney disease',
    'AKI': 'Acute kidney injury', 'NAFLD': 'Non-alcoholic fatty liver disease', 'MASLD': 'Non-alcoholic fatty liver disease',
    'NASH': 'Non-alcoholic fatty liver disease', 'SLE': 'Systemic lupus erythematosus', 'Antinuclear antibody': 'Antinuclear antibodies',
    'CKD–mineral bone disease': 'CKD–mineral bone disorder', 'E. coli O157': 'E. coli O157:H7',
    'Henoch–Schönlein purpura': 'IgA vasculitis (Henoch–Schönlein purpura)', 'IgA vasculitis': 'IgA vasculitis (Henoch–Schönlein purpura)',
    'Myeloma': 'Multiple myeloma', 'Myeloma cast nephropathy': 'Cast nephropathy', 'Postpartum thyroid disease': 'Postpartum thyroiditis',
    'Stress incontinence': 'Stress urinary incontinence', 'Paraneoplastic': 'Paraneoplastic syndrome',
    'Pancreatogenic diabetes': 'Pancreatic (type 3c) diabetes', 'Haemochromatosis': 'Hereditary haemochromatosis',
    'Sick-day management': 'Sick-day rules', 'Charcot foot': 'Charcot neuroarthropathy', 'Synacthen test': 'Short Synacthen test',
    'Diabetic nephropathy': 'Diabetic kidney disease', 'Bile acid malabsorption': 'Bile acid diarrhoea',
    'Autoimmune polyendocrinopathy': 'Autoimmune polyendocrine syndrome', 'EGPA': 'Eosinophilic granulomatosis with polyangiitis',
    'ANCA vasculitis': 'ANCA-associated vasculitis', 'HBV serology': 'Hepatitis B serology',
    'Gastrinoma (Zollinger–Ellison)': 'Zollinger–Ellison syndrome', "Conn's syndrome": 'Primary hyperaldosteronism',
    "Goodpasture's syndrome": 'Anti-GBM disease', 'Spinal stenosis': 'Lumbar spinal stenosis',
    'Pseudogout': 'Calcium pyrophosphate deposition', 'Acute CPP crystal arthritis': 'Calcium pyrophosphate deposition',
    'Diabetes': 'Diabetes mellitus', 'Diverticulitis': 'Acute diverticulitis', 'Iron deficiency': 'Iron-deficiency anaemia',
    'Pancreatitis': 'Acute pancreatitis', 'Synacthen': 'Short Synacthen test', 'Uraemic pericarditis': 'Uraemia',
}
GENERIC = {
    'Management', 'Mechanism', 'Investigation', 'Complications', 'Clinical features', 'Adverse effects', 'Aetiology',
    'Pathogenesis', 'Pathophysiology', 'Radiology', 'Histology', 'Imaging', 'Prognosis', 'Screening', 'Staging',
    'Surveillance', 'Genetics', 'Drug causes', 'Drug safety', 'Contraindications', 'Differential diagnosis', 'Risk factors',
    'Severity assessment', 'Severity scoring', 'Epidemiology of diabetes', 'Inheritance', 'Extra-articular features', 'Extrarenal features',
    'Classification criteria', 'Diagnostic criteria', 'Clinical signs', 'Precipitants', 'Red flags', 'Alarm features', 'Relapse',
    'Supportive care', 'Joint distribution', 'Infection', 'Older adults', 'Exercise', 'Early worsening', 'X-ray', 'Adherence',
    'Poor adherence', 'Pregnancy', 'Vaccination', 'Resuscitation', 'Trauma', 'Secondary causes', 'Pre-operative assessment',
    'Poor prognostic factors', 'Anaesthesia', 'Drug interactions', 'Drug monitoring', 'Drug contraindications', 'Medicines management',
    'Immunosuppression', 'Analgesia', 'Lifestyle modification', 'Smoking', 'Smoking cessation', 'Malignancy', 'Radiotherapy',
    'Causes', 'Classification', 'Diagnosis', 'Epidemiology', 'Physical examination', 'Critical care', 'Primary prevention', 'Secondary prevention',
    'Risk stratification', 'Haemodynamics', 'Treatment', 'Physiology', 'Examination', 'Emergency management', 'Pharmacology', 'Monitoring',
    'Endoscopy', 'Upper GI endoscopy', 'Colonoscopy', 'Abdominal ultrasound', 'CT abdomen', 'Investigations',
}
GENERIC_LOWER = {g.lower() for g in GENERIC}


def index_entries(topics):
    """[(level1, level2 or '')] for a question's topic list."""
    ts = [NORM.get(t, t) for t in (topics or [])]
    specific = [t for t in ts if t.lower() not in GENERIC_LOWER]
    generic = [t for t in ts if t.lower() in GENERIC_LOWER]
    out = [(t, '') for t in dict.fromkeys(specific)]
    if specific:
        for g in dict.fromkeys(generic):
            out.append((specific[0], g[0].lower() + g[1:] if not g[:2].isupper() else g))
    else:
        out += [(g, '') for g in dict.fromkeys(generic)]
    return out


# book.json may define "banks": [{"name": ..., "blurb": ...}, ...] in print order
if book.get('banks'):
    BANK_ORDER = [b['name'] for b in book['banks']]
    BANK_BLURB = {b['name']: b.get('blurb', '') for b in book['banks']}
else:
    BANK_ORDER, BANK_BLURB = DEFAULT_BANK_ORDER, DEFAULT_BANK_BLURB


def esc(s):
    s = (s or '').replace('\\', '\\\\').replace('<', '\\<').replace('>', '\\>')
    s = s.replace('\r', ' ').replace('\n', ' ')
    return re.sub(r'\s{2,}', ' ', s).strip()


def rich(s):
    """Escape + light markup: **bold**, _italic_ and → arrows kept."""
    s = esc(s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<CharStyle:Bold>\1<CharStyle:>', s)
    return s


SFX = ['']   # current chapter suffix, e.g. '-pit'
GLOBAL_CS = ('Bold', 'Italic')


def P(style, text):
    return '<ParaStyle:%s%s>%s' % (style, SFX[0], text)


def C(style, text):
    return '<CharStyle:%s%s>%s<CharStyle:>' % (style, '' if style in GLOBAL_CS else SFX[0], text)


def chapter_questions(cid):
    qs = [q for q in questions if q['chapter'] == cid and q.get('status') != 'deleted']
    qs.sort(key=lambda q: (BANK_ORDER.index(q['bank']) if q['bank'] in BANK_ORDER else 99,
                           0 if q['type'] == 'MCQ' else 1, q['order']))
    return qs


def build_chapter(ch):
    cid = ch['id']
    SFX[0] = '-' + cid
    qs = chapter_questions(cid)
    lines = []
    anchors_q, anchors_a = [], []           # keys in document order
    banks = collections.OrderedDict()
    for q in qs:
        banks.setdefault((q['bank'], q['type']), []).append(q)
    qn = 0
    bank_list = []
    for (bank, typ), items in banks.items():
        # split into sets
        units = []   # (q, sub-item or None)
        for q in items:
            if q['type'] == 'MCQ':
                units.append((q, None))
            else:
                for it in q['items']:
                    units.append((q, it))
        n_units = len(units)
        sets, cur, count = [], [], 0
        for q in items:
            size = 1 if q['type'] == 'MCQ' else len(q['items'])
            if cur and count + size > SET_SIZE and typ == 'MCQ':
                sets.append(cur); cur, count = [], 0
            cur.append(q); count += size
        if cur:
            sets.append(cur)
        label = '%s %s' % (bank, 'EMQs' if typ == 'EMQ' else 'MCQs')
        bank_key = '%s|%s|%s' % (cid, bank, typ)
        bank_list.append(dict(key=bank_key, title=label, count=n_units))
        lines.append(P('BankKicker', esc(('%d %s' % (n_units, 'EMQ items' if typ == 'EMQ' else 'questions')).upper() + '  •  ' + BANK_BLURB.get(bank, '').upper())))
        lines.append(P('BankHead', esc(label)))
        for si, s in enumerate(sets):
            first_n = qn + 1
            if len(sets) > 1:
                lines.append(P('SetHead', esc('Set %d of %d' % (si + 1, len(sets)))))
            for q in s:
                if q['type'] == 'MCQ':
                    qn += 1
                    key = '%s#%d' % (q['id'], 0)
                    q['_n'] = qn
                    anchors_q.append(dict(key=key, id=q['id'], n=qn, ix=index_entries(q.get('topics', []))))
                    lines.append(P('Q', C('QNum', str(qn)) + '\t' + rich(q['stem'])))
                    for img in q.get('images', []):
                        lines.append(P('QImage', '[[IMG:%s]]' % img))
                    opts = q['options']
                    for i, o in enumerate(opts):
                        st = 'OptLast' if i == len(opts) - 1 else 'Opt'
                        lines.append(P(st, C('OptL', chr(65 + i)) + '\t' + rich(o)))
                else:
                    lines.append(P('EmqTheme', esc('THEME') + '\t' + esc(q['theme'])))
                    letters = q.get('option_letters') or [chr(65 + i) for i in range(len(q['options']))]
                    for i, o in enumerate(q['options']):
                        st = 'EmqOptLast' if i == len(q['options']) - 1 else 'EmqOpt'
                        lines.append(P(st, C('OptL', letters[i]) + '\t' + rich(o)))
                    lines.append(P('EmqLead', esc('For each scenario, choose the single most appropriate option. Each option may be used once, more than once or not at all.')))
                    for it in q['items']:
                        qn += 1
                        key = '%s#%d' % (q['id'], it['n'])
                        it['_n'] = qn
                        anchors_q.append(dict(key=key, id=q['id'], n=qn, ix=index_entries(q.get('topics', []))))
                        lines.append(P('Q', C('QNum', str(qn)) + '\t' + rich(it['stem'])))
                        for img in it.get('images', []):
                            lines.append(P('QImage', '[[IMG:%s]]' % img))
                    qtag = '<ParaStyle:Q%s>' % SFX[0]
                    if lines[-1].startswith(qtag):
                        lines[-1] = '<ParaStyle:QLast%s>' % SFX[0] + lines[-1][len(qtag):]
            # answers for this set
            last_n = qn
            head = 'Answers  %d–%d' % (first_n, last_n) if last_n > first_n else 'Answer  %d' % first_n
            lines.append(P('AnsHead', esc(head) + '\t' + esc(label)))
            for q in s:
                if q['type'] == 'MCQ':
                    key = '%s#%d' % (q['id'], 0)
                    anchors_a.append(dict(key=key))
                    L = (q.get('answer') or '?').upper()
                    idx = ord(L) - 65 if L and L != '?' else -1
                    opt = q['options'][idx] if 0 <= idx < len(q['options']) else ''
                    lines.append(P('Ans', C('ANum', str(q['_n'])) + '\t' + C('ALetter', ' %s ' % L) + ' ' + C('AOpt', rich(opt)) + (' — ' if opt and q.get('explanation') else ' ') + rich(q.get('explanation', ''))))
                else:
                    letters = q.get('option_letters') or [chr(65 + i) for i in range(len(q['options']))]
                    for it in q['items']:
                        key = '%s#%d' % (q['id'], it['n'])
                        anchors_a.append(dict(key=key))
                        L = (it.get('answer') or '?').upper()
                        opt = ''
                        if L in letters:
                            opt = q['options'][letters.index(L)]
                        lines.append(P('Ans', C('ANum', str(it['_n'])) + '\t' + C('ALetter', ' %s ' % L) + ' ' + C('AOpt', rich(opt)) + (' — ' if opt and it.get('explanation') else ' ') + rich(it.get('explanation', ''))))
    header = '<UNICODE-WIN>\r\n<Version:20><FeatureSet:InDesign-Roman>\r\n'
    body = header + '\r\n'.join(lines) + '\r\n'
    path = os.path.join(OUT, '%s.txt' % cid)
    with open(path, 'w', encoding='utf-16-le', newline='') as f:
        f.write(chr(0xFEFF))
        f.write(body)
    return dict(id=cid, file=path.replace('\\', '/'), questions=anchors_q, answers=anchors_a, banks=bank_list,
                n_mcq=sum(1 for q in qs if q['type'] == 'MCQ'),
                n_emq=sum(len(q['items']) for q in qs if q['type'] == 'EMQ'))


def main():
    want = sys.argv[1:]
    chapters = sorted(book['chapters'], key=lambda c: c['order'])
    man = dict(book={k: v for k, v in book.items() if k != 'chapters'}, root=ROOT.replace('\\', '/'), chapters=[])
    for ch in chapters:
        if want and ch['id'] not in want:
            continue
        if not chapter_questions(ch['id']) and not ch.get('summaries'):
            continue
        info = build_chapter(ch)
        info.update({k: ch[k] for k in ('order', 'part', 'title', 'short', 'color', 'divider', 'summaries')})
        info['intro'] = ch.get('intro', '')
        info['appendix'] = bool(ch.get('appendix'))
        man['chapters'].append(info)
        print(ch['id'], len(info['questions']), 'q', len(info['answers']), 'a')
    man['stats'] = dict(mcq=sum(c['n_mcq'] for c in man['chapters']), emq=sum(c['n_emq'] for c in man['chapters']),
                        chapters=len(man['chapters']), new=sum(1 for q in questions if q.get('status') == 'new'),
                        corrected=sum(1 for q in questions if q.get('status') == 'corrected'))
    json.dump(man, open(os.path.join(OUT, 'manifest.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
