"""candidate duplicate MCQs across the whole bank (token-set similarity of stem + key text)."""
import json, re, itertools, collections, sys
Q = [q for q in json.load(open('data/questions.json')) if q.get('status') != 'deleted']
TH = float(sys.argv[1]) if len(sys.argv) > 1 else 0.6
STOP = set('a an the of in and or to with is are was for on at by his her he she which what most likely following has have this that be from as it patient year old man woman'.split())
def toks(s): return set(w for w in re.findall(r'[a-z0-9]+', s.lower()) if w not in STOP and len(w) > 2)
U = []
for q in Q:
    if q['type'] == 'MCQ':
        k = ''.join(q['options'][ord(c) - 65] for c in q['answer'] if ord(c) - 65 < len(q['options']))
        U.append((q['id'], q['chapter'], q['bank'], toks(q['stem'] + ' ' + ' '.join(q['options'])), toks(k), q['stem'][:110], k[:40]))
idx = collections.defaultdict(set)
for i, u in enumerate(U):
    for w in u[3]: idx[w].add(i)
seen = set()
for i, u in enumerate(U):
    cand = collections.Counter()
    for w in u[3]:
        if len(idx[w]) < 60:
            for j in idx[w]:
                if j > i: cand[j] += 1
    for j, c in cand.items():
        v = U[j]
        jac = len(u[3] & v[3]) / max(1, len(u[3] | v[3]))
        if jac >= TH and (u[4] & v[4] or not u[4]):
            print('%.2f %s [%s] | %s [%s]\n     %s -> %s\n     %s -> %s' % (jac, u[0], u[2], v[0], v[2], u[5], u[6], v[5], v[6]))
