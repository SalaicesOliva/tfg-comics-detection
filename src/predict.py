"""
Ejecuta inferencia sobre imágenes nuevas y guarda los resultados con bounding boxes.
Uso: py -3.11 src/predict.py <imagen_o_carpeta>
     py -3.11 src/predict.py data/dataset/images/test/
"""

import sys
from pathlib import Path
from ultralytics import YOLO

MODEL      = "runs/detect/runs/comics_yolov8n/weights/best.pt"
OUT_DIR    = "runs/predict"
IMG_SIZE   = 416
CONFIDENCE = 0.25

if __name__ == "__main__":
    source = sys.argv[1] if len(sys.argv) > 1 else "data/dataset/images/test/"

    model = YOLO(MODEL)
    results = model.predict(
        source=source,
        imgsz=IMG_SIZE,
        conf=CONFIDENCE,
        device=0,
        save=True,
        save_txt=True,
        project=OUT_DIR,
        name="comics",
        exist_ok=True,
    )

    total_detections = sum(len(r.boxes) for r in results)
    print(f"\nImagenes procesadas : {len(results)}")
    print(f"Viñetas detectadas  : {total_detections}")
    print(f"Resultados en       : {OUT_DIR}/comics/")
