"""merge data/import/flows/flow_*.json -> data/essentials.json in book chapter order"""
import json, os, glob
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
book = json.load(open(os.path.join(ROOT, 'data', 'book.json'), encoding='utf-8'))
allf = {}
for f in sorted(glob.glob(os.path.join(HERE, 'flow_*.json'))):
    allf.update(json.load(open(f, encoding='utf-8')))
out = {c['id']: allf[c['id']] for c in book['chapters'] if c['id'] in allf}
json.dump(out, open(os.path.join(ROOT, 'data', 'essentials.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print({k: len(v) for k, v in out.items()})
