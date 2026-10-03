"""Build the book with InDesign 2025, one document per part (lighter, no hangs).

Parts, in book order:  front | pit thy adr dm neph elec git rheum gen | back
Each part is its own INDD (+ IDML with --final) and PDF in output/parts/, numbered continuously:
the front matter is pages 1-7, every chapter opens on a left-hand page and ends on a right-hand page.

  python run.py                 build every part (preview quality PDF)
  python run.py --final         every part: INDD + IDML + print-quality PDF, then the InDesign book (.indb)
  python run.py neph            rebuild one chapter; if its page count changed, the following parts are
                                rebuilt automatically so numbering stays continuous
  python run.py back front      rebuild only these parts
Then merge:  python ../tools/merge_book.py   (or double-click Merge-Book.cmd)
"""
import json, os, re, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
PARTS = os.path.join(ROOT, 'output', 'parts')
os.makedirs(PARTS, exist_ok=True)
FRONT_PAGES = 7

args = sys.argv[1:]
final = '--final' in args
jpg = None
if '--jpg' in args:
    jpg = args[args.index('--jpg') + 1]
    args.remove(jpg)
want = [a for a in args if not a.startswith('--')]

subprocess.check_call([sys.executable, os.path.join(HERE, 'gen.py')])
man = json.load(open(os.path.join(HERE, 'out', 'manifest.json'), encoding='utf-8'))
chapters = [c['id'] for c in man['chapters']]
order_no = {c['id']: c['order'] for c in man['chapters']}
ALL = chapters + ['back', 'front']          # front last: it needs every page number


def info(part):
    p = os.path.join(PARTS, part + '.json')
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else None


def file_name(part):
    if part == 'front':
        return '00-front'
    if part == 'back':
        return '%02d-back' % (max(order_no.values()) + 1)
    return '%02d-%s' % (order_no[part], part)


def start_page(part):
    if part == 'front':
        return 1
    seq = chapters + ['back']
    i = seq.index(part)
    if i == 0:
        return FRONT_PAGES + 1
    prev = info(seq[i - 1])
    if not prev:
        raise SystemExit('build %s first (its page numbers are needed)' % seq[i - 1])
    return prev['end'] + 1


def build(part):
    opts = dict(root=ROOT.replace('\\', '/'), outdir=(ROOT + '/output').replace('\\', '/'), part=part,
                startPage=start_page(part), name=file_name(part), idml=final, pdf=True,
                dpi=220 if final else 110, jpg=jpg, keepOpen=False)
    jsx = 'var OPTS = ' + json.dumps(opts) + ';\n' + open(os.path.join(HERE, 'build.jsx'), encoding='utf-8').read()
    run = os.path.join(HERE, '_run.jsx')
    open(run, 'w', encoding='utf-8').write(jsx)
    ps = ('$app = New-Object -ComObject "InDesign.Application.2025"; '
          '$r = $app.DoScript(\'try { $.evalFile(File("%s")) } catch (e) { "ERR line " + e.line + ": " + e.message }\', 1246973031); '
          'Write-Output "RESULT: $r"') % run.replace('\\', '/')
    t = time.time()
    p = subprocess.run(['powershell', '-NoProfile', '-Command', ps], capture_output=True, text=True)
    out = (p.stdout.strip() + ' ' + p.stderr.strip()[:500]).strip()
    inf = info(part)
    print('%-6s %-40s %4.0fs  pages %s-%s' % (part, out[:40], time.time() - t, inf and inf['start'], inf and inf['end']))
    if 'ERR' in out or 'failed' in out:
        raise SystemExit('stopped at %s' % part)


targets = set(p for p in ALL if not want or p in want)
if targets & set(chapters):                 # index + contents depend on every chapter's pages
    targets |= {'back', 'front'}
for i, part in enumerate(ALL):
    if part not in targets:
        continue
    old = info(part)
    build(part)
    new = info(part)
    if part in chapters and old and new and old['end'] != new['end']:
        print('   page count of %s changed -> renumbering the following parts' % part)
        targets |= set(ALL[i + 1:])

# book order for the merge tool + InDesign book file
order = [file_name(p) for p in ['front'] + chapters + ['back']]
bk = man['book']
pdf_name = bk.get('file_name') or re.sub(r'[^A-Za-z0-9]+', '-', bk.get('title', 'Book')).strip('-')
json.dump(dict(title='%s - %s - %s' % (bk.get('title', ''), bk.get('volume', ''), bk.get('edition', '')),
               author=', '.join(bk.get('authors', [])) + (' (%s)' % bk['team'] if bk.get('team') else ''),
               pdf_name=pdf_name, files=order, bookmarks=[dict(file=file_name(c['id']), title='%02d  %s' % (c['order'], c['title'])) for c in man['chapters']]
               + [dict(file=file_name('front'), title='Front matter & contents'), dict(file=file_name('back'), title='Index, credits & back cover')]),
          open(os.path.join(PARTS, 'order.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
if final:
    indb = (PARTS + '/' + pdf_name + '.indb').replace('\\', '/')
    lines = ['var f = File("%s"); if (f.exists) f.remove();' % indb, 'var bk = app.books.add(f);',
             'bk.automaticPagination = false;']
    for n in order:
        lines.append('bk.bookContents.add(File("%s/%s.indd"));' % (PARTS.replace('\\', '/'), n))
    lines.append('bk.save(); bk.close(); "book ok";')
    js = os.path.join(HERE, '_book.jsx')
    open(js, 'w', encoding='utf-8').write('\n'.join(lines))
    ps = '$app = New-Object -ComObject "InDesign.Application.2025"; $r = $app.DoScript(\'try { $.evalFile(File("%s")) } catch (e) { "ERR " + e.message }\', 1246973031); Write-Output $r' % js.replace('\\', '/')
    print('indb:', subprocess.run(['powershell', '-NoProfile', '-Command', ps], capture_output=True, text=True).stdout.strip())
print('parts in', PARTS)
