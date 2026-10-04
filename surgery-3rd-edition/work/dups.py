"""Candidate duplicate clusters (same idea) across all MCQs: TF-IDF on stem + key option."""
import json, re, collections
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
Q = [q for q in json.load(open('data/questions.json')) if q['type'] == 'MCQ' and q.get('status') != 'deleted']
def key_text(q):
    try: return q['options'][ord(q['answer']) - 65]
    except Exception: return ''
docs = [re.sub(r'\d+', ' ', (q['stem'] + ' ' + key_text(q) + ' ' + key_text(q)).lower()) for q in Q]
v = TfidfVectorizer(stop_words='english', ngram_range=(1, 2), min_df=1, sublinear_tf=True)
X = v.fit_transform(docs)
S = cosine_similarity(X)
parent = list(range(len(Q)))
def f(i):
    while parent[i] != i:
        parent[i] = parent[parent[i]]; i = parent[i]
    return i
pairs = []
for i in range(len(Q)):
    for j in range(i + 1, len(Q)):
        a, b = Q[i]['stem'], Q[j]['stem']
        pre = len(__import__('os').path.commonprefix([a, b]))
        if pre > 100 and key_text(Q[i]).lower()[:15] != key_text(Q[j]).lower()[:15]:
            continue
        if S[i, j] >= 0.42:
            pairs.append((S[i, j], i, j)); parent[f(i)] = f(j)
cl = collections.defaultdict(list)
for i in range(len(Q)):
    cl[f(i)].append(i)
clusters = [sorted(m, key=lambda k: Q[k]['id']) for m in cl.values() if len(m) > 1]
out = [[dict(id=Q[k]['id'], bank=Q[k]['bank'], src=Q[k]['source'], key=key_text(Q[k])[:50], stem=Q[k]['stem'][:160]) for k in m] for m in clusters]
json.dump(out, open('work/dup_clusters.json', 'w'), indent=1, ensure_ascii=False)
print('pairs', len(pairs), 'clusters', len(clusters), 'items', sum(len(c) for c in clusters))
