"""Print questions compactly for review.  python dump.py <chapter> [start] [count] [--raw]"""
import json, os, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
Q = json.load(open(os.path.join(ROOT, 'data', 'questions.json'), encoding='utf-8'))
ch = sys.argv[1]
start = int(sys.argv[2]) if len(sys.argv) > 2 else 0
count = int(sys.argv[3]) if len(sys.argv) > 3 else 9999
raw = '--raw' in sys.argv
qs = [q for q in Q if q['chapter'] == ch and q.get('status') != 'deleted']
for q in qs[start:start + count]:
    if q['type'] == 'MCQ':
        print('### %s [%s | %s] ans=%s' % (q['id'], q['bank'], q.get('source', ''), q.get('answer')))
        print('Q:', q['stem'])
        for i, o in enumerate(q['options']):
            print('  %s) %s' % (chr(65 + i), o))
        print('E:', q.get('explanation', ''))
        if q.get('images'):
            print('IMG:', q['images'])
        if raw and q.get('orig'):
            print('RAW:', q['orig'].get('raw', '')[:1500])
            print('RAWANS:', q['orig'].get('answer_raw', '')[:800])
    else:
        L = q.get('option_letters') or [chr(65 + i) for i in range(len(q['options']))]
        print('### %s [%s | %s] EMQ: %s' % (q['id'], q['bank'], q.get('source', ''), q.get('theme')))
        print('  OPTS: ' + ' | '.join('%s) %s' % (l, o) for l, o in zip(L, q['options'])))
        for it in q['items']:
            print('  %d. %s' % (it['n'], it['stem']))
            print('     ans=%s E: %s' % (it.get('answer'), it.get('explanation', '')))
            if raw and it.get('orig'):
                print('     RAWANS:', it['orig'].get('answer_raw', '')[:400])
    print()
print('--- %d of %d records shown (start %d)' % (len(qs[start:start + count]), len(qs), start))
