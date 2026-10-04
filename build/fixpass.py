"""Pass A: clean a section IDML (UPDATED tags, anchored images, divider image + credit)."""
import os
import re
import shutil
import zipfile

from lxml import etree

UPD_RE = re.compile(
    r'<CharacterStyleRange AppliedCharacterStyle="CharacterStyle/Upd-[^"]*"><Content>UPDATED</Content></CharacterStyleRange>'
    r'(<CharacterStyleRange AppliedCharacterStyle="CharacterStyle/\$ID/\[No character style\]"><Content> </Content></CharacterStyleRange>)?')
ANCHOR_RE = re.compile(r'<AnchoredObjectSetting [^>]*/>')
ABOVE_LINE = ('<AnchoredObjectSetting AnchoredPosition="AboveLine" SpineRelative="false" LockPosition="false" '
              'PinPosition="true" AnchorPoint="TopLeftAnchor" HorizontalAlignment="TextAlign" '
              'HorizontalReferencePoint="TextFrame" VerticalAlignment="BottomAlign" '
              'VerticalReferencePoint="LineBaseline" AnchorXoffset="0" AnchorYoffset="0" AnchorSpaceAbove="0"/>')
CREDIT_RE = re.compile(r'<Content>Artwork (generated|drawn) for this edition</Content>')


def fix_section(src, dst, credit, divider_img=None, stats=None):
    """Write a cleaned copy of `src` to `dst` (the Links folder is copied next to it)."""
    zin = zipfile.ZipFile(src)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    zout = zipfile.ZipFile(dst, 'w')
    credit_story = None
    n_upd = n_anchor = 0
    files = {}
    for n in zin.namelist():
        data = zin.read(n)
        if n.startswith('Stories/'):
            s = data.decode('utf-8')
            s, k = UPD_RE.subn('', s)
            n_upd += k
            s, k = ANCHOR_RE.subn(ABOVE_LINE, s)
            n_anchor += k
            if CREDIT_RE.search(s):
                credit_story = re.search(r'<Story Self="([^"]+)"', s).group(1)
                s = CREDIT_RE.sub('<Content>' + credit.replace('&', '&amp;').replace('<', '&lt;') + '</Content>', s)
            data = s.encode('utf-8')
        files[n] = data
    # widen the credit frame so the longer credit line fits
    if credit_story:
        for n, data in files.items():
            if n.startswith('Spreads/') and f'ParentStory="{credit_story}"'.encode() in data:
                root = etree.fromstring(data)
                for tf in root.iter('TextFrame'):
                    if tf.get('ParentStory') == credit_story:
                        pts = list(tf.iter('PathPointType'))
                        xs = [float(p.get('Anchor').split()[0]) for p in pts]
                        x1 = max(xs)
                        x0 = x1 - 470
                        for p in pts:
                            x, y = p.get('Anchor').split()
                            nx = x0 if abs(float(x) - min(xs)) < 0.01 else float(x)
                            v = f'{nx:.4f} {y}'
                            p.set('Anchor', v)
                            p.set('LeftDirection', v)
                            p.set('RightDirection', v)
                files[n] = etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
    for n, data in files.items():
        zout.writestr(n, data, compress_type=zipfile.ZIP_STORED if n == 'mimetype' else zipfile.ZIP_DEFLATED)
    zout.close()
    if stats is not None:
        stats.update(updated=n_upd, anchored=n_anchor, credit_story=credit_story)
    # links
    sl = os.path.join(os.path.dirname(src), 'Links')
    dl = os.path.join(os.path.dirname(dst), 'Links')
    os.makedirs(dl, exist_ok=True)
    for fn in os.listdir(sl):
        if not os.path.exists(os.path.join(dl, fn)):
            shutil.copy2(os.path.join(sl, fn), dl)
    if divider_img:
        shutil.copy2(divider_img, os.path.join(dl, os.path.basename(divider_img)))
    return dst
