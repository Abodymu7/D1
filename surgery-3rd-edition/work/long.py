import json,sys
Q=json.load(open('data/questions.json'))
chs=sys.argv[1].split(',')
for q in Q:
    if q['chapter'] not in chs: continue
    if q['type']=='MCQ':
        L=len(q['explanation'])
        if L==0 or L>200: print(q['id'],L)
    else:
        for i in q['items']:
            L=len(i['explanation'])
            if L==0 or L>200: print('%s#%d'%(q['id'],i['n']),L)
