"""Cloud IDML build (no InDesign needed): writes a native IDML package for one chapter part,
using the engine's style names (Q-<id>, Opt-<id>, Ans-<id> ...), swatches (IMB ...) and fonts
(Acumin Variable Concept / Source Serif Variable / Source Sans Variable).

  python build/idml_build.py git          (run build/pdf_build.py first: page count + bank pages)
Output: output/parts/NN-<ch>.idml

The resources (Fonts, Preferences, Styles base, Graphic base) come from an InDesign-generated IDML in
build/idml_template/. Text flows through threaded 2-column frames on A4 facing pages; pages are
numbered from the part JSON start page. Smart Text Reflow is on (adds pages at the end if needed).
"""
import json, math, os, re, sys, zipfile, random
from xml.sax.saxutils import escape as xesc

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
TPL = os.path.join(HERE, 'idml_template')
sys.path.insert(0, HERE)
import gen

book = gen.book
cid = sys.argv[1] if len(sys.argv) > 1 else book['chapters'][0]['id']
ch = next(c for c in book['chapters'] if c['id'] == cid)
part = json.load(open(os.path.join(ROOT, 'output', 'parts', cid + '.json')))
START = part['start']
CONTENT_PAGES = part['pages'] - 2          # divider + opener come first
NAME = '%02d-%s' % (ch['order'], cid)
SFX = '-' + cid

MM = 72 / 25.4
W, H = 210 * MM, 297 * MM
BLEED = 3 * MM
M = dict(top=21, bottom=20, inside=19, outside=17)
GUT = 6
LAYER = 'ub3'
FD, FSER, FSANS = 'Acumin Variable Concept', 'Source Serif Variable', 'Source Sans Variable'

_id = [0x2000]


def uid():
    _id[0] += 1
    return 'u%x' % _id[0]


def a(v):
    """xml attribute escape"""
    return xesc(str(v), {'"': '&quot;'})


def num(x):
    return ('%.4f' % x).rstrip('0').rstrip('.')


# ------------------------------------------------------------------ colours
COL = {'IMB Ink': '0E1726', 'IMB Ink 2': '1B2A41', 'IMB Muted': '667085', 'IMB Line': 'D0D5DD', 'IMB Mist': 'F2F4F7',
       'IMB Gold': 'E8B64C', 'IMB White': 'FFFFFF', 'IMB ' + cid: ch['color']}
ACC = 'Color/IMB ' + cid
INK, INK2, MUTED, LINE, GOLD, WHITE = 'Color/IMB Ink', 'Color/IMB Ink 2', 'Color/IMB Muted', 'Color/IMB Line', 'Color/IMB Gold', 'Color/IMB White'
GRAD = 'Gradient/IMB Divider ' + cid


def graphic_xml():
    s = open(os.path.join(TPL, 'Resources', 'Graphic.xml'), encoding='utf-8').read()
    add = []
    for n, h in COL.items():
        rgb = ' '.join(str(int(h[i:i + 2], 16)) for i in (0, 2, 4))
        add.append('\t<Color Self="Color/%s" Model="Process" Space="RGB" ColorValue="%s" ColorOverride="Normal" AlternateSpace="NoAlternateColor" '
                   'AlternateColorValue="" Name="%s" ColorEditable="true" ColorRemovable="true" Visible="true" SwatchCreatorID="7937"/>' % (a(n), rgb, a(n)))
    s = s.replace('\t<Ink Self="Ink/$ID/Process Cyan"', '\n'.join(add) + '\n\t<Ink Self="Ink/$ID/Process Cyan"', 1)
    g = ('\t<Gradient Self="%s" Type="Linear" Name="IMB Divider %s" ColorEditable="true" ColorRemovable="true" Visible="true" SwatchCreatorID="7937">\n'
         '\t\t<GradientStop Self="%sStop0" StopColor="%s" Location="0"/>\n'
         '\t\t<GradientStop Self="%sStop1" StopColor="%s" Location="55" Midpoint="50"/>\n'
         '\t\t<GradientStop Self="%sStop2" StopColor="%s" Location="100" Midpoint="50"/>\n\t</Gradient>\n') % (
        a(GRAD), a(cid), 'uGrad' + cid, a(ACC), 'uGrad' + cid, a(INK2), 'uGrad' + cid, a(INK))
    s = s.replace('\t<StrokeStyle Self="StrokeStyle/$ID/Triple_Stroke"', g + '\t<StrokeStyle Self="StrokeStyle/$ID/Triple_Stroke"', 1)
    return s


# ------------------------------------------------------------------ styles
PSTYLES, CSTYLES = [], []


def tablist(tabs):
    if not tabs:
        return ''
    items = ''.join('<ListItem type="record"><Alignment type="enumeration">%s</Alignment><AlignmentCharacter type="string">.</AlignmentCharacter>'
                    '<Leader type="string"></Leader><Position type="unit">%s</Position></ListItem>' % (al, num(pos)) for pos, al in tabs)
    return '<TabList type="list">%s</TabList>' % items


def pstyle(name, based='IMB Base', font=None, leading=None, tabs=None, props=None, **at):
    props = dict(props or {})
    pr = [('<BasedOn type="object">%s</BasedOn>' % a('ParagraphStyle/' + based)) if based != '$NONE' else '<BasedOn type="string">$ID/[No paragraph style]</BasedOn>',
          '<PreviewColor type="enumeration">Nothing</PreviewColor>']
    if font:
        pr.append('<AppliedFont type="string">%s</AppliedFont>' % a(font))
    if leading is not None:
        pr.append('<Leading type="unit">%s</Leading>' % num(leading))
    for k, v in props.items():
        if k.endswith('Color'):
            pr.append('<%s type="object">%s</%s>' % (k, a(v), k))
        else:
            pr.append('<%s type="enumeration">%s</%s>' % (k, a(v), k))
    pr.append(tablist(tabs))
    attrs = ' '.join('%s="%s"' % (k, a(num(v) if isinstance(v, float) else v)) for k, v in at.items())
    PSTYLES.append('\t\t<ParagraphStyle Self="ParagraphStyle/%s" Name="%s" Imported="false" NextStyle="ParagraphStyle/%s" KeyboardShortcut="0 0" %s>'
                   '<Properties>%s</Properties></ParagraphStyle>' % (a(name), a(name), a(name), attrs, ''.join(pr)))


