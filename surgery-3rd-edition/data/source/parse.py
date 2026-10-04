"""Parse the Surgery 1 Version 2.0 IDML text (paras.json from readidml.py) into question records."""
import json, re, collections, unicodedata

P = json.load(open('paras.json'))

# story -> chapter at its start (from first page), headers switch chapters inside a story
STORY_START = {'u672': 'neck', 'u4d47': 'neckemq', 'u4ee5': 'bbreast', 'u51d9': 'breastemq', 'u5336': 'saliv', 'u5c05': 'gitemq',
               'u6114': 'paed', 'u6233': 'paedemq', 'u633c': 'acute', 'u6912': 'abdemq', 'u6a3b': 'uti', 'u6df9': 'uroemq',
               'u7010': 'trauma', 'u71b2': 'extraemq'}
SUMMARY_STORIES = {'u49d8': 'neck', 'u72e7': 'bbreast', 'u745a': 'git', 'u74f5': 'git', 'u7544': 'git', 'u75af': 'git', 'u76f3': 'git',
                   'u7651': 'paed', 'u77a4': 'abd', 'u77eb': 'abd', 'u781e': 'abd', 'u784a': 'abd', 'u78f8': 'uro', 'u7a0c': 'extra',
                   'u7a42': 'extra', 'u7a73': 'extra', 'u7aa1': 'extra', 'u7ad0': 'extra', 'u7b00': 'extra', 'u7b40': 'extra'}
HEADERS = {'endocrine diseases': 'endo', 'breast cancers': 'bca', 'salivary glands diseases': 'saliv', 'esophagous diseases': 'oeso',
           'stomach diseases': 'stom', 'intestine diseases': 'intest', 'anus diseases': 'anus', 'git bleeding': 'gibleed',
           'acute abdomen& trauma': 'acute', 'liver diseases': 'liver', 'gallbladder diseases': 'gb', 'pancreatic diseases': 'panc',
           'splenic diseases': 'spleen', 'adrenal gland diseases': 'adrenal', 'hernias diseases': 'hernia', 'uti': 'uti',
           'urinary lithiasis': 'stone', 'renal tumors': 'renal', 'urology': 'urogen', 'urological emergencies': 'uroemerg',
           'prostate diseases': 'prostate', 'congenital urological diseases': 'congur', 'scrotum surgery': 'scrotum',
           'bladder tumors': 'bladder', 'trauma': 'trauma', 'metabolic response to trauma': 'metab', 'shock': 'shock', 'obesity': 'obesity',
           'neck lumps conditions': 'neck'}


def bank_of(name):
    n = name.replace('​', '').strip().lower()
    if 'ministerial' in n: return 'Ministerial Exam'
    if n.startswith('formative'): return 'Formative'
    if n.startswith('previous'): return 'Previous Years'
    if n.startswith('assay'): return 'Essay to MCQ'
    if n.startswith('bailey'): return 'Bailey & Love'
    if n.startswith('lange'): return 'Lange'
    if n.startswith('sba'): return 'SBA'
    if n.startswith('oxford'): return 'Oxford'
    if n.startswith('pre-test'): return 'PreTest'
    if n.startswith('get a head') or n.startswith('get_a_head') or n.startswith('get ahead'): return 'Get Ahead'
    if n.startswith('crash'): return 'Crash Course'
    if n.startswith('irfan'): return 'Irfan'
    raise ValueError(name)


def clean(s):
    s = s.replace('​', '').replace('‑', '-').replace(' ', ' ').replace('﻿', '')
    s = re.sub(r'[ \t]+', ' ', s).strip()
    return s


def norm(s):
    s = unicodedata.normalize('NFKD', s.lower())
    return re.sub(r'[^a-z0-9]+', '', s)


QNUM = re.compile(r'^(\[IMG\]\s*)*(\d{1,3})\s*[.)]\s*(.*)$', re.S)
OPT = re.compile(r'^([A-Z])\s*\.{1,2}\s*(.*)$|^([A-Z])\)\s*(.*)$', re.S)

