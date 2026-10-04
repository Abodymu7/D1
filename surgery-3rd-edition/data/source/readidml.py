import re,os,json,collections
from xml.etree import ElementTree as ET
D='idml'
dm=open(D+'/designmap.xml',encoding='utf-8').read()
spreads=re.findall(r'<idPkg:Spread src="([^"]+)"',dm)
order=[];pages_of_story=collections.defaultdict(list);frames=[]
pageno=0
imgs=[]
for si,sp in enumerate(spreads):
    t=ET.parse(D+'/'+sp).getroot()
    S=t.find('Spread')
    pnames=[p.get('Name') for p in S.findall('Page')]
    for tf in S.iter('TextFrame'):
        st=tf.get('ParentStory')
        if st not in order: order.append(st)
        pages_of_story[st].append((si,pnames))
    for r in S.iter():
        if r.tag in ('Image','PDF','EPS'):
            lk=r.find('Link'); emb=r.find('Properties/Contents') is not None
            imgs.append((si,pnames,r.tag,lk.get('LinkResourceURI') if lk is not None else None,emb))
print('spreads',len(spreads),'stories in frames',len(order),'images',len(imgs), 'embedded',sum(1 for i in imgs if i[4]))
def story_paras(sid):
    t=ET.parse(D+'/Stories/Story_%s.xml'%sid).getroot()
    paras=[];cur=None;curtext=[]
    out=[]
    for psr in t.iter('ParagraphStyleRange'):
        ps=psr.get('AppliedParagraphStyle','').replace('ParagraphStyle/','')
        buf=[]
        for csr in psr:
            if csr.tag!='CharacterStyleRange': continue
            cs=csr.get('AppliedCharacterStyle','').replace('CharacterStyle/','')
            fill=csr.get('FillColor',''); fs=csr.get('FontStyle','')
            for el in csr:
                if el.tag=='Content': buf.append((el.text or '',cs,fill,fs))
                elif el.tag=='Br': buf.append(('\n',cs,fill,fs))
                elif el.tag in ('Rectangle','Group'):
                    names=[]
                    for lk in el.iter('Link'):
                        u=lk.get('LinkResourceURI','')
                        import urllib.parse
                        names.append(urllib.parse.unquote(u.split('/')[-1]))
                    emb=any(True for _ in el.iter('Contents'))
                    buf.append(('[IMG:%s]'%('|'.join(names) if names else ('EMBEDDED' if emb else 'NONE')),cs,fill,fs))
        # split into paragraphs on \n
        line=[]
        for txt,cs,fill,fs in buf:
            parts=txt.split('\n')
            for k,pt in enumerate(parts):
                if k: out.append((ps,line)); line=[]
                if pt: line.append((pt,cs,fill,fs))
        if line: out.append((ps,line))
    return out
allp=[]
for sid in order:
    for ps,line in story_paras(sid):
        allp.append((sid,ps,line))
json.dump(allp,open('paras.json','w'),ensure_ascii=False)
json.dump({'order':order,'imgs':imgs},open('meta.json','w'))
print('paras',len(allp))
c=collections.Counter(p[1] for p in allp); print(c.most_common(40))