def cstyle(name, font=None, props=None, **at):
    pr = ['<BasedOn type="string">$ID/[No character style]</BasedOn>', '<PreviewColor type="enumeration">Nothing</PreviewColor>']
    if font:
        pr.append('<AppliedFont type="string">%s</AppliedFont>' % a(font))
    for k, v in (props or {}).items():
        pr.append('<%s type="object">%s</%s>' % (k, a(v), k))
    attrs = ' '.join('%s="%s"' % (k, a(num(v) if isinstance(v, float) else v)) for k, v in at.items())
    CSTYLES.append('\t\t<CharacterStyle Self="CharacterStyle/%s" Imported="false" KeyboardShortcut="0 0" Name="%s" %s><Properties>%s</Properties></CharacterStyle>'
                   % (a(name), a(name), attrs, ''.join(pr)))


def define_styles():
    mm = lambda v: v * MM
    TW = (210 - M['inside'] - M['outside']) * MM
    pstyle('IMB Base', based='$NONE', font=FSER, leading=12, FontStyle='Regular', PointSize=9, FillColor=INK, Hyphenation='true',
           HyphenateWordsLongerThan=6, HyphenateCapitalizedWords='false', HyphenateLastWord='false', Justification='LeftAlign',
           KerningMethod='$ID/Optical', Composer='HL Composer', AppliedLanguage='$ID/English: UK', SpaceBefore=0, SpaceAfter=0)
    cstyle('Bold', FontStyle='Bold')
    cstyle('Italic', FontStyle='Italic')
    cstyle('Sup' + SFX, Position='Superscript')
    cstyle('QNum' + SFX, FD, FontStyle='Condensed Bold', PointSize=10.5, FillColor=ACC)
    cstyle('OptL' + SFX, FD, FontStyle='Semibold', PointSize=8.2, FillColor=ACC)
    cstyle('ANum' + SFX, FD, FontStyle='Condensed Bold', PointSize=9.5, FillColor=INK)
    cstyle('ALetter' + SFX, FD, props={'UnderlineColor': ACC}, FontStyle='Bold', PointSize=8, FillColor=WHITE, Underline='true',
           UnderlineWeight=9.4, UnderlineOffset=-2.9, UnderlineTint=100)
    cstyle('AOpt' + SFX, FSANS, FontStyle='Semibold', FillColor=ACC)
    cstyle('Kicker' + SFX, FD, FontStyle='Semibold', FillColor=ACC)
    cstyle('AnsHeadBank' + SFX, FD, FontStyle='Semibold', PointSize=7.5, Tracking=100, Capitalization='AllCaps', FillColor=MUTED)
    cstyle('EmqThemeLbl' + SFX, FD, FontStyle='Semibold', PointSize=7, Tracking=140)

    span = dict(SpanColumnType='SpanColumns')
    sp_all = {'SpanSplitColumnCount': 'All'}
    pstyle('BankKicker' + SFX, font=FD, leading=9, props=sp_all, FontStyle='Semibold', PointSize=7, Tracking=140, FillColor=ACC,
           SpaceBefore=mm(9), KeepWithNext=2, Hyphenation='false', **span)
    pstyle('BankHead' + SFX, font=FD, leading=25, props=dict(sp_all, RuleBelowColor=ACC), FontStyle='Condensed Bold', PointSize=24,
           FillColor=INK, SpaceAfter=mm(5.5), KeepWithNext=2, Hyphenation='false', RuleBelow='true', RuleBelowLineWeight=2.2,
           RuleBelowOffset=mm(2.4), RuleBelowWidth='ColumnWidth', RuleBelowRightIndent=mm(150), **span)
    pstyle('SetHead' + SFX, font=FD, leading=9, FontStyle='Semibold', PointSize=7.5, Tracking=120, Capitalization='AllCaps', FillColor=ACC,
           SpaceBefore=mm(3), SpaceAfter=mm(1), KeepWithNext=2, Hyphenation='false')
    pstyle('Q' + SFX, font=FSER, leading=11.8, tabs=[(mm(7.5), 'LeftAlign')], FontStyle='Regular', PointSize=8.9, LeftIndent=mm(7.5),
           FirstLineIndent=-mm(7.5), SpaceBefore=mm(3.4), SpaceAfter=mm(1), KeepWithNext=2, KeepFirstLines=2, KeepLastLines=2)
    pstyle('QLast' + SFX, based='Q' + SFX, SpaceAfter=mm(3), KeepWithNext=0)
    pstyle('Opt' + SFX, font=FSANS, leading=10.6, tabs=[(mm(12.5), 'LeftAlign')], FontStyle='Regular', PointSize=8.5, LeftIndent=mm(12.5),
           FirstLineIndent=-mm(5), SpaceAfter=mm(0.35), KeepWithNext=1, Hyphenation='false', FillColor=INK2)
    pstyle('OptLast' + SFX, based='Opt' + SFX, KeepWithNext=0, SpaceAfter=mm(1.2))
    pstyle('QImage' + SFX, leading=10, Justification='LeftAlign', LeftIndent=mm(7.5), SpaceBefore=mm(1), SpaceAfter=mm(1.2), KeepWithNext=1)
    # EMQ theme bar: a heavy rule-above sits behind the (white) text
    pstyle('EmqTheme' + SFX, font=FD, leading=12, tabs=[(mm(15), 'LeftAlign')], props={'RuleAboveColor': ACC}, FontStyle='Condensed Bold',
           PointSize=10, FillColor=WHITE, SpaceBefore=mm(6), SpaceAfter=mm(2.6), KeepWithNext=3, Hyphenation='false', LeftIndent=mm(15),
           FirstLineIndent=-mm(15), RuleAbove='true', RuleAboveLineWeight=16, RuleAboveOffset=-4.2, RuleAboveWidth='ColumnWidth',
           RuleAboveLeftIndent=-mm(2), RuleAboveRightIndent=-mm(2))
    pstyle('EmqOpt' + SFX, font=FSANS, leading=10.8, tabs=[(mm(8), 'LeftAlign')], FontStyle='Regular', PointSize=8.4, LeftIndent=mm(8),
           FirstLineIndent=-mm(6), KeepWithNext=1, Hyphenation='false', SpaceAfter=0, FillColor=INK2)
    pstyle('EmqOptLast' + SFX, based='EmqOpt' + SFX, KeepWithNext=1, SpaceAfter=mm(2.6))
    pstyle('EmqLead' + SFX, font=FSER, leading=10, FontStyle='Italic', PointSize=8, FillColor=MUTED, SpaceAfter=mm(0.5), KeepWithNext=2)
    pstyle('AnsHead' + SFX, font=FD, leading=16, props=dict(sp_all, RuleAboveColor=ACC), FontStyle='Condensed Bold',
           PointSize=14, FillColor=ACC, SpaceBefore=mm(8), SpaceAfter=mm(3), KeepWithNext=2, Hyphenation='false', RuleAbove='true',
           RuleAboveLineWeight=0.8, RuleAboveOffset=mm(4.5), RuleAboveWidth='ColumnWidth', **span)
    pstyle('Ans' + SFX, font=FSANS, leading=10.7, tabs=[(mm(7.5), 'LeftAlign')], FontStyle='Regular', PointSize=8.3, LeftIndent=mm(7.5),
           FirstLineIndent=-mm(7.5), SpaceAfter=mm(1.9), FillColor=INK)
    # chrome, divider and opener
    pstyle('Header' + SFX, font=FD, leading=8, FontStyle='Semibold', PointSize=6.8, Tracking=120, FillColor=MUTED, Capitalization='AllCaps', Hyphenation='false')
    pstyle('HeaderR' + SFX, based='Header' + SFX, Justification='RightAlign')
    pstyle('Folio' + SFX, font=FD, leading=10, FontStyle='Condensed Bold', PointSize=9, FillColor=WHITE, Justification='CenterAlign', Hyphenation='false')
    pstyle('DivKicker' + SFX, font=FD, leading=10, FontStyle='Semibold', PointSize=8, Tracking=200, FillColor=GOLD, Capitalization='AllCaps', Hyphenation='false')
    pstyle('DivNum' + SFX, font=FD, leading=150, FontStyle='ExtraCondensed Black', PointSize=150, FillColor=WHITE, Hyphenation='false', Tracking=-10)
    pstyle('DivTitle' + SFX, font=FD, leading=40, FontStyle='ExtraCondensed Black', PointSize=42, FillColor=WHITE, Capitalization='AllCaps', Hyphenation='false')
    pstyle('DivCredit' + SFX, font=FSANS, leading=8, FontStyle='Regular', PointSize=6.5, FillColor=LINE, Hyphenation='false')
    pstyle('OpKicker' + SFX, font=FD, leading=10, FontStyle='Semibold', PointSize=8, Tracking=200, FillColor=ACC, Capitalization='AllCaps', SpaceAfter=mm(3), Hyphenation='false')
    pstyle('OpTitle' + SFX, font=FD, leading=44, FontStyle='ExtraCondensed Black', PointSize=46, FillColor=INK, Capitalization='AllCaps', Hyphenation='false')
    pstyle('OpIntro' + SFX, font=FSER, leading=15, FontStyle='Regular', PointSize=11, FillColor=INK2)
    pstyle('StatNum' + SFX, font=FD, leading=28, FontStyle='ExtraCondensed Black', PointSize=30, FillColor=ACC, Hyphenation='false')
    pstyle('StatLbl' + SFX, font=FD, leading=9, FontStyle='Semibold', PointSize=7, Tracking=120, FillColor=MUTED, Capitalization='AllCaps', Hyphenation='false')
    pstyle('OpHead' + SFX, font=FD, leading=10, FontStyle='Semibold', PointSize=7.5, Tracking=160, FillColor=ACC, Capitalization='AllCaps', SpaceAfter=mm(2.5), Hyphenation='false')
    pstyle('OpToc' + SFX, font=FD, leading=17, tabs=[(mm(120), 'RightAlign'), (mm(174), 'RightAlign')], props={'RuleBelowColor': LINE},
           FontStyle='Condensed Bold', PointSize=13, FillColor=INK, SpaceAfter=mm(2.2), RuleBelow='true', RuleBelowLineWeight=0.5,
           RuleBelowOffset=mm(1.6), RuleBelowWidth='ColumnWidth', Hyphenation='false')
    pstyle('OpTopic' + SFX, font=FSANS, leading=12.5, tabs=[(mm(4), 'LeftAlign')], FontStyle='Regular', PointSize=9, FillColor=INK2,
           LeftIndent=mm(4), FirstLineIndent=-mm(4), Hyphenation='false')
    cstyle('Bullet' + SFX, FD, FontStyle='Bold', FillColor=ACC)
    cstyle('TocCount' + SFX, FSANS, FontStyle='Regular', PointSize=9, FillColor=MUTED)
    cstyle('TocPage' + SFX, FD, FontStyle='Condensed Bold', FillColor=ACC)


