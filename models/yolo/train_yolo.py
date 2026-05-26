from ultralytics import YOLO
import torch, sys

LOG = r"C:\Users\sergi\Desktop\Yolo_v6_seg\train_log.txt"

class Logger:
    def __init__(self, path):
        self.terminal = sys.stdout
        self.log = open(path, 'w', encoding='utf-8', buffering=1)
    def write(self, msg):
        self.terminal.write(msg)
        self.log.write(msg)
    def flush(self):
        self.terminal.flush()
        self.log.flush()

sys.stdout = Logger(LOG)

if __name__ == '__main__':
    device = 0 if torch.cuda.is_available() else 'cpu'
    print(f"Device: {'cuda — ' + torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'cpu'}")
    print(f"VRAM: {round(torch.cuda.get_device_properties(0).total_memory/1024**3,1)} GB")

    model = YOLO('yolo11n-seg.pt')

    results = model.train(
        data    = r"C:\Users\sergi\Desktop\Yolo_v6_seg\data.yaml",
        epochs  = 100,
        imgsz   = 640,
        batch   = 4,
        workers = 0,      # 0 = sin multiprocessing (necesario en Windows)
        device  = device,
        project = r"C:\Users\sergi\Desktop\Yolo_v6_seg\runs",
        name    = "comic_yolo11n_seg",
        exist_ok= True,
        hsv_h   = 0.015,
        hsv_s   = 0.4,
        hsv_v   = 0.4,
        fliplr  = 0.5,
        mosaic  = 0.5,
        lr0     = 0.01,
        lrf     = 0.01,
        momentum= 0.937,
        weight_decay = 0.0005,
        warmup_epochs= 3,
        patience= 20,
        save    = True,
        val     = True,
        verbose = True,
    )

    print("\nEntrenamiento completado.")
    print(f"Resultados en: {results.save_dir}")
