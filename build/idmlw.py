"""IDML writing helpers: XML snippets for pages, frames, rectangles, stories and styles."""
from xml.sax.saxutils import escape, quoteattr

PAGE_W = 595.2756
PAGE_H = 841.8898
HALF_H = PAGE_H / 2
BLEED = 8.5039
LAYER = 'ub3'


def f(v):
    s = f'{v:.4f}'.rstrip('0').rstrip('.')
    return s if s not in ('-0', '') else '0'


def page_origin(side):
    """Spread coordinates of the top-left corner of a page. side 0 = left, 1 = right."""
    return (-PAGE_W if side == 0 else 0.0, -HALF_H)


def path_xml(w, h):
    pts = [(0, 0), (0, h), (w, h), (w, 0)]
    a = ''.join(f'<PathPointType Anchor="{f(x)} {f(y)}" LeftDirection="{f(x)} {f(y)}" RightDirection="{f(x)} {f(y)}"/>'
                for x, y in pts)
    return (f'<Properties><PathGeometry><GeometryPathType PathOpen="false"><PathPointArray>{a}'
            f'</PathPointArray></GeometryPathType></PathGeometry></Properties>')


WRAP = ('<TextWrapPreference Inverse="false" ApplyToMasterPageOnly="false" TextWrapSide="BothSides" '
        'TextWrapMode="None"><Properties><TextWrapOffset Top="0" Left="0" Bottom="0" Right="0"/></Properties>'
        '</TextWrapPreference>')


def link_xml(self_id, fname, fmt='JPEG'):
    lf = '$ID/JPEG' if fmt == 'JPEG' else '$ID/Portable Network Graphics (PNG)'
    return (f'<Link Self="{self_id}" AssetURL="$ID/" AssetID="$ID/" LinkResourceURI="file:Links/{escape(fname)}" '
            f'LinkResourceFormat="{lf}" StoredState="Normal" LinkClassID="35906" LinkClientID="257" '
            f'LinkResourceModified="false" LinkObjectModified="false" ShowInUI="true" CanEmbed="true" '
            f'CanUnembed="true" CanPackage="true" ImportPolicy="NoAutoImport" ExportPolicy="NoAutoExport" '
            f'LinkImportStamp="" LinkImportModificationTime="" LinkImportTime=""/>')


def rect_xml(self_id, x, y, w, h, fill='Swatch/None', stroke='Swatch/None', sw=0, image=None, tint=None):
    """Rectangle at spread coords (x, y). image = (self_id, fname, pxw, pxh, scale, offx, offy)."""
    t = f' FillTint="{f(tint)}"' if tint is not None else ''
    inner = ''
    ctype = 'Unassigned'
    if image:
        iid, fname, pw, ph, sc, ox, oy = image
        fmt = 'PNG' if fname.lower().endswith('.png') else 'JPEG'
        ctype = 'GraphicType'
        tn = '$ID/JPEG' if fmt == 'JPEG' else '$ID/PNG'
        inner = (f'<Image Self="{iid}" ImageTypeName="{tn}" ItemTransform="{f(sc)} 0 0 {f(sc)} {f(ox)} {f(oy)}" '
                 f'Space="$ID/#Links_RGB" ActualPpi="72 72" EffectivePpi="{int(72 / sc)} {int(72 / sc)}" '
                 f'ImageRenderingIntent="UseColorSettings"><Properties><Profile type="string">$ID/None</Profile>'
                 f'<GraphicBounds Left="0" Top="0" Right="{pw}" Bottom="{ph}"/></Properties>'
                 f'{link_xml(iid + "l", fname, fmt)}</Image>')
    return (f'<Rectangle Self="{self_id}" ContentType="{ctype}" StoryTitle="$ID/" FillColor="{fill}"{t} '
            f'StrokeWeight="{f(sw)}" StrokeColor="{stroke}" AppliedObjectStyle="ObjectStyle/$ID/[None]" '
            f'ItemLayer="{LAYER}" Locked="false" LocalDisplaySetting="Default" Visible="true" Name="$ID/" '
            f'ItemTransform="1 0 0 1 {f(x)} {f(y)}">{path_xml(w, h)}{WRAP}{inner}</Rectangle>')


def frame_xml(self_id, story, x, y, w, h, cols=1, gutter=17.0079, vj='TopAlign', prev='n', nxt='n'):
    return (f'<TextFrame Self="{self_id}" ParentStory="{story}" PreviousTextFrame="{prev}" NextTextFrame="{nxt}" '
            f'ContentType="TextType" AppliedObjectStyle="ObjectStyle/$ID/[None]" FillColor="Swatch/None" '
            f'StrokeWeight="0" StrokeColor="Swatch/None" ItemLayer="{LAYER}" Locked="false" '
            f'LocalDisplaySetting="Default" Visible="true" Name="$ID/" ItemTransform="1 0 0 1 {f(x)} {f(y)}">'
            f'{path_xml(w, h)}<TextFramePreference TextColumnCount="{cols}" TextColumnGutter="{f(gutter)}" '
            f'UseFixedColumnWidth="false" FirstBaselineOffset="AscentOffset" VerticalJustification="{vj}"/>'
            f'{WRAP}</TextFrame>')


