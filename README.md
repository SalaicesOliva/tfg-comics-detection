# TFG — Detección de viñetas en prensa histórica

**Trabajo de Fin de Grado — Universidad de Alcalá (UAH)**

Sistema basado en YOLOv8 para detectar automáticamente viñetas y cómics en páginas de prensa histórica digitalizada (1850–1950). Usa el dataset pre-etiquetado **Newspaper Navigator** de la Biblioteca del Congreso de EE.UU. como fuente de datos.

---

## Resultados

| Métrica | Validación | Test |
|---------|-----------|------|
| mAP50 | 94.2% | 79.8% |
| Precisión | 87.6% | 64.9% |
| Recall | 91.3% | 80.7% |

Modelo: YOLOv8n — 697 viñetas detectadas en 486 páginas de periódico.

---

## Estructura

```
tfg-comics-detection/
├── src/
│   ├── download.py       # Exploración inicial (API Chronicling America)
│   ├── build_dataset.py  # Descarga y prepara el dataset desde Newspaper Navigator
│   ├── train.py          # Entrena YOLOv8n con fine-tuning
│   ├── predict.py        # Inferencia sobre imágenes nuevas
│   ├── evaluate.py       # Evaluación formal sobre el conjunto de test
│   ├── build_db.py       # Almacena detecciones en SQLite
│   └── stats.py          # Genera gráficas y estadísticas
├── data/
│   └── dataset/          # Labels YOLO (imágenes excluidas del repo)
├── runs/
│   └── stats/            # Gráficas generadas
├── requirements.txt
├── GUIA.md               # Guía detallada del proyecto
└── README.md
```

---

## Instalación

```bash
# PyTorch con CUDA (GPU NVIDIA recomendada)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124

# Resto de dependencias
pip install -r requirements.txt
```

---

## Uso

```bash
# 1. Construir el dataset (descarga ~170MB de imágenes)
py -3.11 src/build_dataset.py

# 2. Entrenar el modelo
py -3.11 src/train.py

# 3. Detectar viñetas en imágenes nuevas
py -3.11 src/predict.py ruta/a/imagen_o_carpeta/

# 4. Evaluar sobre el conjunto de test
py -3.11 src/evaluate.py

# 5. Guardar detecciones en base de datos
py -3.11 src/build_db.py

# 6. Generar estadísticas
py -3.11 src/stats.py
```

---

## Datos

- **Newspaper Navigator** (Library of Congress) — 526.319 viñetas pre-etiquetadas  
  `biglam/newspaper-navigator` en HuggingFace
- Imágenes servidas via protocolo **IIIF** desde `tile.loc.gov`

---

## Tecnologías

Python 3.11 · PyTorch 2.6 · YOLOv8 (Ultralytics) · SQLite · HuggingFace Datasets · Matplotlib

---

> Para una explicación detallada de cada paso, consulta [GUIA.md](GUIA.md).