def styles_xml():
    s = open(os.path.join(TPL, 'Resources', 'Styles.xml'), encoding='utf-8').read()
    s = s.replace('\t</RootCharacterStyleGroup>', '\n'.join(CSTYLES) + '\n\t</RootCharacterStyleGroup>', 1)
    s = s.replace('\t</RootParagraphStyleGroup>', '\n'.join(PSTYLES) + '\n\t</RootParagraphStyleGroup>', 1)
    return s


# ------------------------------------------------------------------ stories
STORIES = {}      # id -> xml
NO_CS = 'CharacterStyle/$ID/[No character style]'


def story(paras, sid=None):
    """paras: [(pstyle, [(cstyle|None, text, extra_attrs_dict)...])] -> story id"""
    sid = sid or uid()
    out = []
    for i, (ps, runs) in enumerate(paras):
        last = i == len(paras) - 1
        r = []
        for j, (cs, text, ex) in enumerate(runs):
            ex_s = ''.join(' %s="%s"' % (k, a(v)) for k, v in (ex or {}).items())
            content = text if text.startswith('<?ACE') else xesc(text)
            br = '<Br/>' if (j == len(runs) - 1 and not last and not cs) else ''
            r.append('<CharacterStyleRange AppliedCharacterStyle="%s"%s><Content>%s</Content>%s</CharacterStyleRange>'
                     % (a('CharacterStyle/' + cs) if cs else NO_CS, ex_s, content, br))
            if j == len(runs) - 1 and not last and cs:      # paragraph break in a plain run
                r.append('<CharacterStyleRange AppliedCharacterStyle="%s"><Br/></CharacterStyleRange>' % NO_CS)
        out.append('<ParagraphStyleRange AppliedParagraphStyle="%s">%s</ParagraphStyleRange>' % (a('ParagraphStyle/' + ps), ''.join(r)))
    STORIES[sid] = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                    '<idPkg:Story xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging" DOMVersion="7.5">\n'
                    '\t<Story Self="%s" AppliedTOCStyle="n" TrackChanges="false" StoryTitle="$ID/" AppliedNamedGrid="n">\n'
                    '\t\t<StoryPreference OpticalMarginAlignment="false" OpticalMarginSize="12" FrameType="TextFrameType" StoryOrientation="Horizontal" StoryDirection="LeftToRightDirection"/>\n'
                    '\t\t<InCopyExportOption IncludeGraphicProxies="true" IncludeAllResources="false"/>\n\t\t%s\n\t</Story>\n</idPkg:Story>\n') % (sid, '\n\t\t'.join(out))
    return sid


