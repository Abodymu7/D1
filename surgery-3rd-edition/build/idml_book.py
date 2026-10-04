"""Cloud IDML build (no InDesign needed): writes a native IDML package for one chapter part,
using the engine's style names (Q-<id>, Opt-<id>, Ans-<id> ...), swatches (IMB ...) and fonts
(Acumin Variable Concept / Source Serif Variable / Source Sans Variable).

  python build/idml_book.py <chapter-id>   (run build/book.py first: page map + flowchart pages)
Output: output/parts/NN-<ch>.idml

The resources (Fonts, Preferences, Styles base, Graphic base) come from an InDesign-generated IDML in
build/idml_template/. Text flows through threaded 2-column frames on A4 facing pages; pages are
numbered from the part JSON start page. Smart Text Reflow is on (adds pages at the end if needed).
"""
import json, math, os, re, sys, zipfile, random
from urllib.parse import quote
from xml.sax.saxutils import escape as xesc

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
TPL = os.path.join(HERE, 'idml_template')
sys.path.insert(0, HERE)
import gen

book = gen.book
import book as HB            # the PDF builder: captions, case grouping, question order, essentials
cid = sys.argv[1] if len(sys.argv) > 1 else book['chapters'][0]['id']
ch = next(c for c in book['chapters'] if c['id'] == cid)
PM = json.load(open(os.environ.get('PAGEMAP', os.path.join(ROOT, 'output', 'pagemap.json'))))
ORDER = [c['id'] for c in book['chapters']]
PARTS = list(dict.fromkeys(c['part'] for c in book['chapters']))
PARTNO = PARTS.index(ch['part']) + 1


def first_in_part(c):
    return [x for x in book['chapters'] if x['part'] == c['part']][0]['id'] == c['id']


def start_page(c):
    """a part's first chapter starts at its part divider, the others at their opener"""
    return PM['anchors']['part-%d' % (PARTS.index(c['part']) + 1)] if first_in_part(c) else PM['anchors']['ch-' + c['id']]


