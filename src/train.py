"""
Entrena YOLOv8n para detección de viñetas en prensa histórica.
Uso: py -3.11 src/train.py
"""

from ultralytics import YOLO

DATA_YAML  = "data/dataset/data.yaml"
MODEL      = "yolov8n.pt"   # nano: el más ligero, cabe en 2GB VRAM
EPOCHS     = 100
IMG_SIZE   = 416            # reducido para caber en la GT 1030
BATCH      = 4              # pequeño por los 2GB de VRAM
PROJECT    = "runs"
RUN_NAME   = "comics_yolov8n"

if __name__ == "__main__":
    model = YOLO(MODEL)

    results = model.train(
        data=DATA_YAML,
        epochs=EPOCHS,
        imgsz=IMG_SIZE,
        batch=BATCH,
        project=PROJECT,
        name=RUN_NAME,
        device=0,           # GPU
        patience=20,        # early stopping si no mejora en 20 epochs
        save=True,
        plots=True,
    )

    print("\nEntrenamiento completado.")
    print(f"Mejor modelo: runs/{RUN_NAME}/weights/best.pt")