def rich_runs(text, base=None):
    """split **bold** and powers of ten into runs"""
    runs = []
    for part_ in re.split(r'(\*\*.+?\*\*|10⁹|10¹²)', text or ''):
        if not part_:
            continue
        if part_.startswith('**'):
            runs.append(('Bold', part_[2:-2], None))
        elif part_ in ('10⁹', '10¹²'):
            runs.append((base, '10', None))
            runs.append(('Sup' + SFX, '9' if part_ == '10⁹' else '12', None))
        else:
            runs.append((base, part_, None))
    return runs


def main_story():
    qs = gen.chapter_questions(cid)
    banks = {}
    for q in qs:
        banks.setdefault((q['bank'], q['type']), []).append(q)
    P = []
    qn = 0
    for (bank, typ), items in banks.items():
        n_units = sum(1 if q['type'] == 'MCQ' else len(q['items']) for q in items)
        label = '%s %s' % (bank, 'EMQs' if typ == 'EMQ' else 'MCQs')
        sets, cur, count = [], [], 0
        for q in items:
            size = 1 if q['type'] == 'MCQ' else len(q['items'])
            if cur and count + size > gen.SET_SIZE and typ == 'MCQ':
                sets.append(cur); cur, count = [], 0
            cur.append(q); count += size
        if cur:
            sets.append(cur)
        P.append(('BankKicker' + SFX, [(None, ('%d %s  •  %s' % (n_units, 'EMQ items' if typ == 'EMQ' else 'questions', gen.BANK_BLURB.get(bank, ''))).upper(), None)]))
        P.append(('BankHead' + SFX, [(None, label, None)]))
        for si, s in enumerate(sets):
            first = qn + 1
            if len(sets) > 1:
                P.append(('SetHead' + SFX, [(None, 'Set %d of %d' % (si + 1, len(sets)), None)]))
            for q in s:
                if q['type'] == 'MCQ':
                    qn += 1; q['_n'] = qn
                    P.append(('Q' + SFX, [('QNum' + SFX, str(qn), None), (None, '\t', None)] + rich_runs(q['stem'])))
                    for i, o in enumerate(q['options']):
                        st = 'OptLast' if i == len(q['options']) - 1 else 'Opt'
                        P.append((st + SFX, [('OptL' + SFX, chr(65 + i), None), (None, '\t', None)] + rich_runs(o)))
                else:
                    P.append(('EmqTheme' + SFX, [('EmqThemeLbl' + SFX, 'THEME', None), (None, '\t' + q['theme'], None)]))
                    L = q['option_letters']
                    for i, o in enumerate(q['options']):
                        st = 'EmqOptLast' if i == len(q['options']) - 1 else 'EmqOpt'
                        P.append((st + SFX, [('OptL' + SFX, L[i], None), (None, '\t', None)] + rich_runs(o)))
                    P.append(('EmqLead' + SFX, [(None, 'For each scenario, choose the single most appropriate option. Each option may be used once, more than once or not at all.', None)]))
                    for k, it in enumerate(q['items']):
                        qn += 1; it['_n'] = qn
                        st = 'QLast' if k == len(q['items']) - 1 else 'Q'
                        P.append((st + SFX, [('QNum' + SFX, str(qn), None), (None, '\t', None)] + rich_runs(it['stem'])))
            last = qn
            head = 'Answers  %d–%d' % (first, last) if last > first else 'Answer  %d' % first
            P.append(('AnsHead' + SFX, [(None, head, None), (None, '<?ACE 8?>', None), ('AnsHeadBank' + SFX, label, None)]))
            for q in s:
                if q['type'] == 'MCQ':
                    recs = [(q['_n'], q['answer'], q['options'][ord(q['answer']) - 65], q['explanation'])]
                else:
                    L = q['option_letters']
                    recs = [(it['_n'], it['answer'], q['options'][L.index(it['answer'])], it['explanation']) for it in q['items']]
                for n, Lt, opt, ex in recs:
                    P.append(('Ans' + SFX, [('ANum' + SFX, str(n), None), (None, '\t', None), ('ALetter' + SFX, ' %s ' % Lt, None), (None, ' ', None)]
                              + rich_runs(opt, 'AOpt' + SFX) + [(None, ' — ', None)] + rich_runs(ex)))
    return story(P), qn, qs


