"""
Descarga imágenes de páginas de periódico de la API de Chronicling America.
Uso: py -3.11 src/download.py
"""

import requests
import os
import time

BASE = "https://chroniclingamerica.loc.gov"
OUT_DIR = "data/raw"


def search_pages(query="comic", datestart="1920-01-01", dateend="1940-12-31", rows=20):
    url = f"{BASE}/search/pages/results/"
    params = {
        "andtext": query,
        "dateFilterType": "range",
        "date1": datestart,
        "date2": dateend,
        "format": "json",
        "rows": rows,
    }
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json().get("items", [])


def download_page_jpg(page_url, out_dir=OUT_DIR):
    os.makedirs(out_dir, exist_ok=True)
    # La API devuelve URLs tipo /lccn/.../seq-1.jp2 → pedimos .jpg
    jpg_url = page_url.rstrip("/") + ".jpg"
    fname = jpg_url.split("/lccn/")[-1].replace("/", "_")
    fpath = os.path.join(out_dir, fname)
    if os.path.exists(fpath):
        print(f"Ya existe: {fpath}")
        return fpath
    r = requests.get(BASE + jpg_url, timeout=60, stream=True)
    if r.status_code == 200:
        with open(fpath, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
        print(f"Descargado: {fpath}")
        return fpath
    else:
        print(f"Error {r.status_code}: {jpg_url}")
        return None


if __name__ == "__main__":
    print("Buscando páginas con 'comic'...")
    items = search_pages(query="comic", rows=30)
    print(f"Encontradas: {len(items)} páginas")

    descargadas = 0
    for item in items:
        url = item.get("url", "")
        if url:
            result = download_page_jpg(url)
            if result:
                descargadas += 1
            time.sleep(0.5)  # respetar rate limit

    print(f"\nTotal descargadas: {descargadas} imágenes en '{OUT_DIR}/'")
