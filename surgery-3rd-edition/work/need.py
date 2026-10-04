import json,sys,collections
Q=json.load(open('data/questions.json'))
c=collections.Counter()
for q in Q:
    if q['type']=='MCQ':
        L=len(q['explanation'])
        if L==0 or L>200: c[q['chapter']]+=1
    else:
        for i in q['items']:
            L=len(i['explanation'])
            if L==0 or L>200: c[q['chapter']]+=1
print(sum(c.values()), c.most_common())
