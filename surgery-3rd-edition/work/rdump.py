"""compact review dump: python work/rdump.py <chapter> [start] [count]"""
import json,sys
Q=json.load(open('data/questions.json'))
ch=sys.argv[1]; a=int(sys.argv[2]) if len(sys.argv)>2 else 0; n=int(sys.argv[3]) if len(sys.argv)>3 else 9999
qs=[q for q in Q if q['chapter']==ch and q.get('status')!='deleted'][a:a+n]
for q in qs:
    if q['type']=='MCQ':
        opts=' | '.join('%s) %s'%(chr(65+i),o) for i,o in enumerate(q['options']))
        print('## %s [%s %s] %s\n   %s\n   KEY=%s  EX: %s%s'%(q['id'],q['bank'],q['src'].get('num'),q['stem'],opts,q['answer'],q['explanation'][:400],'  IMG='+','.join(q['images']) if q['images'] else ''))
    else:
        opts=' | '.join('%s) %s'%(l,o) for l,o in zip(q['option_letters'],q['options']))
        print('## %s [%s EMQ] THEME: %s\n   OPTS: %s%s'%(q['id'],q['bank'],q['theme'],opts,'  IMG='+','.join(q['images']) if q['images'] else ''))
        for it in q['items']:
            print('   #%d %s\n      KEY=%s EX: %s'%(it['n'],it['stem'],it['answer'],it['explanation'][:300]))
        if q.get('notes'): print('   NOTE:',q['notes'][:300])
