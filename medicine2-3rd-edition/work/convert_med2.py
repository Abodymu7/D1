"""Build data/questions.json from raw_mcq.json, raw_emq.json and the 39 Blocks transcription."""
import json, os, re, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
D = os.path.join(ROOT, 'data')

ns = {}
exec(open(os.path.join(D, 'import', 'b39_src.py'), encoding='utf-8').read(), ns)

# ---------------------------------------------------------------- 39 Blocks chapter classification
KW = [
    ('chd', r'atrial septal|ventricular septal|fallot|ductus|coarctation|congenital|fixed splitting'),
    ('peri', r'pericard|tamponade|endocarditis|rheumatic fever|myocarditis|dressler|duke|blood culture|pulsus paradoxus|constrictive'),
    ('valv', r'murmur|stenosis|regurgitation|valve area|opening snap|collapsing pulse|aortic valve|mitral'),
    ('arr', r'atrial fibrillation|heart block|mobitz|tachycardia|bradycardia|digoxin toxicity|qt interval|pr interval|palpitations|fusion beats|av dissociation|cardioversion|ablation'),
    ('hf', r'heart failure|hfpef|ejection fraction|lvef|cardiomyopathy|pulmonary oedema|frothy|sacubitril|spironolactone|bnp'),
    ('htn', r'hypertension|blood pressure of|antihypertensive|secondary hypertension|bp 16|165/'),
    ('cad', r'st elevation|stemi|angina|myocardial infarction|\bmi\b|troponin|pci|chest pain|aortic|aneurysm|dissection|limb|claudication|antiplatelet|risk factor|hdl'),
    ('cpharm', r'drug|medication'),
    ('airway', r'asthma|copd|chronic bronchitis|emphysema|bronchodilator|salbutamol|fev1|peak flow|pef\b|wheez'),
    ('crit', r'respiratory distress|ards|respiratory failure|mechanical ventilation|type 1'),
    ('pleura', r'pleural|empyema|pneumothorax|haemothorax|chest tube'),
    ('ild', r'fibrosis|fibrosing|velcro|pirfenidone|honeycomb|interstitial|alveolitis|bronchiolitis obliterans|reticulonodular'),
    ('pvasc', r'pulmonary embol|ctpa|pulmonary hypertension|d-dimer'),
    ('lca', r'carcinoma|lung cancer|siadh|sodium 1[02]|cushing|dexamethasone|hilar|cytology|mass'),
    ('resinf', r'tubercul|\btb\b|pneumonia|abscess|curb|bronchiectasis|acid-fast|granuloma|covid|infertility'),
]


def classify(q, sysflag):
    txt = (q['s'] + ' ' + ' '.join(q['o'])).lower()
    order = [k for k in KW if (k[0] in ('chd', 'peri', 'valv', 'arr', 'hf', 'htn', 'cad', 'cpharm')) == (sysflag == 'c')]
    for ch, rx in order:
        if re.search(rx, txt):
            return ch
    return 'cvsx' if sysflag == 'c' else 'resx'


OVERRIDE = {}   # (sys, page, num) -> chapter   (filled after review)
try:
    OVERRIDE = {tuple(k.split('|')[:1]) + (int(k.split('|')[1]), int(k.split('|')[2])): v
                for k, v in json.load(open(os.path.join(D, 'import', 'b39_chapters.json'))).items()}
except FileNotFoundError:
    pass

out = []
counters = collections.Counter()


def new_id(ch):
    counters[ch] += 1
    return '%s-%04d' % (ch, counters[ch])


# 39 Blocks MCQs first (order 0..)
for sysflag, lst in (('c', ns['C']), ('r', ns['R'])):
    for i, q in enumerate(lst):
        sf = q.get('sys', sysflag)
        ch = OVERRIDE.get((sf, q['p'], q['n'])) or classify(q, sf)
        rec = dict(id=None, chapter=ch, order=(i + 1) * 10 + (0 if sysflag == 'c' else 5000), type='MCQ', bank='39 Blocks Questions',
                   source='39 Blocks %s p%d Q%d' % ('Cardiology' if sysflag == 'c' else 'Respiratory', q['p'], q['n']), status='original',
                   topics=[], notes='', stem=q['s'], options=q['o'], answer=q['k'], explanation='',
                   images=[q['img']] if q.get('img') else [], src=dict(file='39B-' + sysflag, page=q['p'], num=q['n'], sys=sf))
        rec['orig'] = dict(stem=rec['stem'], options=list(rec['options']), answer=rec['answer'], explanation='')
        out.append(rec)

# original MCQs
for i, r in enumerate(json.load(open(os.path.join(D, 'raw_mcq.json')))):
    rec = dict(id=None, chapter=r['chapter'], order=100000 + i * 10, type='MCQ', bank=r['bank'], source=r['heading'] or '', status='original',
               topics=[], notes='', stem=r['stem'], options=r['options'], answer=(r['answer'] if r['answer'] != '?' else ''),
               explanation='', images=r['images'], src=dict(file='V3', page=r['page'], num=r['num'], orig_chapter=r['orig_chapter']))
    rec['orig'] = dict(stem=r['stem'], options=list(r['options']), answer=r['answer'], explanation=r['answer_text'])
    out.append(rec)

# EMQs: 39 Blocks first, then original
for i, e in enumerate(ns['EMQ']):
    opts = e['o']
    letters = [chr(65 + k) for k in range(len(opts))]
    items = []
    for n, (stem, key) in enumerate(e['items'], 1):
        if len(key) > 1:
            key = letters[opts.index(key)]
        items.append(dict(n=n, stem=stem, answer=key, explanation='', images=[]))
    ch = 'cvsemq' if e['sys'] == 'c' else 'resemq'
    rec = dict(id=None, chapter=ch, order=i * 10, type='EMQ', bank='39 Blocks Questions', source='39 Blocks p%d' % e['p'], status='original',
               topics=[], notes='', theme=e['theme'], options=opts, option_letters=letters, items=items, stem='', answer='', explanation='',
               images=[], src=dict(file='39B-' + e['sys'], page=e['p']))
    rec['orig'] = dict(theme=e['theme'], options=list(opts), items=[dict(i) for i in items])
    out.append(rec)

for i, e in enumerate(json.load(open(os.path.join(D, 'raw_emq.json')))):
    letters = [chr(65 + k) for k in range(len(e['options']))]
    items = [dict(n=it['n'], stem=it['stem'], answer='', explanation='', images=[]) for it in e['items']]
    rec = dict(id=None, chapter=e['chapter'], order=100000 + i * 10, type='EMQ', bank=e['bank'], source='%s EMQ theme %d' % (e['bank'], e['no']),
               status='original', topics=[], notes='source key: ' + e['answers_raw'][:300], theme=e['theme'], options=e['options'],
               option_letters=letters, items=items, stem='', answer='', explanation='', images=e['images'],
               src=dict(file='V3', page=e['page'], theme_no=e['no'], note=e['note']))
    rec['orig'] = dict(theme=e['theme'], options=list(e['options']), answers_raw=e['answers_raw'])
    out.append(rec)

for rec in out:
    rec['id'] = new_id(rec['chapter'])
json.dump(out, open(os.path.join(D, 'questions.json'), 'w'), ensure_ascii=False, indent=1)
c = collections.Counter((r['chapter'], r['type']) for r in out)
print(len(out), sorted(c.items()))
print(collections.Counter(r['chapter'] for r in out if r['bank'] == '39 Blocks Questions' and r['type'] == 'MCQ'))
