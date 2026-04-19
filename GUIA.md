# Guía del proyecto — Detección de viñetas en prensa histórica

## ¿Qué hace este proyecto?

Detecta automáticamente viñetas y cómics dentro de páginas de periódicos históricos (años 1850-1950) usando inteligencia artificial. Dado una imagen de una página de periódico, el sistema devuelve la posición exacta (bounding box) de cada viñeta que encuentra.

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
4. Descarga las imágenes en alta resolución desde el servidor IIIF de la LOC
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

### Paso 4 — Evaluación (`src/evaluate.py`)
Evalúa el modelo entrenado sobre el conjunto de test (imágenes que el modelo nunca ha visto).

---

## Resultados obtenidos

| Métrica | Valor |
|---------|-------|
| **Precisión** | 87.6% |
| **Recall** | 91.3% |
| **mAP50** | **94.2%** |
| **mAP50-95** | 78.4% |

### ¿Qué significan estas métricas?

- **Precisión (87.6%)**: De cada 10 detecciones que hace el modelo, ~9 son correctas (viñetas reales). El 12.4% restante son falsas alarmas.
- **Recall (91.3%)**: El modelo encuentra el 91.3% de todas las viñetas que hay en las imágenes. Solo se le escapa ~1 de cada 11.
- **mAP50 (94.2%)**: Métrica estándar en detección de objetos. Mide la precisión promedio cuando el umbral de solapamiento (IoU) es del 50%. Un 94.2% es un resultado excelente.
- **mAP50-95 (78.4%)**: Igual que la anterior pero promediando con umbrales más estrictos (50%-95%). Es la métrica más exigente.

Estos resultados son **muy buenos** para un primer entrenamiento con un dataset relativamente pequeño (344 imágenes de entrenamiento).

---

## Estructura del repositorio

```
tfg-comics-detection/
├── src/
│   ├── download.py       # Exploración inicial de datos (API LOC)
│   ├── build_dataset.py  # Construye el dataset desde Newspaper Navigator
│   ├── train.py          # Entrena YOLOv8n
│   └── evaluate.py       # Evalúa el modelo sobre test
├── data/
│   └── dataset/          # Dataset generado (imágenes no en git)
├── runs/                 # Resultados del entrenamiento (no en git)
├── requirements.txt      # Dependencias Python
└── GUIA.md               # Este fichero
```

---

## Cómo reproducir el experimento

```bash
# 1. Instalar dependencias
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
pip install ultralytics datasets requests

# 2. Construir el dataset
py -3.11 src/build_dataset.py

# 3. Entrenar
py -3.11 src/train.py

# 4. Evaluar
py -3.11 src/evaluate.py
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
| **Python 3.11** | Lenguaje de programación |
