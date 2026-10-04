"""Merge the separate part PDFs (output/parts/) into one book PDF.

  python tools/merge_book.py            -> output/Internal-Medicine-Bank-V4.pdf
  python tools/merge_book.py --out X.pdf

What it does
  * joins front matter, every chapter and the back matter in book order (output/parts/order.json)
  * checks that page numbering is continuous (each part's first page = previous part's last + 1)
  * turns the cross-document links (contents, "at a glance" tiles, index -> question) into real
    internal links of the merged PDF, jumping to the exact question on the page
  * keeps each part's own links (question <-> answer, chapter-opener lists)
  * adds bookmarks: one per chapter plus front and back matter
"""
import json, os, re, sys

import fitz  # PyMuPDF
fitz.TOOLS.mupdf_display_errors(False)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PARTS = os.path.join(ROOT, 'output', 'parts')
if '--parts' in sys.argv:
    PARTS = os.path.abspath(sys.argv[sys.argv.index('--parts') + 1])
elif os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'parts', 'order.json')):
    PARTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'parts')   # copy that sits next to its parts folder
_o = json.load(open(os.path.join(PARTS, 'order.json'), encoding='utf-8'))
out = os.path.join(os.path.dirname(PARTS), _o.get('pdf_name', 'Book') + '.pdf')
if '--out' in sys.argv:
    out = sys.argv[sys.argv.index('--out') + 1]

order = json.load(open(os.path.join(PARTS, 'order.json'), encoding='utf-8'))
book = fitz.open()
first_page = {}
problems = []
expected = 1
for name in order['files']:
    pdf = os.path.join(PARTS, name + '.pdf')
    if not os.path.exists(pdf):
        sys.exit('missing %s - build it first (python build/run.py)' % pdf)
    part = fitz.open(pdf)
    jf = os.path.join(PARTS, name.split('-', 1)[1] + '.json')
    meta = json.load(open(jf, encoding='utf-8')) if os.path.exists(jf) else None
    if meta:
        if meta['start'] != expected:
            problems.append('%s starts at page %s, expected %s' % (name, meta['start'], expected))
        if meta['end'] - meta['start'] + 1 != part.page_count:
            problems.append('%s: PDF has %d pages but the layout recorded %d' % (name, part.page_count, meta['end'] - meta['start'] + 1))
    first_page[name] = book.page_count
    book.insert_pdf(part, links=True, annots=True)
    expected = book.page_count + 1
    print('%-12s %4d pages  (book pages %d-%d)' % (name, part.page_count, first_page[name] + 1, book.page_count))
    part.close()

# re-open the joined file so every link has a proper object before we rewrite them
tmp = out + '.tmp.pdf'
book.save(tmp, garbage=3, deflate=True)
book.close()
book = fitz.open(tmp)

# cross-document links  https://imb.local/p/<page>[/<y mm>]
PAT = re.compile(r'https?://imb\.local/p/(\d+)(?:/([\d.]+))?')
fixed = broken = 0
for page in book:
    for lnk in page.get_links():
        uri = lnk.get('uri') or ''
        m = PAT.match(uri)
        if not m:
            continue
        target = int(m.group(1)) - 1
        page.delete_link(lnk)
        if not (0 <= target < book.page_count):
            broken += 1
            continue
        y = float(m.group(2)) * 72 / 25.4 if m.group(2) else 0
        page.insert_link({'kind': fitz.LINK_GOTO, 'from': lnk['from'], 'page': target,
                          'to': fitz.Point(0, max(0, y - 14)), 'zoom': 0})
        fixed += 1

toc = []
for bm in order['bookmarks']:
    if bm['file'] in first_page:
        toc.append([1, bm['title'], first_page[bm['file']] + 1])
toc.sort(key=lambda r: r[2])
book.set_toc(toc)
book.set_metadata({'title': order.get('title', 'Question bank'), 'author': order.get('author', '')})
n_pages = book.page_count
book.save(out, garbage=3, deflate=True)
book.close()
os.remove(tmp)
print('\n%d pages -> %s' % (n_pages, out))
print('cross-document links converted: %d%s' % (fixed, ('  (%d pointed outside the book)' % broken) if broken else ''))
for p in problems:
    print('WARNING:', p)
if not problems:
    print('page numbering continuous: OK')