# ------------------------------------------------------------------ page items
def pts(side, top, left, bottom, right):
    """mm box on a page -> spread-coordinate corners (x0, y0, x1, y1)"""
    ox = -W if side == 'L' else 0
    return ox + left * MM, -H / 2 + top * MM, ox + right * MM, -H / 2 + bottom * MM


def path(points, open_=False):
    pp = ''.join('<PathPointType Anchor="{0} {1}" LeftDirection="{0} {1}" RightDirection="{0} {1}"/>'.format(num(x), num(y)) for x, y in points)
    return ('<Properties><PathGeometry><GeometryPathType PathOpen="%s"><PathPointArray>%s</PathPointArray></GeometryPathType></PathGeometry></Properties>'
            % ('true' if open_ else 'false', pp))


def box(x0, y0, x1, y1):
    return [(x0, y0), (x0, y1), (x1, y1), (x1, y0)]


COMMON = ('ItemLayer="%s" Locked="false" LocalDisplaySetting="Default" Visible="true" Name="$ID/" ItemTransform="1 0 0 1 0 0"' % LAYER)
WRAP = ('<TextWrapPreference Inverse="false" ApplyToMasterPageOnly="false" TextWrapSide="BothSides" TextWrapMode="None">'
        '<Properties><TextWrapOffset Top="0" Left="0" Bottom="0" Right="0"/></Properties></TextWrapPreference>')


def rect(c, fill, tint=None, grad=None):
    g = ''
    if grad:
        g = ' GradientFillStart="%s %s" GradientFillLength="%s" GradientFillAngle="%s"' % (num(grad[0]), num(grad[1]), num(grad[2]), num(grad[3]))
    return ('<Rectangle Self="%s" ContentType="Unassigned" StoryTitle="$ID/" FillColor="%s"%s StrokeWeight="0" StrokeColor="Swatch/None"%s '
            'AppliedObjectStyle="ObjectStyle/$ID/[None]" %s>%s%s</Rectangle>') % (
        uid(), a(fill), '' if tint is None else ' FillTint="%s"' % num(tint), g, COMMON, path(box(*c)), WRAP)


def line(x0, y0, x1, y1, color, weight):
    return ('<GraphicLine Self="%s" ContentType="Unassigned" StrokeWeight="%s" StrokeColor="%s" FillColor="Swatch/None" '
            'AppliedObjectStyle="ObjectStyle/$ID/[None]" %s>%s%s</GraphicLine>') % (uid(), num(weight), a(color), COMMON, path([(x0, y0), (x1, y1)], True), WRAP)


def polyline(points, color, weight, tint):
    return ('<Polygon Self="%s" ContentType="Unassigned" StrokeWeight="%s" StrokeColor="%s" StrokeTint="%s" FillColor="Swatch/None" '
            'AppliedObjectStyle="ObjectStyle/$ID/[None]" %s>%s%s</Polygon>') % (uid(), num(weight), a(color), num(tint), COMMON, path(points, True), WRAP)


def tframe(c, sid, cols=1, gutter=GUT, prev='n', nxt='n', vj='TopAlign', fid=None):
    fid = fid or uid()
    return fid, ('<TextFrame Self="%s" ParentStory="%s" PreviousTextFrame="%s" NextTextFrame="%s" ContentType="TextType" '
                 'AppliedObjectStyle="ObjectStyle/$ID/[None]" FillColor="Swatch/None" StrokeWeight="0" StrokeColor="Swatch/None" %s>%s'
                 '<TextFramePreference TextColumnCount="%d" TextColumnGutter="%s" UseFixedColumnWidth="false" FirstBaselineOffset="AscentOffset" '
                 'VerticalJustification="%s"/>%s</TextFrame>') % (
        fid, sid, prev, nxt, COMMON, path(box(*c)), cols, num(gutter * MM), vj, WRAP)


def simple(ps, text, cs=None):
    return story([(ps, [(cs, text, None)])])


