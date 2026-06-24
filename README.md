# WelVision — Automated Roller Defect Inspection

**A Python vision station that inspects manufactured rollers in real time, scores both faces with YOLO, and drives a Siemens PLC to accept or reject each part on the line.**

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white) ![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=flat&logo=pytorch&logoColor=white) ![Ultralytics YOLO](https://img.shields.io/badge/Ultralytics_YOLO-111F68?style=flat&logo=ultralytics&logoColor=white) ![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=flat&logo=opencv&logoColor=white) ![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=flat&logo=mysql&logoColor=white) ![NVIDIA CUDA](https://img.shields.io/badge/CUDA-76B900?style=flat&logo=nvidia&logoColor=white) ![License](https://img.shields.io/badge/License-MIT-green?style=flat)

## Overview

WelVision is an automated optical inspection (AOI) station for a roller production line. Two industrial cameras watch two faces of each roller as it travels past — the Big Face (BF) and the Outer Diameter (OD) — and YOLO models flag surface defects on each one. When a roller reaches the sorting mechanism, the app tells a Siemens S7 PLC whether to accept it or kick it into the reject chute, and logs the whole inspection session to MySQL.

I built this at **iQube (KCT's innovation center)** as the inspection software for **Welvision Pvt. Ltd.**, an industrial client. The whole thing runs as one desktop application: a Tkinter operator GUI on top, and a set of cooperating Python processes underneath doing camera capture, GPU inference, and PLC I/O at line speed. It's the strongest piece of work I've shipped — a complete system, from camera feed to physical accept/reject, that ran on a real production line.

This README describes what's in the public repository: the application code, the inference pipeline, the PLC protocol, the database schema, and the three trained model weights that ship with it.

## Key Features

- **Dual-face inspection** — independent BF and OD pipelines, each with its own camera, model, thresholds, and counters, running concurrently.
- **Real-time YOLO defect detection** — Ultralytics YOLO models (PyTorch, CUDA half-precision) score every roller as it passes a presence sensor.
- **Head-type classification on the BF face** — a separate model measures the head ring vs. dimple geometry in pixels and flags "High Head" / "Down Head" rollers against per-roller-type limits.
- **Siemens PLC integration** — reads proximity/presence bits and writes accept/reject pulses to a Siemens S7 PLC over `python-snap7`, so the software physically sorts parts.
- **Per-defect, per-model thresholds** — confidence threshold, bounding-box size threshold, and model confidence are all stored in MySQL per model and applied as a two-stage filter on detections.
- **Roller-to-defect association** — defects are matched back to the correct roller instance via bounding-box containment, so multiple rollers in frame don't get their defects mixed up.
- **Role-based access control** — three roles (Operator, Admin, Super Admin) gate the GUI tabs and actions (settings, model upload, user management, global limits, "allow all" image capture).
- **Model management from the UI** — upload, select, and track BF/OD models; the app loads the latest selected model from the database on startup.
- **Inspection history and reporting** — every session writes BF and OD tracking rows (counts of inspected/accepted/rejected plus a breakdown per defect class) for the Diagnosis and Data tabs.
- **Backup and restore tooling** — built-in database backup, image backup with progress windows, and storage checks.
- **System check / diagnostics** — a tab to verify camera and PLC connectivity and watch live processing counters before starting a run.
- **Defect image capture** — annotated frames for defective rollers (and optionally *all* frames, Super-Admin only) are saved to disk for review and re-labelling.

## How It Works

The application is one Tkinter window (`WelVisionApp`) that, when an operator starts a run, spawns a set of OS processes and wires them together with shared memory. Splitting capture, inference, and PLC I/O into separate processes is what keeps inference from stalling when the GUI redraws or a camera blocks.

### 1. Capture

Two `capture_frames_*` processes each open a camera (`cv2.VideoCapture`) at 1280×960 and continuously copy frames into a shared `multiprocessing.Array`. The OD feed is flipped 180° to match the camera mounting. Frame buffers are guarded by locks so the inference processes always read a complete frame.

### 2. Presence-triggered inference

The pipeline is event-driven off PLC sensor bits, not a free-running loop. When the PLC reports a roller present at the BF station, the BF inference process grabs the current frame and runs the BF YOLO model on it; same for OD. Each model is warmed up with 30 passes over a bundled warmup image (`Warmup BF.jpg` / `Warmup OD.jpg`) before the line starts, so the first real roller doesn't eat the CUDA/cuDNN initialisation cost.

YOLO runs on GPU with `half=True` and `agnostic_nms=True`. The model emits roller boxes plus defect boxes; a single class index marks the "roller" itself, everything else is a defect class.

### 3. Detection filtering

Raw detections pass through `filter_detections`, a two-stage gate:

- **Confidence filter** — each defect class has its own percentage threshold pulled from `bf_threshold_history` / `od_threshold_history` (default 50%).
- **Size filter** — bounding-box area in px² must clear a per-class size threshold, which kills tiny spurious boxes.

Thresholds, size limits, and the overall model confidence are all read from MySQL per model, so they can be tuned per part without touching code.

### 4. Roller tracking and defect association

Multiple rollers can be in frame at once, so the app keeps a running `roller_id` counter and a `point_inside` check that assigns each defect box to the roller box that contains it. Defects accumulate per roller (`defect` OR-ed, defect names appended). A roller is only "closed out" and its verdict committed when the next station's sensor fires — which guarantees the part has fully left the inspection window before a decision is sent.

### 5. Head classification (BF only)

On the BF face, a dedicated head model (`BF_head.pt`) detects the head ring and the dimple, computes the horizontal/vertical gap between them in pixels, and compares it to `high_head_pixels` / `down_head_pixels` limits stored per roller type. Out-of-range parts are marked "High Head" or "Down Head" and counted as defects.

### 6. PLC handshake and sorting

A `plc_communication` process owns the Snap7 connection. On startup it waits for both models to report ready, sets the system-ready bits, then loops reading the PLC data block — presence bits, big-face/OD sensors, head-classification trigger, system mode/status. Verdicts flow from the inference processes through `Queue`s to slot-control processes, which push `accept_*` / `reject_*` commands onto a command queue; the PLC process turns those into pulsed boolean writes (`trigger_plc_action`) that fire the physical accept/reject actuator.

PLC and the slot-control helpers run at below-normal OS priority while the YOLO inference processes run high-priority, so the GPU work always wins the CPU.

### 7. Persistence

At the end of a session, `RollerDatabase.save_inspection_session` writes one BF row and one OD row into `welvision_db`: roller type, employee ID, date, start/end time, totals (inspected / accepted / rejected) and a per-defect breakdown. Those rows feed the reporting tabs.

### Shared state, in one place

The processes coordinate through a `multiprocessing.Manager` dict (`shared_data`) for flags and live counters, `Array`s for raw and annotated frames, `Value`s for proximity counts, and `Queue`s for verdicts and PLC commands. A `ProcessManager` tracks every spawned process so they can all be torn down cleanly on stop or window close.

## Defect Classes

The two faces detect different defect sets:

- **Big Face (BF):** rust, dent, damage, high head, down head
- **Outer Diameter (OD):** rust, dent, damage, damage-on-end, spherical mark

Each maps to its own counter and its own column in the tracking tables.

## Results / Highlights

- Ships with **three trained YOLO models**: `BF_sr.pt` (~18 MB), `OD_sr.pt` (~21 MB), and `BF_head.pt` (~6 MB) for head classification.
- Runs **two camera feeds and two GPU inference pipelines concurrently**, driven off PLC sensor events rather than a fixed loop, with per-model GPU warmup to avoid first-frame stalls.
- Designed for continuous shop-floor operation — per the project's industrial deployment, the line handled on the order of **100,000+ rollers per day**.
- Roughly **90 Python modules** across the frontend GUI and backend, organised into self-contained feature packages (inference, settings, diagnosis, model management, user management, backup, system check).

## Tech Stack

- **Language:** Python 3.x
- **Deep learning / CV:** PyTorch, Torchvision, Ultralytics YOLO, OpenCV, Pillow, NumPy (CUDA 12.8 wheels)
- **GUI:** Tkinter, tkcalendar, Matplotlib (charts)
- **Database:** MySQL (`mysql-connector-python`), schema `welvision_db`
- **Hardware / industrial I/O:** `python-snap7` (Siemens S7 PLC), `pygrabber` + PyWin32 (Windows camera access)
- **Runtime / ops:** Python `multiprocessing` (processes, shared `Array`/`Queue`/`Manager`), `psutil` (process priority), `gputil`, `pandas` + `openpyxl` (reports), `tqdm`

## Getting Started

### Prerequisites

- Windows PC with an NVIDIA GPU (CUDA) — the inference path assumes CUDA is available
- Python 3.x
- A running MySQL server
- Two industrial cameras and a Siemens S7 PLC reachable on the network (for live inspection)

### Installation

```bash
git clone https://github.com/DCode-v05/Roller-Defect-Detection.git
cd Roller-Defect-Detection

# Installs PyTorch from the CUDA 12.8 index plus the rest of the stack
pip install -r requirements.txt
```

### Database setup

Create the schema and tables (defaults to `localhost` / `root` / `welvision_db`):

```bash
python utils/create_db.py
```

Adjust the connection details in `frontend/utils/config.py` (`AppConfig.DB_*`) and the PLC settings (`PLC_IP`, `PLC_RACK`, `PLC_SLOT`, `PLC_DB_NUMBER`) to match your hardware.

### Running

```bash
python main.py
```

This opens the WelVision login window. Log in, use the **System Check** tab to confirm the cameras and PLC are connected, pick the roller type and models, then start inspection from the **Inference** tab.

## Usage

- **Login** with an employee ID; your role (Operator / Admin / Super Admin) decides which tabs and actions you can use.
- **System Check** — verify camera and PLC connectivity and watch the processing counters before a run.
- **Settings** — select the active BF/OD models, set per-defect confidence and size thresholds, and configure roller-type limits (Admin/Super Admin).
- **Inference** — start/stop the line, watch the live annotated feeds, and see per-face counts of inspected / OK / not-OK and the defect breakdown updating in real time.
- **Model Management** — upload new `.pt` weights and track which model is in use (Admin/Super Admin).
- **Diagnosis / Data** — review historical sessions, defect-wise and status charts, and per-roller records.
- **Backup** — back up the database and captured images, with storage checks (Admin/Super Admin).

Defect frames are written to `Desktop/Inference/BF` and `Desktop/Inference/OD`; with "Allow All Images" enabled (Super Admin), every frame is saved under `Desktop/All Frames` for re-labelling datasets.

## Project Structure

```
Roller-Defect-Detection/
├── main.py                     # Entry point — launches the Tkinter app
├── backend.py                  # Inference + PLC pipeline: capture, YOLO, filtering, sorting
├── database.py                 # RollerDatabase — writes BF/OD session tracking to MySQL
├── requirements.txt            # Deps (PyTorch CUDA 12.8 index, Ultralytics, snap7, etc.)
├── Warmup BF.jpg / Warmup OD.jpg  # Frames used to warm up the GPU models
├── models/
│   ├── BF_sr.pt                # Big Face defect model (~18 MB)
│   ├── OD_sr.pt                # Outer Diameter defect model (~21 MB)
│   └── BF_head.pt              # Head-type classification model (~6 MB)
├── IC Capture Settings/        # Saved industrial-camera profiles (BF / OD)
├── frontend/
│   ├── app.py                  # WelVisionApp — spawns processes, wires shared memory
│   ├── login/                  # Auth + role selection
│   ├── navbar/                 # Tab navigation
│   ├── inference/              # Live inspection tab: feeds, control, results, state
│   ├── settings/               # Model selection + threshold management
│   ├── model_management/       # Upload / select / track models (DB-backed)
│   ├── system_check/           # Camera + PLC connectivity, plc_controller, counters
│   ├── diagnosis/              # Reports, defect-wise and status charts
│   ├── data/                   # Roller data tables and global limits
│   ├── info/                   # System info, settings history, user manual
│   ├── user_management/        # User CRUD (RBAC)
│   ├── backup/                 # DB + image backup with progress UI
│   └── utils/                  # config, permissions (RBAC), process_manager, logging, helpers
└── utils/                      # create_db, backup/restore, GPU/cache cleanup, model_size
```

---

## Contact

<table>
  <tr><td><b>Portfolio:</b> <a href="https://www.denistan.me">Denistan</a></td><td><b>LinkedIn:</b> <a href="https://www.linkedin.com/in/denistanb">denistanb</a></td></tr>
  <tr><td><b>GitHub:</b> <a href="https://github.com/DCode-v05">DCode-v05</a></td><td><b>LeetCode:</b> <a href="https://leetcode.com/u/Denistan_B">Denistan_B</a></td></tr>
  <tr><td colspan="2" align="center"><b>Email:</b> <a href="mailto:denistanb05@gmail.com">denistanb05@gmail.com</a></td></tr>
</table>

Made with ❤️ by **Denistan B**
