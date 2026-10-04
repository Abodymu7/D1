"""Turn the editorial review sheets data/review/*.tsv into one patch (data/patches/300-review.json),
plus global text clean-ups applied to every question.

TSV line: id[#n] <TAB> FIELD <TAB> value
FIELD: EX KEY STEM OPTA..OPTP OPTS THEME CH DUP DEL NOTES   (#n = EMQ item number)

The patch is a diff between the base data/questions.json and the reviewed state, so re-running
on a fresh base (python data/import/convert_surg.py) reproduces the reviewed book exactly.
  python tools/review2patch.py [--check]
"""
import json, os, re, sys, glob, copy, collections

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
Q = json.load(open(os.path.join(ROOT, 'data', 'questions.json'), encoding='utf-8'))
BY = {q['id']: q for q in Q}
NEW = {q['id']: copy.deepcopy(q) for q in Q}
DELS = {}          # id -> (dup_of or None, why)
ERR = []

# pairs where the paediatric copy should survive in the paediatric chapter: move the earlier intest/stom copy there
# instead of deleting the paediatric one (see review notes)
SWAP_TO_PAED = True


def fix_text(s):
    if not s:
        return s
    s = (s.replace('”uid', 'fluid').replace('!ssure', 'fissure').replace('speci#c', 'specific').replace(' ! ', ' × ')
         .replace(' ', ' '))
    s = re.sub(r'[ \t]{2,}', ' ', s).strip()
    return s


def fix_option(o):
    o = fix_text(o)
    o = re.sub(r'^\(?[A-Pa-p]\)\s+', '', o)
    return o


def fix_ex(e, options=None):
    e = fix_text(e)
    if not e:
        return e
    e = re.sub(r'^\d+\s*[,.)]\s*', '', e)
    e = re.sub(r'^[A-P][.)]\s+(?=\S)', '', e)
    e = re.sub(r'^[)\]%’\'",;:.\-–•\s]+', '', e)
    e = re.sub(r'[,;]+$', '.', e).strip()
    if e.count('"') % 2 == 1:
        e = e.replace('"', '')
    if e and e[0].islower():
        e = e[0].upper() + e[1:]
    return e


def letters_ok(key, n):
    return bool(key) and all('A' <= ch <= chr(64 + n) for ch in key) and len(set(key)) == len(key)


ops = collections.defaultdict(list)
for f in sorted(glob.glob(os.path.join(ROOT, 'data', 'review', '*.tsv'))):
    for ln, line in enumerate(open(f, encoding='utf-8'), 1):
        line = line.rstrip('\n').rstrip('\r')
        if not line.strip():
            continue
        parts = line.split('\t')
        if len(parts) < 2:
            ERR.append('%s:%d bad line' % (os.path.basename(f), ln)); continue
        ref, field = parts[0].strip(), parts[1].strip()
        val = '\t'.join(parts[2:]).strip() if len(parts) > 2 else ''
        ops[ref.split('#')[0]].append((ref, field, val, '%s:%d' % (os.path.basename(f), ln)))

for qid, lst in ops.items():
    if qid not in NEW:
        ERR.append('unknown id %s (%s)' % (qid, lst[0][3])); continue
    q = NEW[qid]
    # OPTS first so letter-addressed edits refer to the new list
    lst = sorted(lst, key=lambda o: 0 if o[1] == 'OPTS' else 1)
    for ref, field, val, where in lst:
        n = int(ref.split('#')[1]) if '#' in ref else None
        if n is not None:
            if q['type'] != 'EMQ':
                ERR.append('%s item ref on MCQ' % where); continue
            it = next((x for x in q['items'] if x['n'] == n), None)
            if it is None:
                it = dict(n=n, stem='', answer='', explanation='', images=[]); q['items'].append(it)
                q['items'].sort(key=lambda x: x['n'])
            if field == 'EX': it['explanation'] = val
            elif field == 'KEY': it['answer'] = val.strip().upper()
            elif field == 'STEM': it['stem'] = val
            elif field == 'DEL': q['items'] = [x for x in q['items'] if x['n'] != n]
            else: ERR.append('%s field %s on item' % (where, field))
            continue
        if field == 'EX': q['explanation'] = val
        elif field == 'KEY': q['answer'] = val.strip().upper()
        elif field == 'STEM': q['stem'] = val
        elif field == 'THEME': q['theme'] = val
        elif field == 'CH': q['chapter'] = val
        elif field == 'NOTES': q['notes'] = ((q.get('notes') or '') + ' ' + val).strip()
        elif field == 'OPTS':
            q['options'] = [x.strip() for x in val.split('|')]
            if q['type'] == 'EMQ':
                q['option_letters'] = [chr(65 + i) for i in range(len(q['options']))]
        elif re.match(r'OPT[A-P]$', field):
            k = ord(field[3]) - 65
            while len(q['options']) <= k:
                q['options'].append('')
            q['options'][k] = val
            if q['type'] == 'EMQ':
                q['option_letters'] = [chr(65 + i) for i in range(len(q['options']))]
        elif field == 'DUP': DELS[qid] = (val, 'duplicate of %s (%s)' % (val, where))
        elif field == 'DEL': DELS[qid] = (None, val or 'removed in review')
        else: ERR.append('%s unknown field %s' % (where, field))