# ------------------------------------------------------------------ master
def master_xml(mid):
    items = []
    for side in ('L', 'R'):
        ins = M['inside'] if side == 'L' else M['outside']
        lft = M['outside'] if side == 'L' else M['inside']
        x0, _, x1, _ = pts(side, 0, lft, 0, 210 - ins)
        y = -H / 2 + 14.2 * MM
        items.append(line(x0, y, x1, y, LINE, 0.5))
        htxt = ('%s  /  %s' % (ch['part'], ch['title'])) if side == 'L' else ('%s  /  %s' % (book['title'], book.get('volume', '')))
        _, fx = tframe(pts(side, 8.4, lft, 13.2, 210 - ins), simple(('Header' if side == 'L' else 'HeaderR') + SFX, htxt.upper()), vj='BottomAlign')
        items.append(fx)
        cx = lft if side == 'L' else 210 - ins - 12
        items.append(rect(pts(side, 282.2, cx, 288.4, cx + 12), ACC))
        _, fx = tframe(pts(side, 282.2, cx, 288.4, cx + 12), simple('Folio' + SFX, '<?ACE 18?>'), vj='CenterAlign')
        items.append(fx)
        ty = 30 + (ch['order'] - 1) * 29
        tx = (-3, 7) if side == 'L' else (203, 213)
        items.append(rect(pts(side, ty, tx[0], ty + 27, tx[1]), ACC))
    pages = []
    for i, side in enumerate(('L', 'R')):
        lm, rm = (M['outside'], M['inside']) if side == 'L' else (M['inside'], M['outside'])
        tx = -W if side == 'L' else 0
        pages.append(('<Page Self="%s" GeometricBounds="0 0 %s %s" ItemTransform="1 0 0 1 %s %s" Name="%s" AppliedTrapPreset="TrapPreset/$ID/kDefaultTrapStyleName" '
                      'OverrideList="" AppliedMaster="n" MasterPageTransform="1 0 0 1 0 0" TabOrder="" GridStartingPoint="TopOutside" UseMasterGrid="true">'
                      '<Properties><PageColor type="enumeration">UseMasterColor</PageColor></Properties>'
                      '<MarginPreference ColumnCount="2" ColumnGutter="%s" Top="%s" Bottom="%s" Left="%s" Right="%s" ColumnDirection="Horizontal" ColumnsPositions="0 %s %s %s"/></Page>')
                     % (uid(), num(H), num(W), num(tx), num(-H / 2), 'A', num(GUT * MM), num(M['top'] * MM), num(M['bottom'] * MM), num(lm * MM), num(rm * MM),
                        num((174 - GUT) / 2 * MM), num((174 + GUT) / 2 * MM), num(174 * MM)))
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<idPkg:MasterSpread xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging" DOMVersion="7.5">\n'
            '\t<MasterSpread Self="%s" ItemTransform="1 0 0 1 0 0" OverriddenPageItemProps="" Name="A-%s" NamePrefix="A" BaseName="%s" ShowMasterItems="true" PageCount="2">'
            '<Properties><PageColor type="enumeration">UseMasterColor</PageColor></Properties>\n\t\t%s\n\t\t%s\n\t</MasterSpread>\n</idPkg:MasterSpread>\n') % (
        mid, a(ch['short']), a(ch['short']), '\n\t\t'.join(pages), '\n\t\t'.join(items))


# ------------------------------------------------------------------ divider + opener
def divider_items():
    it = []
    x0, y0, x1, y1 = pts('L', -3, -3, 300, 210)
    it.append(rect((x0, y0, x1, y1), GRAD, grad=(x0, y1, y1 - y0, 90)))
    random.seed(7)
    for k in range(34):
        mm0 = 20 + k * 8.2 - 3
        amp = 6 + 10 * math.sin(k / 5.0) ** 2
        freq = 0.035 + 0.012 * math.sin(k / 3.0)
        ph = k * 0.55
        P = []
        for i in range(0, 221, 4):
            xm = i - 5
            ym = mm0 + amp * math.sin(freq * xm * 2 * math.pi * 0.16 + ph) + 3 * math.sin(xm / 11.0 + k)
            X, Y, _, _ = pts('L', ym, xm, ym, xm)
            P.append((X, Y))
        it.append(polyline(P, ACC, 0.45 if k % 3 else 0.8, 25 + 45 * k / 34.0))
    for _ in range(26):
        cx, cy, r = random.uniform(7, 203), random.uniform(147, 287), random.uniform(1.5, 9)
        k = 0.5523 * r
        X, Y, _, _ = pts('L', cy, cx, cy, cx)
        R, K = r * MM, k * MM
        pp = [((X, Y - R), (X - K, Y - R), (X + K, Y - R)), ((X + R, Y), (X + R, Y - K), (X + R, Y + K)),
              ((X, Y + R), (X + K, Y + R), (X - K, Y + R)), ((X - R, Y), (X - R, Y + K), (X - R, Y - K))]
        pa = ''.join('<PathPointType Anchor="%s %s" LeftDirection="%s %s" RightDirection="%s %s"/>' % (num(p[0][0]), num(p[0][1]), num(p[1][0]), num(p[1][1]), num(p[2][0]), num(p[2][1])) for p in pp)
        it.append(('<Oval Self="%s" ContentType="Unassigned" StrokeWeight="0.4" StrokeColor="%s" StrokeTint="60" FillColor="Swatch/None" '
                   'AppliedObjectStyle="ObjectStyle/$ID/[None]" %s><Properties><PathGeometry><GeometryPathType PathOpen="false"><PathPointArray>%s'
                   '</PathPointArray></GeometryPathType></PathGeometry></Properties>%s</Oval>') % (uid(), GOLD, COMMON, pa, WRAP))
    it.append(tframe(pts('L', 20, 18, 26, 150), simple('DivKicker' + SFX, ch['part']))[1])
    it.append(tframe(pts('L', 26, 16, 80, 150), simple('DivNum' + SFX, '%02d' % ch['order']))[1])
    it.append(tframe(pts('L', 205, 17, 262, 188), simple('DivTitle' + SFX, ch['title']), vj='BottomAlign')[1])
    it.append(rect(pts('L', 267, 17, 268.6, 55), ACC))
    it.append(tframe(pts('L', 280, 17, 285, 150), simple('DivCredit' + SFX, 'Artwork: generated for this edition'))[1])
    return it


