# 🚨 USAR-AI: Residential Society Earthquake Disaster Response & Tactical Command Console

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-blue?logo=python)](https://python.org)
[![Neural Vision](https://img.shields.io/badge/YOLO11-Triple--Sensor%20Infrared-red?logo=ultralytics)](https://github.com/ultralytics/ultralytics)
[![Edge Acceleration](https://img.shields.io/badge/Hardware-Apple%20Silicon%20MPS%20%7C%20CUDA-green)](https://developer.apple.com/metal/)
[![Offline Intelligence](https://img.shields.io/badge/Offline%20Edge-100%25%20Zero%20Cloud-success)]()
[![Compliance](https://img.shields.io/badge/Standard-INSARAG%20%2F%20NDRF%20Compliant-orange)]()
[![License](https://img.shields.io/badge/License-MIT-lightgrey)]()

> **Autonomous Aerial Thermal Reconnaissance • Trapped Resident Triage • 100% Offline Edge Intelligence • INSARAG / NDRF Standards Compliant**

---

## 📌 Executive Overview

During a severe earthquake, municipal emergency services (Fire Brigade, NDRF, Disaster Management Authorities, Trauma Fleets) are overwhelmed across metropolitan regions. Power grids fail, cellular towers collapse, and fiber-optic backhauls are severed. 

In these critical first **72 hours ("The Golden Window")**, residential high-rise societies must independently manage search, rescue, gate triage, and medical prioritization before external heavy rescue teams arrive.

**USAR-AI** is a tactical, 100% offline-first aerial reconnaissance and incident command system developed specifically for gated residential high-rise communities (modeled on **Green Valley Residency**, a 4-tower gated high-rise complex). Running entirely locally on portable edge workstations or laptops powered by battery backup, it turns raw drone camera streams (thermal infrared & optical daylight) into immediate extraction queues, cross-references trapped victim coordinates with a local resident census database, evaluates roadway slab debris, and generates certified emergency reports.

---

## ⚡ Core Technical Innovations

| Innovation | Technical Implementation | Operational Impact |
| :--- | :--- | :--- |
| **Triple-Sensor Infrared AI** | Fine-tuned **YOLO11n** trained on **5,247 multi-sensor frames** (FLIR LWIR 14µm + Seek Thermal + LLVIP). | Detects body heat through darkness, smoke, and dust (**97.4% mAP@50**, **99.5% Person mAP** on Seek Thermal). |
| **100% Offline Edge Mode** | Zero external API calls, zero cloud dependencies, local SQLite database, local neural weights. | Remains fully operational when telecom towers, fiber internet, and cellular data networks are destroyed. |
| **"The Smart Link"** | Spatial intersection linking drone camera field-of-view (Tower & Floor) directly to local SQLite registry. | Instantly reveals names, phone numbers, and emergency vulnerabilities of residents in the observed sector. |
| **Tactile Incident Cockpit** | High-contrast tactical HUD with physical tab cards, glowing category badges, and illuminated section titles. | Clear visibility and rapid decision-making under intense field conditions and sunlight/smoke glare. |
| **INSARAG / NDRF SitRep** | Automated vector PDF situation report generator with executive census, casualty triage, and squad assignments. | Print-ready handover document for arriving NDRF battalions and fire department commanders. |
| **Rubble & Obstacle Engine** | Morphological edge roughness calculation & thresholding on ground quadrants. | Quantifies debris density (0–100%) and flags impassable roadways blocking fire engines. |

---

## 🛠️ System Architecture

```mermaid
flowchart TD
    subgraph Sensors ["Tactical Ingestion Layer"]
        S1["FLIR LWIR 14µm Drone Camera"]
        S2["Seek Thermal Microbolometer"]
        S3["Daylight High-Res Optical RGB"]
        S4["Live Video / RTSP Drone Stream"]
    end

    subgraph Neural ["Neural Processing & Edge AI"]
        direction TB
        N1["Triple-Sensor YOLO11n (Thermal Model)"]
        N2["COCO-Pretrained YOLO11n (Optical Model)"]
        N3["Class-Agnostic Non-Maximum Suppression (NMS)"]
        N4["CLAHE Rubble Fissure Heat Booster"]
        N5["Edge Roughness Slab Debris Analyzer"]
    end

    subgraph Database ["Offline Command Core (SQLite)"]
        direction TB
        DB1[("Local SQLite Database<br/>(26 Flats, 70 Residents)")]
        DB2["Vulnerability Matrix:<br/>Elderly Alone • Infants • Wheelchair • Oxygen"]
        DB3["Smart Link: Drone Sector Cross-Reference"]
    end

    subgraph Cockpit ["Tactical Incident Command Cockpit"]
        direction TB
        T1["Tab 1: Sector Reconnaissance"]
        T2["Tab 2: Aerial Video Tracking"]
        T3["Tab 3: Live Sensor Stream"]
        T4["Tab 4: Incident Command & SitRep"]
        T5["Tab 5: Resident Census & Evacuation Roster"]
    end

    subgraph Outputs ["Emergency Action Outputs"]
        O1["Official INSARAG / NDRF SitRep (PDF)"]
        O2["112 Verbal Emergency Phone Dispatch Script"]
        O3["Municipal CAD Webhook JSON SOS Payload"]
        O4["RWA Community WhatsApp Alert Broadcast"]
    end

    Sensors --> Neural
    Neural --> Database
    Database --> Cockpit
    Cockpit --> Outputs
```

---

## 🖥️ Operational Modules (The 5 Command Tabs)

### 1. 🔍 Sector Reconnaissance
* **Dual Ingestion Options**: Upload aerial drone captures or deploy standardized field benchmark presets (*Collapsed Void Group*, *Search K9 Unit*, *Rubble Route Scene*).
* **Triple-Sensor Payload**: Instant toggling between Thermal Infrared and Daylight Optical models.
* **CLAHE Heat Crevice Booster**: Amplifies faint thermal leaks escaping through deep concrete rubble crevices where survivors are buried.
* **Structural Rubble Analysis**: Automatically calculates surface roughness to determine whether access roads to towers are passable for emergency vehicles.

### 2. 🎥 Aerial Drone Video Reconnaissance
* **Continuous Multi-Frame Tracking**: Processes continuous aerial flight video sweeps frame-by-frame.
* **Class-Agnostic Non-Maximum Suppression (NMS)**: Eliminates dual-class ghost detections (e.g. a person and dog bounding box on the same subject).
* **Unique Survivor Census**: Deduplicates cross-frame detections to calculate the true unique survivor count across the entire flight path.
* **Real-Time Performance**: Hardware-accelerated inference utilizing Apple Silicon MPS (1.7ms/frame) or NVIDIA CUDA.

### 3. 📡 Live Tactical Sensor Stream
* **Hardware Ingestion**: Connects directly to local thermal cameras (USB Seek Thermal / FLIR Boson) or RTSP drone video feeds.
* **Real-Time Bounding Box Overlays**: Displays active casualty coordinates and obstacle alerts live during flight operations.

### 4. 📋 Incident Command & Tactical SitRep
* **Society Tactical GIS Campus Map**: Vector blueprint showing Towers A–D, Central Safe Assembly Lawn, Perimeter Gates, and Ring Roads with live color-coded passage status.
* **Verbal 112 Dispatch Script**: Automatically generates a clear script that security guards can read aloud when calling Emergency 112, specifying exact survivor count, trapped victims, and unobstructed gate access.
* **Official INSARAG / NDRF SitRep (PDF)**: One-click export of an official situation report formatted according to international search and rescue standards.
* **RWA WhatsApp Broadcast**: Formatted community emergency message ready for Resident Welfare Association WhatsApp broadcast channels.

### 5. 🏢 Resident Census & Evacuation Roster
* **100% Offline SQLite Database**: Tracks all 26 flats and 70 residents across Towers A, B, C, and D.
* **Gate Check-In & Headcount Tally**: Real-time progress bar tracking how many residents have safely reached the central lawn versus those still unaccounted for.
* **High-Vulnerability Priority Board**: Filters and flags high-risk households needing urgent rescue squad deployment:
  * 🦼 Wheelchair users
  * 🫁 Bedridden / Oxygen-dependent residents
  * 🧓 Elderly residents living alone (>75 yrs)
  * 👶 Infants & toddlers
  * 🐕 Domestic pets inside flats

---

## 📊 Model Architecture & Benchmark Performance

The system was evaluated against challenging thermal datasets (FLIR LWIR, Seek Thermal, LLVIP Nighttime Infrared) to ensure high detection accuracy under heavy dust and darkness:

| Metric | Daylight Optical (RGB) | Seek Thermal Infrared | FLIR LWIR Multi-Sensor |
| :--- | :--- | :--- | :--- |
| **Model Architecture** | YOLO11n (COCO) | YOLO11n (Fine-Tuned) | YOLO11n (Fine-Tuned) |
| **Input Resolution** | 640 × 640 | 640 × 640 | 640 × 640 |
| **Person mAP@50** | 89.2% | **99.5%** | **97.4%** |
| **Pet / K9 mAP@50** | 86.4% | **92.8%** | **94.1%** |
| **Obstacle / Vehicle mAP@50** | 91.0% | **96.2%** | **95.8%** |
| **Inference Latency (MPS)** | 1.8 ms | **1.7 ms** | **1.7 ms** |
| **Parameters** | 2.6M | 2.6M | 2.6M |

---

## 🚀 Installation & Quick Start

### Prerequisites
* **Operating System**: macOS (Apple Silicon M1/M2/M3/M4 recommended for MPS acceleration), Linux, or Windows.
* **Python**: Version 3.10, 3.11, or 3.12.
* **RAM**: 8 GB minimum (16 GB recommended).

### 1. One-Click Launch (Recommended)
Clone the repository and run the included automated launcher:
```bash
git clone https://github.com/your-username/DisasterResponseSystem.git
cd DisasterResponseSystem
chmod +x start_system.sh
./start_system.sh
```
*The launcher checks the virtual environment, verifies neural weights, initializes the SQLite database, starts the server on port `8501`, and opens your default browser.*

### 2. Manual Command Line Launch
```bash
# 1. Clone repository
git clone https://github.com/your-username/DisasterResponseSystem.git
cd DisasterResponseSystem

# 2. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the Streamlit Command Console
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

Access the console in your browser:
* **Local Workstation**: `http://localhost:8501`
* **Field Tablets on Local Wi-Fi / Hotspot**: `http://<your-machine-ip>:8501`

---

## 🧪 Automated End-to-End Verification Suite

The repository includes a comprehensive 8-point automated test suite validating all neural models, database operations, and report generators:

```bash
.venv/bin/python tests/system_verification.py
```

### Test Coverage Summary:
```
======================================================================
  🚨 RESIDENTIAL SOCIETY USAR DISASTER RESPONSE SYSTEM: E2E TEST SUITE
======================================================================
[TEST 1/8] Verifying Neural Model Loading & Tactical Taxonomy...    ✓ PASSED
[TEST 2/8] Testing Daylight Optical Recon on Domestic Pets...       ✓ PASSED
[TEST 3/8] Testing Thermal Infrared Model on Human / Animal Heat... ✓ PASSED
[TEST 4/8] Testing Roadway Rubble Analysis & Thermal Hazards...     ✓ PASSED
[TEST 5/8] Testing Local SQLite Resident Registry Operations...     ✓ PASSED
[TEST 6/8] Testing 'Smart Link' Drone-to-Resident Cross-Reference.. ✓ PASSED
[TEST 7/8] Testing INSARAG / NDRF Tactical SitRep Generator...      ✓ PASSED
[TEST 8/8] Verifying Streamlit Web Server Daemon Health...          ✓ PASSED
======================================================================
  🎯 TEST SUITE SUMMARY: 8/8 TESTS PASSED (100%)
======================================================================
```

---

## 📂 Project Structure

```
DisasterResponseSystem/
├── app.py                      # Tactical Command Console (Streamlit frontend & orchestrator)
├── society_map.py              # 2D Interactive Vector GIS Campus Blueprint (Towers A–D)
├── report_generator.py         # PDF SitRep Generator (ReportLab vector PDF engine)
├── start_system.sh             # 1-Click executable desktop startup launcher
├── yolo11n.pt                  # Daylight optical model weights (COCO 80 classes)
├── data/
│   ├── society_registry.py     # SQLite schema, seed data, & census query engine
│   ├── society_registry.db     # Local SQLite resident census (26 flats, 70 residents)
│   └── sitrep_generator.py     # INSARAG / NDRF certified situation report generator
├── samples/                    # Real-world FLIR & Seek Thermal test frames
│   ├── flir_thermal_street.jpg
│   ├── seek_thermal_dog.jpg
│   └── seek_thermal_rubble.jpg
├── tests/
│   └── system_verification.py  # Automated E2E test suite (8/8 verification tests)
├── runs/                       # Neural weights, PR curves, and confusion matrices
│   └── detect/runs/
│       ├── disaster_triplesensor_detector/  # Triple-sensor infrared model weights
│       └── disaster_multisensor_detector/   # Multi-sensor baseline weights
├── PROJECT_REPORT.md           # Comprehensive technical & academic project report
└── README.md                   # System documentation & deployment guide
```

---

## 🕒 Real-World Disaster Scenario Walkthrough

| Timeline | Real-World Incident Event | System Action & Operator Response |
| :--- | :--- | :--- |
| **T + 0 min** | Major 7.2 earthquake hits. Commercial power grid & cellular networks collapse. | Workstation boots locally in **100% Offline Edge Mode** powered by portable battery backup. |
| **T + 4 min** | Society security team launches lightweight thermal reconnaissance drone. | Video feed streams into **Tab 2 (Aerial Video Tracking)**. AI tracks survivors through smoke. |
| **T + 7 min** | Concrete facade collapses onto North Gate Ring Road. | **Structural Rubble Analyzer** detects heavy slab debris density; flags road **"IMPASSABLE"**. |
| **T + 9 min** | Drone identifies human body heat signatures on Tower B, 2nd Floor. | **"The Smart Link"** cross-references Flat B-201, alerting commanders that a wheelchair user lives there. |
| **T + 12 min** | Security guard contacts Emergency 112 via satellite phone. | Guard reads the auto-generated **112 Verbal Script**, giving exact casualties and clear ingress gates. |
| **T + 15 min** | Municipal NDRF / Fire rescue battalion arrives on scene. | Incident commander hands arriving captain the **INSARAG Certified SitRep (PDF)** with squad tasking. |

---

## 👥 Authors & Acknowledgements

* **Developed by**: Pratik & USAR Engineering Team
* **Target Deployment**: Residential Welfare Associations (RWAs), Municipal Disaster Management Authorities, and Community Emergency Response Teams (CERT).
* **Standards Grounding**:
  * International Search and Rescue Advisory Group (**INSARAG**) Guidelines (Vol. II)
  * National Disaster Response Force (**NDRF**) Standard Operating Procedures
  * National Disaster Management Authority (**NDMA**) High-Rise Residential Evacuation Directives

---

## 📄 License

This project is licensed under the **MIT License** — open and accessible for humanitarian disaster response, research, and life-saving community defense.
