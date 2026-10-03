"""Validate patch files WITHOUT applying them.
usage: python3 work/checkpatch.py 'data/patches/12*-peri*.json' [chapter ...]
Checks ids, answer letters, dedupe rules, and (if chapters given) that every live item in those chapters is covered."""
import json, glob, sys
Q = {q['id']: q for q in json.load(open('data/questions.json'))}
ORDER = 'cad hf chd arr valv peri htn cpharm cvsx cvsemq airway resinf crit pleura ild pvasc lca resx resemq'.split()
B39 = '39 Blocks Questions'
files = sorted(glob.glob(sys.argv[1])); chs = sys.argv[2:]
err = []; seen = {}; dels = {}
for f in files:
    try:
        ops = json.load(open(f, encoding='utf-8'))
    except Exception as e:
        err.append('%s: JSON error %s' % (f, e)); continue
    for o in ops:
        if 'new' in o:
            continue
        i = o.get('id'); q = Q.get(i)
        if not q: err.append('%s: unknown id %s' % (f, i)); continue
        if i in seen: err.append('%s: %s also in %s' % (f, i, seen[i]))
        seen[i] = f
        if o.get('delete'):
            t = o.get('dup_of')
            dels[i] = t
            if not o.get('why'): err.append('%s: delete without why' % i)
            if t:
                tq = Q.get(t)
                if not tq: err.append('%s: dup_of unknown %s' % (i, t)); continue
                if t == i: err.append('%s: dup_of self' % i)
                if q['bank'] == B39 and tq['bank'] != B39:
                    err.append('%s: a 39 Blocks item may not be deleted in favour of a non-39B item (%s)' % (i, t))
                if tq['chapter'] != q['chapter'] and not (tq['bank'] == B39 and q['bank'] != B39):
                    if ORDER.index(tq['chapter']) > ORDER.index(q['chapter']):
                        err.append('%s: dup_of %s is in a LATER chapter (only allowed when the target is 39B and this item is not)' % (i, t))
                if tq.get('status') == 'deleted':
                    err.append('%s: dup_of %s which is already deleted (point to its survivor %s)' % (i, t, tq.get('dup_of')))
            continue
        s = o.get('set', {}) or {}
        st = o.get('status')
        if st not in ('expanded', 'corrected'):
            err.append('%s: status must be expanded or corrected' % i)
        if st == 'corrected' and not o.get('why'):
            err.append('%s: corrected without why' % i)
        if q['type'] == 'EMQ':
            L = s.get('option_letters', q.get('option_letters')); opts = s.get('options', q['options'])
            if len(L) != len(opts): err.append('%s: %d letters vs %d options' % (i, len(L), len(opts)))
            items = {str(x['n']): dict(x) for x in q['items']}
            for n, v in (o.get('items') or {}).items():
                items.setdefault(str(n), {}).update(v)
            for n, it in items.items():
                if it.get('delete'): continue
                if it.get('answer') not in L: err.append('%s#%s: answer %r not in letters' % (i, n, it.get('answer')))
                if len(it.get('explanation', '')) < 40: err.append('%s#%s: explanation missing/short' % (i, n))
        else:
            opts = s.get('options', q['options']); a = s.get('answer', q['answer'])
            if not a or len(a) != 1 or ord(a) - 65 >= len(opts) or ord(a) < 65: err.append('%s: bad answer %r for %d options' % (i, a, len(opts)))
            if len(set(x.strip().lower() for x in opts)) != len(opts): err.append('%s: duplicate options' % i)
            if len(s.get('explanation', q.get('explanation', ''))) < 80: err.append('%s: explanation missing/short' % i)
            if not s.get('topics', q.get('topics')): err.append('%s: no topics' % i)
            if s.get('answer') and s['answer'] != q['answer'] and st != 'corrected':
                err.append('%s: answer changed but status is not corrected' % i)
        for x in s.get('images', []):
            import os
            if not os.path.exists('assets/' + x): err.append('%s: image %s not found' % (i, x))
# cycles
for i in dels:
    seen_c = {i}; t = dels[i]
    while t in dels and dels[t]:
        if t in seen_c: err.append('dup_of cycle at %s' % i); break
        seen_c.add(t); t = dels[t]
    if t in dels and not dels[t]: pass
for ch in chs:
    live = [q['id'] for q in Q.values() if q['chapter'] == ch and q.get('status') == 'original']
    miss = [x for x in live if x not in seen]
    print(ch, 'uncovered:', len(miss), ' '.join(miss[:40]))
print('\n'.join(err) or 'OK', '| ops:', len(seen), 'deletes:', len(dels))
