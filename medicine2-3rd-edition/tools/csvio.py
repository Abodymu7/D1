"""CSV <-> data/questions.json

  python csvio.py export [out.csv]      full book CSV (one row per MCQ / per EMQ item), UTF-8 with BOM for Excel
  python csvio.py import in.csv         merge rows back (by id; rows without id are created)
"""
import csv, json, os, sys, time, shutil, re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
QF = os.path.join(ROOT, 'data', 'questions.json')
BF = os.path.join(ROOT, 'data', 'book.json')
MAXOPT = 16
COLS = (['id', 'chapter', 'chapter_title', 'bank', 'source', 'type', 'order', 'emq_theme', 'emq_options', 'item_no', 'stem']
        + ['option_%s' % chr(65 + i) for i in range(MAXOPT)]
        + ['answer', 'answer_text', 'explanation', 'images', 'topics', 'status', 'notes', 'v31_page'])


def load():
    return json.load(open(QF, encoding='utf-8')), json.load(open(BF, encoding='utf-8'))


def save(qs):
    bak = os.path.join(ROOT, 'data', 'backups')
    os.makedirs(bak, exist_ok=True)
    shutil.copy(QF, os.path.join(bak, 'questions-%s.json' % time.strftime('%Y%m%d-%H%M%S')))
    json.dump(qs, open(QF, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


def export(path):
    qs, book = load()
    titles = {c['id']: c['title'] for c in book['chapters']}
    order = {c['id']: c['order'] for c in book['chapters']}
    qs = sorted(qs, key=lambda q: (order.get(q['chapter'], 99), q['bank'], q['type'], q['order']))
    with open(path, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, COLS)
        w.writeheader()
        for q in qs:
            base = dict(id=q['id'], chapter=q['chapter'], chapter_title=titles.get(q['chapter'], ''), bank=q['bank'],
                        source=q.get('source', ''), type=q['type'], order=q['order'], topics='; '.join(q.get('topics', [])),
                        status=q.get('status', ''), notes=q.get('notes', ''), v31_page=(q.get('v31') or {}).get('page', ''))
            if q['type'] == 'MCQ':
                r = dict(base, stem=q['stem'], answer=q.get('answer', ''), explanation=q.get('explanation', ''),
                         images='; '.join(q.get('images', [])))
                for i, o in enumerate(q['options'][:MAXOPT]):
                    r['option_%s' % chr(65 + i)] = o
                L = q.get('answer') or ''
                if L and 0 <= ord(L) - 65 < len(q['options']):
                    r['answer_text'] = q['options'][ord(L) - 65]
                w.writerow(r)
            else:
                letters = q.get('option_letters') or [chr(65 + i) for i in range(len(q['options']))]
                opts = ' | '.join('%s) %s' % (l, o) for l, o in zip(letters, q['options']))
                for it in q['items']:
                    r = dict(base, emq_theme=q.get('theme', ''), emq_options=opts, item_no=it['n'], stem=it['stem'],
                             answer=it.get('answer', ''), explanation=it.get('explanation', ''), images='; '.join(it.get('images', [])))
                    for i, o in enumerate(q['options'][:MAXOPT]):
                        r['option_%s' % letters[i]] = o
                    if it.get('answer') in letters:
                        r['answer_text'] = q['options'][letters.index(it['answer'])]
                    w.writerow(r)
    print('exported', path)


def split_list(s):
    return [x.strip() for x in (s or '').split(';') if x.strip()]


def do_import(path):
    qs, book = load()
    by = {q['id']: q for q in qs}
    rows = list(csv.DictReader(open(path, encoding='utf-8-sig')))
    counters = {}
    for q in qs:
        m = re.match(r'^([a-z]+)-(\d+)$', q['id'])
        if m:
            counters[m.group(1)] = max(counters.get(m.group(1), 0), int(m.group(2)))
    changed = created = 0
    emq_seen = {}
    for r in rows:
        ch = (r.get('chapter') or '').strip()
        typ = (r.get('type') or 'MCQ').strip().upper()
        opts = [r.get('option_%s' % chr(65 + i), '').strip() for i in range(MAXOPT)]
        while opts and not opts[-1]:
            opts.pop()
        qid = (r.get('id') or '').strip()
        if not qid:
            counters[ch] = counters.get(ch, 0) + 1
            qid = '%s-%04d' % (ch, counters[ch] + 9000)
            r['id'] = qid
        q = by.get(qid)
        if q is None:
            q = dict(id=qid, chapter=ch, type=typ, order=int(float(r.get('order') or 99990)), status='new', notes='', topics=[])
            if typ == 'MCQ':
                q.update(stem='', options=[], answer='', explanation='', images=[])
            else:
                q.update(theme='', options=[], option_letters=[], items=[])
            qs.append(q); by[qid] = q; created += 1
        before = json.dumps(q, sort_keys=True)
        q['chapter'] = ch or q['chapter']
        q['bank'] = r.get('bank') or q.get('bank', '')
        q['source'] = r.get('source', q.get('source', ''))
        if r.get('order'):
            q['order'] = int(float(r['order']))
        q['topics'] = split_list(r.get('topics'))
        q['status'] = r.get('status') or q.get('status', '')
        q['notes'] = r.get('notes', '')
        if typ == 'MCQ':
            q['stem'] = r.get('stem', '')
            q['options'] = opts
            q['answer'] = (r.get('answer') or '').strip().upper()
            q['explanation'] = r.get('explanation', '')
            q['images'] = split_list(r.get('images'))
        else:
            q['theme'] = r.get('emq_theme', q.get('theme', ''))
            if r.get('emq_options'):
                pairs = [p.strip() for p in r['emq_options'].split(' | ') if p.strip()]
                q['option_letters'] = [p.split(')', 1)[0].strip() for p in pairs]
                q['options'] = [p.split(')', 1)[1].strip() if ')' in p else p for p in pairs]
            if qid not in emq_seen:
                emq_seen[qid] = []
            n = int(float(r.get('item_no') or len(emq_seen[qid]) + 1))
            it = next((x for x in q['items'] if x['n'] == n), None)
            if it is None:
                it = dict(n=n, stem='', answer='', explanation='', images=[])
                q['items'].append(it)
            it['stem'] = r.get('stem', '')
            it['answer'] = (r.get('answer') or '').strip().upper()
            it['explanation'] = r.get('explanation', '')
            it['images'] = split_list(r.get('images'))
            emq_seen[qid].append(n)
        if json.dumps(q, sort_keys=True) != before:
            changed += 1
    # EMQ items missing from the CSV are removed
    for qid, ns in emq_seen.items():
        by[qid]['items'] = sorted([x for x in by[qid]['items'] if x['n'] in ns], key=lambda x: x['n'])
    save(qs)
    print('imported', len(rows), 'rows; changed', changed, 'created', created)


if __name__ == '__main__':
    if sys.argv[1] == 'export':
        export(sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, 'data', 'questions.csv'))
    else:
        do_import(sys.argv[2])
