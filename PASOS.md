# PASOS — Registro de reproducibilidad
**TFG: Detección de material gráfico en prensa histórica**

Este documento registra todos los pasos realizados para replicar el proyecto desde cero.

---

## Requisitos previos del sistema

- Windows 10/11
- Python 3.11 ([python.org](https://www.python.org/downloads/))
- GPU NVIDIA recomendada (el proyecto se ejecutó en una GT 1030 con 2 GB VRAM)
- Conexión a internet (para descargar dataset e imágenes)

---

## Paso 1 — Instalar dependencias

```bash
# PyTorch con CUDA
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124

# Resto de dependencias
pip install -r requirements.txt
```

> En Windows usar `py -3.11` en lugar de `python` si hay conflicto con la MS Store.

---

## Paso 2 — Construir el dataset

```bash
py -3.11 src/build_dataset.py
```

Descarga metadatos de **Newspaper Navigator** (Library of Congress, vía HuggingFace),
selecciona 500 páginas aleatorias, descarga las imágenes desde el servidor IIIF de la LOC
y convierte las anotaciones al formato YOLO.

**Resultado:** 492 páginas anotadas divididas en train/val/test (70% / 20% / 10%).

```
data/dataset/
├── images/   train(344) · val(98) · test(50)
├── labels/   train(344) · val(98) · test(50)
└── data.yaml
```

> Las imágenes no se suben al repo (están en `.gitignore`). Hay que ejecutar este script
> en local para reproducir el experimento.

---

## Paso 3 — Entrenar el modelo

```bash
py -3.11 src/train.py
```

Fine-tuning de **YOLOv8n** (`yolov8n.pt`, preentrenado en COCO).

Configuración usada:
- Épocas: hasta 100 (paró en 77 por early stopping)
- Mejor época: 69
- Tamaño de imagen: 416×416 px
- Batch size: 4
- GPU: NVIDIA GeForce GT 1030

Resultados sobre validación:

| Métrica | Valor |
|---------|-------|
| Precisión | 87.6% |
| Recall | 91.3% |
| mAP50 | 94.2% |
| mAP50-95 | 78.4% |

El mejor modelo se guarda en `runs/comics_yolov8n/weights/best.pt`.

---

## Paso 4 — Inferencia sobre imágenes nuevas

```bash
py -3.11 src/predict.py ruta/a/imagen_o_carpeta/
```

Ejecuta el modelo entrenado y guarda las páginas con los bounding boxes dibujados encima.

---

## Paso 5 — Evaluación formal sobre el conjunto de test

```bash
py -3.11 src/evaluate.py
```

Evalúa sobre las 50 imágenes de test (nunca vistas durante el entrenamiento).

| Métrica | Valor |
|---------|-------|
| Precisión | 64.9% |
| Recall | 80.7% |
| mAP50 | 79.8% |
| mAP50-95 | 66.8% |

---

## Paso 6 — Poblar la base de datos

```bash
py -3.11 src/build_db.py
```

Ejecuta inferencia sobre todo el dataset y almacena cada detección en `data/detections.db` (SQLite).

**Resultado:** 697 viñetas detectadas en 486 páginas. Confianza media: 0.752.

Esquema:
```
pages      — id, filename, split, lccn, pub_date, batch
detections — id, page_id, x_center, y_center, width, height, confidence, model
```

---

## Paso 7 — Generar estadísticas

```bash
py -3.11 src/stats.py
```

Genera tres gráficas a partir de la base de datos y las guarda en `runs/stats/`:

- `detecciones_por_anyo.png` — evolución temporal de viñetas detectadas
- `vinetas_por_pagina.png` — distribución de viñetas por página
- `distribucion_confianza.png` — histograma de la confianza del modelo

---

## Registro de cambios

| Fecha | Acción |
|-------|--------|
| 17 abr 2026 | Instalación Python 3.11, GitHub CLI, paquetes base |
| 17 abr 2026 | Creación repo GitHub y estructura de carpetas |
| 17 abr 2026 | Script `src/download.py` (exploración inicial API LOC) |
| 17 abr 2026 | Primer commit y push a GitHub |
| 19 abr 2026 | Dataset pipeline con Newspaper Navigator (`src/build_dataset.py`) |
| 19 abr 2026 | Entrenamiento YOLOv8n, script de evaluación y `GUIA.md` |
| 19 abr 2026 | Script de inferencia (`src/predict.py`) |
| 19 abr 2026 | Base de datos SQLite (`src/build_db.py`) |
| 19 abr 2026 | Estadísticas y gráficas (`src/stats.py`) |
| 19 abr 2026 | README finalizado, requirements.txt y `.gitignore` |