def line_xml(self_id, x0, y0, x1, y1, color, sw):
    return (f'<GraphicLine Self="{self_id}" ContentType="Unassigned" StrokeWeight="{f(sw)}" StrokeColor="{color}" '
            f'FillColor="Swatch/None" AppliedObjectStyle="ObjectStyle/$ID/[None]" ItemLayer="{LAYER}" '
            f'Locked="false" LocalDisplaySetting="Default" Visible="true" Name="$ID/" ItemTransform="1 0 0 1 0 0">'
            f'<Properties><PathGeometry><GeometryPathType PathOpen="true"><PathPointArray>'
            f'<PathPointType Anchor="{f(x0)} {f(y0)}" LeftDirection="{f(x0)} {f(y0)}" RightDirection="{f(x0)} {f(y0)}"/>'
            f'<PathPointType Anchor="{f(x1)} {f(y1)}" LeftDirection="{f(x1)} {f(y1)}" RightDirection="{f(x1)} {f(y1)}"/>'
            f'</PathPointArray></GeometryPathType></PathGeometry></Properties>{WRAP}</GraphicLine>')


def page_xml(self_id, name, side, master='n', margins=None):
    m = margins or dict(Top=59.5276, Bottom=56.6929, Left=48.189 if side == 0 else 53.8583,
                        Right=53.8583 if side == 0 else 48.189)
    ox, oy = page_origin(side)
    cw = PAGE_W - m['Left'] - m['Right']
    colw = (cw - 17.0079) / 2
    return (f'<Page Self="{self_id}" GeometricBounds="0 0 {f(PAGE_H)} {f(PAGE_W)}" ItemTransform="1 0 0 1 {f(ox)} {f(oy)}" '
            f'Name="{name}" AppliedTrapPreset="TrapPreset/$ID/kDefaultTrapStyleName" OverrideList="" '
            f'AppliedMaster="{master}" MasterPageTransform="1 0 0 1 0 0" TabOrder="" GridStartingPoint="TopOutside" '
            f'UseMasterGrid="true"><Properties><PageColor type="enumeration">UseMasterColor</PageColor></Properties>'
            f'<MarginPreference ColumnCount="2" ColumnGutter="17.0079" Top="{f(m["Top"])}" Bottom="{f(m["Bottom"])}" '
            f'Left="{f(m["Left"])}" Right="{f(m["Right"])}" ColumnDirection="Horizontal" '
            f'ColumnsPositions="0 {f(colw)} {f(colw + 17.0079)} {f(cw)}"/></Page>')


def spread_xml(self_id, pages_xml, items_xml, page_count, binding):
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<idPkg:Spread xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging" DOMVersion="7.5">\n'
            f'\t<Spread Self="{self_id}" FlattenerOverride="Default" AllowPageShuffle="true" ItemTransform="1 0 0 1 0 0" '
            f'ShowMasterItems="true" PageCount="{page_count}" BindingLocation="{binding}" PageTransitionType="None" '
            f'PageTransitionDirection="NotApplicable" PageTransitionDuration="Medium">\n'
            '\t\t<FlattenerPreference LineArtAndTextResolution="300" GradientAndMeshResolution="150" '
            'ClipComplexRegions="false" ConvertAllStrokesToOutlines="false" ConvertAllTextToOutlines="false">'
            '<Properties><RasterVectorBalance type="double">50</RasterVectorBalance></Properties></FlattenerPreference>\n\t\t'
            + '\n\t\t'.join(pages_xml) + '\n\t\t' + '\n\t\t'.join(items_xml) +
            '\n\t</Spread>\n</idPkg:Spread>\n')


def story_xml(self_id, paras):
    """paras: list of (pstyle, [(cstyle or None, text)]). Text may contain \t; '\x18' = page number."""
    out = []
    for i, (ps, runs) in enumerate(paras):
        rs = []
        for cs, txt in runs:
            cs = cs or '$ID/[No character style]'
            parts = txt.split('\x18')
            content = '<?ACE 18?>'.join(escape(p) for p in parts)
            rs.append(f'<CharacterStyleRange AppliedCharacterStyle="CharacterStyle/{cs}"><Content>{content}</Content></CharacterStyleRange>')
        if i < len(paras) - 1:
            rs.append('<CharacterStyleRange AppliedCharacterStyle="CharacterStyle/$ID/[No character style]"><Br/></CharacterStyleRange>')
        out.append(f'<ParagraphStyleRange AppliedParagraphStyle="ParagraphStyle/{escape(ps)}">' + ''.join(rs) + '</ParagraphStyleRange>')
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<idPkg:Story xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging" DOMVersion="7.5">\n'
            f'\t<Story Self="{self_id}" AppliedTOCStyle="n" TrackChanges="false" StoryTitle="$ID/" AppliedNamedGrid="n">\n'
            '\t\t<StoryPreference OpticalMarginAlignment="false" OpticalMarginSize="12" FrameType="TextFrameType" '
            'StoryOrientation="Horizontal" StoryDirection="LeftToRightDirection"/>\n'
            '\t\t<InCopyExportOption IncludeGraphicProxies="true" IncludeAllResources="false"/>\n\t\t'
            + '\n\t\t'.join(out) + '\n\t</Story>\n</idPkg:Story>\n')


