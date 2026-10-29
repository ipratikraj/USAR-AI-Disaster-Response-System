# USAR-AI: Autonomous Multi-Sensor Thermal Reconnaissance & Triage
## Post-Earthquake Search & Rescue Decision Support System

---

### 1. Executive Summary
During post-earthquake Urban Search and Rescue (USAR) operations, optical cameras frequently fail due to heavy particulate dust, thick smoke plumes, power grid collapse, and structural voids. Long-Wave Infrared (LWIR) and thermal vision sensors are essential for locating trapped survivors and working search dogs.

However, thermal computer vision models suffer heavily from **Camera Domain Shift** (differences in sensor focal lengths, spectral responses, palettes, and resolutions) and **Dynamic Motion Confusion** (walking human leg-strides resembling quadruped silhouettes in low-resolution thermal feeds).

**USAR-AI** solves these challenges by combining:
1. **Triple-Sensor Cross-Domain Neural Training**: A universal YOLO11n thermal detector fine-tuned across 5,247 thermal images (FLIR LWIR, Seek Thermal microbolometer, and LLVIP nighttime infrared).
2. **Tactical Earthquake Command HUD**: A high-contrast obsidian-themed reconnaissance dashboard with priority triage scoring for structural void collapses.
3. **Robust Centroid Multi-Object Tracking with Temporal Confirmation**: Eliminates phantom detections, flickering classifications, and frame-count ballooning in drone video feeds.

---

### 2. The Domain Shift Problem & Technical Challenges

#### Challenge A: FLIR vs. Seek Thermal Camera Domain Shift
- **FLIR Tau2 / Boson**: High dynamic range, 640x512 resolution, calibrated high-contrast thermal signatures.
- **Seek Thermal Compact**: 206x156 native microbolometer interpolated to 416x416, distinct rainbow/ironbow palettes, lower signal-to-noise ratio.
- **Observation**: A baseline YOLO model trained purely on FLIR achieved **0.0% mAP** when deployed on Seek Thermal captures.

#### Challenge B: Walking Silhouettes vs. Quadruped Confusion
- When pedestrians walk towards or away from thermal cameras, ground thermal reflection and leg-swing cycles create momentary silhouettes resembling four-legged animals.
- Under FLIR-only weights, walking survivors intermittently flickered as "dog" detections with low confidence (20–35%).

#### Challenge C: Compression & Resolution Vulnerability
- In disaster field communications (e.g., transmitting drone captures over low-bandwidth cellular/mesh networks), lossy compression (such as WhatsApp/MMS) smoothed out 15-pixel human thermal gradients, dropping raw detection rates to zero.

---

### 3. Model Architecture & Progressive Evolution

We trained and evaluated three progressive model generations on Apple Silicon M5 GPU using PyTorch MPS:

| Generation | Training Data | Total Images | Person mAP@50 | Dog mAP@50 | Seek Test mAP@50 | Key Capability |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Gen 1: FLIR Baseline** | FLIR LWIR | 3,247 | 94.2% | 88.0% | **0.0%** | Baseline; fails completely on non-FLIR sensors. |
| **Gen 2: Dual-Sensor** | FLIR + Seek Thermal | 3,247 | 99.4% | 99.1% | **94.1%** | Bridges Seek sensor domain gap. |
| **Gen 3: Triple-Sensor Universal** | FLIR + Seek + LLVIP | **5,247** | **93.5%** | **99.3%** | **99.5%** | Eliminates walking motion confusion; immune to compression decay. |

#### Gen 3 Validation Highlights (disaster_triplesensor_detector)
- **Overall mAP@50**: **97.4%** across all classes.
- **Seek Thermal Test Benchmark**: **99.5% mAP@50 for Person** with **100% recall** (16/16 trapped survivors identified).
- **Inference Speed**: ~0.6 ms inference / 22 ms total on Apple M5 (~45+ FPS real-time processing).

---

### 4. System Architecture & Innovations

```
[ Thermal Camera / Drone Feed ]
              │
              ▼
   [ Streamlit Tactical HUD ]
              │
              ├──▶ [ Model Engine: YOLO11n Triple-Sensor ]
              │         │
              │         ├── 0: Person (Survivor)
              │         ├── 1: Car (Road Obstacle)
              │         └── 2: Dog (Search & Rescue K9)
              │
              ├──▶ [ Robust Centroid Multi-Object Tracker ]
              │         │
              │         ├── Temporal Confirmation Window (4-frame minimum)
              │         ├── Class Majority-Voting (Histogram persistence)
              │         └── Cumulative Unique ID Preservation
              │
              └──▶ [ Earthquake Structural Triage Alert Engine ]
                        │
                        ├── Collapsed Void Cluster Warning (<220px proximity)
                        ├── Priority 1: High-Density Void Extractions
                        ├── Priority 2: Isolated Survivors
                        └── Priority 3: Active Working K9 Telemetry
```

#### 1. Zero-Dependency Centroid Tracker (`RobustVideoTracker`)
To prevent external C++ dependency incompatibilities (e.g. `lap` / `cython_bbox`) on ARM macOS, a pure-Python tracker was implemented:
- **Euclidean Centroid Distance Matching** with Hungarian greedy assignment.
- **Majority-Voting Class Memory**: Every track retains a rolling histogram of detected labels (`t['votes']`). A walking survivor whose leg posture flickers for 1 frame is stabilized by historical consensus.
- **Temporal Confirmation**: Transient noise is filtered out; tracks must persist across at least 4 frames before triggering USAR rescue alerts.

#### 2. Earthquake Structural Triage Engine
The tactical UI categorizes detections into live triage alerts:
- **🔴 Priority 1 (Collapsed Structural Voids)**: Automatically computes Euclidean pixel distance between survivors. Multiple victims within `< 220px` are flagged as trapped in a collapsed structural void, dispatching heavy shoring teams.
- **🟡 Priority 2 (Isolated Survivors)**: Single victims flagged for field medic triage.
- **🐕 Priority 3 (Search K9 Monitoring)**: Tracks active canine search units to ensure rescue dogs are safely mapped during collapse searches.
- **🚗 Evacuation Route Clearance**: Monitors vehicles blocking emergency evacuation corridors.

#### 3. Rubble Void Enhancer (CLAHE Pipeline Separation)
Contrast Limited Adaptive Histogram Equalization (CLAHE) helps human operators spot subtle thermal gradients in dense rubble. However, feeding CLAHE images into neural networks distorts calibrated sensor values. USAR-AI strictly isolates CLAHE to the **display presentation layer**, preserving raw sensor fidelity for neural inference.

---

### 5. Repository Structure
```
DisasterResponseSystem/
├── app.py                      # Streamlit Tactical Command Dashboard & Triage HUD
├── run.sh                      # One-click launch script
├── PROJECT_REPORT.md           # Engineering & architectural documentation
├── README.md                   # Quickstart guide
├── .gitignore                  # VCS configuration
├── datasets/
│   ├── disaster_combined/      # Master dataset (5,247 images across FLIR, Seek, LLVIP)
│   └── thermal_extra/          # Seek Thermal evaluation dataset
└── runs/detect/runs/
    ├── disaster_triplesensor_detector/  # Gen 3 Production Weights (best.pt)
    └── disaster_multisensor_detector-2/ # Gen 2 Weights (best.pt)
```

---

### 6. Verification & Results Summary
- **Walking Person Verification**: Detection confidence on walking pedestrians in low-resolution thermal crops jumped from **0.0% / 36%** to **66.4%** with zero false animal classifications.
- **Edge Deployment**: Complete edge autonomy with zero cloud latency and zero external API dependencies.
