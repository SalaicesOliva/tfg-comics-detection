"""
Ejecuta inferencia sobre el dataset y almacena los resultados en SQLite.
Uso: py -3.11 src/build_db.py
"""

import sqlite3
import cv2
from pathlib import Path
from ultralytics import YOLO

MODEL      = "runs/detect/runs/comics_yolov8n/weights/best.pt"
DATA_DIR   = Path("data/dataset/images")
DB_PATH    = Path("data/detections.db")
IMG_SIZE   = 416
CONFIDENCE = 0.25


def init_db(conn):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS pages (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            filename    TEXT NOT NULL,
            split       TEXT NOT NULL,
            lccn        TEXT,
            pub_date    TEXT,
            batch       TEXT
        );

        CREATE TABLE IF NOT EXISTS detections (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            page_id     INTEGER NOT NULL REFERENCES pages(id),
            x_center    REAL NOT NULL,
            y_center    REAL NOT NULL,
            width       REAL NOT NULL,
            height      REAL NOT NULL,
            confidence  REAL NOT NULL,
            model       TEXT NOT NULL
        );
    """)
    conn.commit()


def parse_filename(stem):
    """Extrae lccn, fecha y batch del nombre de fichero generado por build_dataset.py."""
    parts = stem.split("_")
    try:
        date_idx = next(i for i, p in enumerate(parts) if len(p) == 10 and p[4] == "-")
        pub_date = parts[date_idx]
        lccn     = parts[date_idx - 1]
        batch    = "_".join(parts[:date_idx - 1])
        return lccn, pub_date, batch
    except (StopIteration, IndexError):
        return None, None, None


def is_valid_image(path):
    try:
        img = cv2.imread(str(path))
        return img is not None and img.size > 0
    except Exception:
        return False


def main():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    model = YOLO(MODEL)

    with sqlite3.connect(DB_PATH) as conn:
        init_db(conn)

        total_pages = total_det = skipped = 0

        for split in ("train", "val", "test"):
            img_dir = DATA_DIR / split
            if not img_dir.exists():
                continue

            images = sorted(img_dir.glob("*.jpg"))
            print(f"\n[{split}] {len(images)} imagenes...")

            for i, img_path in enumerate(images, 1):
                if not is_valid_image(img_path):
                    skipped += 1
                    continue

                try:
                    results = model.predict(
                        source=str(img_path),
                        imgsz=IMG_SIZE,
                        conf=CONFIDENCE,
                        device=0,
                        verbose=False,
                    )
                except Exception:
                    skipped += 1
                    continue

                lccn, pub_date, batch = parse_filename(img_path.stem)
                cur = conn.execute(
                    "INSERT INTO pages (filename, split, lccn, pub_date, batch) VALUES (?,?,?,?,?)",
                    (img_path.name, split, lccn, pub_date, batch),
                )
                page_id = cur.lastrowid

                for box in results[0].boxes:
                    xc, yc, w, h = box.xywhn[0].tolist()
                    conf = float(box.conf[0])
                    conn.execute(
                        "INSERT INTO detections (page_id, x_center, y_center, width, height, confidence, model) "
                        "VALUES (?,?,?,?,?,?,?)",
                        (page_id, xc, yc, w, h, conf, "yolov8n"),
                    )
                    total_det += 1

                total_pages += 1
                if i % 50 == 0:
                    print(f"  {i}/{len(images)} procesadas...")

            conn.commit()

        print(f"\n=== Base de datos creada: {DB_PATH} ===")
        print(f"  Paginas procesadas : {total_pages}")
        print(f"  Saltadas (corruptas): {skipped}")
        print(f"  Detecciones totales: {total_det}")

        print("\n--- Top 5 paginas con mas vinetas ---")
        for row in conn.execute("""
            SELECT p.filename, p.pub_date, COUNT(d.id) as n
            FROM pages p JOIN detections d ON d.page_id = p.id
            GROUP BY p.id ORDER BY n DESC LIMIT 5
        """):
            print(f"  {row[2]} vinetas | {row[1]} | {row[0][:50]}")

        print("\n--- Detecciones por split ---")
        for row in conn.execute("""
            SELECT p.split, COUNT(d.id)
            FROM pages p JOIN detections d ON d.page_id = p.id
            GROUP BY p.split
        """):
            print(f"  {row[0]}: {row[1]} detecciones")


if __name__ == "__main__":
    main()
