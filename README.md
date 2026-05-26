# TFG — Detección de material gráfico en prensa histórica

**Trabajo de Fin de Grado — Universidad de Alcalá (UAH) · Sergio Salaices Oliva · 2026**

Comparativa de cuatro modelos de segmentación de instancias para detectar viñetas, títulos y fechas en páginas de prensa histórica digitalizada (1850–1950).

---

## Dataset

- **400 imágenes** de prensa histórica americana (Chronicling America / Library of Congress)
- **5 clases:** `Comic`, `Titulo_Periodico`, `Titulo_Comic`, `Fecha`, `Autor`
- Anotado manualmente con **CVAT** (segmentación de instancias)
- Split: **320 train / 80 val**
- Formato COCO JSON (Mask R-CNN, MaskDINO, DocSAM) y YOLO-seg (YOLOv11n-seg)

---

## Resultados

> Métricas estándar COCO. AP = mAP@[0.5:0.95] · AP50 = mAP@0.5

| Modelo | Backbone | AP box | AP50 box | AP mask | AP50 mask |
|--------|----------|-------:|---------:|--------:|----------:|
| **YOLOv11n-seg** | CSPDarknet | **47.68** | **78.97** | 34.13 | **65.91** |
| Mask R-CNN X101-FPN | ResNeXt-101 | 36.88 | 60.55 | **36.71** | 58.81 |
| MaskDINO R50 | ResNet-50 | 2.00 | 4.49 | 2.58 | 4.94 |
| DocSAM | — | — | — | — | — |

> **Nota MaskDINO:** los resultados bajos son esperables con 320 imágenes y 4000 iteraciones. Los modelos basados en transformer requieren significativamente más datos y tiempo de fine-tuning para converger.

---

## Estructura

```
tfg-comics-detection/
├── dataset/            # Descripción del dataset
├── models/
│   ├── yolo/           # YOLOv11n-seg — entrenamiento local (GT 1030)
│   ├── mask_rcnn/      # Mask R-CNN X101-FPN — Kaggle T4
│   ├── maskdino/       # MaskDINO R50 — Kaggle T4
│   └── docsam/         # DocSAM — pendiente
└── results/
    └── comparativa_modelos.csv
```

---

## Tecnologías

Python 3.11 · PyTorch 2.x · Ultralytics YOLOv11 · Detectron2 · CVAT · Kaggle T4
