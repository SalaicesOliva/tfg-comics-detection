# Guía del proyecto — Detección de viñetas en prensa histórica

## ¿Qué hace este proyecto?

Detecta automáticamente viñetas y cómics dentro de páginas de periódicos históricos (años 1850-1950) usando inteligencia artificial. Dado una imagen de una página de periódico, el sistema devuelve la posición exacta (bounding box) de cada viñeta que encuentra y almacena los resultados en una base de datos.

---

## ¿Qué se ha hecho paso a paso?

### Paso 1 — Descarga de datos (`src/download.py`)
Inicialmente se descargaron páginas de periódico desde la API pública de Chronicling America (Biblioteca del Congreso de EE.UU.). Este script fue el punto de partida para explorar los datos disponibles. Las páginas descargadas aquí **no se usan en el entrenamiento final**.

### Paso 2 — Construcción del dataset (`src/build_dataset.py`)
En lugar de anotar imágenes a mano (lo que llevaría semanas), se usó el dataset **Newspaper Navigator** de la Biblioteca del Congreso. Este dataset ya tiene **526.319 viñetas etiquetadas** con bounding boxes en páginas de periódicos históricos.

El script:
1. Descarga los metadatos desde HuggingFace (`biglam/newspaper-navigator`, config `comics`)
2. Agrupa las anotaciones por página única (420.312 páginas distintas)
3. Selecciona aleatoriamente 500 páginas
4. Descarga las imágenes desde el servidor IIIF de la LOC
5. Convierte los bounding boxes al formato YOLO (`x_centro, y_centro, ancho, alto` normalizados)
6. Divide automáticamente en train/val/test (70% / 20% / 10%)
7. Genera el fichero `data/dataset/data.yaml` que YOLO necesita para entrenar

**Resultado:** 492 páginas anotadas listas para entrenar.

```
data/dataset/
├── images/
│   ├── train/   (344 imágenes)
│   ├── val/     (98 imágenes)
│   └── test/    (50 imágenes)
├── labels/
│   ├── train/   (344 ficheros .txt con bounding boxes)
│   ├── val/     (98 ficheros .txt)
│   └── test/    (50 ficheros .txt)
└── data.yaml    (configuración para YOLO)
```

Cada fichero `.txt` de etiquetas contiene una línea por viñeta en formato YOLO:
```
0  0.512  0.334  0.280  0.145
^  ^^^^^  ^^^^^  ^^^^^  ^^^^^
clase  x_c   y_c   w     h   (todos normalizados 0-1)
```

### Paso 3 — Entrenamiento (`src/train.py`)
Se entrenó **YOLOv8 nano** (`yolov8n.pt`), la variante más ligera de la familia YOLO, haciendo fine-tuning sobre nuestro dataset.

Configuración usada:
- Modelo base: `yolov8n.pt` (preentrenado en COCO)
- Épocas: hasta 100 (paró en 77 por early stopping)
- Mejor época: 69
- Tamaño de imagen: 416×416 px
- Batch size: 4
- GPU: NVIDIA GeForce GT 1030

El **early stopping** paró el entrenamiento automáticamente en la época 77 al no detectar mejoras en las últimas 20 épocas. El mejor modelo guardado corresponde a la época 69.

### Paso 4 — Inferencia (`src/predict.py`)
Ejecuta el modelo entrenado sobre imágenes nuevas y guarda las páginas con los bounding boxes dibujados encima. Se puede usar con una imagen suelta o una carpeta entera.

```bash
py -3.11 src/predict.py data/dataset/images/test/
```

### Paso 5 — Evaluación (`src/evaluate.py`)
Evalúa el modelo sobre el conjunto de test (imágenes que nunca vio durante el entrenamiento) y devuelve las métricas oficiales.

### Paso 6 — Base de datos (`src/build_db.py`)
Ejecuta inferencia sobre todo el dataset y almacena cada detección en una base de datos SQLite (`data/detections.db`).