# paediatric copies: keep them in paed (move the earlier general-chapter twin across)
if SWAP_TO_PAED:
    for qid, (tgt, why) in list(DELS.items()):
        if tgt and NEW[qid]['chapter'] in ('paed', 'paedemq') and NEW.get(tgt, {}).get('chapter') in ('intest', 'stom') \
                and qid.startswith('paed-0') and NEW[qid]['type'] == 'MCQ':
            NEW[tgt]['chapter'] = 'paed'

# a DUP should point at a surviving question (follow chains)
for qid, (tgt, why) in DELS.items():
    if tgt and tgt not in NEW:
        ERR.append('DUP target missing %s -> %s' % (qid, tgt))

def fix_stem(s):
    s = fix_text(s)
    s = re.sub(r'^Regarding to\b', 'Regarding', s)
    s = re.sub(r'\s+,\s*(Which|which)\b', ', which', s)
    s = re.sub(r'^Regarding ([A-Z])(?=[a-z])', lambda m: 'Regarding ' + m.group(1).lower(), s)
    s = re.sub(r'^(Regarding [^.?]{3,80}?)\s*[:,]?\s+(Which|What|All|The following)\b', lambda m: m.group(1) + ', ' + m.group(2)[0].lower() + m.group(2)[1:], s)
    s = re.sub(r'^(Regarding [^.?]{3,80}?), the following', r'\1, the following', s)
    return s


# global clean-ups + validation
for q in NEW.values():
    q['stem'] = fix_stem(q.get('stem', ''))
    q['options'] = [fix_option(o) for o in q.get('options', [])]
    q['images'] = [i for i in q.get('images', []) if not i.endswith('EMBEDDED')]   # embedded INDD graphics could not be recovered
    for it in q.get('items', []):
        it['images'] = [i for i in it.get('images', []) if not i.endswith('EMBEDDED')]
    if q['type'] == 'MCQ':
        q['explanation'] = fix_ex(q.get('explanation', ''), q['options'])
        if q['id'] not in DELS and not letters_ok(q['answer'], len(q['options'])):
            ERR.append('bad key %s %r (%d options)' % (q['id'], q['answer'], len(q['options'])))
    else:
        q['theme'] = fix_text(q.get('theme', ''))
        for it in q['items']:
            it['stem'] = fix_text(it['stem']); it['explanation'] = fix_ex(it['explanation'])
            if q['id'] not in DELS and not letters_ok(it['answer'], len(q['options'])):
                ERR.append('bad key %s#%d %r (%d options)' % (q['id'], it['n'], it['answer'], len(q['options'])))

FIELDS = ['images', 'stem', 'options', 'answer', 'explanation', 'theme', 'option_letters', 'chapter', 'notes']
out = []
for qid, q in NEW.items():
    b = BY[qid]
    if qid in DELS:
        tgt, why = DELS[qid]
        op = dict(id=qid, delete=True, why=why)
        if tgt:
            op['dup_of'] = tgt
        else:
            op['silent'] = True
        out.append(op); continue
    s = {k: q[k] for k in FIELDS if k in q and q.get(k) != b.get(k) and k != 'items'}
    items = {}
    if q['type'] == 'EMQ':
        bi = {x['n']: x for x in b['items']}
        for it in q['items']:
            d = {k: it.get(k) for k in ('stem', 'answer', 'explanation', 'images') if it.get(k) != bi.get(it['n'], {}).get(k)}
            if d:
                items[str(it['n'])] = d
        if [x['n'] for x in q['items']] != [x['n'] for x in b['items']]:
            s['items'] = q['items']; items = {}
    if s or items:
        op = dict(id=qid, status='corrected', why='editorial review (3rd edition)')
        if s: op['set'] = s
        if items: op['items'] = items; op['items_order'] = True
        out.append(op)

print('ops', len(out), 'deletes', sum(1 for o in out if o.get('delete')), 'errors', len(ERR))
for e in ERR[:80]:
    print('  !', e)
if '--check' not in sys.argv:
    p = os.path.join(ROOT, 'data', 'patches', '300-review.json')
    json.dump(out, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('wrote', p)
