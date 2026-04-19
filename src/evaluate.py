"""
Evalúa el modelo entrenado sobre el conjunto de test.
Uso: py -3.11 src/evaluate.py
"""

from ultralytics import YOLO
from pathlib import Path

MODEL    = "runs/detect/runs/comics_yolov8n/weights/best.pt"
DATA     = "data/dataset/data.yaml"
IMG_SIZE = 416

if __name__ == "__main__":
    model = YOLO(MODEL)

    print("=== Evaluacion sobre conjunto de TEST ===")
    metrics = model.val(data=DATA, split="test", imgsz=IMG_SIZE, device=0)

    p  = metrics.box.mp
    r  = metrics.box.mr
    m50 = metrics.box.map50
    m5095 = metrics.box.map

    print(f"\nResultados finales:")
    print(f"  Precision : {p:.3f}  ({p*100:.1f}%)")
    print(f"  Recall    : {r:.3f}  ({r*100:.1f}%)")
    print(f"  mAP50     : {m50:.3f}  ({m50*100:.1f}%)")
    print(f"  mAP50-95  : {m5095:.3f}  ({m5095*100:.1f}%)")
    print(f"\nResultados guardados en: runs/detect/")
