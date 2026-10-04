"""Build the 36 section-divider images from real sources (see CREDITS in the output json)."""
import csv
import json
import os
import sys

import nibabel as nib
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
from divider import compose, prepare  # noqa: E402
from vol import window  # noqa: E402

IMG = sys.argv[1]  # scratchpad/img
OUT = sys.argv[2]
os.makedirs(OUT, exist_ok=True)
C = json.load(open(f'{IMG}/colors.json'))
IDX = json.load(open(f'{IMG}/oi/sheet_index.json'))

# Open Images metadata (author / licence)
META = {}
for f in ('valmeta.csv', 'testmeta.csv'):
    for r in csv.DictReader(open(f'{IMG}/oi/{f}')):
        META[r['ImageID']] = r


def oi(n):
    key = IDX[n][1]
    iid = key.split('_', 1)[1]
    m = META.get(iid, {})
    lic = m.get('License', '')
    lic = 'CC BY 2.0' if 'by/2.0' in lic else ('CC BY-SA 2.0' if 'by-sa' in lic else lic)
    credit = f"Photo: {m.get('Author', 'unknown').strip()} / Flickr, {lic} (Open Images)"
    return Image.open(f'{IMG}/oi/cand/{key}.jpg'), credit, m.get('OriginalLandingURL', '')


VOL = {}


def vol(name):
    if name not in VOL:
        VOL[name] = np.load(f'{IMG}/idc/{name}.npy')
    return VOL[name]


IDC = {
    'kid_cor': 'CT: NCI Imaging Data Commons, CPTAC-CCRCC, CC BY 4.0',
    'adr': 'CT: NCI Imaging Data Commons, Adrenal-ACC-Ki67-Seg, CC BY 4.0',
    'chest1': 'CT: NCI Imaging Data Commons, Mediastinal-Lymph-Node-SEG, CC BY 4.0',
    'chest2': 'CT: NCI Imaging Data Commons, Mediastinal-Lymph-Node-SEG, CC BY 4.0',
}
MRI = 'MRI: OpenNeuro ds000001 (Schonberg et al.), CC0'
ECG = 'ECG: PTB-XL, PhysioNet (Wagner et al.), CC BY 4.0'


def mri(sub, plane, idx):
    n = nib.as_closest_canonical(nib.load(f'{IMG}/mri/sub-{sub}.nii.gz'))
    a = n.get_fdata()
    a = a / np.percentile(a, 99.6)
    if plane == 'sag':
        s = np.rot90(a[idx, :, :])
    else:
        s = np.rot90(a[:, :, idx])
    return np.clip(s, 0, 1)


def ecg(rec, leads=(1,), seconds=(0, 10), rows=1):
    import wfdb
    r = wfdb.rdrecord(f'{IMG}/ecg/{rec}')
    fs = r.fs
    sig = r.p_signal
    W, Hh = 2400, 1600
    img = Image.new('L', (W, Hh), 0)
    from PIL import ImageDraw
    d = ImageDraw.Draw(img)
    # faint ECG paper grid
    for x in range(0, W, 40):
        d.line([(x, 0), (x, Hh)], fill=28 if x % 200 else 46, width=1)
    for y in range(0, Hh, 40):
        d.line([(0, y), (W, y)], fill=28 if y % 200 else 46, width=1)
    n = len(leads)
    for k, lead in enumerate(leads):
        s = sig[int(seconds[0] * fs):int(seconds[1] * fs), lead]
        s = s - np.median(s)
        cy = Hh * (k + 0.5) / n
        xs = np.linspace(0, W, len(s))
        ys = cy - s * 300
        pts = list(zip(xs, ys))
        d.line(pts, fill=255, width=9, joint='curve')
    return np.asarray(img, float) / 255.0


def crop(a, x0, y0, x1, y1):
    h, w = a.shape[:2]
    return a[int(y0 * h):int(y1 * h), int(x0 * w):int(x1 * w)]


def aspect(a, f):
    im = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
    im = im.resize((im.width, int(im.height * f)), Image.LANCZOS)
    return np.asarray(im, float) / 255.0


SPECS = {}


def spec(key):
    def deco(fn):
        SPECS[key] = fn
        return fn
    return deco


