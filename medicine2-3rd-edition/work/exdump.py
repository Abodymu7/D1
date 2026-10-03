"""Dump explanation units needing shortening: python3 work/exdump.py <start> <n>  (global order of live units with len>LIMIT)"""
import json,sys,re
LIMIT=190
Q=json.load(open('data/questions.json'))
book=json.load(open('data/book.json')); order=[c['id'] for c in book['chapters']]
L=[q for q in Q if q['status']!='deleted']
L.sort(key=lambda q:(order.index(q['chapter']),q['id']))
import glob
DONE=set()
for f in glob.glob('data/shortex/*.tsv'):
    for ln in open(f,encoding='utf-8'):
        if '\t' in ln: DONE.add(ln.split('\t')[0])
units=[]
for q in L:
    if q['type']=='MCQ':
        if len(q['explanation'])>LIMIT and q['id'] not in DONE:
            k=ord(q['answer'])-65
            units.append((q['id'],None,q['stem'],q['options'][k] if k<len(q['options']) else '?',q['explanation']))
    else:
        for it in q['items']:
            if len(it['explanation'])>LIMIT and '%s#%d'%(q['id'],it['n']) not in DONE:
                L2=q['option_letters']; units.append((q['id'],it['n'],it['stem'],q['options'][L2.index(it['answer'])],it['explanation']))
if len(sys.argv)<2: print(len(units)); sys.exit()
a,n=int(sys.argv[1]),int(sys.argv[2])
for i,(qid,itn,stem,key,ex) in enumerate(units[a:a+n]):
    st=stem if len(stem)<220 else stem[:110]+' … '+stem[-100:]
    print('%s%s | Q: %s\n  KEY: %s\n  EX: %s\n'%(qid,'#%d'%itn if itn else '',st,key,ex))
