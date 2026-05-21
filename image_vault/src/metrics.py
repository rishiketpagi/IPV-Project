import numpy as np
from PIL import Image


def mse(a: Image.Image, b: Image.Image) -> float:
    A = np.array(a.convert("RGB"), dtype=np.float64)
    B = np.array(b.convert("RGB"), dtype=np.float64)
    err = np.mean((A - B) ** 2)
    return float(err)


def psnr(a: Image.Image, b: Image.Image) -> float:
    m = mse(a, b)
    if m == 0:
        return float('inf')
    PIXEL_MAX = 255.0
    return float(20 * np.log10(PIXEL_MAX / np.sqrt(m)))


def entropy(img: Image.Image) -> float:
    arr = np.array(img.convert("L"))
    hist, _ = np.histogram(arr.flatten(), bins=256, range=(0,255), density=True)
    hist = hist[hist > 0]
    ent = -np.sum(hist * np.log2(hist))
    return float(ent)


def edge_density(img: Image.Image) -> float:
    arr = np.array(img.convert("L"), dtype=np.float32)
    # simple sobel kernels
    Kx = np.array([[1,0,-1],[2,0,-2],[1,0,-1]], dtype=np.float32)
    Ky = np.array([[1,2,1],[0,0,0],[-1,-2,-1]], dtype=np.float32)
    from scipy.signal import convolve2d
    gx = convolve2d(arr, Kx, mode='same', boundary='symm')
    gy = convolve2d(arr, Ky, mode='same', boundary='symm')
    mag = np.hypot(gx, gy)
    # threshold
    thresh = np.percentile(mag, 75)
    edges = (mag > thresh).astype(np.float32)
    return float(edges.mean())


def cover_score(img: Image.Image) -> tuple:
    ent = entropy(img)
    try:
        ed = edge_density(img)
    except Exception:
        ed = 0.0
    score = ent * (0.5 + ed)
    if score > 6.5:
        label = "Excellent"
    elif score > 4.0:
        label = "Good"
    else:
        label = "Poor"
    return label, {'entropy': ent, 'edge_density': ed, 'score': score}
