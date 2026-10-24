import os
import sys
import numpy as np
from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "textures")
PHOTOS = os.path.join(ROOT, "..", "materials", "Фото обработанное")
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(123)


def smooth_noise(size, scale, seed):
    r = np.random.default_rng(seed)
    n = max(2, size // scale)
    base = r.random((n, n)).astype(np.float32)
    img = Image.fromarray((base * 255).astype(np.uint8)).resize((size, size), Image.BICUBIC)
    return np.asarray(img, np.float32) / 255.0


def tileable_noise(size, scale, seed):
    r = np.random.default_rng(seed)
    n = max(2, size // scale)
    base = r.random((n, n)).astype(np.float32)
    tiled = np.tile(base, (3, 3))
    img = Image.fromarray((tiled * 255).astype(np.uint8)).resize((size * 3, size * 3), Image.BICUBIC)
    a = np.asarray(img, np.float32) / 255.0
    return a[size:2 * size, size:2 * size]


def herringbone(size=1024, L=5):
    period = 2 * L
    px = size / period
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32) / px
    plank_id = np.full((size, size), -1, np.int64)
    along = np.zeros((size, size), np.float32)
    across = np.zeros((size, size), np.float32)
    for i in range(-3 * period, 3 * period):
        for j in range(-3, 4):
            ox = i + j * L
            oy = i - j * L
            for kind, (x0, y0, dx, dy) in enumerate([(ox, oy, L, 1), (ox, oy + 1, 1, L)]):
                for tx in (-period, 0, period):
                    for ty in (-period, 0, period):
                        X0, Y0 = x0 + tx, y0 + ty
                        if X0 >= period or Y0 >= period or X0 + dx <= 0 or Y0 + dy <= 0:
                            continue
                        m = (xx >= X0) & (xx < X0 + dx) & (yy >= Y0) & (yy < Y0 + dy)
                        if not m.any():
                            continue
                        key = ((X0 % period) * period + (Y0 % period)) * 2 + kind
                        plank_id[m] = key
                        if kind == 0:
                            along[m] = (xx[m] - X0) / dx
                            across[m] = yy[m] - Y0
                        else:
                            along[m] = (yy[m] - Y0) / dy
                            across[m] = xx[m] - X0
    ids = np.unique(plank_id)
    tone = {k: rng.normal(0, 1) for k in ids}
    t = np.vectorize(tone.get)(plank_id).astype(np.float32)
    grain_seed = (plank_id % 997).astype(np.float32)
    grain = np.sin((across * 9.0 + np.sin(along * 6.0 + grain_seed) * 0.6 + grain_seed) * 6.2831) * 0.5 + 0.5
    fine = tileable_noise(size, 6, 7)
    base = np.array([0.78, 0.60, 0.42], np.float32)
    col = base[None, None, :] * (1.0 + 0.07 * t[..., None])
    col *= (0.92 + 0.10 * grain[..., None]) * (0.96 + 0.08 * fine[..., None])
    edge_a = np.minimum(across, 1 - across) * px
    edge_l = np.minimum(along, 1 - along) * L * px
    seam = np.clip(np.minimum(edge_a, edge_l) / 1.6, 0, 1)
    col *= (0.55 + 0.45 * seam[..., None])
    img = Image.fromarray((np.clip(col, 0, 1) * 255).astype(np.uint8))
    img.save(os.path.join(OUT, "floor_herringbone.jpg"), quality=88)


def plaster(size=1024):
    a = tileable_noise(size, 64, 1) * 0.5 + tileable_noise(size, 16, 2) * 0.3 + tileable_noise(size, 4, 3) * 0.2
    base = np.array([0.90, 0.87, 0.81], np.float32)
    col = base[None, None, :] * (0.93 + 0.12 * a[..., None])
    Image.fromarray((np.clip(col, 0, 1) * 255).astype(np.uint8)).save(os.path.join(OUT, "wall_plaster.jpg"), quality=85)


CLUTTER = [
    (125, 155, 500, 600), (240, 268, 505, 620), (252, 290, 490, 525), (380, 440, 480, 700),
    (492, 552, 490, 640), (796, 815, 555, 615), (815, 852, 500, 620), (905, 972, 430, 640),
    (1140, 1180, 560, 630), (395, 415, 645, 700),
]


def inpaint_rows(a, x0, x1, y0, y1):
    left = a[y0:y1, max(0, x0 - 3):x0].mean(axis=1)
    right = a[y0:y1, x1:x1 + 3].mean(axis=1)
    t = np.linspace(0, 1, x1 - x0)[None, :, None]
    fill = left[:, None, :] * (1 - t) + right[:, None, :] * t
    fill += rng.normal(0, 4, fill.shape)
    a[y0:y1, x0:x1] = fill


def view():
    src = Image.open(os.path.join(PHOTOS, "21.png")).convert("RGB")
    a = np.asarray(src, np.float32).copy()
    for x0, x1, y0, y1 in CLUTTER:
        inpaint_rows(a, x0, x1, y0, y1)
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    soft = img.filter(ImageFilter.GaussianBlur(2))
    mask = Image.new("L", img.size, 0)
    for x0, x1, y0, y1 in CLUTTER:
        mask.paste(255, (x0 - 2, y0, x1 + 2, y1))
    img = Image.composite(soft, img, mask.filter(ImageFilter.GaussianBlur(3)))
    crop = img.crop((60, 0, 1140, 600))
    crop = crop.resize((2048, int(2048 * crop.size[1] / crop.size[0])), Image.LANCZOS)
    crop.save(os.path.join(OUT, "view_library.jpg"), quality=85)


if __name__ == "__main__":
    herringbone()
    plaster()
    view()
    print("ok", os.listdir(OUT))
