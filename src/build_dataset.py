"""
Construye el dataset YOLO desde Newspaper Navigator (HuggingFace).
Descarga páginas completas de periódico con viñetas ya etiquetadas.
Uso: py -3.11 src/build_dataset.py
"""

import os
import time
import random
import requests
from pathlib import Path
from datasets import load_dataset

# ── Configuración ──────────────────────────────────────────────────────────────
TARGET_PAGES = 500       # páginas únicas a descargar
IMG_PCT      = 15        # resolución IIIF (15% del original, ~600px ancho, más rápido)
SEED         = 42
SPLIT        = (0.70, 0.20, 0.10)   # train / val / test
OUT_BASE     = Path("data/dataset")
HEADERS      = {"User-Agent": "TFG-ComicsDetection/1.0 (sergiosalaicesoliva@gmail.com)"}
# ──────────────────────────────────────────────────────────────────────────────

def box_to_yolo(box):
    """Convierte [x1,y1,x2,y2] normalizado → [xc,yc,w,h] normalizado (YOLO)."""
    x1, y1, x2, y2 = [float(v) for v in box]
    return ((x1 + x2) / 2, (y1 + y2) / 2, x2 - x1, y2 - y1)


def page_key(ex):
    return f"{ex['batch']}_{ex['lccn']}_{ex['pub_date']}_{ex['page_seq_num']}"


def iiif_url(ex):
    return ex["iiif_full_url"].replace("/full/full/", f"/full/pct:{IMG_PCT}/")


def download(url, path):
    for attempt in range(3):
        try:
            r = requests.get(url, headers=HEADERS, timeout=60, stream=True)
            if r.status_code == 200:
                with open(path, "wb") as f:
                    for chunk in r.iter_content(8192):
                        f.write(chunk)
                return True
            print(f"  HTTP {r.status_code}")
            return False
        except (requests.exceptions.ConnectionError,
                requests.exceptions.ChunkedEncodingError,
                requests.exceptions.ReadTimeout):
            if attempt == 2:
                return False
            time.sleep(3)
    return False


def main():
    print("Cargando metadatos del dataset (comics)...")
    ds = load_dataset("biglam/newspaper-navigator", "comics", split="train")

    # Agrupar anotaciones por página única
    print("Agrupando por página...")
    pages: dict[str, list] = {}
    for ex in ds:
        key = page_key(ex)
        pages.setdefault(key, []).append(ex)
    print(f"  Páginas únicas: {len(pages)}")

    # Seleccionar subconjunto aleatorio
    random.seed(SEED)
    selected_keys = random.sample(list(pages.keys()), min(TARGET_PAGES, len(pages)))

    # Splits
    n = len(selected_keys)
    n_train = int(n * SPLIT[0])
    n_val   = int(n * SPLIT[1])
    splits = (
        ("train", selected_keys[:n_train]),
        ("val",   selected_keys[n_train:n_train + n_val]),
        ("test",  selected_keys[n_train + n_val:]),
    )

    # Crear carpetas
    for split_name, _ in splits:
        (OUT_BASE / "images" / split_name).mkdir(parents=True, exist_ok=True)
        (OUT_BASE / "labels" / split_name).mkdir(parents=True, exist_ok=True)

    # Descargar imágenes y escribir etiquetas
    total_ok = 0
    for split_name, keys in splits:
        print(f"\n--- {split_name.upper()} ({len(keys)} paginas) ---")
        img_dir = OUT_BASE / "images" / split_name
        lbl_dir = OUT_BASE / "labels" / split_name

        for i, key in enumerate(keys):
            annotations = pages[key]
            ex0 = annotations[0]
            img_path = img_dir / f"{key}.jpg"

            if not img_path.exists():
                url = iiif_url(ex0)
                ok = download(url, img_path)
                if not ok:
                    print(f"  [{i+1}/{len(keys)}] FALLO: {key}")
                    continue
                time.sleep(0.4)
            print(f"  [{i+1}/{len(keys)}] OK: {key[:60]}")

            # Escribir archivo de etiquetas YOLO (clase 0 = comic)
            lbl_path = lbl_dir / f"{key}.txt"
            with open(lbl_path, "w") as f:
                for ann in annotations:
                    xc, yc, w, h = box_to_yolo(ann["box"])
                    f.write(f"0 {xc:.6f} {yc:.6f} {w:.6f} {h:.6f}\n")
            total_ok += 1

    # Generar data.yaml para Ultralytics YOLO
    yaml_path = OUT_BASE / "data.yaml"
    abs_base = OUT_BASE.resolve().as_posix()
    yaml_path.write_text(
        f"path: {abs_base}\n"
        f"train: images/train\n"
        f"val: images/val\n"
        f"test: images/test\n"
        f"\nnc: 1\n"
        f"names:\n"
        f"  0: comic\n"
    )

    print(f"\nDataset listo en '{OUT_BASE}/'")
    print(f"  Páginas descargadas: {total_ok}/{n}")
    print(f"  data.yaml: {yaml_path}")


if __name__ == "__main__":
    main()
