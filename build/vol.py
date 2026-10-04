"""Load DICOM CT/MR series into a volume and make slices / projections."""
import glob

import numpy as np
import pydicom
from PIL import Image
from scipy import ndimage


def load(d):
    fs = []
    for f in glob.glob(d + '/*'):
        try:
            ds = pydicom.dcmread(f)
            if hasattr(ds, 'pixel_array'):
                fs.append(ds)
        except Exception:
            pass
    ori = np.array(fs[0].ImageOrientationPatient, float)
    nrm = np.cross(ori[:3], ori[3:])
    fs.sort(key=lambda ds: float(np.dot(np.array(ds.ImagePositionPatient, float), nrm)))
    arr = np.stack([ds.pixel_array.astype(np.float32) * float(getattr(ds, 'RescaleSlope', 1)) +
                    float(getattr(ds, 'RescaleIntercept', 0)) for ds in fs])
    ps = [float(x) for x in fs[0].PixelSpacing]
    pos = [float(np.dot(np.array(ds.ImagePositionPatient, float), nrm)) for ds in fs]
    dz = abs(np.median(np.diff(pos))) if len(pos) > 1 else 1.0
    return arr, (dz, ps[0], ps[1]), ori


def window(a, c, w):
    lo, hi = c - w / 2, c + w / 2
    return np.clip((a - lo) / (hi - lo), 0, 1)


def to_img(a, aspect=1.0, size=None):
    im = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
    if aspect != 1.0:
        im = im.resize((im.width, max(1, int(round(im.height * aspect)))), Image.LANCZOS)
    if size:
        im.thumbnail(size, Image.LANCZOS)
    return im
