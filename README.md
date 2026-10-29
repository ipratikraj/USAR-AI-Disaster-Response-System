# 🚨 USAR-AI: Earthquake Search & Rescue Thermal Reconnaissance System

An edge-deployable, multi-sensor thermal computer vision and tactical decision-support system designed for post-earthquake Urban Search and Rescue (USAR) operations.

---

## ⚡ Highlights

- **Multi-Sensor Thermal AI**: Fine-tuned YOLO11n trained across **5,247 images** (FLIR LWIR + Seek Thermal Microbolometer + LLVIP Nighttime Infrared) achieving **97.4% mAP@50** and **99.5% Person mAP on Seek Thermal**.
- **Tactical Command Dashboard**: High-contrast dark obsidian HUD featuring real-time earthquake structural triage alerts, trapped void cluster warnings, and K9 telemetry.
- **Drone Video Multi-Object Tracking**: Built-in zero-dependency centroid tracker with temporal confirmation and majority-vote class persistence to prevent flickering and count inflation.
- **Zero Cloud Dependency**: Runs 100% locally and offline on Apple Silicon GPU (`mps`) or CPU with sub-25ms latency.

---

## 🚀 Quickstart

### 1. Launch with One Click
```bash
./run.sh
```

### 2. Manual Launch
```bash
source .venv/bin/activate
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

Open your browser to:
- **Local**: `http://localhost:8501`
- **Field Network / Phone**: `http://<your-ip>:8501`

---

## 🎯 Target Classes

| Class ID | Name | USAR Role |
| :---: | :---: | :--- |
| `0` | **Person** | Trapped Survivors & Extraction Targets |
| `1` | **Car** | Evacuation Route Blockages & Vehicles |
| `2` | **Dog** | Active Urban Search & Rescue K9s |

---

## 📄 Documentation

For complete technical benchmarks, domain-shift analysis, and architecture details, see:
👉 [PROJECT_REPORT.md](PROJECT_REPORT.md)