# ------------------------------------------------------------- Medicine 1
@spec('pit')
def _():
    s = mri('01', 'sag', 80)
    return crop(s, 0.12, 0.10, 0.92, 0.80) ** 0.9, MRI, {}


@spec('thy')
def _():
    c = vol('chest1')
    a = window(c[283], 60, 380)
    return crop(a, 0.18, 0.22, 0.82, 0.78), IDC['chest1'], {}


@spec('adr')
def _():
    a = vol('adr')
    s = window(a[:, 262, :][::-1], 60, 380)
    s = aspect(s, 1.25 / 0.744)
    return crop(s, 0.05, 0.25, 0.95, 0.85) ** 1.7, IDC['adr'], {}


@spec('dm')
def _():
    im, cr, _ = oi(183)
    return prepare(im, crop=(0.0, 0.05, 1.0, 1.0), autocontrast=1, gamma=1.8), cr, dict(glow=0.15)


@spec('neph')
def _():
    k = vol('kid_cor')
    a = window(k[76], 90, 420)
    return crop(a, 0.04, 0.22, 0.98, 0.98) ** 1.35, IDC['kid_cor'], {}


@spec('elec')
def _():
    im, cr, _ = oi(581)
    return prepare(im, crop=(0.05, 0.03, 0.95, 0.97), invert=True, gamma=1.6), cr, dict(glow=0.2)


@spec('git')
def _():
    k = vol('kid_cor')
    a = window(k[52], 60, 400)
    return crop(a, 0.02, 0.02, 0.98, 0.95) ** 1.3, IDC['kid_cor'], {}


@spec('rheum')
def _():
    im, cr, _ = oi(14)
    return prepare(im, autocontrast=0.5), cr, {}


@spec('gen')
def _():
    im, cr, _ = oi(1)
    return prepare(im, crop=(0.0, 0.0, 0.85, 0.8), invert=True, gamma=1.5), cr, dict(glow=0.25, hi_mix=0.9)


# ------------------------------------------------------------- Medicine 2
@spec('cad')
def _():
    c = vol('chest1')
    s = window(c[:, 240, :][::-1], 90, 480)
    s = aspect(s, 1 / 0.945)
    return crop(s, 0.15, 0.12, 0.85, 0.75) ** 1.2, IDC['chest1'], dict(glow=0.1)


@spec('hf')
def _():
    im, cr, _ = oi(8)
    return prepare(im, crop=(0.04, 0.17, 0.96, 0.92), autocontrast=0.5, invert=True, gamma=1.9), cr, dict(glow=0.1)


@spec('chd')
def _():
    c = vol('chest1')
    a = window(c[int(c.shape[0] * 0.42)], 60, 420)
    return crop(a, 0.24, 0.24, 0.76, 0.66), IDC['chest1'], {}


@spec('arr')
def _():
    return ecg('AFIB', leads=(1, 6, 10), seconds=(0, 6.5)), ECG + ' (atrial fibrillation)', dict(glow=0.35, box=(0.0, 0.08, 1.0, 0.80))


@spec('valv')
def _():
    c = vol('chest1')
    c = vol('chest2')
    s = window(c[:, 240, :][::-1], 70, 450)
    s = aspect(s, 2 / 0.785)
    return crop(s, 0.12, 0.05, 0.88, 0.8) ** 1.2, IDC['chest2'], {}


@spec('peri')
def _():
    c = vol('chest2')
    a = window(c[int(c.shape[0] * 0.42)], 50, 400)
    return crop(a, 0.1, 0.12, 0.9, 0.85), IDC['chest2'], {}


@spec('htn')
def _():
    im, cr, _ = oi(329)
    return prepare(im, crop=(0.25, 0.1, 1.0, 1.0), gamma=1.5), cr, {}


@spec('cpharm')
def _():
    im, cr, _ = oi(109)
    return prepare(im, gamma=1.15), cr, {}


@spec('cvsx')
def _():
    im, cr, _ = oi(375)
    return prepare(im, crop=(0.05, 0.0, 0.95, 1.0), gamma=1.1), cr, dict(hi_mix=0.85)


@spec('cvsemq')
def _():
    return ecg('IMI', leads=(1, 2, 7, 9), seconds=(0, 5)), ECG + ' (inferior MI)', dict(glow=0.3, box=(0.0, 0.08, 1.0, 0.80))