def pstyle_xml(name, font='Acumin Variable Concept', style='Regular', size=10, leading=12, color='Color/IMB Ink',
               align='LeftAlign', tracking=0, caps=False, sb=0, sa=0, li=0, fi=0, ri=0, tabs=None,
               rule_above=None, rule_below=None, hyph=False, tint=None, keep_next=0, based='ParagraphStyle/IMB Base'):
    a = (f'<ParagraphStyle Self="ParagraphStyle/{escape(name)}" Name={quoteattr(name)} Imported="false" '
         f'NextStyle="ParagraphStyle/{escape(name)}" KeyboardShortcut="0 0" FontStyle={quoteattr(style)} '
         f'PointSize="{f(size)}" FillColor="{color}" Justification="{align}" Tracking="{f(tracking)}" '
         f'Capitalization="{"AllCaps" if caps else "Normal"}" SpaceBefore="{f(sb)}" SpaceAfter="{f(sa)}" '
         f'LeftIndent="{f(li)}" FirstLineIndent="{f(fi)}" RightIndent="{f(ri)}" Hyphenation="{"true" if hyph else "false"}" '
         f'KeepWithNext="{keep_next}"')
    if tint is not None:
        a += f' FillTint="{f(tint)}"'
    props = [f'<BasedOn type="object">{based}</BasedOn>', '<PreviewColor type="enumeration">Nothing</PreviewColor>',
             f'<AppliedFont type="string">{escape(font)}</AppliedFont>', f'<Leading type="unit">{f(leading)}</Leading>']
    if rule_above:
        w, off, col, l, r = rule_above
        a += (f' RuleAbove="true" RuleAboveLineWeight="{f(w)}" RuleAboveOffset="{f(off)}" RuleAboveWidth="ColumnWidth" '
              f'RuleAboveLeftIndent="{f(l)}" RuleAboveRightIndent="{f(r)}"')
        props.append(f'<RuleAboveColor type="object">{col}</RuleAboveColor>')
    if rule_below:
        w, off, col, l, r = rule_below
        a += (f' RuleBelow="true" RuleBelowLineWeight="{f(w)}" RuleBelowOffset="{f(off)}" RuleBelowWidth="ColumnWidth" '
              f'RuleBelowLeftIndent="{f(l)}" RuleBelowRightIndent="{f(r)}"')
        props.append(f'<RuleBelowColor type="object">{col}</RuleBelowColor>')
    if tabs:
        items = ''.join(f'<ListItem type="record"><Alignment type="enumeration">{al}</Alignment>'
                        f'<AlignmentCharacter type="string">.</AlignmentCharacter><Leader type="string"></Leader>'
                        f'<Position type="unit">{f(p)}</Position></ListItem>' for al, p in tabs)
        props.append(f'<TabList type="list">{items}</TabList>')
    return a + '><Properties>' + ''.join(props) + '</Properties></ParagraphStyle>'


def cstyle_xml(name, font=None, style=None, size=None, color=None, tracking=None, caps=None):
    a = f'<CharacterStyle Self="CharacterStyle/{escape(name)}" Imported="false" KeyboardShortcut="0 0" Name={quoteattr(name)}'
    if style:
        a += f' FontStyle={quoteattr(style)}'
    if size:
        a += f' PointSize="{f(size)}"'
    if color:
        a += f' FillColor="{color}"'
    if tracking is not None:
        a += f' Tracking="{f(tracking)}"'
    if caps is not None:
        a += f' Capitalization="{"AllCaps" if caps else "Normal"}"'
    props = '<BasedOn type="string">$ID/[No character style]</BasedOn><PreviewColor type="enumeration">Nothing</PreviewColor>'
    if font:
        props += f'<AppliedFont type="string">{escape(font)}</AppliedFont>'
    return a + '><Properties>' + props + '</Properties></CharacterStyle>'


def color_xml(name, rgb):
    return (f'<Color Self="Color/{escape(name)}" Model="Process" Space="RGB" ColorValue="{rgb[0]} {rgb[1]} {rgb[2]}" '
            f'ColorOverride="Normal" AlternateSpace="NoAlternateColor" AlternateColorValue="" Name={quoteattr(name)} '
            f'ColorEditable="true" ColorRemovable="true" Visible="true" SwatchCreatorID="7937"/>')
