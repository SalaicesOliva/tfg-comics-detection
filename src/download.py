"""
Descarga imágenes de páginas de periódico de la API de Chronicling America (LOC).
Uso: py -3.11 src/download.py
"""

import requests
import os
import time

BASE = "https://www.loc.gov"
OUT_DIR = "data/raw"
HEADERS = {
    "User-Agent": "TFG-ComicsDetection/1.0 (research; sergiosalaicesoliva@gmail.com)",
    "Accept": "application/json",
}


def search_pages(query="comic strip", datestart="1920", dateend="1940", rows=20):
    params = {
        "q": query,
        "dates": f"{datestart}/{dateend}",
        "fo": "json",
        "c": rows,
        "at": "results,pagination",
        "dl": "page",
    }
    for attempt in range(3):
        try:
            r = requests.get(
                f"{BASE}/collections/chronicling-america/",
                params=params,
                headers=HEADERS,
                timeout=60,
            )
            break
        except requests.exceptions.ConnectionError:
            if attempt == 2:
                raise
            print(f"Reintento {attempt + 1}/3...")
            time.sleep(5)
    r.raise_for_status()
    return r.json().get("results", [])


def pick_image_url(image_urls):
    """Elige la URL IIIF de mayor resolución (pct:50) entre las disponibles."""
    for url in image_urls:
        if "default.jpg" in url and "text-services" not in url:
            # Reemplaza el porcentaje por una resolución mayor
            return url.split("/full/")[0] + "/full/pct:50/0/default.jpg"
    return None


def download_image(image_url, out_dir=OUT_DIR):
    os.makedirs(out_dir, exist_ok=True)
    fname = (
        image_url.split("service:")[-1]
        .replace("/", "_")
        .replace(":", "_")
        .split("?")[0]
    )
    if not fname.endswith(".jpg"):
        fname += ".jpg"
    fpath = os.path.join(out_dir, fname)
    if os.path.exists(fpath):
        print(f"Ya existe: {fpath}")
        return fpath
    try:
        r = requests.get(image_url, headers=HEADERS, timeout=60, stream=True)
        if r.status_code != 200:
            print(f"Error {r.status_code}: {image_url}")
            return None
        with open(fpath, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
        print(f"Descargado: {fpath}")
        return fpath
    except (requests.exceptions.ConnectionError, requests.exceptions.ChunkedEncodingError) as e:
        print(f"Fallo de red, saltando: {e}")
        if os.path.exists(fpath):
            os.remove(fpath)
        return None


if __name__ == "__main__":
    print("Buscando páginas con 'comic strip' (1920-1940)...")
    items = search_pages(query="comic strip", datestart="1920", dateend="1940", rows=30)
    print(f"Encontradas: {len(items)} páginas")

    descargadas = 0
    for item in items:
        image_urls = item.get("image_url", [])
        url = pick_image_url(image_urls)
        if url:
            result = download_image(url)
            if result:
                descargadas += 1
            time.sleep(0.5)

    print(f"\nTotal descargadas: {descargadas} imágenes en '{OUT_DIR}/'")