def opener_items(total, qs):
    it = []
    L, R = M['inside'], 210 - M['outside']
    it.append(tframe(pts('R', 27, L, 80, R), story([('OpKicker' + SFX, [(None, 'Chapter %02d  /  %s' % (ch['order'], ch['part']), None)]),
                                                   ('OpTitle' + SFX, [(None, ch['title'], None)])]))[1])
    it.append(rect(pts('R', 83, L, 84.6, L + 38), ACC))
    it.append(tframe(pts('R', 91, L, 124, L + 150), simple('OpIntro' + SFX, ch.get('intro', '')))[1])
    x0, _, x1, _ = pts('R', 0, L, 0, R)
    for yy in (128, 146):
        y = -H / 2 + yy * MM
        it.append(line(x0, y, x1, y, LINE, 0.6))
    n_mcq = sum(1 for q in qs if q['type'] == 'MCQ')
    n_emq = sum(len(q['items']) for q in qs if q['type'] == 'EMQ')
    n_th = sum(1 for q in qs if q['type'] == 'EMQ')
    stats = [(total, 'questions'), (n_mcq, 'single best answers'), (n_emq, 'EMQ items'), (n_th, 'EMQ themes')]
    for i, (n, lbl) in enumerate(stats):
        xl = L + i * 43.5
        it.append(tframe(pts('R', 131, xl, 144, xl + 42), story([('StatNum' + SFX, [(None, str(n), None)]), ('StatLbl' + SFX, [(None, lbl, None)])]))[1])
    toc = [('OpHead' + SFX, [(None, 'In this chapter', None)])]
    for b in part['banks']:
        toc.append(('OpToc' + SFX, [(None, b['title'] + '\t', None), ('TocCount' + SFX, str(b['count']), None), (None, '\t', None),
                                    ('TocPage' + SFX, str(b.get('page') or ''), None)]))
    it.append(tframe(pts('R', 154, L, 190, R), story(toc))[1])
    topics = list(dict.fromkeys(q['topics'][0] for q in qs if q.get('topics')))[:24]
    tp = [('OpHead' + SFX, [(None, 'High-yield topics', None)])] + [('OpTopic' + SFX, [('Bullet' + SFX, '■', None), (None, '\t' + x, None)]) for x in topics]
    it.append(tframe(pts('R', 196, L, 277, R), story(tp), cols=2, gutter=8)[1])
    return it


# ------------------------------------------------------------------ spreads + package
def page_xml(pid, side, number, master):
    tx = -W if side == 'L' else 0
    lm, rm = (M['outside'], M['inside']) if side == 'L' else (M['inside'], M['outside'])
    return ('<Page Self="%s" GeometricBounds="0 0 %s %s" ItemTransform="1 0 0 1 %s %s" Name="%d" AppliedTrapPreset="TrapPreset/$ID/kDefaultTrapStyleName" '
            'OverrideList="" AppliedMaster="%s" MasterPageTransform="1 0 0 1 0 0" TabOrder="" GridStartingPoint="TopOutside" UseMasterGrid="true">'
            '<Properties><PageColor type="enumeration">UseMasterColor</PageColor></Properties>'
            '<MarginPreference ColumnCount="2" ColumnGutter="%s" Top="%s" Bottom="%s" Left="%s" Right="%s" ColumnDirection="Horizontal" ColumnsPositions="0 %s %s %s"/></Page>') % (
        pid, num(H), num(W), num(tx), num(-H / 2), number, master, num(GUT * MM), num(M['top'] * MM), num(M['bottom'] * MM), num(lm * MM), num(rm * MM),
        num((174 - GUT) / 2 * MM), num((174 + GUT) / 2 * MM), num(174 * MM))


def spread_xml(sid, idx, pages_xml, items):
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<idPkg:Spread xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging" DOMVersion="7.5">\n'
            '\t<Spread Self="%s" FlattenerOverride="Default" AllowPageShuffle="true" ItemTransform="1 0 0 1 0 %s" ShowMasterItems="true" PageCount="%d" '
            'BindingLocation="1" PageTransitionType="None" PageTransitionDirection="NotApplicable" PageTransitionDuration="Medium">\n'
            '\t\t<FlattenerPreference LineArtAndTextResolution="300" GradientAndMeshResolution="150" ClipComplexRegions="false" ConvertAllStrokesToOutlines="false" ConvertAllTextToOutlines="false">'
            '<Properties><RasterVectorBalance type="double">50</RasterVectorBalance></Properties></FlattenerPreference>\n'
            '\t\t%s\n\t\t%s\n\t</Spread>\n</idPkg:Spread>\n') % (sid, num(idx * (H + 60)), len(pages_xml), '\n\t\t'.join(pages_xml), '\n\t\t'.join(items))