FIRST = first_in_part(ch)
HEAD = 2 if FIRST else 1                     # divider (+) opener
START = start_page(ch)
_nxt = ORDER.index(cid) + 1
END = (start_page(book['chapters'][_nxt]) - 1) if _nxt < len(ORDER) else PM['anchors']['index'] - 1
PLAN = HB.chapter_plan(cid)                  # sections numbered from 1 (local exams share one sequence)
# management flowcharts are placed as full-page images rendered from the PDF build
FC_FIRST = PM['anchors'].get('ess-' + cid)
FC_PAGES = list(range(FC_FIRST, PM['anchors'][PLAN[0]['bid']])) if FC_FIRST else []
CONTENT_PAGES = END - START + 1 - HEAD - len(FC_PAGES)    # (divider +) opener + flowcharts come first
PDF = os.path.join(ROOT, 'output', book.get('file_name', 'book') + '.pdf')
NAME = '%02d-%s' % (ch['order'], cid)
SFX = '-' + cid
OUTDIR = os.path.join(ROOT, 'output', 'idml')
os.makedirs(os.path.join(OUTDIR, 'Links'), exist_ok=True)
SUBS = [(r'\b(SpO|PaO|PaCO|FiO|SaO|CO|O|PO|PCO)2\b', '\\1₂'), (r'\bFEV1\b', 'FEV₁'), (r'\bHCO3', 'HCO₃')]

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
       'IMB Gold': 'E8B64C', 'IMB White': 'FFFFFF', 'IMB Gold Dark': '8A5A00', 'IMB ' + cid: ch['color']}
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
    pstyle('DivKicker' + SFX, font=FD, leading=10, FontStyle='Semibold', PointSize=7.6, Tracking=200, FillColor=WHITE, Capitalization='AllCaps', Hyphenation='false')
    pstyle('DivNum' + SFX, font=FD, leading=190, FontStyle='ExtraCondensed Black', PointSize=190, FillColor=ACC, Hyphenation='false', Tracking=-20)
    pstyle('DivTitle' + SFX, font=FD, leading=19, FontStyle='Condensed Bold', PointSize=17, FillColor=WHITE, Capitalization='AllCaps', Hyphenation='false')
    pstyle('OpGhost' + SFX, font=FD, leading=260, FontStyle='ExtraCondensed Black', PointSize=260, FillColor=ACC, FillTint=9, Hyphenation='false', Justification='RightAlign')
    pstyle('DivCredit' + SFX, font=FSANS, leading=8, FontStyle='Regular', PointSize=6.5, FillColor=LINE, Hyphenation='false')
    pstyle('OpKicker' + SFX, font=FD, leading=10, FontStyle='Semibold', PointSize=8, Tracking=200, FillColor=ACC, Capitalization='AllCaps', SpaceAfter=mm(3), Hyphenation='false')
    pstyle('OpTitle' + SFX, font=FD, leading=43, FontStyle='Condensed Bold', PointSize=46, FillColor=INK, Hyphenation='false')
    pstyle('OpIntro' + SFX, font=FSER, leading=15, FontStyle='Regular', PointSize=11, FillColor=INK2)
    pstyle('StatNum' + SFX, font=FD, leading=28, FontStyle='ExtraCondensed Black', PointSize=30, FillColor=ACC, Hyphenation='false')
    pstyle('StatLbl' + SFX, font=FD, leading=9, FontStyle='Semibold', PointSize=7, Tracking=120, FillColor=MUTED, Capitalization='AllCaps', Hyphenation='false')
    pstyle('OpHead' + SFX, font=FD, leading=10, FontStyle='Semibold', PointSize=7.5, Tracking=160, FillColor=ACC, Capitalization='AllCaps', SpaceAfter=mm(2.5), Hyphenation='false')
    pstyle('OpToc' + SFX, font=FD, leading=14, tabs=[(mm(9), 'LeftAlign'), (mm(140), 'RightAlign'), (mm(172), 'RightAlign')], props={'RuleBelowColor': LINE},
           FontStyle='Condensed Bold', PointSize=10.5, FillColor=INK, SpaceAfter=mm(2.2), RuleBelow='true', RuleBelowLineWeight=0.5,
           RuleBelowOffset=mm(1.6), RuleBelowWidth='ColumnWidth', Hyphenation='false')
    pstyle('OpTopic' + SFX, font=FSANS, leading=12.5, tabs=[(mm(4), 'LeftAlign')], FontStyle='Regular', PointSize=9, FillColor=INK2,
           LeftIndent=mm(4), FirstLineIndent=-mm(4), Hyphenation='false')
    cstyle('Bullet' + SFX, FD, FontStyle='Bold', FillColor=ACC)
    cstyle('TocCount' + SFX, FSANS, FontStyle='Regular', PointSize=9, FillColor=MUTED)
    cstyle('TocPage' + SFX, FD, FontStyle='Condensed Bold', FillColor=ACC)
    # --- v4 additions: essentials, case, repeat caption, updated tag
    GD = 'Color/IMB Gold Dark'
    pstyle('BankKickerFirst' + SFX, based='BankKicker' + SFX, SpaceBefore=0)
    pstyle('EssKicker' + SFX, based='BankKicker' + SFX, SpaceBefore=0)
    pstyle('EssHead' + SFX, based='BankHead' + SFX)
    pstyle('BoxHead' + SFX, font=FD, leading=15, props=sp_all, FontStyle='Condensed Bold', PointSize=13, FillColor=INK, SpaceBefore=mm(5),
           SpaceAfter=mm(2), KeepWithNext=2, Hyphenation='false', **span)
    pstyle('PairHead' + SFX, font=FD, leading=9, tabs=[(TW, 'RightAlign')], props=dict(sp_all, RuleBelowColor=INK), FontStyle='Semibold', PointSize=6.6,
           Tracking=160, FillColor=MUTED, SpaceAfter=mm(1.5), RuleBelow='true', RuleBelowLineWeight=0.8, RuleBelowOffset=mm(1), RuleBelowWidth='ColumnWidth',
           KeepWithNext=1, Hyphenation='false', **span)
    pstyle('PairRow' + SFX, font=FSANS, leading=14, tabs=[(TW, 'RightAlign')], props=sp_all, FontStyle='Regular', PointSize=8.6, SpaceAfter=mm(0.6),
           Hyphenation='false', KeepLinesTogether='true', **span)
    pstyle('FactRow' + SFX, font=FSANS, leading=11.4, tabs=[(mm(38), 'LeftAlign')], props=dict(sp_all, RuleBelowColor=LINE), FontStyle='Regular',
           PointSize=8.5, LeftIndent=mm(38), FirstLineIndent=-mm(38), SpaceAfter=mm(2.2), RuleBelow='true', RuleBelowLineWeight=0.4,
           RuleBelowOffset=mm(1.2), RuleBelowWidth='ColumnWidth', KeepLinesTogether='true', **span)
    pstyle('CardName' + SFX, font=FD, leading=13, props=dict(sp_all, RuleAboveColor=ACC), FontStyle='Condensed Bold', PointSize=11, FillColor=ACC,
           SpaceBefore=mm(3), SpaceAfter=mm(0.8), KeepWithNext=2, RuleAbove='true', RuleAboveLineWeight=2.2, RuleAboveOffset=mm(4.6),
           RuleAboveWidth='ColumnWidth', Hyphenation='false', **span)
    pstyle('CardLine' + SFX, font=FSANS, leading=10.4, tabs=[(mm(30), 'LeftAlign')], props=sp_all, FontStyle='Regular', PointSize=8, LeftIndent=mm(30),
           FirstLineIndent=-mm(30), SpaceAfter=mm(0.6), KeepLinesTogether='true', **span)
    pstyle('StepRow' + SFX, font=FSANS, leading=11.6, tabs=[(mm(10), 'LeftAlign')], props=sp_all, FontStyle='Regular', PointSize=8.6, LeftIndent=mm(10),
           FirstLineIndent=-mm(10), SpaceAfter=mm(2.4), KeepLinesTogether='true', **span)
    pstyle('ChipsRow' + SFX, font=FSANS, leading=16, props=sp_all, FontStyle='Regular', PointSize=8.4, SpaceAfter=mm(1.5), **span)
    pstyle('Note' + SFX, font=FSER, leading=11, props=sp_all, FontStyle='Italic', PointSize=8.4, FillColor=INK2, **span)
    cstyle('Chip' + SFX, FSANS, props={'UnderlineColor': ACC}, FontStyle='Semibold', PointSize=8, FillColor=ACC, Underline='true',
           UnderlineWeight=11, UnderlineOffset=-3.2, UnderlineTint=14)
    cstyle('FactLbl' + SFX, FD, FontStyle='Condensed Bold', PointSize=9.4, FillColor=ACC)
    cstyle('CardLbl' + SFX, FD, FontStyle='Semibold', PointSize=6, Tracking=140, FillColor=MUTED)
    cstyle('StepNum' + SFX, FD, props={'UnderlineColor': ACC}, FontStyle='Condensed Bold', PointSize=10, FillColor=WHITE, Underline='true',
           UnderlineWeight=12, UnderlineOffset=-3.4, UnderlineTint=100)
    cstyle('StepTitle' + SFX, FD, FontStyle='Condensed Bold', PointSize=10.5, FillColor=INK)
    pstyle('CaseKicker' + SFX, font=FD, leading=9, props={'RuleAboveColor': ACC}, FontStyle='Semibold', PointSize=6.6, Tracking=140, FillColor=ACC,
           SpaceBefore=mm(2), SpaceAfter=mm(0.8), KeepWithNext=2, RuleAbove='true', RuleAboveLineWeight=1.4, RuleAboveOffset=mm(3), RuleAboveWidth='ColumnWidth',
           Hyphenation='false')
    pstyle('Case' + SFX, font=FSER, leading=11.6, FontStyle='Italic', PointSize=8.8, SpaceAfter=mm(2.6), KeepWithNext=2, KeepAllLinesTogether='true')
    pstyle('Repeat' + SFX, font=FSANS, leading=9.4, props={'RuleAboveColor': GOLD}, FontStyle='Regular', PointSize=7.4, FillColor=INK2, LeftIndent=mm(7.5),
           SpaceBefore=mm(1.4), SpaceAfter=mm(3), RuleAbove='true', RuleAboveLineWeight=1.4, RuleAboveOffset=mm(2.6), RuleAboveWidth='ColumnWidth',
           RuleAboveLeftIndent=mm(7.5), KeepLinesTogether='true')
    cstyle('RepeatK' + SFX, FD, FontStyle='Bold', PointSize=6.6, Tracking=140, FillColor=GD)
    cstyle('Upd' + SFX, FD, FontStyle='Semibold', PointSize=5.8, Tracking=120, FillColor=MUTED)
    # --- 3rd edition: source sub-heads in the local-exams section, EMQ answer themes
    pstyle('SubSrc' + SFX, font=FD, leading=10, props={'RuleBelowColor': ACC}, FontStyle='Condensed Bold', PointSize=7.4, Tracking=120, FillColor=ACC,
           SpaceBefore=mm(1.5), SpaceAfter=mm(2.4), KeepWithNext=2, RuleBelow='true', RuleBelowLineWeight=0.6, RuleBelowOffset=mm(1.2),
           RuleBelowWidth='ColumnWidth', Hyphenation='false')
    cstyle('SubSrcNote' + SFX, FSANS, FontStyle='Regular', PointSize=6.8, Tracking=0, Capitalization='Normal', FillColor=MUTED)
    pstyle('AnsTheme' + SFX, font=FD, leading=10.4, FontStyle='Condensed Bold', PointSize=8.6, FillColor=ACC, SpaceBefore=mm(2.2), SpaceAfter=mm(1.2),
           KeepWithNext=1, Hyphenation='false')


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
            br = '<Br/>' if (j == len(runs) - 1 and not last and not cs) else ''
            if text.startswith('<Rectangle'):
                r.append('<CharacterStyleRange AppliedCharacterStyle="%s">%s%s</CharacterStyleRange>' % (NO_CS, text, br))
            else:
                content = text if text.startswith('<?ACE') else xesc(text)
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
    for pat, rep in SUBS:
        text = re.sub(pat, rep, text or '')
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


