# TFG — Estado actual del proyecto
**Detección de material gráfico en prensa histórica mediante IA**
*Última actualización: 17 abril 2026*

---

## Qué tenemos hecho

### Anteproyecto (completado)
El anteproyecto está aprobado y subido a Overleaf con la plantilla LaTeX oficial de la UAH.
Cubre: introducción, estado del arte, objetivos, descripción del trabajo, metodología (incremental+iterativa), Gantt y medios.
Bibliografía con 12 referencias en `biblio.bib`, todas con URLs de libre acceso.

### Entorno de desarrollo (completado)
- Python 3.11.9 instalado en `C:\Users\sergi\AppData\Local\Programs\Python\Python311\`
- Usar siempre `py -3.11` en lugar de `python` (evita conflicto con alias de MS Store)
- GitHub CLI instalado, autenticado como **SalaicesOliva**
- Paquetes instalados: `requests`, `opencv-python`, `pillow`

### Repositorio GitHub
**https://github.com/SalaicesOliva/tfg-comics-detection**

Estructura actual:
```
tfg-comics-detection/
├── data/
│   ├── raw/          ← imágenes descargadas (no se suben al repo, en .gitignore)
│   ├── annotated/    ← dataset anotado formato YOLO
│   └── processed/    ← imágenes preprocesadas
├── src/
│   └── download.py   ← script de descarga de Chronicling America ✓
├── models/           ← pesos entrenados (no se suben al repo)
├── results/          ← métricas y gráficas
├── requirements.txt
├── README.md
├── PASOS.md
└── .gitignore
```

---

## Siguiente paso inmediato

Probar el script de descarga:
```
cd C:\Users\sergi\Desktop\TFG\tfg-comics-detection
py -3.11 src/download.py
```

Esto descargará ~30 páginas de periódicos históricos (1920-1940) que contienen la palabra "comic"
en los metadatos de Chronicling America. Las imágenes se guardan en `data/raw/`.

---

## Pipeline completo (pendiente)

```
[1] Descarga imágenes        → src/download.py        ✓ hecho
[2] Preprocesado             → src/preprocess.py      pendiente
[3] Anotación (labeling)     → Roboflow o LabelImg    pendiente
[4] Entrenamiento YOLO       → src/train.py           pendiente
[5] Evaluación               → src/inference.py       pendiente
[6] Base de datos SQLite     → src/db.py              pendiente
```

---

## Decisiones tomadas

| Decisión | Elección | Motivo |
|----------|----------|--------|
| Dataset principal | Chronicling America | API pública, alta resolución, libre acceso |
| Modelo | YOLOv8 (Ultralytics) | Equilibrio velocidad/precisión, bien documentado |
| Base de datos | SQLite | Sin servidor, suficiente para el volumen del TFG |
| Metodología | Incremental + iterativa | Permite ajustar según resultados del modelo |
| Formato anotaciones | YOLO txt | Compatible directo con Ultralytics |
