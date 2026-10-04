import json,glob,sys
Q={q['id']:q for q in json.load(open('data/questions.json'))}
n=0;long=[]
for f in sorted(glob.glob('data/shortex/*.tsv')):
    for i,ln in enumerate(open(f,encoding='utf-8')):
        ln=ln.rstrip('\n')
        if not ln.strip(): continue
        k,t=ln.split('\t')
        qid,_,it=k.partition('#')
        assert qid in Q,(f,k)
        if it: assert any(x['n']==int(it) for x in Q[qid]['items']),k
        n+=1
        if len(t)>200: long.append((len(t),k))
print('units',n,'too long',long)
