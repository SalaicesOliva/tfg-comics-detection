# TFG — Detección de material gráfico en prensa histórica

Trabajo de Fin de Grado — Universidad de Alcalá (UAH)

Sistema para detectar y clasificar viñetas y cómics en páginas de prensa histórica digitalizada usando modelos de detección de objetos.

## Estructura

```
data/
  raw/          → imágenes descargadas de repositorios digitales
  annotated/    → dataset anotado en formato YOLO
  processed/    → imágenes preprocesadas
src/
  download.py   → descarga imágenes de Chronicling America
  preprocess.py → normalización y limpieza de imágenes
  train.py      → entrenamiento del modelo
  inference.py  → detección sobre nuevas imágenes
  db.py         → almacenamiento de resultados en SQLite
models/         → pesos entrenados
results/        → métricas y gráficas de evaluación
```

## Requisitos

```bash
py -3.11 -m pip install -r requirements.txt
```

## Fuente de datos

- [Chronicling America](https://chroniclingamerica.loc.gov) — Library of Congress
- [CDNC](https://cdnc.ucr.edu) — California Digital Newspaper Collection
- [UNT Digital Library](https://digital.library.unt.edu)
