import streamlit as st
import pandas as pd
import numpy as np
import cv2
import time
import tempfile
from PIL import Image
from pathlib import Path
from ultralytics import YOLO
from report_generator import generate_society_pdf_report

# ---------------- PAGE CONFIGURATION ----------------
st.set_page_config(
    page_title="Residential Society // Earthquake USAR AI",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- HIGH-TECH TACTICAL HUD STYLING ----------------
st.markdown("""
<style>
    /* Dark tactical command aesthetic */
    .stApp {
        background-color: #0d1117;
        color: #e6edf3;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }
    
    /* Top HUD header bar */
    .hud-header {
        background: linear-gradient(90deg, #161b22 0%, #0d1117 100%);
        border: 1px solid #30363d;
        border-left: 6px solid #ff3366;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }
    .hud-title {
        font-size: 1.8rem;
        font-weight: 800;
        letter-spacing: 1.5px;
        color: #ffffff;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .hud-sub {
        font-size: 0.9rem;
        color: #8b949e;
        letter-spacing: 0.5px;
        margin-top: 4px;
    }
    
    /* Tactical Status Badges */
    .status-badge-container {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 12px;
    }
    .hud-badge {
        font-size: 0.75rem;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 20px;
        letter-spacing: 0.8px;
        text-transform: uppercase;
    }
    .badge-online {
        background: rgba(0, 245, 155, 0.15);
        color: #00f59b;
        border: 1px solid rgba(0, 245, 155, 0.4);
    }
    .badge-mps {
        background: rgba(0, 240, 255, 0.15);
        color: #00f0ff;
        border: 1px solid rgba(0, 240, 255, 0.4);
    }
    .badge-earthquake {
        background: rgba(255, 51, 102, 0.15);
        color: #ff3366;
        border: 1px solid rgba(255, 51, 102, 0.4);
    }

    /* Metric Cards */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
        gap: 14px;
        margin: 16px 0;
    }
    .tactical-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 16px;
        position: relative;
        overflow: hidden;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .tactical-card:hover {
        border-color: #58a6ff;
        transform: translateY(-2px);
    }
    .card-victim { border-top: 4px solid #ff3366; }
    .card-k9 { border-top: 4px solid #00f0ff; }
    .card-vehicle { border-top: 4px solid #ffd166; }
    .card-total { border-top: 4px solid #00f59b; }

    .card-label {
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #8b949e;
    }
    .card-value {
        font-size: 2.2rem;
        font-weight: 800;
        margin: 6px 0 2px 0;
        letter-spacing: 1px;
    }
    .val-victim { color: #ff3366; text-shadow: 0 0 12px rgba(255, 51, 102, 0.3); }
    .val-k9 { color: #00f0ff; text-shadow: 0 0 12px rgba(0, 240, 255, 0.3); }
    .val-vehicle { color: #ffd166; text-shadow: 0 0 12px rgba(255, 209, 102, 0.3); }
    .val-total { color: #00f59b; text-shadow: 0 0 12px rgba(0, 245, 155, 0.3); }

    /* Alert Banners */
    .alert-box {
        background: #161b22;
        border-radius: 8px;
        padding: 14px 18px;
        margin: 14px 0;
        border-left: 5px solid;
    }
    .alert-critical {
        border-color: #ff3366;
        background: rgba(255, 51, 102, 0.08);
    }
    .alert-k9 {
        border-color: #00f0ff;
        background: rgba(0, 240, 255, 0.08);
    }
    .alert-safe {
        border-color: #00f59b;
        background: rgba(0, 245, 155, 0.08);
    }
    
    /* Crop gallery styling */
    .crop-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 8px;
        text-align: center;
        margin-bottom: 10px;
    }
    
    /* Tabs styling */
    button[data-baseweb="tab"] {
        color: #8b949e !important;
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        padding: 10px 18px !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #58a6ff !important;
        border-bottom-color: #58a6ff !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- HUD TOP BANNER ----------------
st.markdown("""
<div class="hud-header">
    <div class="hud-title">🚨 RESIDENTIAL SOCIETY // EARTHQUAKE DISASTER RECONNAISSANCE</div>
    <div class="hud-sub">Autonomous Aerial Thermal Reconnaissance • Trapped Resident Triage • Gate Obstacle Assessment • Utility Hazard Defense</div>
    <div class="status-badge-container">
        <span class="hud-badge badge-online">🟢 System: Online</span>
        <span class="hud-badge badge-mps">⚡ Hardware: Apple Silicon MPS (1.7ms / frame)</span>
        <span class="hud-badge badge-earthquake">🏘️ Sector: Residential High-Rise Complex</span>
        <span class="hud-badge badge-online">📡 Offline Edge Mode: Active (Zero Cloud Dependency)</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------- MODEL LOADING & CONFIG ----------------
AVAILABLE_MODELS = {}
_triple_weights = "/Users/pratik/DisasterResponseSystem/runs/detect/runs/disaster_triplesensor_detector/weights/best.pt"
if Path(_triple_weights).exists():
    AVAILABLE_MODELS["🌟 Triple-Sensor Universal Model (FLIR + Seek + LLVIP)"] = _triple_weights
AVAILABLE_MODELS["☀️ Daylight Optical Recon Mode (RGB / Visible Light)"] = "/Users/pratik/DisasterResponseSystem/yolo11n.pt"
AVAILABLE_MODELS["⚡ Multi-Sensor Model (FLIR + Seek)"] = "/Users/pratik/DisasterResponseSystem/runs/detect/runs/disaster_multisensor_detector-2/weights/best.pt"
AVAILABLE_MODELS["⚠️ FLIR-Only Baseline Model"] = "/Users/pratik/DisasterResponseSystem/runs/detect/runs/flir_thermal_detector/weights/best.pt"

TARGET_CLASSES = {
    0: "Person",
    1: "Obstacle / Vehicle",
    2: "Dog"
}

def check_thermal_hazards(img_np):
    """Detects extreme saturation (>248) indicative of gas fire or electrical transformer rupture."""
    if len(img_np.shape) == 3:
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    else:
        gray = img_np
    hot_pixels = int(np.sum(gray >= 248))
    is_hazard = hot_pixels > 350
    return is_hazard, hot_pixels

@st.cache_resource
def load_yolo_model(path: str):
    return YOLO(path)

# Sidebar
st.sidebar.markdown("### 🏘️ SOCIETY CONFIGURATION")
society_name = st.sidebar.text_input("Housing Society / Complex Name", value="Green Valley Residency")
safe_assembly_point = st.sidebar.text_input("Designated Safe Assembly Point", value="Central Community Lawn / Park")
main_gate_name = st.sidebar.text_input("Primary Evacuation Gate", value="Main North Security Gate")

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ TACTICAL CONFIGURATION")

selected_model_name = st.sidebar.selectbox(
    "Active Thermal Vision Model",
    options=list(AVAILABLE_MODELS.keys()),
    index=0
)
model_path = AVAILABLE_MODELS[selected_model_name]
is_optical_model = "Daylight Optical" in selected_model_name

try:
    model = load_yolo_model(model_path)
    st.sidebar.success(f"✓ Neural Weights Online")
except Exception as e:
    st.sidebar.error(f"Error loading model: {e}")
    st.stop()

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎯 SENSOR TUNING")

sensitivity_mode = st.sidebar.radio(
    "Operational Sensitivity Mode",
    options=[
        "🚨 High Sensitivity (USAR / Faint Heat / Distant Victims)",
        "🎯 Balanced Operations (Standard)",
        "🛡️ High Confidence (Zero False Alarms)"
    ],
    index=0,
    help="High Sensitivity catches distant or faint thermal signatures (down to 12% confidence) — essential for partially buried or distant earthquake survivors."
)

if "High Sensitivity" in sensitivity_mode:
    default_conf = 0.15
elif "Balanced" in sensitivity_mode:
    default_conf = 0.30
else:
    default_conf = 0.50

confidence = st.sidebar.slider(
    "Minimum Detection Confidence",
    min_value=0.05,
    max_value=0.90,
    value=default_conf,
    step=0.01,
    help="Lower values (0.05 - 0.15) help detect distant, faint, or compressed WhatsApp thermal images."
)

iou_thresh = st.sidebar.slider(
    "NMS Duplicate Suppression (IoU)",
    min_value=0.20,
    max_value=0.80,
    value=0.45,
    step=0.05,
    help="Suppresses duplicate overlapping bounding boxes on the same object."
)

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚡ THERMAL ENHANCEMENT")
enable_clahe = st.sidebar.checkbox(
    "Rubble Void Enhancer (CLAHE)",
    value=False,
    help="Applies Contrast Limited Adaptive Histogram Equalization to amplify faint heat leaks escaping through concrete rubble cracks."
)

def apply_thermal_enhancement(img_rgb):
    """Amplify weak thermal gradients in rubble crevices."""
    lab = cv2.cvtColor(np.array(img_rgb), cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    enhanced_lab = cv2.merge((cl, a, b))
    return Image.fromarray(cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2RGB))

# ---------------- MAIN APPLICATION TABS ----------------
tab_image, tab_video, tab_dispatch = st.tabs([
    "🛰️ Sector Imagery Reconnaissance", 
    "🎥 Aerial Drone Video Recon", 
    "📋 USAR Tactical Dispatch & Triage"
])

# Global state to share detections with dispatch tab
if "latest_detections" not in st.session_state:
    st.session_state.latest_detections = []
    st.session_state.latest_source = "None"
    st.session_state.latest_crops = []

# =======================================================
# TAB 1: SECTOR IMAGERY RECON
# =======================================================
with tab_image:
    st.markdown("#### 📥 Reconnaissance Imagery Feed")
    
    c_input1, c_input2 = st.columns([1, 1])
    selected_img = None
    img_name = "custom_image.jpg"
    
    with c_input1:
        st.markdown("**Option A: Ingest Thermal Frame**")
        uploaded_file = st.file_uploader(
            "Upload drone/handheld thermal capture", 
            type=["jpg", "jpeg", "png"],
            key="img_uploader"
        )
        if uploaded_file:
            selected_img = Image.open(uploaded_file).convert("RGB")
            img_name = uploaded_file.name
            try:
                selected_img.save("/tmp/debug_latest_uploaded.png")
            except Exception:
                pass
            
    with c_input2:
        st.markdown("**Option B: Deploy Tactical Benchmark Presets**")
        p_c1, p_c2, p_c3 = st.columns(3)
        sample_dir = Path("samples")
        
        with p_c1:
            if st.button("🐕 Search K9 Unit", use_container_width=True):
                s_path = sample_dir / "seek_thermal_dog.jpg"
                if s_path.exists():
                    selected_img = Image.open(s_path).convert("RGB")
                    img_name = "seek_thermal_dog.jpg"
                    
        with p_c2:
            if st.button("👥 Collapsed Void Group", use_container_width=True):
                s_path = sample_dir / "seek_thermal_group.jpg"
                if s_path.exists():
                    selected_img = Image.open(s_path).convert("RGB")
                    img_name = "seek_thermal_group.jpg"
                    
        with p_c3:
            if st.button("🚗 Rubble Route Scene", use_container_width=True):
                s_path = sample_dir / "flir_thermal_street.jpg"
                if s_path.exists():
                    selected_img = Image.open(s_path).convert("RGB")
                    img_name = "flir_thermal_street.jpg"

    if selected_img is not None:
        # Pre-process with Rubble Void Enhancer if toggled
        processed_input = apply_thermal_enhancement(selected_img) if enable_clahe else selected_img

        st.markdown("---")
        col_raw, col_detect = st.columns(2)
        
        with col_raw:
            st.markdown(f"**📡 Thermal Sensor Feed (`{img_name}`)**")
            caption_enh = "Thermal View (CLAHE Boost Active)" if enable_clahe else "Raw Thermal Sensor View"
            st.image(processed_input, caption=caption_enh, use_container_width=True)

        # Always run model on clean, authentic sensor imagery (unmodified weights distribution)
        t0 = time.time()
        if is_optical_model:
            results = model.predict(
                source=selected_img,
                conf=confidence,
                iou=iou_thresh,
                classes=[0, 1, 2, 3, 16],
                verbose=False
            )[0]
        else:
            results = model.predict(
                source=selected_img,
                conf=confidence,
                iou=iou_thresh,
                verbose=False
            )[0]
        dt_ms = (time.time() - t0) * 1000

        print(f"=== INFERENCE DEBUG ===", flush=True)
        print(f"Image: {img_name} | Size: {selected_img.size} | Mode: {selected_img.mode}", flush=True)
        print(f"Confidence Slider: {confidence} | IoU: {iou_thresh}", flush=True)
        print(f"Raw Boxes in results: {len(results.boxes) if results.boxes is not None else 0}", flush=True)
        if results.boxes is not None and len(results.boxes) > 0:
            for b in results.boxes:
                raw_cls = int(b.cls[0])
                cname = TARGET_CLASSES.get({0: 0, 1: 1, 2: 1, 3: 1, 16: 2}.get(raw_cls, raw_cls) if is_optical_model else raw_cls)
                print(f"  -> Cls: {raw_cls} ({cname}) | Conf: {float(b.conf[0]):.3f} | Box: {b.xyxy[0].tolist()}", flush=True)
        else:
            test_res = model.predict(source=selected_img, conf=0.01, verbose=False)[0]
            print(f"DEBUG: No boxes at {confidence:.2f}! Top hits at 0.01 threshold: {[f'{test_res.names[int(b.cls[0])]}: {float(b.conf[0]):.3f}' for b in test_res.boxes[:5]]}", flush=True)
        print(f"=======================", flush=True)

        annotated_bgr = results.plot()
        annotated_rgb = annotated_bgr[:, :, ::-1]

        with col_detect:
            st.markdown(f"**🔍 AI Tactical Target Overlay (`{dt_ms:.1f}ms`)**")
            st.image(annotated_rgb, caption=f"Inference Engine: {selected_model_name}", use_container_width=True)

        # Parse Detections
        detections = []
        crops = []
        counts = {"Person": 0, "Obstacle / Vehicle": 0, "Dog": 0}
        orig_np = np.array(processed_input)
        
        if results.boxes is not None:
            for idx, box in enumerate(results.boxes):
                raw_cid = int(box.cls[0].item())
                if is_optical_model:
                    coco_to_usar = {0: 0, 1: 1, 2: 1, 3: 1, 16: 2}
                    if raw_cid not in coco_to_usar:
                        continue
                    cid = coco_to_usar[raw_cid]
                else:
                    cid = raw_cid
                score = float(box.conf[0].item())
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                cname = TARGET_CLASSES.get(cid, f"Class {cid}")
                if cname in counts:
                    counts[cname] += 1
                elif cname == "Car" and "Obstacle / Vehicle" in counts:
                    counts["Obstacle / Vehicle"] += 1
                
                # Extract crop thumbnail
                ix1, iy1, ix2, iy2 = max(0, int(x1)), max(0, int(y1)), min(orig_np.shape[1], int(x2)), min(orig_np.shape[0], int(y2))
                if ix2 > ix1 and iy2 > iy1:
                    crop = orig_np[iy1:iy2, ix1:ix2]
                    crops.append((cname, score, crop, (ix1, iy1, ix2, iy2)))

                detections.append({
                    "Target ID": f"TRG-{idx+1:02d}",
                    "Category": cname,
                    "Confidence": f"{score:.1%}",
                    "Confidence_Score": score,
                    "Sector Box [X1,Y1,X2,Y2]": f"[{int(x1)}, {int(y1)}, {int(x2)}, {int(y2)}]",
                    "Width (px)": int(x2 - x1),
                    "Height (px)": int(y2 - y1),
                    "Grid Center": f"({int((x1+x2)/2)}, {int((y1+y2)/2)})",
                    "Center_X": (x1 + x2) / 2,
                    "Center_Y": (y1 + y2) / 2
                })

        # Update session state for dispatch tab
        st.session_state.latest_detections = detections
        st.session_state.latest_source = img_name
        st.session_state.latest_crops = crops

        # ---------------- EARTHQUAKE TRIAGE ASSESSMENT ----------------
        st.markdown("""
        <div class="metric-grid">
            <div class="tactical-card card-victim">
                <div class="card-label">🔴 Trapped Survivors (People)</div>
                <div class="card-value val-victim">{}</div>
                <div style="font-size: 0.75rem; color: #8b949e;">Immediate extraction target</div>
            </div>
            <div class="tactical-card card-k9">
                <div class="card-label">🐕 Search & Rescue K9s</div>
                <div class="card-value val-k9">{}</div>
                <div style="font-size: 0.75rem; color: #8b949e;">Active canine search teams</div>
            </div>
            <div class="tactical-card card-vehicle">
                <div class="card-label">🚗 Evacuation / Obstacles</div>
                <div class="card-value val-vehicle">{}</div>
                <div style="font-size: 0.75rem; color: #8b949e;">Road clearance assessment</div>
            </div>
            <div class="tactical-card card-total">
                <div class="card-label">🟢 Total Thermal Signatures</div>
                <div class="card-value val-total">{}</div>
                <div style="font-size: 0.75rem; color: #8b949e;">Latency: {:.1f} ms</div>
            </div>
        </div>
        """.format(counts["Person"], counts["Dog"], counts.get("Obstacle / Vehicle", counts.get("Car", 0)), len(detections), dt_ms), unsafe_allow_html=True)

        # Tactical Alert Evaluation
        people_boxes = [d for d in detections if d["Category"] == "Person"]
        dog_boxes = [d for d in detections if d["Category"] == "Dog"]
        obs_count = counts.get("Obstacle / Vehicle", counts.get("Car", 0))

        # Check for multi-victim cluster in rubble
        multi_victim = False
        if len(people_boxes) >= 2:
            for i in range(len(people_boxes)):
                for j in range(i+1, len(people_boxes)):
                    dist = np.hypot(people_boxes[i]["Center_X"] - people_boxes[j]["Center_X"],
                                    people_boxes[i]["Center_Y"] - people_boxes[j]["Center_Y"])
                    if dist < 220:
                        multi_victim = True
                        break

        if multi_victim:
            st.markdown("""
            <div class="alert-box alert-critical">
                <strong>🚨 CRITICAL USAR TRIAGE ALERT: HIGH-DENSITY COLLAPSED VOID DETECTED!</strong><br>
                Multiple thermal signatures confirmed in tight structural proximity (&lt;220px). High probability of residents trapped in common room/slab collapse. Dispatch Heavy Rescue Void Shoring team immediately.
            </div>
            """, unsafe_allow_html=True)
        elif len(people_boxes) == 1:
            st.markdown("""
            <div class="alert-box alert-critical">
                <strong>⚠️ PRIORITY 2 ALERT: ISOLATED RESIDENT DETECTED</strong><br>
                Single heat signature detected. Dispatch technical search camera & acoustic listening team to establish contact.
            </div>
            """, unsafe_allow_html=True)

        if dog_boxes and people_boxes:
            st.markdown("""
            <div class="alert-box alert-k9">
                <strong>🐕 ACTIVE K9 OPERATIONS IN SECTOR:</strong> SAR Dog handler team identified operating in this reconnaissance grid.
            </div>
            """, unsafe_allow_html=True)

        # ---------------- RESIDENTIAL SOCIETY SPECIALIZED SAFETY AUDIT ----------------
        is_thermal_hazard, hot_px = check_thermal_hazards(orig_np) if not is_optical_model else (False, 0)
        gate_blocked = obs_count > 0

        if gate_blocked:
            st.markdown(f"""
            <div class="alert-box alert-critical">
                <strong>🚨 CRITICAL ACCESS OBSTACLE: {main_gate_name} & PERIMETER FIRE LANE BLOCKED!</strong><br>
                {obs_count} vehicle(s)/two-wheeler(s) detected obstructing <strong>{main_gate_name}</strong> or internal driveways. Ingress for Fire Brigade ladder trucks & ambulances is obstructed. Dispatch RWA security immediately to tow/clear access.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="alert-box alert-k9" style="border-left: 4px solid #2ea043; background: rgba(46, 160, 67, 0.12);">
                <strong>🟢 SOCIETY ACCESS GATE ({main_gate_name}): CLEAR</strong><br>
                Perimeter fire lane and primary entrance are clear. Unobstructed ingress confirmed for emergency ambulances and heavy rescue vehicles.
            </div>
            """, unsafe_allow_html=True)

        if is_thermal_hazard:
            st.markdown("""
            <div class="alert-box alert-critical">
                <strong>🔥 SECONDARY UTILITY HAZARD: HIGH-HEAT ANOMALY DETECTED (&gt;300°C)!</strong><br>
                Extreme thermal pixel saturation detected in utility sector. High risk of electrical transformer explosion or ruptured piped gas (PNG/LPG) line. Evacuate adjacent towers and isolate main gas valves before entry.
            </div>
            """, unsafe_allow_html=True)

        # One-Click PDF Report & RWA WhatsApp Broadcast Actions
        st.markdown("---")
        act_c1, act_c2 = st.columns([1, 1])
        with act_c1:
            pdf_bytes = generate_society_pdf_report(
                society_name=society_name,
                safe_zone=safe_assembly_point,
                gate_name=main_gate_name,
                model_name=selected_model_name,
                counts={"Person": counts["Person"], "Dog": counts["Dog"], "Car": obs_count},
                gate_blocked=gate_blocked,
                thermal_hazard=is_thermal_hazard,
                detections=detections
            )
            st.download_button(
                label="📄 Download Official Society USAR Incident Report (PDF)",
                data=pdf_bytes,
                file_name=f"USAR_Report_{society_name.replace(' ', '_')}_{int(time.time())}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        with act_c2:
            with st.popover("📢 Generate RWA WhatsApp / SMS Emergency Notice"):
                broadcast_txt = f"""🚨 *URGENT RWA EARTHQUAKE DIRECTIVE* 🚨
*Complex:* {society_name} | *Time:* {time.strftime('%Y-%m-%d %H:%M:%S')}
*Reconnaissance System:* USAR-AI Aerial Drone Sweep

━━━━━━━━━━━━━━━━━━━━━
📊 *SOCIETY SITUATION REPORT:*
• Confirmed Trapped Residents: *{counts['Person']}*
• Main Access Gate ({main_gate_name}): *{'🔴 BLOCKED (Towing Required)' if gate_blocked else '🟢 CLEAR'}*
• Utility Corridors (Gas/DG): *{'🔥 HIGH HEAT / FIRE HAZARD' if is_thermal_hazard else '🟢 NORMAL'}*
• Active Search K9 Teams: *{counts['Dog']}*

━━━━━━━━━━━━━━━━━━━━━
⚠️ *DIRECTIVES FOR ALL RESIDENTS:*
1. 🏃 Do NOT use elevators under any circumstances. Use external stairwells.
2. 🌳 Proceed immediately to designated Safe Zone: *{safe_assembly_point}*.
3. 🚗 Keep internal society ring-roads CLEAR for fire engines and ambulances.
4. 🛑 Stay away from electrical transformer yard and gas line manifolds.
━━━━━━━━━━━━━━━━━━━━━
_Issued by Disaster Management Taskforce // {society_name}_"""
                st.code(broadcast_txt, language="markdown")

        # ---------------- THERMAL CROPS GALLERY ----------------
        if crops:
            with st.expander(f"🎯 Confirmed Thermal Signature Thumbnails ({len(crops)} Targets Extracted)", expanded=True):
                cols = st.columns(min(len(crops), 6))
                for i, (cname, conf, crop_arr, bbox) in enumerate(crops[:12]):
                    with cols[i % len(cols)]:
                        st.image(crop_arr, caption=f"{cname} ({conf:.0%})", use_container_width=True)

# =======================================================
# TAB 2: AERIAL DRONE VIDEO RECON
# =======================================================
with tab_video:
    st.markdown("#### 🎥 Drone Video Surveillance & Search Grid")
    st.caption("Inspect aerial drone flights frame-by-frame with persistent multi-object tracking and noise suppression.")

    v_c1, v_c2 = st.columns([1, 1])
    
    with v_c1:
        st.markdown("**Option A: Ingest Drone Flight Video**")
        uploaded_video = st.file_uploader("Upload flight recording (.mp4, .avi, .mov)", type=["mp4", "avi", "mov"], key="vid_uploader")
        if uploaded_video:
            tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            tfile.write(uploaded_video.read())
            st.session_state["active_video_path"] = tfile.name

    with v_c2:
        st.markdown("**Option B: Deploy Tactical Benchmark Video Presets**")
        demo_drone = Path("samples/drone_recon_demo.mp4")
        demo_ped = Path("samples/pedestrians_thermal_recon.mp4")
        
        b_c1, b_c2 = st.columns(2)
        with b_c1:
            if demo_drone.exists():
                if st.button("🚁 Preset 1: Aerial FLIR Recon", use_container_width=True):
                    st.session_state["active_video_path"] = str(demo_drone)
        with b_c2:
            if demo_ped.exists():
                if st.button("🚶 Preset 2: Night IR Pedestrians", use_container_width=True):
                    st.session_state["active_video_path"] = str(demo_ped)

    video_source_path = st.session_state.get("active_video_path", None)

    # Video controls
    v_ctrl1, v_ctrl2 = st.columns([1, 1])
    with v_ctrl1:
        vid_conf = st.slider(
            "Video Detection Confidence Threshold",
            min_value=0.15,
            max_value=0.85,
            value=0.35,
            step=0.05,
            help="Higher threshold (0.35+) filters out low-confidence sensor noise and walking leg artifacts."
        )
    with v_ctrl2:
        mission_tracking_mode = st.radio(
            "Mission Target Focus",
            options=[
                "👥 Human Survivors Only (Recommended - Zero Animal False Positives)",
                "🐕 Complete SAR Grid (Humans + Rescue K9s + Vehicles)"
            ],
            index=0,
            help="Select 'Human Survivors Only' when inspecting disaster zones without working K9 teams to completely eliminate false dog detections."
        )
        if "Human Survivors Only" in mission_tracking_mode:
            track_classes = [0]
        else:
            track_classes = [0, 1, 2]

    if video_source_path:
        st.markdown("---")
        cap = cv2.VideoCapture(video_source_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        st.info(f"Loaded: `{Path(video_source_path).name}` | Total Frames: {total_frames} | Native FPS: {fps:.1f}")

        if not is_optical_model:
            chk_cap = cv2.VideoCapture(video_source_path)
            c_ret, c_frame = chk_cap.read()
            chk_cap.release()
            if c_ret:
                hsv = cv2.cvtColor(c_frame, cv2.COLOR_BGR2HSV)
                if hsv[:, :, 1].mean() > 22.0:
                    st.warning("☀️ **Visible-Light Daylight Video Detected**: This footage has standard color saturation (optical RGB). Our primary thermal models specialize in infrared heat radiation (night/dust/rubble). For daylight optical video, select **'☀️ Daylight Optical Recon Mode (RGB / Visible Light)'** in the sidebar!")

        start_btn = st.button("▶️ Begin AI Drone Video Reconnaissance & Tracking", type="primary")
        
        if start_btn:
            frame_window = st.image([])
            progress_bar = st.progress(0)
            
            # Live Metrics HUD
            m_col1, m_col2, m_col3, m_col4 = st.columns(4)
            metric_curr_people = m_col1.empty()
            metric_total_people = m_col2.empty()
            metric_k9 = m_col3.empty()
            metric_veh = m_col4.empty()

            from collections import Counter

            # Robust Centroid Tracker with Temporal Confirmation and Majority Voting
            class RobustVideoTracker:
                def __init__(self, max_disappeared=20, max_dist=75, min_hits=4):
                    self.next_id = 1
                    self.tracks = {}  # tid -> dict
                    self.max_disappeared = max_disappeared
                    self.max_dist = max_dist
                    self.min_hits = min_hits

                def update(self, detections):
                    # detections: list of (cx, cy, cid, conf, [x1,y1,x2,y2])
                    if not detections:
                        for tid in list(self.tracks.keys()):
                            self.tracks[tid]['disappeared'] += 1
                            if self.tracks[tid]['disappeared'] > self.max_disappeared:
                                del self.tracks[tid]
                        return self.get_active()

                    if not self.tracks:
                        for d in detections:
                            v = Counter()
                            v[d[2]] += 1
                            self.tracks[self.next_id] = {
                                'tid': self.next_id,
                                'centroid': (d[0], d[1]),
                                'votes': v,
                                'conf': d[3],
                                'disappeared': 0,
                                'hits': 1,
                                'bbox': d[4]
                            }
                            self.next_id += 1
                        return self.get_active()

                    tids = list(self.tracks.keys())
                    track_pts = np.array([self.tracks[t]['centroid'] for t in tids])
                    det_pts = np.array([[d[0], d[1]] for d in detections])

                    dists = np.linalg.norm(track_pts[:, None] - det_pts[None, :], axis=2)
                    matched_tracks = set()
                    matched_dets = set()

                    for _ in range(min(len(tids), len(detections))):
                        r, c = np.unravel_index(np.argmin(dists), dists.shape)
                        if dists[r, c] > self.max_dist: break
                        tid = tids[r]
                        self.tracks[tid]['centroid'] = (detections[c][0], detections[c][1])
                        self.tracks[tid]['votes'][detections[c][2]] += 1
                        self.tracks[tid]['conf'] = detections[c][3]
                        self.tracks[tid]['bbox'] = detections[c][4]
                        self.tracks[tid]['disappeared'] = 0
                        self.tracks[tid]['hits'] += 1

                        matched_tracks.add(r)
                        matched_dets.add(c)
                        dists[r, :] = 1e5
                        dists[:, c] = 1e5

                    for r, tid in enumerate(tids):
                        if r not in matched_tracks:
                            self.tracks[tid]['disappeared'] += 1
                            if self.tracks[tid]['disappeared'] > self.max_disappeared:
                                del self.tracks[tid]

                    for c, d in enumerate(detections):
                        if c not in matched_dets:
                            v = Counter()
                            v[d[2]] += 1
                            self.tracks[self.next_id] = {
                                'tid': self.next_id,
                                'centroid': (d[0], d[1]),
                                'votes': v,
                                'conf': d[3],
                                'disappeared': 0,
                                'hits': 1,
                                'bbox': d[4]
                            }
                            self.next_id += 1

                    return self.get_active()

                def get_active(self):
                    active = []
                    for tid, t in self.tracks.items():
                        if t['hits'] >= self.min_hits:
                            majority_cls = t['votes'].most_common(1)[0][0]
                            active.append({
                                'tid': tid,
                                'cls': majority_cls,
                                'conf': t['conf'],
                                'bbox': t['bbox']
                            })
                    return active

                def get_unique_counts(self):
                    counts = {0: 0, 1: 0, 2: 0}
                    for tid, t in self.tracks.items():
                        if t['hits'] >= self.min_hits:
                            majority_cls = t['votes'].most_common(1)[0][0]
                            if majority_cls in counts:
                                counts[majority_cls] += 1
                    return counts

            tracker = RobustVideoTracker(min_hits=4)
            frame_idx = 0
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_idx += 1
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Inference on clean sensor frame
                if is_optical_model:
                    coco_classes = [0] if "Human Survivors Only" in mission_tracking_mode else [0, 1, 2, 3, 16]
                    res = model.predict(
                        source=frame_rgb,
                        conf=vid_conf,
                        iou=iou_thresh,
                        classes=coco_classes,
                        verbose=False
                    )[0]
                else:
                    res = model.predict(
                        source=frame_rgb,
                        conf=vid_conf,
                        iou=iou_thresh,
                        classes=track_classes if track_classes else None,
                        verbose=False
                    )[0]
                
                raw_dets = []
                if res.boxes is not None:
                    for b in res.boxes:
                        raw_cid = int(b.cls[0].item())
                        if is_optical_model:
                            coco_to_usar = {0: 0, 1: 1, 2: 1, 3: 1, 16: 2}
                            if raw_cid not in coco_to_usar:
                                continue
                            cid = coco_to_usar[raw_cid]
                        else:
                            cid = raw_cid
                        score = float(b.conf[0].item())
                        x1, y1, x2, y2 = b.xyxy[0].tolist()
                        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
                        raw_dets.append((cx, cy, cid, score, [int(x1), int(y1), int(x2), int(y2)]))

                # Update temporal tracker (filters out 1-frame glitches with majority vote)
                active_tracks = tracker.update(raw_dets)

                # Draw persistent tracks on frame
                draw_img = frame_rgb.copy()
                curr_people = 0
                curr_dogs = 0
                curr_cars = 0

                for t in active_tracks:
                    cid = t['cls']
                    tid = t['tid']
                    conf_val = t['conf']
                    bx1, by1, bx2, by2 = t['bbox']
                    
                    if cid == 0:
                        curr_people += 1
                        color = (255, 51, 102)   # Red
                        label = f"Survivor #{tid} ({conf_val:.0%})"
                    elif cid == 1:
                        curr_cars += 1
                        color = (255, 209, 102)  # Amber
                        label = f"Obstacle #{tid} ({conf_val:.0%})"
                    else:
                        curr_dogs += 1
                        color = (0, 240, 255)    # Cyan
                        label = f"K9 #{tid} ({conf_val:.0%})"

                    cv2.rectangle(draw_img, (bx1, by1), (bx2, by2), color, 2)
                    cv2.putText(draw_img, label, (bx1, max(15, by1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

                frame_window.image(draw_img, caption=f"Recon Scan — Frame {frame_idx}/{total_frames}", use_container_width=True)
                progress_bar.progress(min(1.0, frame_idx / max(1, total_frames)))

                # Update Live HUD with confirmed unique counts
                unique_counts = tracker.get_unique_counts()
                metric_curr_people.metric("🔴 In Current Frame", f"{curr_people} Survivors")
                metric_total_people.metric("📍 Total Unique Survivors", f"{unique_counts[0]} People")
                metric_k9.metric("🐕 Confirmed K9s", f"{unique_counts[2]} Dogs")
                metric_veh.metric("🚗 Confirmed Vehicles", f"{unique_counts[1]} Obstacles")

            cap.release()
            final_counts = tracker.get_unique_counts()
            st.success(f"✅ Drone Aerial Reconnaissance Complete! Found {final_counts[0]} unique survivor(s), {final_counts[1]} obstacle(s) across {total_frames} frames.")

            # Action buttons for video recon
            v_act1, v_act2 = st.columns(2)
            with v_act1:
                v_pdf = generate_society_pdf_report(
                    society_name=society_name,
                    safe_zone=safe_assembly_point,
                    gate_name=main_gate_name,
                    model_name=selected_model_name,
                    counts={"Person": final_counts[0], "Dog": final_counts[2], "Car": final_counts[1]},
                    gate_blocked=final_counts[1] > 0,
                    thermal_hazard=False,
                    detections=[]
                )
                st.download_button(
                    label="📄 Download Flight Mission Incident Report (PDF)",
                    data=v_pdf,
                    file_name=f"Flight_Report_{society_name.replace(' ', '_')}_{int(time.time())}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            with v_act2:
                with st.popover("📢 Generate RWA WhatsApp Broadcast"):
                    v_broadcast = f"""🚨 *URGENT RWA EARTHQUAKE DIRECTIVE* 🚨
*Complex:* {society_name} | *Time:* {time.strftime('%Y-%m-%d %H:%M:%S')}
*Reconnaissance System:* Drone Video Flight Recon ({total_frames} frames scanned)

━━━━━━━━━━━━━━━━━━━━━
📊 *SOCIETY SITUATION REPORT:*
• Unique Survivors Tracked: *{final_counts[0]}*
• Main Access Gate ({main_gate_name}): *{'🔴 BLOCKED (Towing Required)' if final_counts[1] > 0 else '🟢 CLEAR'}*
• Active Search K9 Teams: *{final_counts[2]}*

━━━━━━━━━━━━━━━━━━━━━
⚠️ *DIRECTIVES FOR ALL RESIDENTS:*
1. 🏃 Do NOT use elevators. Use external emergency stairwells.
2. 🌳 Proceed immediately to designated Safe Zone: *{safe_assembly_point}*.
3. 🚗 Keep internal society driveways CLEAR for fire engines and ambulances.
━━━━━━━━━━━━━━━━━━━━━
_Issued by Disaster Management Taskforce // {society_name}_"""
                    st.code(v_broadcast, language="markdown")

# =======================================================
# TAB 3: USAR TACTICAL DISPATCH & TRIAGE
# =======================================================
with tab_dispatch:
    st.markdown(f"#### 📋 {society_name} // Incident Command & RWA Dispatch")
    st.caption("Coordinate residential tower evacuations, gate clearance, medical triage, and multi-agency response.")

    current_dets = st.session_state.latest_detections
    
    # Society Overview KPI Cards
    soc_c1, soc_c2, soc_c3 = st.columns(3)
    soc_c1.info(f"**Housing Society:**\n{society_name}")
    soc_c2.success(f"**Designated Safe Assembly Point:**\n{safe_assembly_point}")
    soc_c3.warning(f"**Primary Access Point:**\n{main_gate_name}")

    if current_dets:
        df = pd.DataFrame(current_dets)
        
        col_d1, col_d2 = st.columns([2, 1])
        
        with col_d1:
            st.markdown(f"**Active Target Reconnaissance Log (`{st.session_state.latest_source}`)**")
            display_cols = ["Target ID", "Category", "Confidence", "Sector Box [X1,Y1,X2,Y2]", "Grid Center"]
            st.dataframe(df[display_cols], use_container_width=True)

        with col_d2:
            st.markdown("**Official Mission Exports**")
            
            # PDF Report Export
            c_p = len([d for d in current_dets if d['Category'] == 'Person'])
            c_d = len([d for d in current_dets if d['Category'] == 'Dog'])
            c_o = len([d for d in current_dets if d['Category'] in ['Obstacle / Vehicle', 'Car']])
            
            pdf_data = generate_society_pdf_report(
                society_name=society_name,
                safe_zone=safe_assembly_point,
                gate_name=main_gate_name,
                model_name=selected_model_name,
                counts={"Person": c_p, "Dog": c_d, "Car": c_o},
                gate_blocked=c_o > 0,
                thermal_hazard=False,
                detections=current_dets
            )
            st.download_button(
                label="📄 Download Official Society USAR Report (PDF)",
                data=pdf_data,
                file_name=f"USAR_Report_{society_name.replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

            csv_bytes = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Tactical Manifest (CSV)",
                data=csv_bytes,
                file_name=f"USAR_DISPATCH_{Path(st.session_state.latest_source).stem}.csv",
                mime="text/csv",
                use_container_width=True
            )
            
            st.markdown(f"""
            **Residential Society Response Checklist:**
            * [ ] **Isolate PNG Gas Mains**: Shut down main manifold valve immediately.
            * [ ] **Transformer Yard**: Verify DG set and transformer room are clear of fire.
            * [ ] **Clear {main_gate_name}**: Tow/push vehicles to allow fire brigade ingress.
            * [ ] **Lawn Headcount**: Account for elderly and children at {safe_assembly_point}.
            * [ ] **Broadcast WhatsApp Alert**: Broadcast emergency directive to society group.
            """)
    else:
        st.info("ℹ️ No active reconnaissance data in session. Ingest a thermal frame in the Recon tab to populate the Tactical Dispatch manifest.")
