"""Parse EMQ chapters from work/stream.txt -> data/raw_emq.json (themes with options, items, source answer hints)."""
import json, os, re, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
lines = []
for ln in open(os.path.join(HERE, 'stream.txt'), encoding='utf-8'):
    pg, t = ln.rstrip('\n').split('\t', 1)
    pg = int(pg)
    if 177 <= pg <= 233 or 346 <= pg <= 377:
        lines.append((pg, t.strip()))

BANKS = [(r'formative', 'Formative & Previous Years'), (r'irfan', 'Irfan'), (r'get a ?head', 'Get Ahead'), (r'crash', 'Crash Course'),
         (r'2016|2019', 'Formative & Previous Years'), (r'pre ?-?test', 'PreTest'), (r'passmed', 'Passmedicine'),
         (r'pastest', 'PasTest'), (r'other|previous', 'Other Sources')]
TH = re.compile(r'^Theme\s*(\d+)\s*[:\-]?\s*(.*)$', re.I)
THA = re.compile(r'^Theme\s*(\d+)\s*answers?\b', re.I)
OPT = re.compile(r'^([A-Za-z])[\.\)]\s+(.*)$')
ITEM = re.compile(r'^(?:Q)?(\d{1,2})[\.\)\-:]\s*(.*)$')

themes, cur, mode, bank, section = [], None, None, 'Other Sources', None
answers = collections.defaultdict(list)   # (section id, theme no) -> raw lines
sec_id = 0
ans_key = None
for pg, t in lines:
    if t.startswith('-----'):
        continue
    low = t.lower()
    if re.search(r"emq", low) and len(t) < 45 and not TH.match(t):
        if 'answer' in low:
            mode = 'ans'
            continue
        for rx, b in BANKS:
            if re.search(rx, low):
                bank = b
                break
        sec_id += 1
        mode = None
        continue
    ma = THA.match(t)
    if ma or re.match(r'^Theme\s*\d+\s*answers', t, re.I):
        ans_key = (sec_id, int(ma.group(1)))
        mode = 'ans'
        continue
    m = TH.match(t)
    if m and mode != 'ans' or (m and mode == 'ans' and not re.search('answer', low)):
        if m:
            cur = dict(section=sec_id, bank=bank, no=int(m.group(1)), theme=m.group(2).strip(' :'), page=pg,
                       options={}, _order=[], items=[], images=[], note='')
            themes.append(cur)
            mode = 'opt'
            continue
    if mode == 'ans':
        if ans_key:
            answers[ans_key].append(t)
        continue
    if cur is None:
        continue
    if t.startswith('[[IMG:'):
        cur['images'].append(t[6:-2])
        continue
    if re.match(r'^questions?$', low):
        mode = 'items'
        continue
    if mode == 'opt':
        mo = OPT.match(t)
        if mo:
            L = mo.group(1).upper()
            cur['options'][L] = mo.group(2)
            cur['_order'].append(L)
        elif cur['_order']:
            cur['options'][cur['_order'][-1]] += ' ' + t
        else:
            cur['note'] += ' ' + t
    elif mode == 'items':
        mi = ITEM.match(t)
        if mi:
            cur['items'].append(dict(n=int(mi.group(1)), stem=mi.group(2)))
        elif cur['items']:
            cur['items'][-1]['stem'] += ' ' + t
        else:
            cur['note'] += ' ' + t

out = []
for th in themes:
    letters = sorted(th['options'])
    ans_raw = ' '.join(answers.get((th['section'], th['no']), []))
    out.append(dict(section=th['section'], bank=th['bank'], no=th['no'], theme=th['theme'], page=th['page'],
                    chapter='cvsemq' if th['page'] <= 233 else 'resemq',
                    option_letters=letters, options=[re.sub(r'\s+', ' ', th['options'][L]).strip() for L in letters],
                    items=[dict(n=i['n'], stem=re.sub(r'\s+', ' ', i['stem']).strip()) for i in th['items']],
                    images=th['images'], note=th['note'].strip(), answers_raw=ans_raw))
json.dump(out, open(os.path.join(ROOT, 'data', 'raw_emq.json'), 'w'), ensure_ascii=False, indent=1)
print('themes', len(out), 'items', sum(len(t['items']) for t in out))
print(collections.Counter((t['chapter'], t['bank']) for t in out))
for t in out:
    if len(t['options']) < 3 or not t['items']:
        print('CHECK', t['chapter'], t['bank'], t['no'], t['theme'][:40], len(t['options']), len(t['items']))
