import json, sys, collections
Q = json.load(open('data/questions.json'))
cl = json.load(open('work/dup_clusters.json'))
dup = collections.defaultdict(list)
for c in cl:
    for x in c:
        dup[x['id']] += [y['id'] for y in c if y['id'] != x['id']]
ch, a, n = sys.argv[1], sys.argv[2], int(sys.argv[3])
qs = [q for q in Q if q['chapter'] == ch and q.get('status') != 'deleted']
qs.sort(key=lambda q: (0 if q['bank'] == '39 Blocks Questions' else 1, q['order']))
a = next((i for i, q in enumerate(qs) if q['id'] >= a), len(qs)) if '-' in a else int(a)
for q in qs[a:a + n]:
    if q['type'] == 'MCQ':
        s = q.get('src', {})
        print('## %s [%s p%s#%s] key=%s%s%s' % (q['id'], q['bank'][:10], s.get('page'), s.get('num'), q['answer'],
              ' IMG=' + ','.join(q['images']) if q['images'] else '', ' DUP?' + ','.join(dup[q['id']]) if dup[q['id']] else ''))
        print(q['stem'])
        for i, o in enumerate(q['options']):
            print(' %s. %s' % (chr(65 + i), o))
        oe = q.get('orig', {}).get('explanation', '')
        if oe:
            print(' ~', oe[:260])
    else:
        print('## %s [%s p%s] EMQ: %s | %s' % (q['id'], q['bank'], q.get('src', {}).get('page'), q['theme'], q.get('notes', '')[:200]))
        for l, o in zip(q['option_letters'], q['options']):
            print('  %s. %s' % (l, o))
        if q['images']:
            print('  IMG', q['images'])
        for it in q['items']:
            print(' %d) [%s] %s' % (it['n'], it['answer'], it['stem']))
print('-- %d-%d of %d' % (a, a + len(qs[a:a + n]), len(qs)))