Esquema de la base de datos:
```
pages
  id, filename, split, lccn, pub_date, batch

detections
  id, page_id, x_center, y_center, width, height, confidence, model
```

- `pages`: una fila por página de periódico procesada
- `detections`: una fila por viñeta detectada, con su posición normalizada y la confianza del modelo

**Resultado:** 697 viñetas detectadas en 486 páginas. La confianza media es 0.752.

### Paso 7 — Estadísticas (`src/stats.py`)
Genera tres gráficas a partir de la base de datos:
- Detecciones por año de publicación
- Distribución de viñetas por página
- Distribución de la confianza del modelo

Las gráficas se guardan en `runs/stats/`.

---

## Resultados obtenidos

### Durante el entrenamiento (conjunto de validación)
| Métrica | Valor |
|---------|-------|
| Precisión | 87.6% |
| Recall | 91.3% |
| mAP50 | 94.2% |
| mAP50-95 | 78.4% |

### Evaluación final (conjunto de test — datos nunca vistos)
| Métrica | Valor |
|---------|-------|
| **Precisión** | 64.9% |
| **Recall** | 80.7% |
| **mAP50** | **79.8%** |
| **mAP50-95** | 66.8% |

La diferencia entre validación y test es normal e indica que el modelo generaliza razonablemente bien, aunque hay margen de mejora con más datos de entrenamiento.

### ¿Qué significan estas métricas?

- **Precisión (64.9%)**: De cada 10 detecciones, ~6-7 son viñetas reales. El resto son falsas alarmas.
- **Recall (80.7%)**: El modelo encuentra el 80.7% de todas las viñetas que hay en las imágenes.
- **mAP50 (79.8%)**: Métrica estándar en detección de objetos con umbral IoU=50%. Un resultado sólido para un dataset pequeño.
- **mAP50-95 (66.8%)**: Versión más estricta de la anterior, promediando varios umbrales de solapamiento.

---

## Estructura del repositorio

```
tfg-comics-detection/
├── src/
│   ├── download.py       # Exploración inicial de datos (API LOC)
│   ├── build_dataset.py  # Construye el dataset desde Newspaper Navigator
│   ├── train.py          # Entrena YOLOv8n
│   ├── predict.py        # Inferencia sobre imágenes nuevas
│   ├── evaluate.py       # Evaluación formal sobre test
│   ├── build_db.py       # Guarda detecciones en SQLite
│   └── stats.py          # Gráficas y estadísticas
├── data/
│   ├── dataset/          # Dataset generado (imágenes no en git)
│   └── detections.db     # Base de datos SQLite (no en git)
├── runs/
│   └── stats/            # Gráficas generadas
├── requirements.txt      # Dependencias Python
└── GUIA.md               # Este fichero
```

---

## Cómo reproducir el experimento

```bash
# 1. Instalar dependencias
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
pip install ultralytics datasets requests matplotlib

# 2. Construir el dataset
py -3.11 src/build_dataset.py

# 3. Entrenar
py -3.11 src/train.py

# 4. Inferencia sobre el test
py -3.11 src/predict.py data/dataset/images/test/

# 5. Evaluación formal
py -3.11 src/evaluate.py

# 6. Poblar la base de datos
py -3.11 src/build_db.py

# 7. Generar estadísticas
py -3.11 src/stats.py
```

---

## Tecnologías usadas

| Herramienta | Para qué |
|-------------|----------|
| **YOLOv8 (Ultralytics)** | Modelo de detección de objetos |
| **PyTorch** | Framework de deep learning |
| **Newspaper Navigator (LOC)** | Dataset de viñetas pre-etiquetadas |
| **HuggingFace Datasets** | Acceso al dataset |
| **IIIF (LOC)** | Descarga de imágenes en alta resolución |
| **SQLite** | Base de datos de resultados |
| **Matplotlib** | Gráficas y estadísticas |
| **Python 3.11** | Lenguaje de programación |
