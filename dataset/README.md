# Dataset

## Descripción

- **400 imágenes** de páginas de periódico histórico americano (1850–1950)
- Fuente: [Chronicling America](https://chroniclingamerica.loc.gov/) — Library of Congress
- Anotación manual realizada con **CVAT** (Computer Vision Annotation Tool)
- Split: **320 train / 80 val**

## Clases

| ID | Clase | Descripción |
|----|-------|-------------|
| 0 | `Titulo_Periodico` | Cabecera del periódico |
| 1 | `Fecha` | Fecha de publicación |
| 2 | `Comic` | Viñeta o tira cómica |
| 3 | `Titulo_Comic` | Título de la tira cómica |
| 4 | `Autor` | Firma del autor |

## Formatos

- **COCO JSON** (`instances_train.json` / `instances_val.json`) — usado por Mask R-CNN, MaskDINO y DocSAM
- **YOLO-seg** (polígonos rectangulares en `.txt`) — usado por YOLOv11n-seg

Las imágenes no están incluidas en el repositorio por tamaño (~1.2 GB).
El dataset está disponible en Kaggle: [sergiosalaicesoliva/comic-coco](https://www.kaggle.com/datasets/sergiosalaicesoliva/comic-coco)