LINKS = {}


def placeholder(fn):
    """grey stand-in with the original file name: replace the file in Links/ by the real picture and update the link"""
    from PIL import Image as PImage, ImageDraw
    d = os.path.join(OUTDIR, 'Links')
    dst = os.path.join(d, fn)
    if not os.path.exists(dst):
        im = PImage.new('RGB', (900, 560), (236, 239, 242))
        dr = ImageDraw.Draw(im)
        dr.rectangle([6, 6, 893, 553], outline=(150, 156, 166), width=4)
        dr.text((40, 250), 'FIGURE - original picture not supplied', fill=(90, 96, 110))
        dr.text((40, 290), fn, fill=(90, 96, 110))
        ext = fn.rsplit('.', 1)[-1].lower()
        im.save(dst, 'PNG' if ext == 'png' else 'JPEG')
    return dst


def inline_image(rel, max_w_mm=76.5, max_h_mm=62):
    """anchored inline graphic linked to Links/<file>"""
    from PIL import Image as PImage
    src = os.path.join(ROOT, 'assets', rel)
    fn = os.path.basename(rel)
    if not os.path.exists(src):
        src = placeholder(fn)
    LINKS[fn] = src
    pw, ph = PImage.open(src).size
    w = max_w_mm * MM; h = w * ph / pw
    if h > max_h_mm * MM:
        h = max_h_mm * MM; w = h * pw / ph
    sx, sy = w / pw, h / ph
    ext = fn.rsplit('.', 1)[-1].lower()
    fmt = {'png': '$ID/Portable Network Graphics (PNG)', 'jpg': '$ID/JPEG', 'jpeg': '$ID/JPEG'}.get(ext, '$ID/JPEG')
    return ('<Rectangle Self="%s" ContentType="GraphicType" StoryTitle="$ID/" StrokeWeight="0.5" StrokeColor="%s" FillColor="Swatch/None" '
            'ItemTransform="1 0 0 1 0 0" AppliedObjectStyle="ObjectStyle/$ID/[None]">%s'
            '<AnchoredObjectSetting AnchoredPosition="InlinePosition" SpineRelative="false" LockPosition="false" PinPosition="true" '
            'AnchorYoffset="0"/>%s'
            '<FrameFittingOption FittingOnEmptyFrame="Proportionally"/>'
            '<Image Self="%s" ImageTypeName="%s" ItemTransform="%s 0 0 %s 0 0" Space="$ID/#Links_RGB" ActualPpi="72 72" EffectivePpi="%s %s" ImageRenderingIntent="UseColorSettings">'
            '<Properties><Profile type="string">$ID/None</Profile><GraphicBounds Left="0" Top="0" Right="%d" Bottom="%d"/></Properties>'
            '<Link Self="%s" AssetURL="$ID/" AssetID="$ID/" LinkResourceURI="file:Links/%s" LinkResourceFormat="%s" StoredState="Normal" '
            'LinkClassID="35906" LinkClientID="257" LinkResourceModified="false" LinkObjectModified="false" ShowInUI="true" CanEmbed="true" '
            'CanUnembed="true" CanPackage="true" ImportPolicy="NoAutoImport" ExportPolicy="NoAutoExport" LinkImportStamp="" LinkImportModificationTime="" LinkImportTime=""/>'
            '</Image></Rectangle>') % (
        uid(), LINE, path(box(0, 0, w, h)), WRAP, uid(), a(fmt.replace('Portable Network Graphics (PNG)', 'PNG')), num(sx), num(sy), int(72 / sx), int(72 / sy), pw, ph, uid(), a(quote(fn)), a(fmt))


