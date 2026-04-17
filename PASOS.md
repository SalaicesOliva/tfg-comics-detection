# PASOS — Registro de reproducibilidad
**TFG: Detección de material gráfico en prensa histórica**

Este documento registra todos los pasos realizados para que cualquier persona pueda replicar el proyecto desde cero, en orden cronológico.

---

## Paso 0 — Requisitos previos del sistema

- Sistema operativo: Windows 10/11
- Conexión a internet
- Cuenta en GitHub

---

## Paso 1 — Instalar Python 3.11

**Fecha:** 17 abril 2026

Python 3.11 es la versión usada en todo el proyecto (más estable con PyTorch/YOLO que versiones más nuevas).

### Opción A: via winget (recomendado)
Abrir PowerShell o cmd y ejecutar:
```
winget install Python.Python.3.11 --accept-package-agreements --accept-source-agreements
```

### Opción B: descarga manual
Ir a https://www.python.org/downloads/ → descargar Python 3.11.x → en el instalador marcar **"Add Python to PATH"** antes de instalar.

### Verificar instalación
```
py --version
```
Debe mostrar: `Python 3.11.x`

> **Nota Windows:** Si `python` da error o abre la MS Store, usar siempre `py -3.11` en su lugar. Es equivalente.

---

## Paso 2 — Instalar dependencias Python

```
py -3.11 -m pip install requests opencv-python pillow
```

Para instalar todas las dependencias del proyecto de una vez (una vez clonado el repo):
```
py -3.11 -m pip install -r requirements.txt
```

---

## Paso 3 — Instalar GitHub CLI y autenticarse

**Fecha:** 17 abril 2026

```
winget install GitHub.cli --accept-package-agreements --accept-source-agreements
```

Autenticarse (abre el navegador):
```
gh auth login
```
Seleccionar: GitHub.com → HTTPS → Login with a web browser → seguir instrucciones.

Verificar:
```
gh auth status
```

---

## Paso 4 — Clonar el repositorio

```
git clone https://github.com/SalaicesOliva/tfg-comics-detection.git
cd tfg-comics-detection
```

O si se parte desde cero (ya hecho en este proyecto):
```
git init
git remote add origin https://github.com/SalaicesOliva/tfg-comics-detection.git
```

---

## Paso 5 — Configurar identidad de Git

Solo necesario la primera vez en un equipo nuevo:
```
git config --global user.email "tu_email@gmail.com"
git config --global user.name "TuUsuarioGitHub"
```

---

## Paso 6 — Descargar imágenes del dataset

**Fecha:** 17 abril 2026 (script creado, pendiente ejecutar)

El script `src/download.py` conecta con la API de Chronicling America y descarga páginas de periódicos históricos (1920-1940) que contienen la palabra "comic" en sus metadatos.

```
cd tfg-comics-detection
py -3.11 src/download.py
```

Las imágenes se guardan en `data/raw/` en formato `.jpg`.

**Fuente de datos:** https://chroniclingamerica.loc.gov  
**API usada:** `https://chroniclingamerica.loc.gov/search/pages/results/?format=json`

> Las imágenes descargadas NO se suben al repositorio (están en `.gitignore`) por su tamaño.
> Para reproducir, ejecutar este script en el equipo local.

---

## Paso 7 — Preprocesado de imágenes *(pendiente)*

Script: `src/preprocess.py`

Operaciones previstas:
- Redimensionar a 640×640 px (tamaño estándar YOLO)
- Convertir a escala de grises si procede
- Normalizar contraste (útil para documentos deteriorados)

---

## Paso 8 — Anotación del dataset *(pendiente)*

Herramienta: **Roboflow** (https://roboflow.com) o **LabelImg** (local)

Clases a etiquetar:
- `comic` — tira cómica, viñeta, ilustración narrativa

Formato de salida: **YOLO** (un `.txt` por imagen con coordenadas normalizadas)

Mínimo para primer entrenamiento: ~50-100 imágenes anotadas  
Objetivo final: ~300-500 imágenes

---

## Paso 9 — Entrenamiento del modelo *(pendiente)*

Instalar Ultralytics YOLO:
```
py -3.11 -m pip install ultralytics
```

Script: `src/train.py`

Comando base de entrenamiento:
```
yolo train model=yolov8n.pt data=dataset.yaml epochs=50 imgsz=640
```

---

## Paso 10 — Evaluación *(pendiente)*

Script: `src/inference.py`

Métricas: precisión, recall, mAP@0.5, mAP@0.5:0.95

---

## Paso 11 — Base de datos SQLite *(pendiente)*

Script: `src/db.py`

Almacena por cada detección: imagen, clase, confianza, coordenadas, fuente, fecha de la página, identificador del periódico.

---

## Registro de cambios

| Fecha | Acción |
|-------|--------|
| 17 abr 2026 | Instalación Python 3.11, GitHub CLI, paquetes base |
| 17 abr 2026 | Creación repo GitHub y estructura de carpetas |
| 17 abr 2026 | Script `src/download.py` creado |
| 17 abr 2026 | Primer commit y push a GitHub |