recs = []          # questions in book order
chapter = None
bank = None
mode = None        # 'mcq' | 'emq_opts' | 'emq_items' | 'ans' | 'emq_ans'
cur = None         # current MCQ or EMQ record
bankq = {}         # number -> MCQ rec, current bank segment
chapq = {}         # number -> MCQ rec, current chapter
pending_case = []
pending_imgs = []
PIMG = []
emq = None
emq_keyed = set()
last_ex = None
summary = collections.defaultdict(list)
order = 0
cur_story = None
themes = {}


def new_mcq(n, stem, img):
    global cur, order
    order += 1
    cur = dict(chapter=chapter, bank=bank, sub=sub_name, type='MCQ', num=n, stem=stem, options=[], answer='', explanation='',
               img=img, order=order, images=pending_imgs + PIMG)
    pending_imgs.clear()
    if pending_case:
        cur['case'] = ' '.join(pending_case)
        pending_case.clear()
    recs.append(cur)
    bankq[n] = cur; chapq[n] = cur


def parse_mcq_answer(q, rest):
    """rest = text after 'N.' : one or more 'L. option text' then explanation"""
    letters = []
    s = rest.strip()
    first = True
    while True:
        m = re.match(r'^,?\s*([A-Pa-p])\s*(?:[.)]|\s-|-|:)?\s+', s) if not first else re.match(r'^([A-Pa-p])\s*(?:[.)]|\s-|-|:)?\s*', s)
        if not m:
            break
        L = m.group(1).upper()
        idx = ord(L) - 65
        if idx >= len(q['options']) or L in letters:
            break
        s2 = s[m.end():]
        opt = q['options'][idx]
        no = norm(opt)
        # for follow-on letters require the option text to be repeated
        if not first and not norm(s2[:len(opt) + 10]).startswith(no[:max(6, min(len(no), 12))]):
            break
        letters.append(L)
        if no:
            acc = ''
            k = 0
            for k in range(len(s2) + 1):
                acc = norm(s2[:k])
                if len(acc) >= len(no):
                    break
            if acc[:len(no)] == no:
                s2 = s2[k:]
            else:
                part = no[:max(6, int(len(no) * .6))]
                if norm(s2[:len(opt) + 10]).startswith(part):
                    s2 = s2[len(opt):]
        s = s2.lstrip(' .,:;)')
        first = False
    return letters, s.strip()