def main_story():
    P = []
    n_sets = 0
    qs = [q for sec in PLAN for q in sec['items']]
    for bi, sec in enumerate(PLAN):
        typ, label = sec['type'], sec['label']
        n_sets += len(sec['sets'])
        kind = 'THEMES  /  %d SCENARIOS' % sec['units'] if typ == 'EMQ' else 'QUESTIONS'
        cnt = len(sec['items']) if typ == 'EMQ' else sec['units']
        P.append(('BankKickerFirst' + SFX if bi == 0 else 'BankKicker' + SFX, [(None, ('%d %s  •  %s' % (cnt, kind, sec['blurb'].replace(' · ', ' / '))).upper(), None)]))
        P.append(('BankHead' + SFX, [(None, label, None)]))
        for si, s in enumerate(sec['sets']):
            if len(sec['sets']) > 1:
                P.append(('SetHead' + SFX, [(None, 'Set %d of %d' % (si + 1, len(sec['sets'])), None)]))
            groups = HB.case_groups(s) if typ == 'MCQ' else {}
            strip = {}
            for gi, (pre, cnt_) in groups.items():
                for k in range(gi, gi + cnt_):
                    strip[k] = len(pre)
            for qi, q in enumerate(s):
                if q.get('_sub'):
                    a_, b_ = HB.SUBLAB.get(q['_sub'], (q['_sub'], ''))
                    P.append(('SubSrc' + SFX, [(None, a_.upper(), None)] + ([(None, '\u2028', None), ('SubSrcNote' + SFX, b_, None)] if b_ else [])))
                if qi in groups:
                    pre, cnt_ = groups[qi]
                    P.append(('CaseKicker' + SFX, [(None, 'CASE  /  QUESTIONS %d–%d' % (q['_num'], s[qi + cnt_ - 1]['_num']), None)]))
                    P.append(('Case' + SFX, rich_runs(pre)))
                if typ == 'MCQ':
                    stem = q['stem'][strip[qi]:].strip() if qi in strip else q['stem']
                    stem = stem[:1].upper() + stem[1:]
                    P.append(('Q' + SFX, [('QNum' + SFX, str(q['_num']), None), (None, '\t', None)] + rich_runs(stem)))
                    for im in q.get('images') or []:
                        P.append(('QImage' + SFX, [(None, inline_image(im), None)]))
                    for i, o in enumerate(q['options']):
                        st = 'OptLast' if i == len(q['options']) - 1 else 'Opt'
                        P.append((st + SFX, [('OptL' + SFX, chr(65 + i), None), (None, '\t', None)] + rich_runs(o)))
                else:
                    P.append(('EmqTheme' + SFX, [('EmqThemeLbl' + SFX, 'THEME %d' % q['_num'], None), (None, '\t' + q['theme'], None)]))
                    for im in q.get('images') or []:
                        P.append(('QImage' + SFX, [(None, inline_image(im), None)]))
                    for i, o in enumerate(q['options']):
                        st = 'EmqOptLast' if i == len(q['options']) - 1 else 'EmqOpt'
                        P.append((st + SFX, [('OptL' + SFX, chr(65 + i), None), (None, '\t', None)] + rich_runs(o)))
                    P.append(('EmqLead' + SFX, [(None, 'For each scenario, choose the single most appropriate option. Each option may be used once, more than once or not at all.', None)]))
                    for k, it in enumerate(q['items']):
                        st = 'QLast' if k == len(q['items']) - 1 else 'Q'
                        P.append((st + SFX, [('QNum' + SFX, str(it['_num']), None), (None, '\t', None)] + rich_runs(it['stem'])))
                        for im in it.get('images') or []:
                            P.append(('QImage' + SFX, [(None, inline_image(im), None)]))
                if q['id'] in HB.CAP:
                    n, order = HB.CAP[q['id']]
                    src = '  /  '.join('%s%s' % (b_, ' ×%d' % k_ if k_ > 1 else '') for b_, k_ in order)
                    P.append(('Repeat' + SFX, [('RepeatK' + SFX, 'REPEATED %d×  /  ALSO ASKED IN' % n, None), (None, '\u2028', None)] + rich_runs(src)))
            if typ == 'MCQ':
                head = 'Answers  %d–%d' % (s[0]['_num'], s[-1]['_num']) if len(s) > 1 else 'Answer  %d' % s[0]['_num']
            else:
                head = 'Answers  /  Themes %d–%d' % (s[0]['_num'], s[-1]['_num']) if len(s) > 1 else 'Answers  /  Theme %d' % s[0]['_num']
            P.append(('AnsHead' + SFX, [(None, head, None), (None, '<?ACE 8?>', None), ('AnsHeadBank' + SFX, label, None)]))
            for q in s:
                if typ == 'MCQ':
                    opt = q['options'][ord(q['answer']) - 65] if len(q['answer']) == 1 else 'True: ' + ', '.join(q['answer'])
                    recs = [(q['_num'], ' '.join(q['answer']), opt, q['explanation'], q)]
                else:
                    P.append(('AnsTheme' + SFX, [(None, 'Theme %d  /  %s' % (q['_num'], q['theme']), None)]))
                    L = q['option_letters']
                    recs = [(it['_num'], chr(65 + L.index(it['answer'])), q['options'][L.index(it['answer'])], it['explanation'], None) for it in q['items']]
                for n, Lt, opt, ex, qq in recs:
                    upd = [('Upd' + SFX, 'UPDATED', None), (None, ' ', None)] if qq and qq.get('status') == 'corrected' else []
                    P.append(('Ans' + SFX, [('ANum' + SFX, str(n), None), (None, '\t', None), ('ALetter' + SFX, ' %s ' % Lt, None), (None, ' ', None)]
                              + rich_runs(opt, 'AOpt' + SFX) + [(None, ' — ', None)] + upd + rich_runs(ex)))
    total = sum(sec['units'] for sec in PLAN)
    return story(P), total, qs, n_sets