@spec('airway')
def _():
    c = vol('chest1')
    lung = np.load(f'{IMG}/idc/chest1_lung.npy')
    mn = np.where(lung, c, 0)[:, 150:330, :].min(1)[::-1]
    s = 1 - window(mn, -990, 260)
    s = aspect(s, 1 / 0.945)
    return crop(s, 0.25, 0.08, 0.75, 0.55) ** 0.7, IDC['chest1'], dict(glow=0.35)


@spec('resinf')
def _():
    im, cr, _ = oi(18)
    return prepare(im, crop=(0.05, 0.02, 0.95, 0.9), autocontrast=0.5, invert=True, gamma=1.9), cr, dict(glow=0.1)


@spec('crit')
def _():
    im, cr, _ = oi(403)
    return prepare(im, gamma=2.0), cr, {}


@spec('pleura')
def _():
    c = vol('chest2')
    a = window(c[int(c.shape[0] * 0.35)], 40, 420)
    return crop(a, 0.08, 0.15, 0.92, 0.82), IDC['chest2'], {}


@spec('ild')
def _():
    im, cr, _ = oi(550)
    return prepare(im, crop=(0.05, 0.05, 0.95, 0.9)), cr, {}


@spec('pvasc')
def _():
    s = np.asarray(Image.open(f'{IMG}/idc/pvasc_mip.png').convert('L'), float) / 255
    return crop(s, 0.24, 0.0, 0.80, 0.85) ** 1.2, IDC['chest1'], dict(glow=0.2)


@spec('lca')
def _():
    im, cr, _ = oi(48)
    return prepare(im, crop=(0.42, 0.0, 0.98, 1.0)), cr, {}


@spec('resx')
def _():
    im, cr, _ = oi(20)
    return prepare(im, crop=(0.03, 0.0, 0.97, 1.0), autocontrast=0.5, invert=True, gamma=1.9), cr, dict(hi_mix=0.85, glow=0.1)


@spec('resemq')
def _():
    c = vol('chest2')
    a = window(c[int(c.shape[0] * 0.5)], -550, 1500)
    return crop(a, 0.08, 0.12, 0.92, 0.85), IDC['chest2'], {}


# ------------------------------------------------------------- Surgery 2
@spec('ul')
def _():
    im, cr, _ = oi(47)
    return prepare(im, crop=(0.0, 0.0, 0.92, 1.0), autocontrast=0.5), cr, {}


@spec('ll')
def _():
    im, cr, _ = oi(9)
    return prepare(im, crop=(0.08, 0.08, 0.85, 0.9)), cr, {}


@spec('bone')
def _():
    im, cr, _ = oi(13)
    return prepare(im), cr, {}


@spec('thor')
def _():
    c = vol('chest1')
    s = window(c[:, 120:330, :].max(1)[::-1], 450, 900)
    s = aspect(s, 1 / 0.945)
    return crop(s, 0.12, 0.08, 0.88, 0.85), IDC['chest1'], {}


@spec('vasc')
def _():
    c = vol('chest2')
    s = window(c[:, 230, :][::-1], 90, 460)
    s = aspect(s, 2 / 0.785)
    return crop(s, 0.15, 0.0, 0.85, 0.72) ** 1.2, IDC['chest2'], dict(glow=0.1)


@spec('neuro')
def _():
    s = mri('02', 'ax', 86)
    return crop(s, 0.05, 0.12, 0.95, 0.95), MRI, {}


@spec('plas')
def _():
    im, cr, _ = oi(407)
    return prepare(im, gamma=1.1), cr, {}


@spec('anaes')
def _():
    im, cr, _ = oi(384)
    return prepare(im, gamma=1.5), cr, {}


if __name__ == '__main__':
    only = sys.argv[3:] or list(SPECS)
    credits = {}
    cf = f'{OUT}/credits.json'
    if os.path.exists(cf):
        credits = json.load(open(cf))
    for k in only:
        g, cr, kw = SPECS[k]()
        im = compose(g, C[k], **kw)
        im.save(f'{OUT}/divider-{k}.jpg', quality=90)
        credits[k] = cr
        print(k, cr)
    json.dump(credits, open(cf, 'w'), indent=1)
