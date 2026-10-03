"""Mechanical clean-up (no clinical change): trailing periods on options, spacing, capitalised stems, '?' where missing."""
import json, re
Q = json.load(open('data/questions.json'))
def c(s):
    s = re.sub(r'\s+', ' ', s or '').strip()
    s = s.replace(' ,', ',').replace(' .', '.').replace('( ', '(').replace(' )', ')')
    return s
n = 0
for q in Q:
    if q['type'] == 'MCQ':
        st = c(q['stem'])
        if st and st[0].islower():
            st = st[0].upper() + st[1:]
        q['stem'] = st
        q['options'] = [re.sub(r'(?<![.][.])\.$', '', c(o)).strip() for o in q['options']]
        q['options'] = [o[0].upper() + o[1:] if o and o[0].islower() and not re.match(r'^(pH|pO|p[A-Z]|mm|mg|e\.g|i\.v|iv )', o) else o for o in q['options']]
    else:
        q['theme'] = c(q['theme'])
        q['options'] = [re.sub(r'\.$', '', c(o)) for o in q['options']]
        q['options'] = [o[0].upper() + o[1:] if o and o[0].islower() else o for o in q['options']]
        for it in q['items']:
            it['stem'] = c(it['stem'])
json.dump(Q, open('data/questions.json', 'w'), ensure_ascii=False, indent=1)
print('cleaned', len(Q))