def flowchart_pages():
    """render the chapter's flowchart pages of the PDF build to JPEGs for placing"""
    import fitz
    out = []
    if not FC_PAGES:
        return out
    d = fitz.open(PDF)
    for pg in FC_PAGES:
        fn = 'flowchart-%s-p%d.jpg' % (cid, pg)
        dst = os.path.join(OUTDIR, 'Links', fn)
        d[pg - 1].get_pixmap(dpi=300).save(dst, jpg_quality=90)
        out.append((pg, dst, fn))
    return out


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
        ty = 24 + HB.tab_pos(ch) * 25
        tx = (-3, 6) if side == 'L' else (204, 213)
        items.append(rect(pts(side, ty, tx[0], ty + 23, tx[1]), ACC))
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
def placed_image(c, rel_src, fn):
    """rectangle (spread coords) with a linked image fitted proportionally to fill it"""
    from PIL import Image as PImage
    LINKS[fn] = rel_src
    pw, ph = PImage.open(rel_src).size
    x0, y0, x1, y1 = c
    sc = max((x1 - x0) / pw, (y1 - y0) / ph)
    ox = x0 + ((x1 - x0) - pw * sc) / 2
    oy = y0 + ((y1 - y0) - ph * sc) / 2
    return ('<Rectangle Self="%s" ContentType="GraphicType" StoryTitle="$ID/" FillColor="%s" StrokeWeight="0" StrokeColor="Swatch/None" '
            'AppliedObjectStyle="ObjectStyle/$ID/[None]" %s>%s%s'
            '<Image Self="%s" ImageTypeName="$ID/JPEG" ItemTransform="%s 0 0 %s %s %s" Space="$ID/#Links_RGB" ActualPpi="72 72" EffectivePpi="%d %d" ImageRenderingIntent="UseColorSettings">'
            '<Properties><Profile type="string">$ID/None</Profile><GraphicBounds Left="0" Top="0" Right="%d" Bottom="%d"/></Properties>'
            '<Link Self="%s" AssetURL="$ID/" AssetID="$ID/" LinkResourceURI="file:Links/%s" LinkResourceFormat="$ID/JPEG" StoredState="Normal" '
            'LinkClassID="35906" LinkClientID="257" LinkResourceModified="false" LinkObjectModified="false" ShowInUI="true" CanEmbed="true" '
            'CanUnembed="true" CanPackage="true" ImportPolicy="NoAutoImport" ExportPolicy="NoAutoExport" LinkImportStamp="" LinkImportModificationTime="" LinkImportTime=""/>'
            '</Image></Rectangle>') % (uid(), INK, COMMON, path(box(*c)), WRAP, uid(), num(sc), num(sc), num(ox), num(oy),
                                       int(72 / sc), int(72 / sc), pw, ph, uid(), a(fn))