for sid, ps, line in P:
    if sid in SUMMARY_STORIES:
        summary[SUMMARY_STORIES[sid]].append(clean(''.join(x[0] for x in line)))
        continue
    if sid not in STORY_START:
        continue
    if sid in STORY_START and sid != cur_story:
        chapter = STORY_START[sid]
    cur_story = sid
    txt = clean(''.join(x[0] for x in line))
    PIMG = re.findall(r'\[IMG:([^\]]*)\]', txt)
    txt = re.sub(r'\[IMG:[^\]]*\]', '[IMG]', txt).strip()
    if not txt:
        continue
    img = len(PIMG)
    if ps.startswith('Header'):
        key = txt.lower().strip()
        chapter = HEADERS.get(key, chapter)
        if key not in HEADERS:
            print('?? header', txt)
        bankq = {}; chapq = {}
        continue
    if ps == 'subtitle':
        if txt == 'Questions':
            mode = 'emq_items'; continue
        bank = bank_of(txt); sub_name = txt.replace('​', '')
        bankq = {}
        mode = 'mcq'
        continue
    if ps == 'Theme name':
        order += 1
        title = re.sub(r'^(?:Theme\s*)?\d+\s*:\s*', '', txt).strip()
        emq = dict(chapter=chapter, bank=bank, sub=sub_name, type='EMQ', theme=title, theme_label=txt, options=[], items=[], order=order, img=0)
        recs.append(emq); emq_keyed = set(); last_ex = None
        mth = re.match(r'^(?:Theme\s*)?(\d+)', txt)
        if mth: themes[(chapter, int(mth.group(1)))] = emq
        mode = 'emq_opts'
        continue
    if ps == 'theme answers':
        mode = 'emq_ans'; last_ex = None
        mth = re.match(r'^Theme\s*(\d+)', txt)
        if mth and (chapter, int(mth.group(1))) in themes:
            emq = themes[(chapter, int(mth.group(1)))]
            emq_keyed = set(i['n'] for i in emq['items'] if i['answer'])
        else:
            print('?? theme answers', chapter, txt)
        continue
    if ps == 'Box green':
        mode = 'ans'
        continue
    if ps == 'table':
        continue
    if mode == 'emq_opts':
        exp = chr(65 + len(emq['options']))
        m = re.match(r'^([A-Za-z])\s*(?:\.{1,2}|\))?\s+(.*)$|^([A-Za-z])\.(\S.*)$', txt)
        if m and (m.group(1) or m.group(3)).upper() == exp:
            body = m.group(2) if m.group(1) else m.group(4)
            emq['options'].append(clean(body.rstrip(',').strip()))
        else:
            emq.setdefault('unparsed', []).append(txt)
        if PIMG: emq.setdefault('images', []).extend(PIMG)
        continue
    if mode == 'emq_items':
        m = QNUM.match(txt)
        if m:
            emq['items'].append(dict(n=int(m.group(2)), stem=clean(m.group(3).replace('[IMG]', '')), answer='', explanation='', img=img, images=list(PIMG)))
        elif emq['items']:
            emq['items'][-1]['stem'] += ' ' + txt.replace('[IMG]', '')
            emq['items'][-1]['img'] += img; emq['items'][-1]['images'] += PIMG
        else:
            emq.setdefault('lead', []).append(txt)
        continue
    if mode == 'emq_ans':
        items = emq['items']; nopt = len(emq['options'])
        def item(n):
            return next((i for i in items if i['n'] == n), None)
        def strip_opt(tail, L):
            on = norm(emq['options'][ord(L) - 65]); tn = norm(tail)
            if not tn or on.startswith(tn) or (tn.startswith(on) and len(tn) <= len(on) + 3):
                return ''
            if tn.startswith(on):
                acc = ''
                for k in range(len(tail) + 1):
                    if len(norm(tail[:k])) >= len(on): return tail[k:].lstrip(' .,:;-')
            return tail
        if re.match(r'^\d+\s*[A-Z]\b\s*(,\s*\d+\s*[A-Z]\b\s*)+', txt):
            for n, L in re.findall(r'(\d+)\s*([A-Z])\b', txt):
                it = item(int(n))
                if it: it['answer'] = L; emq_keyed.add(int(n))
            continue
        if re.match(r'^[A-Z](\s*,\s*[A-Z])+\s*$', txt):
            for it, L in zip(items, re.findall(r'[A-Z]', txt)):
                it['answer'] = L; emq_keyed.add(it['n'])
            emq['_expl_ptr'] = 0
            continue
        mg = re.match(r'^(\d+)([A-Z])(?:\.|\s)\s*(.*)$', txt) or re.match(r'^(\d+)([A-Z])(\d+\..*)$', txt)
        if mg and item(int(mg.group(1))) and ord(mg.group(2)) - 65 < nopt:
            it = item(int(mg.group(1))); it['answer'] = mg.group(2); emq_keyed.add(it['n'])
            tail = mg.group(3).strip()
            m3 = re.match(r'^(\d+)\.\s*(.*)$', tail)
            if m3 and item(int(m3.group(1))):
                it2 = item(int(m3.group(1))); it2['explanation'] = (it2['explanation'] + ' ' + m3.group(2)).strip(); last_ex = it2
            continue
        m = re.match(r'^(\d+)\s*[.)\-,]\s*(.*)$', txt)
        if m:
            n = int(m.group(1)); rest = m.group(2).strip()
            it = item(n)
            if it is None:
                emq.setdefault('unparsed', []).append(txt); continue
            if n not in emq_keyed:
                m2 = re.match(r'^([A-Z])(?:\s*[.):]\s*|\s+|$)(.*)$', rest, re.S) or re.match(r'^([a-z])(?:\s*[.)]\s*|$)(.*)$', rest, re.S)
                if m2 and ord(m2.group(1).upper()) - 65 < nopt and not re.match(r'^(A|I)\s+[a-z]', rest):
                    L = m2.group(1).upper(); it['answer'] = L; emq_keyed.add(n)
                    tail = strip_opt(m2.group(2).strip().rstrip(','), L)
                    if tail: it['explanation'] = (it['explanation'] + ' ' + tail).strip()
                    last_ex = it
                    continue
                rn = norm(rest.rstrip(',.'))
                hit = [k for k, o in enumerate(emq['options']) if norm(o) == rn or (len(rn) > 3 and (norm(o).startswith(rn) or rn.startswith(norm(o))) and len(rest) < len(o) + 25)]
                if hit and len(rest) < 90:
                    it['answer'] = chr(65 + hit[0]); emq_keyed.add(n)
                    continue
            it['explanation'] = (it['explanation'] + ' ' + rest).strip()
            last_ex = it
            continue
        m = re.match(r'^([A-Z])\s*:\s*(.*)$', txt)
        if m and '_expl_ptr' in emq and emq['_expl_ptr'] < len(items):
            it = items[emq['_expl_ptr']]; emq['_expl_ptr'] += 1
            it['explanation'] = (it['explanation'] + ' ' + m.group(2)).strip(); last_ex = it
            continue
        if last_ex is not None:
            last_ex['explanation'] += ' ' + txt
        else:
            emq.setdefault('unparsed', []).append(txt)
        continue
    if mode == 'ans':
        m = re.match(r'^(\d+)\s*[.)]?\s*(.*)$', txt)
        if m and m.group(2):
            n = int(m.group(1))
            q = bankq.get(n) or chapq.get(n)
            if q is None:
                print('?? answer without q', chapter, bank, txt[:80]); continue
            letters, ex = parse_mcq_answer(q, m.group(2))
            q['answer'] = ''.join(letters)
            q['explanation'] = ex
            q['_raw_ans'] = txt
            last_ex = q
        elif last_ex is not None:
            last_ex['explanation'] += ' ' + txt
        continue
    # question text (mode mcq)
    m = QNUM.match(txt)
    if m and not OPT.match(txt):
        new_mcq(int(m.group(2)), clean(m.group(3).replace('[IMG]', '')), img)
        mode = 'mcq'
        continue
    m = OPT.match(txt)
    if m and cur is not None and cur['type'] == 'MCQ' and (cur['options'] or len(cur['options']) == 0):
        L = m.group(1) or m.group(3)
        body = clean(m.group(2) if m.group(1) else m.group(4))
        body = re.sub(r'^[a-e]\s*[.)]\s*', '', body)          # 'A. a. text'
        body = re.sub(r'^\(?[A-E]\)?\s+(?=[A-Z])', '', body) if re.match(r'^[A-E] [A-Z]', body) else body   # 'A. A Anaplastic'
        if ord(L) - 65 == len(cur['options']):
            cur['options'].append(body)
            continue
    if txt.strip() == '[IMG]' or (img and len(txt) < 12):
        if cur is not None and cur['type'] == 'MCQ' and not cur['options']:
            cur['img'] += img; cur['images'] += PIMG
        else:
            pending_imgs.extend(PIMG)
        continue
    # free text: continuation of stem before options, else case preamble for next question
    if cur is not None and cur['type'] == 'MCQ' and not cur['options']:
        cur['stem'] += ' ' + txt.replace('[IMG]', '').strip(); cur['img'] += img; cur['images'] += PIMG
    else:
        pending_case.append(txt.replace('[IMG]', '').strip()); pending_imgs.extend(PIMG)

json.dump(recs, open('parsed.json', 'w'), ensure_ascii=False, indent=0)
json.dump(summary, open('summaries.json', 'w'), ensure_ascii=False, indent=0)
mc = [r for r in recs if r['type'] == 'MCQ']; em = [r for r in recs if r['type'] == 'EMQ']
print('MCQ', len(mc), 'EMQ', len(em), 'items', sum(len(e['items']) for e in em))
print('no answer', sum(1 for r in mc if not r['answer']), 'multi', sum(1 for r in mc if len(r['answer']) > 1),
      'opts<2', sum(1 for r in mc if len(r['options']) < 2), 'case', sum(1 for r in mc if r.get('case')))
print('emq items no key', sum(1 for e in em for i in e['items'] if not i['answer']), 'no ex', sum(1 for e in em for i in e['items'] if not i['explanation']))
print(collections.Counter(r['chapter'] for r in recs))
print(collections.Counter(r['bank'] for r in recs))
