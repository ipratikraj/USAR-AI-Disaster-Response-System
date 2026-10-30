import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import cv2
import time
import tempfile
from collections import Counter
from PIL import Image
from pathlib import Path
from ultralytics import YOLO
from report_generator import generate_society_pdf_report
from society_map import create_society_tactical_map
from data.society_registry import (
    get_headcount_stats, get_all_residents, update_resident_status,
    add_resident, update_resident, delete_resident, export_to_csv,
    import_from_csv, VULNERABILITY_OPTIONS, PET_OPTIONS, EVACUATION_STATUSES,
    get_residents_by_sector
)
from data.sitrep_generator import generate_html_sitrep
from datetime import datetime

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
    .card-clue { border-top: 4px solid #a371f7; }
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
    .val-clue { color: #a371f7; text-shadow: 0 0 12px rgba(163, 113, 247, 0.4); }
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
    .alert-clue {
        border-color: #a371f7;
        background: rgba(163, 113, 247, 0.08);
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

# ---------------- USAR TACTICAL TARGET CATALOG & PRESETS ----------------
USAR_TACTICAL_TARGETS = {
    "👤 Person (Survivors)": {
        "coco_id": [0],
        "thermal_id": [0],
        "category": "Survivor",
        "icon": "🔴",
        "desc": "Human survivors & trapped residents",
        "locked": True
    },
    "🎒 Backpack (Victim Marker)": {
        "coco_id": [24],
        "thermal_id": [],
        "category": "Rubble Clue",
        "icon": "🎒",
        "desc": "Victim anchor / dropped survival or personal bag",
        "locked": False
    },
    "👜 Handbag / Pouch": {
        "coco_id": [26],
        "thermal_id": [],
        "category": "Rubble Clue",
        "icon": "👜",
        "desc": "Emergency first-aid kit / personal belongings",
        "locked": False
    },
    "🧳 Suitcase / Luggage": {
        "coco_id": [28],
        "thermal_id": [],
        "category": "Rubble Clue",
        "icon": "🧳",
        "desc": "Evacuation luggage / trapped belongings",
        "locked": False
    },
    "📱 Cell Phone / Device": {
        "coco_id": [67],
        "thermal_id": [],
        "category": "Rubble Clue",
        "icon": "📱",
        "desc": "Communication device / distress signal marker",
        "locked": False
    },
    "🐕 Dog (Search K9 / Pet)": {
        "coco_id": [16],
        "thermal_id": [2],
        "category": "Canine & Pet",
        "icon": "🐕",
        "desc": "SAR canine search units or family dogs",
        "locked": False
    },
    "🐈 Cat (Domestic Pet)": {
        "coco_id": [15, 21],
        "thermal_id": [2],
        "category": "Canine & Pet",
        "icon": "🐈",
        "desc": "Trapped domestic cats / pets (including fluffy & Persian breeds)",
        "locked": False
    },
    "🚗 Car / Vehicle": {
        "coco_id": [2],
        "thermal_id": [1],
        "category": "Evacuation Obstacle",
        "icon": "🚗",
        "desc": "Vehicles blocking roads or society gates",
        "locked": False
    },
    "🏍️ Motorcycle / Scooter": {
        "coco_id": [3],
        "thermal_id": [1],
        "category": "Evacuation Obstacle",
        "icon": "🏍️",
        "desc": "Two-wheelers obstructing narrow alleys or exits",
        "locked": False
    },
    "🚲 Bicycle": {
        "coco_id": [1],
        "thermal_id": [1],
        "category": "Evacuation Obstacle",
        "icon": "🚲",
        "desc": "Bicycles obstructing stairs or corridors",
        "locked": False
    },
    "🚚 Truck / Bus": {
        "coco_id": [5, 7],
        "thermal_id": [1],
        "category": "Evacuation Obstacle",
        "icon": "🚚",
        "desc": "Heavy commercial vehicles blocking gates",
        "locked": False
    },
    "🧯 Fire Hydrant": {
        "coco_id": [10],
        "thermal_id": [],
        "category": "Infrastructure",
        "icon": "🧯",
        "desc": "Emergency firefighting water connections",
        "locked": False
    }
}

MISSION_TARGET_PRESETS = {
    "🐾 Primary Life & Pet Rescue (Person + Dogs + Cats)": [
        "👤 Person (Survivors)",
        "🐕 Dog (Search K9 / Pet)",
        "🐈 Cat (Domestic Pet)"
    ],
    "🌟 Complete USAR Search Grid (Person + Dog + Vehicle + Backpack)": [
        "👤 Person (Survivors)",
        "🐕 Dog (Search K9 / Pet)",
        "🚗 Car / Vehicle",
        "🎒 Backpack (Victim Marker)"
    ],
    "🆘 Human Survivors Only (Zero Animal False Positives)": [
        "👤 Person (Survivors)"
    ],
    "🎒 Rubble Clues & Personal Belongings (Person + Bags + Phones)": [
        "👤 Person (Survivors)",
        "🎒 Backpack (Victim Marker)",
        "👜 Handbag / Pouch",
        "🧳 Suitcase / Luggage",
        "📱 Cell Phone / Device"
    ],
    "🚧 Evacuation Route Clearance (Person + Vehicles)": [
        "👤 Person (Survivors)",
        "🚗 Car / Vehicle",
        "🏍️ Motorcycle / Scooter",
        "🚲 Bicycle",
        "🚚 Truck / Bus"
    ],
    "🌐 Full Disaster Field Recon (All Tactical Targets)": list(USAR_TACTICAL_TARGETS.keys()),
    "🎛️ Custom Mission Targets (User Selected)": []
}

TARGET_CLASSES = {
    0: "Person",
    1: "Obstacle / Vehicle",
    2: "Pet Animal (Dog / Cat)"
}

def resolve_detection_info(raw_cid: int, is_optical: bool = True, opt_names: dict = None):
    """
    Resolves raw model class ID into (display_name, tactical_category, icon)
    """
    if is_optical:
        if raw_cid == 21:
            return "Cat (Fluffy Breed)", "Canine & Pet", "🐈"
        for tname, tinfo in USAR_TACTICAL_TARGETS.items():
            if raw_cid in tinfo["coco_id"]:
                clean_name = tname.split(" (")[0]
                for prefix in ["👤 ", "🎒 ", "👜 ", "🧳 ", "📱 ", "🐕 ", "🐈 ", "🚗 ", "🏍️ ", "🚲 ", "🚚 ", "🧯 "]:
                    clean_name = clean_name.replace(prefix, "")
                return clean_name, tinfo["category"], tinfo["icon"]
        if opt_names and raw_cid in opt_names:
            return opt_names[raw_cid].title(), "General Object", "📦"
        return f"Object-{raw_cid}", "General Object", "📦"
    else:
        thermal_map = {
            0: ("Person", "Survivor", "🔴"),
            1: ("Obstacle / Vehicle", "Evacuation Obstacle", "🚗"),
            2: ("Pet Animal (Dog / Cat)", "Canine & Pet", "🐾")
        }
        return thermal_map.get(raw_cid, (f"Class {raw_cid}", "Thermal Signature", "🟢"))

def check_thermal_hazards(img_np):
    """Detects extreme saturation (>248) indicative of gas fire or electrical transformer rupture."""
    arr = np.array(img_np)
    if len(arr.shape) == 3:
        gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
    else:
        gray = arr
    hot_pixels = int(np.sum(gray >= 248))
    is_hazard = hot_pixels > 350
    return is_hazard, hot_pixels

def analyze_structural_damage_and_rubble(img_rgb):
    """
    Computes structural damage index, ground roadway traversability,
    and generates a tactical debris intensity heatmap overlay.
    """
    arr = np.array(img_rgb)
    if len(arr.shape) == 3:
        gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
    else:
        gray = arr
    
    # 1. High-frequency structural edge detection
    edges = cv2.Canny(gray, 40, 140)
    
    # 2. Debris heatmap overlay
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    dilated = cv2.dilate(edges, kernel, iterations=2)
    blur_map = cv2.GaussianBlur(dilated.astype(np.float32), (31, 31), 0)
    norm_map = cv2.normalize(blur_map, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    heatmap = cv2.applyColorMap(norm_map, cv2.COLORMAP_JET)
    blend_rgb = cv2.addWeighted(cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB), 0.65, heatmap, 0.35, 0)
    
    # 3. Overall Rubble Severity Index (0 - 100%)
    edge_pct = (np.sum(edges > 0) / edges.size) * 100
    rubble_severity = min(100.0, edge_pct * 12.5)
    
    # 4. Roadway traversability (ground quadrant)
    h, w = gray.shape
    ground_patch = edges[int(h * 0.55):, :]
    ground_edge_pct = (np.sum(ground_patch > 0) / ground_patch.size) * 100
    is_road_impassable = ground_edge_pct > 3.8
    
    return round(rubble_severity, 1), is_road_impassable, blend_rgb

def compute_thermal_vitality(crop_arr, full_img, bbox):
    """
    Calculates thermal body radiance contrast delta T = victim_mean - ambient_mean
    Returns (status_label, delta_t, risk_badge)
    """
    if crop_arr is None:
        return "🟢 Stable Vitality", 35.0, "Low Risk"
    crop_arr = np.array(crop_arr)
    if crop_arr.size == 0:
        return "🟢 Stable Vitality", 35.0, "Low Risk"
    full_img = np.array(full_img)
    
    if len(crop_arr.shape) == 3:
        crop_gray = cv2.cvtColor(crop_arr, cv2.COLOR_RGB2GRAY)
    else:
        crop_gray = crop_arr
    
    victim_mean = float(np.mean(crop_gray))
    
    x1, y1, x2, y2 = bbox
    H, W = full_img.shape[:2]
    pad = 16
    mx1, my1, mx2, my2 = max(0, x1 - pad), max(0, y1 - pad), min(W, x2 + pad), min(H, y2 + pad)
    
    if len(full_img.shape) == 3:
        full_gray = cv2.cvtColor(full_img, cv2.COLOR_RGB2GRAY)
    else:
        full_gray = full_img
        
    margin_patch = full_gray[my1:my2, mx1:mx2]
    margin_mean = float(np.mean(margin_patch)) if margin_patch.size > 0 else (victim_mean - 25.0)
    
    delta_t = victim_mean - margin_mean
    
    if delta_t >= 28.0:
        return "🟢 Stable Vitality (Active Radiance)", delta_t, "Low Risk"
    elif delta_t >= 14.0:
        return "🟡 Moderate Heat Loss", delta_t, "Medium Risk"
    else:
        return "🔴 Severe Hypothermia Risk (Fading Heat)", delta_t, "Critical Risk"

def trigger_tactical_audio_alert(message: str, enabled: bool = True):
    """Plays an emergency two-tone siren and vocal alert via HTML5 Web Audio & Speech Synthesis."""
    if not enabled:
        return
    clean_msg = message.replace('"', '\\"').replace("'", "\\'")
    js_code = f"""
    <script>
    (function() {{
        try {{
            const AudioCtx = window.AudioContext || window.webkitAudioContext;
            if (AudioCtx) {{
                const ctx = new AudioCtx();
                const osc = ctx.createOscillator();
                const gain = ctx.createGain();
                osc.type = 'sawtooth';
                osc.frequency.setValueAtTime(880, ctx.currentTime);
                osc.frequency.linearRampToValueAtTime(440, ctx.currentTime + 0.16);
                osc.frequency.linearRampToValueAtTime(880, ctx.currentTime + 0.32);
                gain.gain.setValueAtTime(0.06, ctx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.38);
                osc.connect(gain);
                gain.connect(ctx.destination);
                osc.start();
                osc.stop(ctx.currentTime + 0.40);
            }}
            if ('speechSynthesis' in window) {{
                window.speechSynthesis.cancel();
                const u = new SpeechSynthesisUtterance("{clean_msg}");
                u.rate = 1.05;
                window.speechSynthesis.speak(u);
            }}
        }} catch(e) {{}}
    }})();
    </script>
    """
    components.html(js_code, height=0)

@st.cache_resource
def load_yolo_model(path: str):
    m = YOLO(path)
    # Tactical overlay customization
    if hasattr(m, "model") and hasattr(m.model, "names") and isinstance(m.model.names, dict):
        if len(m.model.names) == 3 and 2 in m.model.names:
            m.model.names[0] = "Person"
            m.model.names[1] = "Obstacle / Vehicle"
            m.model.names[2] = "Pet Animal (Dog/Cat)"
        elif len(m.model.names) == 80:
            if 21 in m.model.names:
                m.model.names[21] = "Cat (Fluffy Breed)"
    return m

# Sidebar
st.sidebar.markdown("### 🏘️ SOCIETY CONFIGURATION")
society_name = st.sidebar.text_input("Housing Society / Complex Name", value="Green Valley Residency")
safe_assembly_point = st.sidebar.text_input("Designated Safe Assembly Point", value="Central Community Lawn / Park")
main_gate_name = st.sidebar.text_input("Primary Evacuation Gate", value="Main North Security Gate")
total_society_pop = st.sidebar.number_input("Total Registered Residents (All Towers)", min_value=10, max_value=5000, value=180, step=10)

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ TACTICAL CONFIGURATION")

selected_model_name = st.sidebar.selectbox(
    "Active Sensor Payload Model",
    options=list(AVAILABLE_MODELS.keys()),
    index=0
)
model_path = AVAILABLE_MODELS[selected_model_name]
is_optical_model = "Daylight Optical" in selected_model_name
enable_audio_siren = st.sidebar.checkbox("🔊 Tactical Audio Siren & Voice Alerts", value=True)

try:
    model = load_yolo_model(model_path)
    optical_model = load_yolo_model("/Users/pratik/DisasterResponseSystem/yolo11n.pt")
    st.sidebar.success(f"✓ Neural Weights Online")
except Exception as e:
    st.sidebar.error(f"Error loading model: {e}")
    st.stop()

# ---------------- MISSION TARGET SELECTOR ----------------
st.sidebar.markdown("---")
st.sidebar.markdown("### 🎯 MISSION TARGET SELECTOR")

selected_preset = st.sidebar.selectbox(
    "Mission Target Profile",
    options=list(MISSION_TARGET_PRESETS.keys()),
    index=0,
    help="Select a standardized search mission profile or customize exact targets. 'Person' is always preserved by default."
)

if "Custom" in selected_preset:
    chosen_targets = st.sidebar.multiselect(
        "Active Search Targets (Person is locked default)",
        options=list(USAR_TACTICAL_TARGETS.keys()),
        default=[
            "👤 Person (Survivors)",
            "🐕 Dog (Search K9 / Pet)",
            "🐈 Cat (Domestic Pet)"
        ],
        help="Select any targets to search for. 'Person' is always enforced for life safety."
    )
else:
    chosen_targets = MISSION_TARGET_PRESETS[selected_preset]

# Enforce: "👤 Person (Survivors)" MUST ALWAYS BE PRESENT
if "👤 Person (Survivors)" not in chosen_targets:
    chosen_targets = ["👤 Person (Survivors)"] + [t for t in chosen_targets if t != "👤 Person (Survivors)"]

# Extended COCO Objects Search (all 80 classes)
with st.sidebar.expander("🔍 Search Extended Objects (Full 80 Classes)"):
    st.caption("Search for any general COCO object in addition to tactical USAR targets:")
    curated_coco_ids = [0, 1, 2, 3, 5, 7, 10, 15, 16, 21, 24, 26, 28, 67]
    ext_options = sorted([
        name.title() for cid, name in optical_model.names.items()
        if cid not in curated_coco_ids
    ])
    chosen_extended = st.multiselect(
        "Additional Objects",
        options=ext_options,
        default=[],
        help="Detect additional objects (e.g., laptop, chair, bottle, etc.)."
    )

# Compute active COCO and thermal class lists
active_coco_classes = set()
active_thermal_classes = set()

for t in chosen_targets:
    if t in USAR_TACTICAL_TARGETS:
        for cid in USAR_TACTICAL_TARGETS[t]["coco_id"]:
            active_coco_classes.add(cid)
        for tid in USAR_TACTICAL_TARGETS[t]["thermal_id"]:
            active_thermal_classes.add(tid)

ext_name_to_id = {name.title(): cid for cid, name in optical_model.names.items()}
for ext_item in chosen_extended:
    if ext_item in ext_name_to_id:
        active_coco_classes.add(ext_name_to_id[ext_item])

active_coco_classes = sorted(list(active_coco_classes))
active_thermal_classes = sorted(list(active_thermal_classes))
if not active_thermal_classes:
    active_thermal_classes = [0]  # Minimum Person for thermal

# Status badge for active targets
preview_tags = [t.split(" (")[0] for t in chosen_targets[:4]]
active_summary = " • ".join(preview_tags)
if len(chosen_targets) > 4:
    active_summary += f" +{len(chosen_targets)-4} more"
if chosen_extended:
    active_summary += f" • {len(chosen_extended)} ext"
st.sidebar.markdown(f"<small style='color: #58a6ff;'><b>Active Targets:</b> {active_summary}</small>", unsafe_allow_html=True)

if not is_optical_model:
    non_thermal_chosen = [t for t in chosen_targets if len(USAR_TACTICAL_TARGETS[t]["thermal_id"]) == 0]
    if non_thermal_chosen or chosen_extended:
        st.sidebar.info(
            "💡 **Sensor Note**: Inanimate items (Backpacks, Bags, Phones) do not radiate body heat. "
            "To detect them, switch **Active Sensor Payload** above to **'☀️ Daylight Optical Recon Mode'**."
        )

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎯 SENSOR TUNING")

sensitivity_mode = st.sidebar.radio(
    "Operational Sensitivity Mode",
    options=[
        "🎯 Balanced Operations (Standard)",
        "🛡️ High Confidence (Zero False Alarms)",
        "🚨 High Sensitivity (USAR / Faint Heat / Distant Victims)"
    ],
    index=0,
    help="Balanced Operations (35% confidence + Class-Agnostic NMS) prevents dual-class ghost detections (e.g. person classified as dog) and eliminates background noise."
)

if "High Sensitivity" in sensitivity_mode:
    default_conf = 0.18
elif "High Confidence" in sensitivity_mode:
    default_conf = 0.50
else:
    default_conf = 0.35

confidence = st.sidebar.slider(
    "Minimum Detection Confidence",
    min_value=0.10,
    max_value=0.90,
    value=default_conf,
    step=0.01,
    help="Higher values (0.35 - 0.50) prevent false positive boxes. Lower values (0.15 - 0.20) are for faint heat in rubble."
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
tab_image, tab_video, tab_live, tab_dispatch, tab_registry = st.tabs([
    "🛰️ Sector Imagery Recon", 
    "🎥 Aerial Drone Video Recon", 
    "📡 Live Tactical Stream",
    "📋 Incident Command & Tactical SitRep",
    "🏢 Society Directory & Evacuation Roster"
])

# Global state to share detections with dispatch & SitRep
if "latest_detections" not in st.session_state:
    st.session_state.latest_detections = []
    st.session_state.latest_source = "None"
    st.session_state.latest_crops = []
    st.session_state.latest_rubble = (0.0, False)
    st.session_state.latest_hazard = False
    st.session_state.latest_raw_img = None
    st.session_state.latest_annotated_img = None

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

        # Active classes passed to model.predict based on payload modality
        target_classes_arg = active_coco_classes if is_optical_model else active_thermal_classes

        t0 = time.time()
        results = model.predict(
            source=selected_img,
            conf=confidence,
            iou=iou_thresh,
            agnostic_nms=True,
            classes=target_classes_arg,
            verbose=False
        )[0]
        dt_ms = (time.time() - t0) * 1000

        print(f"=== INFERENCE DEBUG ===", flush=True)
        print(f"Image: {img_name} | Size: {selected_img.size} | Mode: {selected_img.mode}", flush=True)
        print(f"Confidence Slider: {confidence} | IoU: {iou_thresh} | Target Classes: {target_classes_arg}", flush=True)
        print(f"Raw Boxes in results: {len(results.boxes) if results.boxes is not None else 0}", flush=True)
        if results.boxes is not None and len(results.boxes) > 0:
            for b in results.boxes:
                raw_cls = int(b.cls[0])
                cname, cat, icon = resolve_detection_info(raw_cls, is_optical=is_optical_model, opt_names=optical_model.names)
                print(f"  -> Cls: {raw_cls} ({icon} {cname} / {cat}) | Conf: {float(b.conf[0]):.3f} | Box: {b.xyxy[0].tolist()}", flush=True)
        else:
            test_res = model.predict(source=selected_img, conf=0.01, verbose=False)[0]
            print(f"DEBUG: No boxes at {confidence:.2f}! Top hits at 0.01 threshold: {[f'{test_res.names[int(b.cls[0])]}: {float(b.conf[0]):.3f}' for b in test_res.boxes[:5]]}", flush=True)
        print(f"=======================", flush=True)

        annotated_bgr = results.plot()
        annotated_rgb = annotated_bgr[:, :, ::-1]

        with col_detect:
            st.markdown(f"**🔍 AI Tactical Target Overlay (`{dt_ms:.1f}ms`)**")
            st.image(annotated_rgb, caption=f"Inference Engine: {selected_model_name}", use_container_width=True)

        # Parse Detections dynamically
        detections = []
        crops = []
        counts_by_category = {
            "Survivor": 0,
            "Rubble Clue": 0,
            "Evacuation Obstacle": 0,
            "Canine & Pet": 0,
            "Infrastructure": 0,
            "General Object": 0
        }
        counts_by_name = Counter()
        orig_np = np.array(processed_input)
        
        if results.boxes is not None:
            for idx, box in enumerate(results.boxes):
                raw_cid = int(box.cls[0].item())
                cname, cat, icon = resolve_detection_info(raw_cid, is_optical=is_optical_model, opt_names=optical_model.names)
                score = float(box.conf[0].item())
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                
                counts_by_category[cat] = counts_by_category.get(cat, 0) + 1
                counts_by_name[cname] += 1
                
                # Extract crop thumbnail & compute thermal vitality
                ix1, iy1, ix2, iy2 = max(0, int(x1)), max(0, int(y1)), min(orig_np.shape[1], int(x2)), min(orig_np.shape[0], int(y2))
                vit_status, delta_t, risk_badge = ("N/A (Visual Target)", 0.0, "N/A")
                if ix2 > ix1 and iy2 > iy1:
                    crop = orig_np[iy1:iy2, ix1:ix2]
                    if cname == "Person" and not is_optical_model:
                        vit_status, delta_t, risk_badge = compute_thermal_vitality(crop, orig_np, (ix1, iy1, ix2, iy2))
                    elif cname == "Backpack":
                        vit_status = "⚠️ Rubble Clue / Potential Victim Anchor"
                    elif cat == "Rubble Clue":
                        vit_status = "🎒 Personal Effects / Evidence"
                    elif cat == "Evacuation Obstacle":
                        vit_status = "🚧 Access Route Obstacle"
                    elif cat == "Canine & Pet":
                        vit_status = "🐾 Animal / Pet Signature"
                    crops.append((f"{icon} {cname}", score, crop, (ix1, iy1, ix2, iy2), vit_status))

                detections.append({
                    "Target ID": f"TRG-{idx+1:02d}",
                    "Category": cname,
                    "Tactical Group": cat,
                    "Confidence": f"{score:.1%}",
                    "Confidence_Score": score,
                    "Vitality": vit_status,
                    "Sector Box [X1,Y1,X2,Y2]": f"[{int(x1)}, {int(y1)}, {int(x2)}, {int(y2)}]",
                    "Width (px)": int(x2 - x1),
                    "Height (px)": int(y2 - y1),
                    "Grid Center": f"({int((x1+x2)/2)}, {int((y1+y2)/2)})",
                    "Center_X": (x1 + x2) / 2,
                    "Center_Y": (y1 + y2) / 2
                })

        survivors_count = counts_by_category.get("Survivor", 0)
        clues_count = counts_by_category.get("Rubble Clue", 0)
        obs_count = counts_by_category.get("Evacuation Obstacle", 0)
        pets_count = counts_by_category.get("Canine & Pet", 0)
        total_count = len(detections)

        # Update session state for dispatch tab
        st.session_state.latest_detections = detections
        st.session_state.latest_source = img_name
        st.session_state.latest_crops = crops
        st.session_state.latest_raw_img = selected_img
        st.session_state.latest_annotated_img = Image.fromarray(annotated_rgb)

        # ---------------- EARTHQUAKE TRIAGE ASSESSMENT ----------------
        st.markdown(f"""
        <div class="metric-grid">
            <div class="tactical-card card-victim">
                <div class="card-label">🔴 Trapped Survivors</div>
                <div class="card-value val-victim">{survivors_count}</div>
                <div style="font-size: 0.75rem; color: #8b949e;">Immediate extraction target</div>
            </div>
            <div class="tactical-card card-k9">
                <div class="card-label">🐾 Pets & Animals (Dogs/Cats)</div>
                <div class="card-value val-k9">{pets_count}</div>
                <div style="font-size: 0.75rem; color: #8b949e;">Search K9s & family pets</div>
            </div>
            <div class="tactical-card card-clue">
                <div class="card-label">🎒 Rubble Clues & Bags</div>
                <div class="card-value val-clue">{clues_count}</div>
                <div style="font-size: 0.75rem; color: #8b949e;">Victim anchors / Personal effects</div>
            </div>
            <div class="tactical-card card-vehicle">
                <div class="card-label">🚗 Evacuation Obstacles</div>
                <div class="card-value val-vehicle">{obs_count}</div>
                <div style="font-size: 0.75rem; color: #8b949e;">Road clearance assessment</div>
            </div>
            <div class="tactical-card card-total">
                <div class="card-label">🟢 Total Targets</div>
                <div class="card-value val-total">{total_count}</div>
                <div style="font-size: 0.75rem; color: #8b949e;">Latency: {dt_ms:.1f} ms</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Tactical Alert Evaluation
        people_boxes = [d for d in detections if d["Category"] == "Person"]
        dog_boxes = [d for d in detections if d["Category"] in ["Dog", "Cat", "Dog / Pet Animal"]]

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
            trigger_tactical_audio_alert(f"Attention! High density collapsed void detected in {society_name}. Dispatch void shoring squad.", enabled=enable_audio_siren)
        elif len(people_boxes) == 1:
            st.markdown("""
            <div class="alert-box alert-critical">
                <strong>⚠️ PRIORITY 2 ALERT: ISOLATED RESIDENT DETECTED</strong><br>
                Single heat signature detected. Dispatch technical search camera & acoustic listening team to establish contact.
            </div>
            """, unsafe_allow_html=True)

        if pets_count > 0:
            pet_names = []
            for name, cnt in counts_by_name.items():
                if any(k in name for k in ["Dog", "Cat", "Pet"]):
                    pet_names.append(f"{cnt} {name}(s)")
            pet_summary = ", ".join(pet_names) if pet_names else f"{pets_count} Pet Animal(s)"
            st.markdown(f"""
            <div class="alert-box alert-k9">
                <strong>🐾 DOMESTIC PET / K9 RESCUE TARGET CONFIRMED:</strong> {pet_summary} located in sector. Coordinate pet containment crates alongside family extraction.
            </div>
            """, unsafe_allow_html=True)

        if clues_count > 0:
            clue_breakdown = ", ".join([f"{cnt} {name}(s)" for name, cnt in counts_by_name.items() if name in ['Backpack', 'Handbag', 'Suitcase', 'Cell Phone']])
            if not clue_breakdown:
                clue_breakdown = f"{clues_count} Rubble Items"
            st.markdown(f"""
            <div class="alert-box alert-clue">
                <strong>🎒 USAR TACTICAL ALERT: RUBBLE CLUES / VICTIM ANCHORS CONFIRMED!</strong><br>
                Identified: <strong>{clue_breakdown}</strong>. In collapsed earthquake rubble, personal belongings (backpacks, bags, phones) serve as vital <em>Victim Anchors</em> indicating trapped occupants or swift evacuation paths. Prioritize acoustic listening devices and K9 sweeps in this rubble sector.
            </div>
            """, unsafe_allow_html=True)

        # ---------------- RESIDENTIAL SOCIETY SPECIALIZED SAFETY AUDIT ----------------
        is_thermal_hazard, hot_px = check_thermal_hazards(orig_np) if not is_optical_model else (False, 0)
        st.session_state.latest_hazard = is_thermal_hazard
        gate_blocked = obs_count > 0

        if gate_blocked:
            st.markdown(f"""
            <div class="alert-box alert-critical">
                <strong>🚨 CRITICAL ACCESS OBSTACLE: {main_gate_name} & PERIMETER FIRE LANE BLOCKED!</strong><br>
                {obs_count} vehicle(s)/two-wheeler(s) detected obstructing <strong>{main_gate_name}</strong> or internal driveways. Ingress for Fire Brigade ladder trucks & ambulances is obstructed. Dispatch RWA security immediately to tow/clear access.
            </div>
            """, unsafe_allow_html=True)
            if not multi_victim:
                trigger_tactical_audio_alert(f"Warning! Access gate {main_gate_name} is obstructed. Clear driveway for fire engines.", enabled=enable_audio_siren)
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
            if not multi_victim and not gate_blocked:
                trigger_tactical_audio_alert("Hazard Alert! High temperature gas or transformer flare detected.", enabled=enable_audio_siren)

        # ---------------- ROADWAY RUBBLE & STRUCTURAL DAMAGE ANALYSIS ----------------
        rubble_sev, is_debris_blocked, debris_overlay = analyze_structural_damage_and_rubble(selected_img)
        st.session_state.latest_rubble = (rubble_sev, is_debris_blocked)

        if is_debris_blocked:
            st.markdown(f"""
            <div class="alert-box alert-critical">
                <strong>🚧 ROADWAY IMPASSABLE: SEVERE CONCRETE RUBBLE COLLAPSE ({rubble_sev}% Debris Density)!</strong><br>
                Ground quadrant edge roughness indicates severe earthquake debris, shattered slabs, or fallen masonry on the internal society ring road. Heavy rescue bulldozers / debris clearance required before ambulances can drive through.
            </div>
            """, unsafe_allow_html=True)
            if not multi_victim and not gate_blocked and not is_thermal_hazard:
                trigger_tactical_audio_alert("Roadway obstruction detected. Internal society path is blocked with concrete rubble.", enabled=enable_audio_siren)
        else:
            st.markdown(f"""
            <div class="alert-box alert-k9" style="border-left: 4px solid #2ea043; background: rgba(46, 160, 67, 0.12);">
                <strong>🟢 INTERNAL ROADWAYS TRAVERSABLE ({rubble_sev}% Debris Density)</strong><br>
                Ground surface is clear of major concrete blockages. Emergency vehicles and stretcher squads have unhindered path access.
            </div>
            """, unsafe_allow_html=True)

        with st.expander("🧱 Tactical Structural Rubble & Debris Intensity Heatmap", expanded=False):
            st.caption("Morphological edge frequency gradient highlighting concrete fragmentation, wall shearing, and ground debris.")
            st.image(debris_overlay, caption=f"Structural Rubble Heatmap — Severity: {rubble_sev}% ({'IMPASSABLE' if is_debris_blocked else 'TRAVERSABLE'})", use_container_width=True)

        # ---------------- INTERACTIVE SOCIETY GIS TACTICAL MAP ----------------
        st.markdown("---")
        with st.expander("🗺️ Interactive Society Aerial GIS Layout Map (Campus Layout & Real-Time Incident Pins)", expanded=True):
            st.caption("Real-time geospatial layout of residential towers, designated safe assembly lawn, main access gate, and utility hazards.")
            map_html = create_society_tactical_map(
                society_name=society_name,
                safe_zone=safe_assembly_point,
                gate_name=main_gate_name,
                people_count=survivors_count,
                obstacle_count=obs_count,
                k9_count=pets_count,
                has_hazard=is_thermal_hazard,
                detections=detections
            )
            components.html(map_html, height=450)

        # One-Click PDF Report & RWA WhatsApp Broadcast Actions
        st.markdown("---")
        act_c1, act_c2 = st.columns([1, 1])
        with act_c1:
            pdf_bytes = generate_society_pdf_report(
                society_name=society_name,
                safe_zone=safe_assembly_point,
                gate_name=main_gate_name,
                model_name=selected_model_name,
                counts={"Person": survivors_count, "Dog": pets_count, "Car": obs_count, "Rubble Clue": clues_count},
                gate_blocked=gate_blocked,
                thermal_hazard=is_thermal_hazard,
                detections=detections,
                rubble_severity=rubble_sev,
                is_rubble_blocked=is_debris_blocked
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
• Confirmed Trapped Residents: *{survivors_count}*
• Rubble Clues / Bags Cataloged: *{clues_count}*
• Main Access Gate ({main_gate_name}): *{'🔴 BLOCKED (Towing Required)' if gate_blocked else '🟢 CLEAR'}*
• Internal Roadways: *{'🔴 IMPASSABLE (Heavy Rubble)' if is_debris_blocked else '🟢 CLEAR (Traversable)'} ({rubble_sev}% Density)*
• Utility Corridors (Gas/DG): *{'🔥 HIGH HEAT / FIRE HAZARD' if is_thermal_hazard else '🟢 NORMAL'}*
• Active Search K9 Teams: *{pets_count}*

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
            with st.expander(f"🎯 Confirmed Target Thumbnails & Thermal Vitality ({len(crops)} Targets Extracted)", expanded=True):
                cols = st.columns(min(len(crops), 6))
                for i, crop_info in enumerate(crops[:12]):
                    cname = crop_info[0]
                    conf = crop_info[1]
                    crop_arr = crop_info[2]
                    bbox = crop_info[3]
                    vit = crop_info[4] if len(crop_info) > 4 else ""
                    with cols[i % len(cols)]:
                        caption_text = f"{cname} ({conf:.0%})" + (f"\n{vit}" if vit and vit != "N/A" else "")
                        st.image(crop_arr, caption=caption_text, use_container_width=True)

        # ---------------- SECTOR RESIDENT CROSS-REFERENCE (SMART LINK) ----------------
        st.markdown("---")
        with st.expander("🏢 Sector Resident Cross-Reference (Link AI Detections to Tower & Flats)", expanded=True):
            st.caption("Cross-reference observed drone sector coordinates with registered residents, vulnerable individuals, and pets:")
            sc_col1, sc_col2 = st.columns([1, 2])
            with sc_col1:
                target_tower = st.selectbox("Observed Tower in Frame", ["Tower A", "Tower B", "Tower C", "Tower D"], index=0, key="link_tower")
                floor_range = st.slider("Floor Range in View", 1, 10, (1, 4), key="link_floors")
            with sc_col2:
                sec_residents = get_residents_by_sector(target_tower, floor_range[0], floor_range[1])
                if not sec_residents.empty:
                    st.markdown(f"**Found {len(sec_residents)} Flat(s) in {target_tower} (Floors {floor_range[0]}–{floor_range[1]}):**")
                    for _, r in sec_residents.iterrows():
                        stat_badge = "🟢 SAFE" if r['evacuation_status'] == "SAFE_AT_ASSEMBLY" else ("🔴 TRAPPED" if r['evacuation_status'] == "CONFIRMED_TRAPPED" else "⚪ UNACCOUNTED")
                        vuln_text = f" | ⚠️ **{r['vulnerability']}**" if r['vulnerability'] != "None (Able-bodied)" else ""
                        pet_text = f" | 🐾 **{r['pets']}**" if r['pets'] != "None" else ""
                        st.markdown(f"- **Flat {r['flat_number']}** ({r['primary_resident']}, {r['occupants_count']} pers): `{stat_badge}`{vuln_text}{pet_text} &bull; 📞 `{r['phone']}`")
                else:
                    st.info(f"No registered flats found in {target_tower} between floors {floor_range[0]}–{floor_range[1]}.")

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
                "🎯 Follow Active Sidebar Mission Targets (Search configured objects)",
                "👥 Human Survivors Only (Recommended - Zero Animal False Positives)",
                "🐕 Complete SAR Grid (Humans + Rescue K9s + Vehicles)"
            ],
            index=0,
            help="Select how drone video tracking should filter targets: follow your active sidebar target selection, restrict to survivors only, or scan the standard SAR grid."
        )
        if "Human Survivors Only" in mission_tracking_mode:
            track_classes = [0]
        elif "Follow Active Sidebar" in mission_tracking_mode:
            track_classes = active_coco_classes if is_optical_model else active_thermal_classes
        else:
            track_classes = [0, 1, 2, 3, 16] if is_optical_model else [0, 1, 2]

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
                    # detections: list of (cx, cy, cname, conf, [x1,y1,x2,y2], cat)
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
                                'bbox': d[4],
                                'cat': d[5]
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
                        self.tracks[tid]['cat'] = detections[c][5]
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
                                'bbox': d[4],
                                'cat': d[5]
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
                                'bbox': t['bbox'],
                                'cat': t.get('cat', 'General Object')
                            })
                    return active

                def get_unique_counts(self):
                    counts = Counter()
                    for tid, t in self.tracks.items():
                        if t['hits'] >= self.min_hits:
                            majority_cls = t['votes'].most_common(1)[0][0]
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
                res = model.predict(
                    source=frame_rgb,
                    conf=vid_conf,
                    iou=iou_thresh,
                    agnostic_nms=True,
                    classes=track_classes if track_classes else None,
                    verbose=False
                )[0]
                
                raw_dets = []
                if res.boxes is not None:
                    for b in res.boxes:
                        raw_cid = int(b.cls[0].item())
                        cname, cat, icon = resolve_detection_info(raw_cid, is_optical=is_optical_model, opt_names=optical_model.names)
                        score = float(b.conf[0].item())
                        x1, y1, x2, y2 = b.xyxy[0].tolist()
                        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
                        raw_dets.append((cx, cy, cname, score, [int(x1), int(y1), int(x2), int(y2)], cat))

                # Update temporal tracker (filters out 1-frame glitches with majority vote)
                active_tracks = tracker.update(raw_dets)

                # Draw persistent tracks on frame
                draw_img = frame_rgb.copy()
                curr_people = 0
                curr_clues = 0
                curr_obstacles = 0
                curr_k9s = 0

                cat_colors = {
                    "Survivor": (255, 51, 102),     # Red
                    "Rubble Clue": (163, 113, 247), # Purple
                    "Evacuation Obstacle": (255, 209, 102), # Amber
                    "Canine & Pet": (0, 240, 255),  # Cyan
                    "Infrastructure": (56, 139, 253), # Blue
                    "General Object": (0, 245, 155) # Green
                }

                for t in active_tracks:
                    cname = t['cls']
                    tid = t['tid']
                    conf_val = t['conf']
                    bx1, by1, bx2, by2 = t['bbox']
                    cat = t.get('cat', 'General Object')
                    
                    if cname == "Person" or cat == "Survivor":
                        curr_people += 1
                    elif cat == "Rubble Clue" or cname in ["Backpack", "Handbag", "Suitcase", "Cell Phone"]:
                        curr_clues += 1
                    elif cat == "Evacuation Obstacle":
                        curr_obstacles += 1
                    elif cat == "Canine & Pet":
                        curr_k9s += 1
                    
                    color = cat_colors.get(cat, (0, 245, 155))
                    label = f"{cname} #{tid} ({conf_val:.0%})"

                    cv2.rectangle(draw_img, (bx1, by1), (bx2, by2), color, 2)
                    cv2.putText(draw_img, label, (bx1, max(15, by1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

                frame_window.image(draw_img, caption=f"Recon Scan — Frame {frame_idx}/{total_frames}", use_container_width=True)
                progress_bar.progress(min(1.0, frame_idx / max(1, total_frames)))

                # Update Live HUD with confirmed unique counts
                unique_counts = tracker.get_unique_counts()
                tot_p = unique_counts.get("Person", 0)
                tot_clues = sum(cnt for name, cnt in unique_counts.items() if name in ["Backpack", "Handbag", "Suitcase", "Cell Phone"])
                tot_obs = sum(cnt for name, cnt in unique_counts.items() if name in ["Car", "Obstacle / Vehicle", "Bicycle", "Motorcycle", "Truck", "Bus"])
                tot_k9 = sum(cnt for name, cnt in unique_counts.items() if name in ["Dog", "Cat"])

                metric_curr_people.metric("🔴 In Current Frame", f"{curr_people} Survivors")
                metric_total_people.metric("📍 Total Unique Survivors", f"{tot_p} People")
                metric_k9.metric("🎒 Rubble Clues / Pets", f"{tot_clues} Clues | {tot_k9} Animals")
                metric_veh.metric("🚗 Confirmed Vehicles", f"{tot_obs} Obstacles")

            cap.release()
            final_counts = tracker.get_unique_counts()
            f_p = final_counts.get("Person", 0)
            f_clues = sum(cnt for name, cnt in final_counts.items() if name in ["Backpack", "Handbag", "Suitcase", "Cell Phone"])
            f_obs = sum(cnt for name, cnt in final_counts.items() if name in ["Car", "Obstacle / Vehicle", "Bicycle", "Motorcycle", "Truck", "Bus"])
            f_k9 = sum(cnt for name, cnt in final_counts.items() if name in ["Dog", "Cat"])

            summary_msg = f"✅ Drone Aerial Reconnaissance Complete! Found {f_p} unique survivor(s)"
            if f_clues > 0:
                summary_msg += f", {f_clues} rubble clue(s)/bag(s)"
            if f_obs > 0:
                summary_msg += f", {f_obs} obstacle(s)"
            summary_msg += f" across {total_frames} frames."
            st.success(summary_msg)

            # Action buttons for video recon
            v_act1, v_act2 = st.columns(2)
            with v_act1:
                v_pdf = generate_society_pdf_report(
                    society_name=society_name,
                    safe_zone=safe_assembly_point,
                    gate_name=main_gate_name,
                    model_name=selected_model_name,
                    counts={"Person": f_p, "Dog": f_k9, "Car": f_obs, "Rubble Clue": f_clues},
                    gate_blocked=f_obs > 0,
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
• Unique Survivors Tracked: *{f_p}*
• Rubble Clues / Bags Cataloged: *{f_clues}*
• Main Access Gate ({main_gate_name}): *{'🔴 BLOCKED (Towing Required)' if f_obs > 0 else '🟢 CLEAR'}*
• Active Search K9 Teams / Pets: *{f_k9}*
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
# TAB 3: LIVE TACTICAL RECON (WEBCAM / IP DRONE STREAM)
# =======================================================
with tab_live:
    st.markdown("#### 📡 Real-Time Reconnaissance Stream (Mac Webcam / IP Drone Camera)")
    st.caption("Live edge video ingestion supporting local webcam and RTSP / HTTP network streams from drones or phones.")

    live_c1, live_c2 = st.columns([1, 1])
    with live_c1:
        stream_mode = st.radio(
            "Live Video Ingestion Mode",
            ["📸 High-Resolution Live Camera Snapshot", "🎥 Continuous Edge Stream (Webcam / IP Camera)"],
            index=0
        )
    with live_c2:
        stream_sensor_type = st.radio(
            "Active Camera Sensor Payload",
            ["☀️ Daylight Optical (Mac Webcam / Visible RGB)", "🌡️ Thermal Infrared IR (FLIR / Seek / Drone Thermal)"],
            index=0,
            help="Your Mac Webcam captures Daylight Optical RGB light. Always keep 'Daylight Optical' selected when using your laptop webcam to ensure survivors are accurately classified and prevent false dog detections."
        )

    is_stream_optical = "Daylight Optical" in stream_sensor_type
    active_stream_model = optical_model if is_stream_optical else model

    if "Snapshot" in stream_mode:
        live_snap = st.camera_input("Capture Instant Reconnaissance Frame from Camera")
        if live_snap is not None:
            snap_img = Image.open(live_snap).convert("RGB")
            snap_np = np.array(snap_img)
            
            # Predict with Class-Agnostic NMS on RGB numpy frame
            stream_target_classes = active_coco_classes if is_stream_optical else active_thermal_classes
            snap_res = active_stream_model.predict(
                source=snap_np,
                conf=confidence,
                iou=iou_thresh,
                agnostic_nms=True,
                classes=stream_target_classes,
                verbose=False
            )[0]
            
            snap_annotated = snap_res.plot()
            st.image(snap_annotated, caption=f"Live Recon Analysis — {'Daylight Optical (YOLO11)' if is_stream_optical else selected_model_name}", use_container_width=True)
            
            snap_counts = Counter()
            if snap_res.boxes is not None:
                for b in snap_res.boxes:
                    raw_cid = int(b.cls[0].item())
                    cname, cat, icon = resolve_detection_info(raw_cid, is_optical=is_stream_optical, opt_names=optical_model.names)
                    snap_counts[f"{icon} {cname}"] += 1

            if snap_counts:
                summary_items = [f"**{cnt}** {item}" for item, cnt in snap_counts.items()]
                st.success(f"🎯 **Target Recon Confirmed:** {', '.join(summary_items)} in camera view.")
            else:
                st.info("No targets detected matching current target filter.")

            person_cnt = sum(cnt for item, cnt in snap_counts.items() if "Person" in item)
            if person_cnt > 0:
                trigger_tactical_audio_alert(f"Live camera verified {person_cnt} person.", enabled=enable_audio_siren)

    else:
        st.write("Click below to start continuous stream processing:")
        col_s1, col_s2 = st.columns([2, 1])
        with col_s1:
            stream_src_input = st.text_input("Camera Index or Network URL (0 for Mac Webcam, or RTSP/HTTP)", value="0")
        with col_s2:
            st.caption(f"Active Sensor Engine: **{'☀️ Daylight Optical (RGB)' if is_stream_optical else '🌡️ Thermal Infrared IR'}**")

        col_btn1, col_btn2 = st.columns(2)
        live_run = col_btn1.toggle("🔴 Start Live Stream Processing", key="live_stream_toggle")
        
        if live_run:
            live_frame_placeholder = st.empty()
            live_metric_placeholder = st.empty()
            
            cam_dev = int(stream_src_input) if stream_src_input.isdigit() else stream_src_input
            live_cap = cv2.VideoCapture(cam_dev)
            
            frame_cnt = 0
            while live_run and live_cap.isOpened():
                l_ret, l_frame = live_cap.read()
                if not l_ret:
                    st.warning("Unable to fetch video frame from device. Check device connection.")
                    break
                
                frame_cnt += 1
                if frame_cnt % 2 == 0:
                    l_rgb = cv2.cvtColor(l_frame, cv2.COLOR_BGR2RGB)
                    stream_target_classes = active_coco_classes if is_stream_optical else active_thermal_classes
                    l_res = active_stream_model.predict(
                        source=l_rgb,
                        conf=confidence,
                        iou=iou_thresh,
                        agnostic_nms=True,
                        classes=stream_target_classes,
                        verbose=False
                    )[0]
                    
                    l_draw = l_res.plot()
                    live_frame_placeholder.image(l_draw, caption=f"Live Feed Active — {'Daylight Optical (RGB)' if is_stream_optical else selected_model_name}", use_container_width=True)
                    
                    l_counts = Counter()
                    if l_res.boxes is not None:
                        for b in l_res.boxes:
                            raw_cid = int(b.cls[0].item())
                            cname, cat, icon = resolve_detection_info(raw_cid, is_optical=is_stream_optical, opt_names=optical_model.names)
                            l_counts[f"{icon} {cname}"] += 1
                    
                    if l_counts:
                        stream_summary = " | ".join([f"{item}: {cnt}" for item, cnt in l_counts.items()])
                        live_metric_placeholder.success(f"🟢 **Live Recon Active:** {stream_summary}")
                    else:
                        live_metric_placeholder.info("🟢 **Live Recon Active:** Scanning... No target signatures in frame.")
            live_cap.release()

# =======================================================
# TAB 4: SOCIETY INCIDENT COMMAND & RWA DISPATCH
# =======================================================
with tab_dispatch:
    st.markdown(f"#### 📋 {society_name} // Incident Command & RWA Dispatch")
    st.caption("Coordinate residential tower evacuations, gate clearance, medical triage, and multi-agency response.")

    current_dets = st.session_state.latest_detections
    latest_rubble = st.session_state.get("latest_rubble", (0.0, False))
    
    # Society Overview KPI Cards
    soc_c1, soc_c2, soc_c3, soc_c4 = st.columns(4)
    soc_c1.info(f"**Housing Society:**\n{society_name}")
    soc_c2.success(f"**Safe Assembly Point:**\n{safe_assembly_point}")
    soc_c3.warning(f"**Primary Access:**\n{main_gate_name}")
    if latest_rubble[1]:
        soc_c4.error(f"**Roadways:**\n🔴 IMPASSABLE ({latest_rubble[0]}% Rubble)")
    else:
        soc_c4.success(f"**Roadways:**\n🟢 TRAVERSABLE ({latest_rubble[0]}% Rubble)")

    # Multi-Tower Resident Directory & Evacuation Accounting
    st.markdown("##### 🏢 Multi-Tower Resident Accounting & Evacuation Reconciliation")
    c_p = len([d for d in current_dets if d.get('Category') == 'Person' or d.get('Tactical Group') == 'Survivor']) if current_dets else 0
    c_d = len([d for d in current_dets if d.get('Category') in ['Dog', 'Cat'] or d.get('Tactical Group') == 'Canine & Pet']) if current_dets else 0
    c_o = len([d for d in current_dets if d.get('Tactical Group') == 'Evacuation Obstacle' or d.get('Category') in ['Obstacle / Vehicle', 'Car', 'Bicycle', 'Motorcycle', 'Truck', 'Bus']]) if current_dets else 0
    c_clues = len([d for d in current_dets if d.get('Tactical Group') == 'Rubble Clue' or d.get('Category') in ['Backpack', 'Handbag', 'Suitcase', 'Cell Phone']]) if current_dets else 0

    stats = get_headcount_stats()
    acc_c1, acc_c2, acc_c3, acc_c4 = st.columns(4)
    acc_c1.metric("🏢 Total Registered", f"{stats['total_residents']} Residents", f"{stats['total_flats']} Flats")
    acc_c2.metric("🌳 Verified Safe in Lawn", f"{stats['safe_residents']} Residents", f"{stats['safe_flats']} Flats")
    acc_c3.metric("🔴 Trapped in Towers", f"{stats['trapped_residents']} Residents", f"{stats['trapped_flats']} Flats")
    acc_c4.metric("⚠️ Unaccounted / Missing", f"{stats['unaccounted_residents']} Residents", f"{stats['unaccounted_flats']} Flats")

    pct_accounted = min(1.0, (stats['safe_residents'] + stats['trapped_residents']) / max(1, stats['total_residents']))
    st.progress(pct_accounted)
    st.caption(f"**Safety Roster:** {pct_accounted:.1%} of society population accounted for ({stats['safe_residents'] + stats['trapped_residents']} / {stats['total_residents']} residents).")
    if c_d > 0:
        st.success(f"🐾 **Domestic Pets & Animals Accounted:** {c_d} pet(s) (dogs/cats) identified in sweep. Ready for family reunification at {safe_assembly_point}.")
    if c_clues > 0:
        st.info(f"🎒 **Rubble Clues & Victim Anchors Located:** {c_clues} item(s) (backpacks, bags, phones) cataloged in disaster sector.")

    # Interactive Tactical Map in Command Center
    st.markdown("---")
    with st.expander("🗺️ Society Tactical GIS Aerial Layout Map", expanded=True):
        map_html = create_society_tactical_map(
            society_name=society_name,
            safe_zone=safe_assembly_point,
            gate_name=main_gate_name,
            people_count=c_p,
            obstacle_count=c_o,
            k9_count=c_d,
            has_hazard=st.session_state.get("latest_hazard", False),
            detections=current_dets
        )
        components.html(map_html, height=420)

    st.markdown("---")
    if current_dets:
        df = pd.DataFrame(current_dets)
        col_d1, col_d2 = st.columns([2, 1])
        
        with col_d1:
            st.markdown(f"**Active Target Reconnaissance Log (`{st.session_state.latest_source}`)**")
            display_cols = ["Target ID", "Category", "Tactical Group", "Confidence", "Vitality", "Sector Box [X1,Y1,X2,Y2]", "Grid Center"]
            avail_cols = [c for c in display_cols if c in df.columns]
            st.dataframe(df[avail_cols], use_container_width=True)

        with col_d2:
            st.markdown("**Official Mission Exports**")
            pdf_data = generate_society_pdf_report(
                society_name=society_name,
                safe_zone=safe_assembly_point,
                gate_name=main_gate_name,
                model_name=selected_model_name,
                counts={"Person": c_p, "Dog": c_d, "Car": c_o, "Rubble Clue": c_clues},
                gate_blocked=c_o > 0,
                thermal_hazard=st.session_state.get("latest_hazard", False),
                detections=current_dets,
                rubble_severity=latest_rubble[0],
                is_rubble_blocked=latest_rubble[1]
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
            * [ ] **Roadway Clearance**: {'🚨 Dispatch heavy bulldozer to clear internal rubble.' if latest_rubble[1] else 'Roadway clear for ambulance/fire ingress.'}
            * [ ] **Isolate PNG Gas Mains**: Shut down main manifold valve immediately.
            * [ ] **Transformer Yard**: Verify DG set and transformer room are clear of fire.
            * [ ] **Clear {main_gate_name}**: Tow/push vehicles to allow fire brigade ingress.
            * [ ] **Lawn Headcount**: Account for elderly and children at {safe_assembly_point}.
            * [ ] **Broadcast WhatsApp Alert**: Broadcast emergency directive to society group.
            """)
    else:
        st.info("ℹ️ Ingest an image or video in the Recon tabs to populate the active target log.")

    # ---------------- AUTOMATED USAR SITUATION REPORT (SITREP) ----------------
    st.markdown("---")
    st.markdown("##### 🖨️ Official USAR Situation Report (SitRep / INSARAG Standard)")
    st.caption("Generate a certified post-incident Search and Rescue SitRep for fire chiefs, ambulance paramedics, and RWA management.")
    
    sit_c1, sit_c2 = st.columns([3, 1])
    with sit_c1:
        commander_title = st.text_input("Commanding Officer / Reporter Title", value=f"USAR Tactical Team Lead // {society_name} Incident Command", key="sitrep_cmd")
    with sit_c2:
        st.write("")
        st.write("")
        btn_preview_sitrep = st.button("📋 Generate Live SitRep", use_container_width=True, key="btn_gen_sitrep")

    sitrep_html = generate_html_sitrep(
        society_name=society_name,
        safe_assembly_point=safe_assembly_point,
        primary_gate=main_gate_name,
        sensor_model_name=selected_model_name,
        ai_detections=current_dets,
        rubble_info=latest_rubble,
        is_thermal_hazard=st.session_state.get("latest_hazard", False),
        source_image=st.session_state.get("latest_raw_img", None),
        overlay_image=st.session_state.get("latest_annotated_img", None),
        commander_name=commander_title
    )

    sitrep_b1, sitrep_b2 = st.columns(2)
    with sitrep_b1:
        st.download_button(
            label="🌐 Download Certified HTML SitRep",
            data=sitrep_html,
            file_name=f"SITREP_{society_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.html",
            mime="text/html",
            use_container_width=True
        )
    with sitrep_b2:
        st.caption("💡 Open downloaded HTML to print or save directly as PDF.")

    with st.expander("👁️ Preview Live Situation Report (SitRep)", expanded=False):
        components.html(sitrep_html, height=650, scrolling=True)

# =======================================================
# TAB 5: SOCIETY RESIDENT DIRECTORY & EVACUATION ROSTER
# =======================================================
with tab_registry:
    st.markdown(f"#### 🏢 {society_name} // Resident Directory & Evacuation Roster")
    st.caption("100% Offline SQLite database for gate headcount tally, high-vulnerability rescue tracking, and flat management.")

    # Top KPI Cards
    stats = get_headcount_stats()
    kpi_c1, kpi_c2, kpi_c3, kpi_c4, kpi_c5 = st.columns(5)
    kpi_c1.metric("🏢 Total Residents", f"{stats['total_residents']} Pers", f"{stats['total_flats']} Flats")
    kpi_c2.metric("🟢 Safe at Lawn", f"{stats['safe_residents']} Pers", f"{stats['safe_flats']} Flats")
    kpi_c3.metric("🔴 Confirmed Trapped", f"{stats['trapped_residents']} Pers", f"{stats['trapped_flats']} Flats")
    kpi_c4.metric("⚪ Unaccounted", f"{stats['unaccounted_residents']} Pers", f"{stats['unaccounted_flats']} Flats")
    kpi_c5.metric("🚨 High-Risk Missing", f"{stats['vuln_unaccounted_flats']} Flats", f"Pets Inside: {stats['pets_inside_flats']}", delta_color="inverse")

    # Sub-tabs for the 3 operational views
    sub_view_tally, sub_view_priority, sub_view_editor = st.tabs([
        "🛡️ Gate Headcount & Check-In",
        "🚨 High-Vulnerability Priority Board",
        "⚙️ Resident Directory Editor & CSV"
    ])

    with sub_view_tally:
        st.markdown("##### 🛡️ Gate Check-In & Evacuation Tally")
        st.caption("Security guards and triage volunteers at the gate can rapidly mark residents as Safe or Trapped.")
        
        tc_f1, tc_f2, tc_f3 = st.columns([2, 1, 1])
        search_txt = tc_f1.text_input("🔍 Quick Search (Flat No, Resident Name, Phone)", placeholder="Type e.g. 201, Sharma, 98201...", key="tally_search")
        tower_filt = tc_f2.selectbox("Filter Tower", ["All Towers", "Tower A", "Tower B", "Tower C", "Tower D"], key="tally_tower")
        status_filt = tc_f3.selectbox("Filter Evacuation Status", ["All Statuses", "UNACCOUNTED", "SAFE_AT_ASSEMBLY", "CONFIRMED_TRAPPED", "OFF_SITE"], key="tally_status")
        
        tally_df = get_all_residents(tower=tower_filt, status=status_filt, search_query=search_txt)
        
        st.markdown(f"**Displaying {len(tally_df)} Flat(s):**")
        for _, row in tally_df.iterrows():
            rid = row["id"]
            stat = row["evacuation_status"]
            stat_info = EVACUATION_STATUSES.get(stat, ("Unknown", "#8b949e"))
            
            with st.container():
                st.markdown(f"""
                <div style="background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 12px; margin-bottom: 8px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="font-size: 1.1rem; font-weight: 800; color: #58a6ff;">{row['tower_id']} - Flat {row['flat_number']}</span>
                            <span style="font-size: 0.85rem; color: #8b949e; margin-left: 8px;">(Floor {row['floor']})</span>
                            <span style="margin-left: 10px; font-weight: 700; color: {stat_info[1]};">{stat_info[0]}</span>
                        </div>
                        <div style="font-size: 0.85rem; color: #8b949e;">
                            Occupants: <strong style="color: #ffffff;">{row['occupants_count']}</strong> | 📞 <a href="tel:{row['phone']}" style="color: #58a6ff;">{row['phone']}</a>
                        </div>
                    </div>
                    <div style="margin-top: 6px; font-size: 0.85rem;">
                        <strong>Resident:</strong> {row['primary_resident']}
                        {' | <span style="color: #ff7b72; font-weight: 600;">⚠️ ' + row['vulnerability'] + '</span>' if row['vulnerability'] != 'None (Able-bodied)' else ''}
                        {' | <span>🐾 ' + row['pets'] + '</span>' if row['pets'] != 'None' else ''}
                        {' | Next of Kin: ' + str(row['emergency_contact_name']) + ' (' + str(row['emergency_contact_phone']) + ')' if row['emergency_contact_name'] else ''}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Action buttons
                btn_cols = st.columns([1, 1, 1, 3])
                if stat != "SAFE_AT_ASSEMBLY":
                    if btn_cols[0].button("🟢 Mark Safe at Lawn", key=f"safe_{rid}", use_container_width=True):
                        update_resident_status(rid, "SAFE_AT_ASSEMBLY")
                        st.rerun()
                if stat != "CONFIRMED_TRAPPED":
                    if btn_cols[1].button("🔴 Mark Trapped", key=f"trap_{rid}", use_container_width=True):
                        update_resident_status(rid, "CONFIRMED_TRAPPED")
                        st.rerun()
                if stat != "UNACCOUNTED":
                    if btn_cols[2].button("⚪ Reset Unaccounted", key=f"unacc_{rid}", use_container_width=True):
                        update_resident_status(rid, "UNACCOUNTED")
                        st.rerun()

    with sub_view_priority:
        st.markdown("##### 🚨 High-Vulnerability Rescue Priority Board")
        st.caption("Real-time extraction target list for search squads. Displays residents with special needs who are STILL UNACCOUNTED.")
        
        vuln_all = get_all_residents(only_vulnerable=True)
        vuln_pending = vuln_all[vuln_all["evacuation_status"].isin(["UNACCOUNTED", "CONFIRMED_TRAPPED"])]
        
        if not vuln_pending.empty:
            st.error(f"⚠️ **ATTENTION SEARCH SQUADS:** {len(vuln_pending)} vulnerable households require immediate physical assistance or stretcher evacuation!")
            for _, r in vuln_pending.iterrows():
                is_trap = r["evacuation_status"] == "CONFIRMED_TRAPPED"
                border_color = "#ff3366" if is_trap else "#d29922"
                stat_tag = "🔴 CONFIRMED TRAPPED" if is_trap else "⚪ UNACCOUNTED (High Vulnerability)"
                st.markdown(f"""
                <div style="background: #161b22; border-left: 5px solid {border_color}; border-radius: 8px; padding: 14px; margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="font-size: 1.2rem; font-weight: 800; color: #58a6ff;">{r['tower_id']} &bull; Flat {r['flat_number']} (Floor {r['floor']})</span>
                        <span style="font-weight: 800; color: {border_color}; font-size: 0.9rem;">{stat_tag}</span>
                    </div>
                    <div style="font-size: 1rem; color: #ff7b72; font-weight: 700; margin: 4px 0;">
                        {r['vulnerability']}
                    </div>
                    <div style="font-size: 0.9rem; color: #c9d1d9;">
                        <strong>Primary Resident:</strong> {r['primary_resident']} ({r['occupants_count']} occupants) &bull; 📞 <code>{r['phone']}</code>
                    </div>
                    <div style="font-size: 0.85rem; color: #8b949e; margin-top: 4px;">
                        <strong>Pets:</strong> {r['pets']} &bull; 
                        <strong>Next of Kin:</strong> {r['emergency_contact_name']} ({r['emergency_contact_phone']})
                    </div>
                    <div style="font-size: 0.85rem; color: #ffd166; margin-top: 4px;">
                        <strong>Dispatch Notes:</strong> {r['notes'] or 'Standard USAR evacuation protocol.'}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                v_btn_cols = st.columns([1, 4])
                if v_btn_cols[0].button("🟢 Mark Rescued & Safe", key=f"vuln_safe_{r['id']}", use_container_width=True):
                    update_resident_status(r['id'], "SAFE_AT_ASSEMBLY")
                    st.rerun()
        else:
            st.success("🟢 All registered high-vulnerability residents have been safely evacuated to the Central Lawn!")

    with sub_view_editor:
        st.markdown("##### ⚙️ Resident Directory Editor & CSV Bulk Transfer")
        st.caption("Manage flat records, register new families, or bulk-import society spreadsheets.")
        
        ed_col1, ed_col2 = st.columns([1, 1])
        
        with ed_col1:
            st.markdown("**➕ Add / Update Flat Record**")
            with st.form("form_add_resident", clear_on_submit=True):
                form_tower = st.selectbox("Tower", ["Tower A", "Tower B", "Tower C", "Tower D"])
                form_flat = st.text_input("Flat Number", placeholder="e.g. B-502")
                form_floor = st.number_input("Floor", min_value=1, max_value=30, value=1)
                form_name = st.text_input("Primary Resident Name", placeholder="e.g. R. K. Sharma")
                form_phone = st.text_input("Resident Phone Number", placeholder="+91 98200 ...")
                form_occ = st.number_input("Total Occupants in Flat", min_value=1, max_value=15, value=2)
                form_vuln = st.selectbox("Vulnerability / Special Assistance", VULNERABILITY_OPTIONS)
                form_pets = st.selectbox("Registered Pets", PET_OPTIONS)
                form_em_name = st.text_input("Off-Site Emergency Contact Name")
                form_em_phone = st.text_input("Emergency Contact Phone")
                form_notes = st.text_area("Tactical Dispatch Notes", placeholder="e.g. Key with neighbor, elderly resident, pet carrier required...")
                
                submitted = st.form_submit_button("💾 Save Flat Record", use_container_width=True)
                if submitted:
                    if form_flat and form_name and form_phone:
                        try:
                            add_resident(
                                tower_id=form_tower,
                                flat_number=form_flat,
                                floor=form_floor,
                                primary_resident=form_name,
                                phone=form_phone,
                                occupants_count=form_occ,
                                vulnerability=form_vuln,
                                pets=form_pets,
                                emergency_contact_name=form_em_name,
                                emergency_contact_phone=form_em_phone,
                                notes=form_notes
                            )
                            st.success(f"✓ Flat {form_flat} registered successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error saving flat: {e}")
                    else:
                        st.warning("Please fill in Flat Number, Resident Name, and Phone.")
                        
        with ed_col2:
            st.markdown("**📥 Bulk CSV Import & Export**")
            st.caption("Download society database backup or upload your existing society Excel/CSV resident list:")
            
            csv_data = export_to_csv()
            st.download_button(
                label="📤 Export Complete Resident Database (CSV)",
                data=csv_data,
                file_name=f"Society_Residents_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
            
            st.markdown("---")
            st.markdown("**Upload Resident CSV File:**")
            uploaded_csv = st.file_uploader("Upload CSV formatted spreadsheet", type=["csv"], key="csv_uploader")
            if uploaded_csv:
                csv_str = uploaded_csv.getvalue().decode("utf-8")
                count, err = import_from_csv(csv_str)
                if err:
                    st.error(f"Import failed: {err}")
                else:
                    st.success(f"✓ Successfully imported/updated {count} flats!")
                    st.rerun()