def divider_items():
    it = []
    pch = [x for x in book['chapters'] if x['part'] == ch['part']]
    it.append(placed_image(pts('L', -3, -3, 300, 210), os.path.join(ROOT, 'assets', 'dividers', 'part-%d.jpg' % PARTNO), 'divider-part-%d.jpg' % PARTNO))
    it.append(tframe(pts('L', 18, 18, 24, 190), simple('DivKicker' + SFX, 'Part %02d  /  %d chapters' % (PARTNO, len(pch))))[1])
    it.append(tframe(pts('L', 34, 18, 34 + 5.2 * len(pch), 120), story([('DivKicker' + SFX, [(None, '%02d   %s' % (x['order'], x['title']), None)]) for x in pch]))[1])
    it.append(tframe(pts('L', 180, 13, 252, 190), simple('DivNum' + SFX, '%02d' % PARTNO), vj='BottomAlign')[1])
    it.append(tframe(pts('L', 253, 18, 266, 190), simple('DivTitle' + SFX, ch['part']))[1])
    it.append(tframe(pts('L', 283, 120, 288, 198), simple('DivCredit' + SFX, 'Artwork drawn for this edition'))[1])
    return it


def opener_items(total, qs, n_sets, side='R'):
    it = []
    L, R = (M['inside'], 210 - M['outside']) if side == 'R' else (M['outside'], 210 - M['inside'])
    it.append(tframe(pts(side, 185, 100, 296, 214) if side == 'R' else pts(side, 185, -4, 296, 110), simple('OpGhost' + SFX, '%02d' % ch['order']), vj='BottomAlign')[1])
    ty = 24 + HB.tab_pos(ch) * 25
    tx = (204, 213) if side == 'R' else (-3, 6)
    it.append(rect(pts(side, ty, tx[0], ty + 23, tx[1]), ACC))
    it.append(tframe(pts(side, 25, L, 80, R), story([('OpKicker' + SFX, [(None, ch['part'], None)]),
                                                   ('OpTitle' + SFX, [(None, ch['title'], None)])]), vj='BottomAlign')[1])
    it.append(rect(pts(side, 83, L, 84.4, L + 34), ACC))
    it.append(tframe(pts(side, 90, L, 120, L + 150), simple('OpIntro' + SFX, ch.get('intro', '')))[1])
    n_mcq = sum(1 for q in qs if q['type'] == 'MCQ')
    n_emq = sum(len(q['items']) for q in qs if q['type'] == 'EMQ')
    n_rep = sum(1 for q in qs if q['id'] in HB.CAP)
    stats = [(n_mcq, 'MCQs'), (n_emq, 'EMQ scenarios'), (len(PLAN), 'sources'), (n_rep, 'repeated ideas')]
    for i, (n, lbl) in enumerate(stats):
        xl = L + i * 43.5
        it.append(rect(pts(side, 124, xl, 124.5, xl + 38), ACC))
        it.append(tframe(pts(side, 126, xl, 142, xl + 40), story([('StatNum' + SFX, [(None, str(n), None)]), ('StatLbl' + SFX, [(None, lbl, None)])]))[1])
    toc = [('OpHead' + SFX, [(None, 'In this chapter', None)])]
    rows = []
    if HB.ESS.get(cid):
        rows.append(('Management flowcharts', '%d charts' % len(HB.ESS[cid]), PM['anchors'].get('ess-' + cid)))
    for sec in PLAN:
        rows.append((sec['label'], '%d Q' % sec['units'], PM['anchors'].get(sec['bid'])))
    for k, (ttl, cnt, pg) in enumerate(rows):
        toc.append(('OpToc' + SFX, [('TocPage' + SFX, '%02d' % (k + 1), None), (None, '\t' + ttl + '\t', None), ('TocCount' + SFX, cnt, None), (None, '\t', None),
                                    ('TocPage' + SFX, 'page %s' % (pg or ''), None)]))
    it.append(tframe(pts(side, 150, L, 277, R), story(toc))[1])
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
    main_sid, total, qs, n_sets = main_story()
    # content frames, threaded
    FCP = flowchart_pages()
    NF = len(FCP)
    n_pages = HEAD + NF + CONTENT_PAGES
    numbers = list(range(START, START + n_pages))
    sides = ['L' if n % 2 == 0 else 'R' for n in numbers]
    fids = [uid() for _ in range(CONTENT_PAGES)]
    page_items = {HEAD - 1: opener_items(total, qs, n_sets, sides[HEAD - 1])}
    if FIRST:
        page_items[0] = divider_items()
    for k, (pg, dst, fn) in enumerate(FCP):
        side = sides[HEAD + k]
        page_items[HEAD + k] = [placed_image(pts(side, 0, 0, 297, 210), dst, fn)]
    for k in range(CONTENT_PAGES):
        pi = HEAD + NF + k
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
            pxml.append(page_xml(pid, sides[pi], numbers[pi], 'n' if pi < HEAD + NF else mid))
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

    out = os.path.join(OUTDIR, NAME + '.idml')
    import shutil
    for fn, src in LINKS.items():
        dst = os.path.join(OUTDIR, 'Links', fn)
        if os.path.abspath(src) != os.path.abspath(dst):
            shutil.copy(src, dst)
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
