"""Apply review patches (data/patches/*.json) to data/questions.json and log every change.

Patch file = JSON list of operations:
  {"id": "pit-0002", "set": {field: value, ...}, "items": {"1": {field: value}}, "status": "corrected", "why": "..."}
  {"id": "pit-0007", "delete": true, "why": "duplicate of pit-0003"}
  {"new": {full question record incl. id}, "why": "..."}
Each patch file is applied once (names recorded in data/patches/applied.txt).
  python apply.py            apply pending patches
  python apply.py --force f  re-apply one file
"""
import csv, json, os, sys, time, shutil

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
QF = os.path.join(ROOT, 'data', 'questions.json')
PD = os.path.join(ROOT, 'data', 'patches')
APPLIED = os.path.join(PD, 'applied.txt')
LOG = os.path.join(ROOT, 'data', 'corrections.csv')
os.makedirs(PD, exist_ok=True)

Q = json.load(open(QF, encoding='utf-8'))
by = {q['id']: q for q in Q}
done = set(open(APPLIED, encoding='utf-8').read().split()) if os.path.exists(APPLIED) else set()
force = sys.argv[sys.argv.index('--force') + 1] if '--force' in sys.argv else None
files = sorted(f for f in os.listdir(PD) if f.endswith('.json') and (f not in done or f == force))
if not files:
    print('nothing to apply'); sys.exit()

new_log = not os.path.exists(LOG)
logf = open(LOG, 'a', encoding='utf-8-sig' if new_log else 'utf-8', newline='')
lw = csv.writer(logf)
if new_log:
    lw.writerow(['time', 'patch', 'id', 'field', 'before', 'after', 'why'])
T = time.strftime('%Y-%m-%d %H:%M')


def short(v):
    s = v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)
    return s if len(s) < 400 else s[:397] + '...'


shutil.copy(QF, os.path.join(ROOT, 'data', 'backups', 'questions-before-%s.json' % time.strftime('%Y%m%d-%H%M%S')))
stats = {'changed': 0, 'deleted': 0, 'new': 0, 'missing': 0}
for fn in files:
    ops = json.load(open(os.path.join(PD, fn), encoding='utf-8'))
    for op in ops:
        why = op.get('why', '')
        if 'new' in op:
            rec = op['new']
            rec.setdefault('status', 'new'); rec.setdefault('topics', []); rec.setdefault('notes', '')
            if rec['id'] in by:
                Q.remove(by[rec['id']])
            Q.append(rec); by[rec['id']] = rec
            lw.writerow([T, fn, rec['id'], 'NEW', '', short(rec.get('stem') or rec.get('theme', '')), why]); stats['new'] += 1
            continue
        q = by.get(op['id'])
        if q is None:
            print('missing', op['id'], fn); stats['missing'] += 1; continue
        if op.get('delete'):
            q['prev_status'] = q.get('status'); q['status'] = 'deleted'
            if op.get('dup_of'):
                q['dup_of'] = op['dup_of']
            if op.get('silent'):
                q['dup_silent'] = True
            lw.writerow([T, fn, q['id'], 'DELETED', '', '', why]); stats['deleted'] += 1
            continue
        for k, v in (op.get('set') or {}).items():
            if q.get(k) != v:
                if k not in ('topics', 'order', 'explanation'):
                    lw.writerow([T, fn, q['id'], k, short(q.get(k, '')), short(v), why])
                elif k == 'explanation':
                    lw.writerow([T, fn, q['id'], k, short(q.get(k, '')), '(rewritten)', why])
                q[k] = v
        for n, fields in (op.get('items') or {}).items():
            it = next((x for x in q.get('items', []) if str(x['n']) == str(n)), None)
            if it is None:
                it = dict(n=int(n), stem='', answer='', explanation='', images=[]); q['items'].append(it)
            for k, v in fields.items():
                if it.get(k) != v:
                    if k != 'explanation':
                        lw.writerow([T, fn, '%s#%s' % (q['id'], n), k, short(it.get(k, '')), short(v), why])
                    it[k] = v
        if 'items_order' in op:
            q['items'] = sorted(q['items'], key=lambda x: x['n'])
        if op.get('status'):
            q['status'] = op['status']
        stats['changed'] += 1
    done.add(fn)
json.dump(Q, open(QF, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
open(APPLIED, 'w', encoding='utf-8').write('\n'.join(sorted(done)))
logf.close()
print(files, stats)
