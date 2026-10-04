"""Create static font instances (Chromium embeds variable fonts as Type3)."""
import os
import sys
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

src_dir, out_dir = sys.argv[1], sys.argv[2]
os.makedirs(out_dir, exist_ok=True)
jobs = []
for w in (300, 400, 500, 600, 700):
    for it in ('', '-Italic'):
        jobs.append((f'SourceSerif4{it}.ttf', {'wght': w, 'opsz': 10}, f'Serif-{w}{it}'))
for w in (400, 600, 700):
    for it in ('', '-Italic'):
        jobs.append((f'SourceSans3{it}.ttf', {'wght': w}, f'Sans-{w}{it}'))
for wd in (62, 75, 100):
    for w in (300, 400, 500, 600, 700, 800, 900):
        jobs.append(('Archivo.ttf', {'wght': w, 'wdth': wd}, f'Archivo-{wd}-{w}'))
    for w in (400, 700):
        jobs.append(('Archivo-Italic.ttf', {'wght': w, 'wdth': wd}, f'Archivo-{wd}-{w}-Italic'))
for src, loc, tag in jobs:
    f = TTFont(os.path.join(src_dir, src))
    inst = instancer.instantiateVariableFont(f, loc, updateFontNames=False)
    for rec in inst['name'].names:
        if rec.nameID in (1, 3, 4, 6, 16, 17):
            rec.string = 'Bank' + tag.replace('-', '')
    inst.save(os.path.join(out_dir, tag + '.ttf'))
print(len(jobs), 'instances')
