"""Deliverable CSVs:
  output/questions.csv          every live question / EMQ item with its number in the book, answer, explanation,
                                topics, status and the repeat caption
  output/removed-duplicates.csv every question removed as a repeated idea, with the question it was merged into
"""
import csv, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, os.path.join(ROOT, 'build'))
import gen
import book as HB

B = gen.book
titles = {c['id']: c['title'] for c in B['chapters']}
num = {}
n = 0
rows = []
for c in B['chapters']:
    for q in gen.chapter_questions(c['id']):
        cap = ''
        if q['id'] in HB.CAP:
            k, order = HB.CAP[q['id']]
            cap = 'Repeated idea %dx: %s' % (k, '; '.join('%s%s' % (b, ' x%d' % m if m > 1 else '') for b, m in order))
        base = dict(chapter=c['order'], chapter_title=c['title'], id=q['id'], bank=q['bank'], type=q['type'],
                    topics='; '.join(q.get('topics', [])), status=q.get('status', ''), repeat_caption=cap)
        if q['type'] == 'MCQ':
            n += 1; num[q['id']] = n
            r = dict(base, number=n, stem=q['stem'], answer=q['answer'], answer_text=q['options'][ord(q['answer']) - 65],
                     explanation=q['explanation'], images='; '.join(q.get('images', [])))
            for i, o in enumerate(q['options']):
                r['option_' + chr(65 + i)] = o
            rows.append(r)
        else:
            L = q['option_letters']
            first = n + 1
            for it in q['items']:
                n += 1
                r = dict(base, number=n, emq_theme=q['theme'], emq_options=' | '.join('%s) %s' % x for x in zip(L, q['options'])),
                         item=it['n'], stem=it['stem'], answer=it['answer'], answer_text=q['options'][L.index(it['answer'])],
                         explanation=it['explanation'], images='; '.join(it.get('images', [])))
                rows.append(r)
            num[q['id']] = first
cols = ['number', 'chapter', 'chapter_title', 'id', 'bank', 'type', 'emq_theme', 'emq_options', 'item', 'stem'] + \
       ['option_' + chr(65 + i) for i in range(8)] + ['answer', 'answer_text', 'explanation', 'topics', 'images', 'status', 'repeat_caption']
with open(os.path.join(ROOT, 'output', 'questions.csv'), 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, cols, extrasaction='ignore'); w.writeheader(); w.writerows(rows)

Q = {q['id']: q for q in gen.questions}
out = []
for q in gen.questions:
    if q.get('status') != 'deleted':
        continue
    t = q.get('dup_of') or ''
    seen = set()
    while t and Q[t].get('status') == 'deleted' and Q[t].get('dup_of') and t not in seen:
        seen.add(t); t = Q[t]['dup_of']
    why = ''
    out.append(dict(id=q['id'], chapter=titles.get(q['chapter'], q['chapter']), bank=q['bank'], type=q['type'],
                    stem=q.get('stem') or q.get('theme', ''), kept_as=t, kept_number=num.get(t, ''),
                    counted_in_caption='no' if (q.get('dup_silent') or not t) else 'yes'))
logwhy = {}
for r in csv.DictReader(open(os.path.join(ROOT, 'data', 'corrections.csv'), encoding='utf-8-sig')):
    if r['field'] == 'DELETED':
        logwhy[r['id']] = r['why']
for r in out:
    r['reason'] = logwhy.get(r['id'], '')
with open(os.path.join(ROOT, 'output', 'removed-duplicates.csv'), 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, ['id', 'chapter', 'bank', 'type', 'stem', 'kept_as', 'kept_number', 'counted_in_caption', 'reason'])
    w.writeheader(); w.writerows(out)
print('questions', len(rows), 'removed', len(out))
