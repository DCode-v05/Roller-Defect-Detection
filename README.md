# Roller-Defect-Detection

A desktop inspection station for a roller production line. Two cameras watch two faces of each roller, YOLO models flag surface defects, and the app tells a Siemens S7 PLC to accept or reject the part. Each session is logged to MySQL.

I built it at iQube (KCT's innovation centre) for Welvision Pvt. Ltd., and the project is called WelVision in the code. It is one Tkinter application that starts several worker processes for camera capture, GPU inference and PLC I/O. Splitting them keeps inference from stalling when the GUI redraws or a camera blocks. The repo contains the application code, the three trained model weights, the camera profiles and the database setup script.

## How it works

- **Capture.** Two `capture_frames_*` processes open a camera with `cv2.VideoCapture` at 1280x960 and copy frames into shared `multiprocessing.Array` buffers. The OD feed is flipped 180 degrees to match how the camera is mounted.
- **Inference.** It is driven by PLC sensor bits, not a free-running loop. When the PLC reports a roller at the Big Face (BF) or Outer Diameter (OD) station, that station's process runs its YOLO model on the current frame (`half=True`, `agnostic_nms=True`, on CUDA). Each model is warmed up with 30 passes over `Warmup BF.jpg` / `Warmup OD.jpg` before the line starts. These images are loaded by relative path, so run `main.py` from the repo root.
- **Filtering.** `filter_detections` applies a per-class confidence threshold and a per-class minimum box area. Both are read from MySQL per model (`bf_threshold_history`, `od_threshold_history`, default 50%).
- **Tracking.** Several rollers can be in frame, so the app keeps a `roller_id` counter and assigns each defect box to the roller box that contains it. A roller's verdict is committed only when the next station's sensor fires.
- **Head check (BF only).** `BF_head.pt` detects the head ring and the dimple, measures the gap between them in pixels, and compares it with `high_head_pixels` / `down_head_pixels` for the roller type. Out-of-range parts are marked High Head or Down Head.
- **PLC.** A `plc_communication` process owns the `python-snap7` connection. It reads the presence and sensor bits and writes pulsed accept/reject bits. Verdicts reach it through queues. The YOLO processes run at high OS priority and the PLC and slot-control helpers at below normal.
- **Persistence.** At the end of a session `RollerDatabase.save_inspection_session` writes one BF row and one OD row to `welvision_db`: roller type, employee ID, times, inspected/accepted/rejected totals and a per-defect breakdown.

Processes share state through a `multiprocessing.Manager` dict, `Array`s for frames, `Value`s for counters and `Queue`s for verdicts and PLC commands. `ProcessManager` tracks every process so they can be stopped together.

Defect classes: BF has rust, dent, damage, high head and down head. OD has rust, dent, damage, damage on end and spherical mark.

The GUI has role-based access (Operator, Admin, Super Admin) and tabs for System Check, Settings, Inference, Model Management, Diagnosis, Data, Info, User Management and Backup.

## Models

| File | Use | Size |
|------|-----|------|
| `models/BF_sr.pt` | Big Face defects | about 18 MB |
| `models/OD_sr.pt` | Outer Diameter defects | about 21 MB |
| `models/BF_head.pt` | BF head-type check | about 6 MB |

The app loads the latest selected models from the database at startup. New `.pt` files can be uploaded from the Model Management tab. The line was reported to handle on the order of 100,000 rollers a day. I have no measurements in the repo to back that up.

## Stack

Python, PyTorch (CUDA 12.8 wheels), Ultralytics YOLO, OpenCV, Tkinter, tkcalendar, Matplotlib, pandas and openpyxl for reports, MySQL (`mysql-connector-python`), `python-snap7`, `pygrabber` and pywin32 for camera access, `psutil`, `gputil`.

## Setup

You need Windows with an NVIDIA GPU, a running MySQL server, and for live inspection two industrial cameras and a Siemens S7 PLC on the network.

```bash
git clone https://github.com/DCode-v05/Roller-Defect-Detection.git
cd Roller-Defect-Detection
pip install -r requirements.txt
python utils/create_db.py
python main.py
```

`requirements.txt` pulls PyTorch from the CUDA 12.8 index. Database settings (`DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_DATABASE`) and PLC settings (`PLC_IP`, `PLC_RACK`, `PLC_SLOT`, `PLC_DB_NUMBER`) are in `AppConfig` in `frontend/utils/config.py`. Change them for your hardware.

After login, use System Check to confirm the cameras and PLC, choose the roller type and models in Settings, then start the run from the Inference tab.

Defect frames are saved to `Desktop/Inference/BF` and `Desktop/Inference/OD`. With Allow All Images on (Super Admin only), every frame goes to `Desktop/All Frames`.

## Structure

```
main.py                 entry point
backend.py              capture, YOLO inference, filtering, PLC and sorting processes
database.py             RollerDatabase, writes session tracking to MySQL
models/                 trained weights
IC Capture Settings/    saved camera profiles for BF and OD
Warmup BF.jpg, Warmup OD.jpg
frontend/
  app.py                WelVisionApp, starts processes and shared memory
  login/ navbar/ inference/ settings/ model_management/ system_check/
  diagnosis/ data/ info/ user_management/ backup/
  utils/                config, permissions, process manager, logging, helpers
utils/                  create_db, backup/restore, GPU and cache cleanup, model_size
```

## Contact

[Portfolio](https://www.denistan.me) · [LinkedIn](https://www.linkedin.com/in/denistanb) · [GitHub](https://github.com/DCode-v05) · denistanb05@gmail.com