def main():
    define_styles()
    mid = uid()
    master = master_xml(mid)
    main_sid, total, qs = main_story()
    # content frames, threaded
    n_pages = 2 + CONTENT_PAGES
    numbers = list(range(START, START + n_pages))
    sides = ['L' if n % 2 == 0 else 'R' for n in numbers]
    fids = [uid() for _ in range(CONTENT_PAGES)]
    page_items = {0: divider_items(), 1: opener_items(total, qs)}
    for k in range(CONTENT_PAGES):
        pi = 2 + k
        side = sides[pi]
        lft = M['outside'] if side == 'L' else M['inside']
        rgt = 210 - (M['inside'] if side == 'L' else M['outside'])
        prev = fids[k - 1] if k else 'n'
        nxt = fids[k + 1] if k + 1 < CONTENT_PAGES else 'n'
        page_items[pi] = [tframe(pts(side, M['top'], lft, 297 - M['bottom'], rgt), main_sid, cols=2, prev=prev, nxt=nxt, fid=fids[k])[1]]
    # spreads: pages paired L/R
    spreads, i, first_pid = [], 0, None
    while i < n_pages:
        grp = [i] if sides[i] == 'R' else ([i, i + 1] if i + 1 < n_pages else [i])
        pxml, items = [], []
        for pi in grp:
            pid = uid()
            first_pid = first_pid or pid
            pxml.append(page_xml(pid, sides[pi], numbers[pi], 'n' if pi < 2 else mid))
            items += page_items.get(pi, [])
        sid = uid()
        spreads.append((sid, spread_xml(sid, len(spreads), pxml, items)))
        i += len(grp)

    dm = open(os.path.join(TPL, 'designmap.xml'), encoding='utf-8').read()
    dm = dm.replace('DOMVersion="7.5"', 'DOMVersion="7.5"')
    story_ids = list(STORIES) + ['ubackx']
    dm = re.sub(r'StoryList="[^"]*"', 'StoryList="%s"' % ' '.join(story_ids), dm, 1)
    dm = re.sub(r'\t<idPkg:MasterSpread src="[^"]*"/>\n', '', dm)
    dm = re.sub(r'\t<idPkg:Spread src="[^"]*"/>\n', '', dm)
    dm = re.sub(r'\t<idPkg:Story src="[^"]*"/>\n', '', dm)
    dm = re.sub(r'<Section Self="uc9" Length="4" Name="" ContinueNumbering="true"', '<Section Self="uc9" Length="%d" Name="" ContinueNumbering="false" PageNumberStart="%d"' % (n_pages, START), dm)
    dm = dm.replace('PageStart="ubb"', 'PageStart="%s"' % first_pid)
    ms_ref = '\t<idPkg:MasterSpread src="MasterSpreads/MasterSpread_%s.xml"/>\n' % mid
    sp_ref = ''.join('\t<idPkg:Spread src="Spreads/Spread_%s.xml"/>\n' % s for s, _ in spreads)
    dm = dm.replace('\t<Section Self="uc9"', ms_ref + sp_ref + '\t<Section Self="uc9"', 1)
    st_ref = ''.join('\t<idPkg:Story src="Stories/Story_%s.xml"/>\n' % s for s in STORIES)
    dm = dm.replace('\t<idPkg:BackingStory src="XML/BackingStory.xml"/>\n', '\t<idPkg:BackingStory src="XML/BackingStory.xml"/>\n' + st_ref, 1)
    dm = dm.replace('Name="$ID/Running Header" VariableType', 'Name="$ID/Running Header" VariableType')

    prefs = open(os.path.join(TPL, 'Resources', 'Preferences.xml'), encoding='utf-8').read()
    prefs = re.sub(r'<DocumentPreference PageHeight="[^"]*" PageWidth="[^"]*"', '<DocumentPreference PageHeight="%s" PageWidth="%s"' % (num(H), num(W)), prefs)
    for k in ('DocumentBleedTopOffset', 'DocumentBleedBottomOffset', 'DocumentBleedInsideOrLeftOffset', 'DocumentBleedOutsideOrRightOffset'):
        prefs = prefs.replace('%s="0"' % k, '%s="%s"' % (k, num(BLEED)), 1)
    prefs = prefs.replace('LimitToMasterTextFrames="true"', 'LimitToMasterTextFrames="false"').replace('DeleteEmptyPages="false"', 'DeleteEmptyPages="true"')
    prefs = re.sub(r'<MarginPreference ColumnCount="1" ColumnGutter="12" Top="36" Bottom="36" Left="36" Right="36"',
                   '<MarginPreference ColumnCount="2" ColumnGutter="%s" Top="%s" Bottom="%s" Left="%s" Right="%s"' % (
                       num(GUT * MM), num(M['top'] * MM), num(M['bottom'] * MM), num(M['inside'] * MM), num(M['outside'] * MM)), prefs, 1)

    backing = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
               '<idPkg:BackingStory xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging" DOMVersion="7.5">\n'
               '\t<XmlStory Self="ubackx" AppliedTOCStyle="n" TrackChanges="false" StoryTitle="$ID/" AppliedNamedGrid="n">\n'
               '\t\t<ParagraphStyleRange AppliedParagraphStyle="ParagraphStyle/$ID/NormalParagraphStyle">\n'
               '\t\t\t<CharacterStyleRange AppliedCharacterStyle="CharacterStyle/$ID/[No character style]">\n'
               '\t\t\t\t<XMLElement Self="di2" MarkupTag="XMLTag/Root"/>\n'
               '\t\t\t\t<Content>﻿</Content>\n\t\t\t</CharacterStyleRange>\n\t\t</ParagraphStyleRange>\n\t</XmlStory>\n</idPkg:BackingStory>\n')
    tags = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<idPkg:Tags xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging" DOMVersion="7.5">\n'
            '\t<XMLTag Self="XMLTag/Root" Name="Root"><Properties><TagColor type="enumeration">LightBlue</TagColor></Properties></XMLTag>\n</idPkg:Tags>\n')

    out = os.path.join(ROOT, 'output', 'parts', NAME + '.idml')
    files = {'designmap.xml': dm, 'META-INF/container.xml': open(os.path.join(TPL, 'META-INF', 'container.xml'), encoding='utf-8').read(),
             'META-INF/metadata.xml': open(os.path.join(TPL, 'META-INF', 'metadata.xml'), encoding='utf-8').read(),
             'Resources/Fonts.xml': open(os.path.join(TPL, 'Resources', 'Fonts.xml'), encoding='utf-8').read(),
             'Resources/Graphic.xml': graphic_xml(), 'Resources/Styles.xml': styles_xml(), 'Resources/Preferences.xml': prefs,
             'XML/BackingStory.xml': backing, 'XML/Tags.xml': tags,
             'MasterSpreads/MasterSpread_%s.xml' % mid: master}
    for s, x in spreads:
        files['Spreads/Spread_%s.xml' % s] = x
    for s, x in STORIES.items():
        files['Stories/Story_%s.xml' % s] = x
    with zipfile.ZipFile(out, 'w') as z:
        z.writestr(zipfile.ZipInfo('mimetype'), 'application/vnd.adobe.indesign-idml-package', compress_type=zipfile.ZIP_STORED)
        for n, x in files.items():
            z.writestr(n, x.encode('utf-8'), compress_type=zipfile.ZIP_DEFLATED)
    print('idml', out, 'pages', n_pages, '(%d-%d)' % (START, START + n_pages - 1), 'stories', len(STORIES), 'spreads', len(spreads))


if __name__ == '__main__':
    main()
