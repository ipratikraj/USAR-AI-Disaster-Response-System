"""
Interactive 2D Tactical GIS Campus Blueprint for Green Valley Residency.
100% Offline Vector GIS Architecture (Zero internet / tile server dependency).
Renders precise residential campus boundaries, 4 towers (A-D), Central Lawn,
internal ring-road traversability, gate status, and live AI incident overlays.
"""

def create_society_tactical_map(
    society_name: str = "Green Valley Residency",
    safe_zone: str = "Central Community Lawn / Park",
    gate_name: str = "Main North Security Gate",
    people_count: int = 0,
    obstacle_count: int = 0,
    k9_count: int = 0,
    has_hazard: bool = False,
    detections: list = None
) -> str:
    """
    Renders an interactive, responsive vector GIS layout blueprint of the residential complex.
    Never relies on external tile servers or internet connectivity.
    """
    # Dynamic status calculations
    gate_color = "#ff3366" if obstacle_count > 0 else "#00f59b"
    gate_status_text = f"BLOCKED ({obstacle_count} Obstacles)" if obstacle_count > 0 else "CLEAR (Accessible)"
    
    t_a_trapped = min(people_count, 2)
    t_b_trapped = max(0, people_count - 2)
    
    t_a_status = f"🔴 {t_a_trapped} TRAPPED" if t_a_trapped > 0 else "🟢 ALL SAFE"
    t_b_status = f"🔴 {t_b_trapped} TRAPPED" if t_b_trapped > 0 else "🟢 ALL SAFE"
    
    t_a_class = "tower-box tower-alert" if t_a_trapped > 0 else "tower-box"
    t_b_class = "tower-box tower-alert" if t_b_trapped > 0 else "tower-box"
    
    t_a_color = "#ff3366" if t_a_trapped > 0 else "#00f59b"
    t_b_color = "#ff3366" if t_b_trapped > 0 else "#00f59b"
    
    road_stroke = "#ff3366" if obstacle_count > 0 else "#00f59b"
    road_dash = "8, 6" if obstacle_count > 0 else "none"
    road_label = "ROADWAY IMPASSABLE // CONCRETE RUBBLE BLOCKAGE" if obstacle_count > 0 else "INTERNAL RING ROAD // TRAVERSABLE FOR AMBULANCES"
    
    util_fill = "rgba(255, 51, 102, 0.25)" if has_hazard else "rgba(48, 54, 61, 0.5)"
    util_stroke = "#ff3366" if has_hazard else "#8b949e"
    util_badge = "🔥 CRITICAL HEAT HAZARD (&gt;300°C)" if has_hazard else "🟢 NORMAL UTILITY STATUS"

    t_a_tip = f"&lt;b&gt;🏢 TOWER A (A-Wing)&lt;/b&gt;&lt;br&gt;Floors: 10 &bull; Flats: A-101 to A-401&lt;br&gt;Status: {t_a_status}&lt;br&gt;Special: Bedridden / Oxygen patient."
    t_b_tip = f"&lt;b&gt;🏢 TOWER B (B-Wing)&lt;/b&gt;&lt;br&gt;Floors: 10 &bull; Flats: B-101 to B-401&lt;br&gt;Status: {t_b_status}&lt;br&gt;Special: Wheelchair user in B-301."
    t_c_tip = "&lt;b&gt;🏢 TOWER C (C-Wing)&lt;/b&gt;&lt;br&gt;Floors: 10 &bull; Flats: C-101 to C-501&lt;br&gt;Status: 🔴 1 Trapped (C-301)&lt;br&gt;Special: Elderly resident Kamla Devi."
    t_d_tip = "&lt;b&gt;🏢 TOWER D (D-Wing)&lt;/b&gt;&lt;br&gt;Floors: 10 &bull; Flats: D-101 to D-401&lt;br&gt;Status: 🟢 SEARCH SQUAD ACTIVE&lt;br&gt;Special: Ground floor ramp accessible."
    lawn_tip = f"&lt;b&gt;🟢 CENTRAL COMMUNITY LAWN&lt;/b&gt;&lt;br&gt;Designated Safe Assembly Point ({safe_zone}).&lt;br&gt;Open sky, free from falling glass/masonry."
    gate_tip = f"&lt;b&gt;🚪 {gate_name}&lt;/b&gt;&lt;br&gt;Status: &lt;b&gt;{gate_status_text}&lt;/b&gt;&lt;br&gt;Primary entrance for Fire Brigade and Ambulances."
    south_gate_tip = "&lt;b&gt;🚪 SOUTH EMERGENCY GATE&lt;/b&gt;&lt;br&gt;Status: 🟢 CLEAR&lt;br&gt;Secondary pedestrian evacuation exit."
    util_tip = f"&lt;b&gt;⚡ UTILITY YARD &amp; PNG GAS STATION&lt;/b&gt;&lt;br&gt;Status: {util_badge}&lt;br&gt;Transformer sub-station and piped gas isolation valves."

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    body {{
        margin: 0;
        padding: 0;
        background: #0d1117;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: #c9d1d9;
        overflow: hidden;
    }}
    .map-wrapper {{
        position: relative;
        width: 100%;
        height: 440px;
        background: radial-gradient(circle at center, #161b22 0%, #0d1117 100%);
        border: 1px solid #30363d;
        border-radius: 10px;
        overflow: hidden;
    }}
    .map-header {{
        position: absolute;
        top: 10px;
        left: 14px;
        z-index: 10;
        display: flex;
        align-items: center;
        gap: 10px;
    }}
    .map-title {{
        font-size: 0.85rem;
        font-weight: 800;
        letter-spacing: 0.8px;
        color: #ffffff;
        text-transform: uppercase;
        background: rgba(13, 17, 23, 0.85);
        padding: 4px 10px;
        border-radius: 4px;
        border: 1px solid #30363d;
    }}
    .map-legend {{
        position: absolute;
        bottom: 10px;
        left: 14px;
        z-index: 10;
        display: flex;
        gap: 8px;
        font-size: 0.72rem;
        background: rgba(13, 17, 23, 0.85);
        padding: 4px 10px;
        border-radius: 4px;
        border: 1px solid #30363d;
    }}
    .legend-item {{
        display: flex;
        align-items: center;
        gap: 5px;
    }}
    .dot {{
        width: 8px;
        height: 8px;
        border-radius: 50%;
    }}
    .tower-box {{
        fill: #161b22;
        stroke: #58a6ff;
        stroke-width: 2;
        transition: all 0.2s ease;
        cursor: pointer;
    }}
    .tower-box:hover {{
        fill: #1f2937;
        stroke: #79c0ff;
    }}
    .tower-alert {{
        stroke: #ff3366 !important;
        fill: rgba(255, 51, 102, 0.15) !important;
        animation: pulse-red 2s infinite;
    }}
    @keyframes pulse-red {{
        0% {{ stroke-opacity: 1; }}
        50% {{ stroke-opacity: 0.3; }}
        100% {{ stroke-opacity: 1; }}
    }}
    .lawn-box {{
        fill: rgba(46, 160, 67, 0.18);
        stroke: #00f59b;
        stroke-width: 2;
        stroke-dasharray: 4, 3;
    }}
    .road-ring {{
        fill: none;
        stroke: {road_stroke};
        stroke-width: 3.5;
        stroke-dasharray: {road_dash};
        opacity: 0.85;
    }}
    .gate-marker {{
        cursor: pointer;
    }}
    .tooltip-card {{
        position: absolute;
        background: #161b22;
        border: 1px solid #58a6ff;
        color: #ffffff;
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 0.78rem;
        pointer-events: none;
        display: none;
        z-index: 100;
        box-shadow: 0 4px 14px rgba(0,0,0,0.6);
        max-width: 240px;
    }}
</style>
</head>
<body>

<div class="map-wrapper">
    <div class="map-header">
        <div class="map-title">📍 {society_name} // 2D GIS Campus Layout</div>
        <div style="font-size: 0.75rem; color: #8b949e; background: rgba(13,17,23,0.85); padding: 4px 8px; border-radius: 4px; border: 1px solid #30363d;">
            Private Campus Boundary &bull; 4 Towers (A, B, C, D)
        </div>
    </div>

    <div class="map-legend">
        <div class="legend-item"><span class="dot" style="background: #58a6ff;"></span> Residential Tower</div>
        <div class="legend-item"><span class="dot" style="background: #00f59b;"></span> Safe Assembly Lawn</div>
        <div class="legend-item"><span class="dot" style="background: {gate_color};"></span> Security Gates</div>
        <div class="legend-item"><span class="dot" style="background: #ff3366;"></span> Active Incident</div>
    </div>

    <div id="tooltip" class="tooltip-card"></div>

    <svg viewBox="0 0 800 440" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                <path d="M 20 0 L 0 0 0 20" fill="none" stroke="rgba(48, 54, 61, 0.35)" stroke-width="0.8"/>
            </pattern>
        </defs>

        <rect width="800" height="440" fill="url(#grid)" />

        <!-- 1. Society Boundary Fence (Cyan Dashed Outer Wall) -->
        <rect x="50" y="45" width="700" height="350" rx="8" fill="none" stroke="#00f0ff" stroke-width="2" stroke-dasharray="6, 5" opacity="0.6"/>
        <text x="60" y="65" fill="#00f0ff" font-size="10" font-weight="700" letter-spacing="1">COMPOUND PERIMETER WALL</text>

        <!-- 2. Internal Society Ring Road (Connects Gates and Towers) -->
        <rect x="110" y="90" width="580" height="260" rx="16" class="road-ring" />
        <text x="400" y="344" fill="{road_stroke}" font-size="9" font-weight="700" text-anchor="middle" letter-spacing="0.5">{road_label}</text>

        <!-- 3. Central Safe Assembly Lawn -->
        <rect x="310" y="150" width="180" height="140" rx="10" class="lawn-box" onmousemove="showTip(evt, '{lawn_tip}')" onmouseout="hideTip()"/>
        <text x="400" y="210" fill="#00f59b" font-size="13" font-weight="800" text-anchor="middle">🌳 SAFE ZONE</text>
        <text x="400" y="228" fill="#8b949e" font-size="10" text-anchor="middle">Central Assembly Lawn</text>
        <text x="400" y="244" fill="#00f59b" font-size="9" font-weight="700" text-anchor="middle">PRIORITY MEDICAL TENT</text>

        <!-- 4. TOWERS (A, B, C, D) -->
        <!-- Tower A (North-West) -->
        <g onmousemove="showTip(evt, '{t_a_tip}')" onmouseout="hideTip()">
            <rect x="150" y="120" width="120" height="85" rx="6" class="{t_a_class}"/>
            <text x="210" y="152" fill="#ffffff" font-size="13" font-weight="800" text-anchor="middle">TOWER A</text>
            <text x="210" y="168" fill="#8b949e" font-size="9.5" text-anchor="middle">10 Floors &bull; 6 Flats</text>
            <text x="210" y="186" fill="{t_a_color}" font-size="9" font-weight="700" text-anchor="middle">{t_a_status}</text>
        </g>

        <!-- Tower B (North-East) -->
        <g onmousemove="showTip(evt, '{t_b_tip}')" onmouseout="hideTip()">
            <rect x="530" y="120" width="120" height="85" rx="6" class="{t_b_class}"/>
            <text x="590" y="152" fill="#ffffff" font-size="13" font-weight="800" text-anchor="middle">TOWER B</text>
            <text x="590" y="168" fill="#8b949e" font-size="9.5" text-anchor="middle">10 Floors &bull; 6 Flats</text>
            <text x="590" y="186" fill="{t_b_color}" font-size="9" font-weight="700" text-anchor="middle">{t_b_status}</text>
        </g>

        <!-- Tower C (South-West) -->
        <g onmousemove="showTip(evt, '{t_c_tip}')" onmouseout="hideTip()">
            <rect x="150" y="245" width="120" height="85" rx="6" class="tower-box tower-alert"/>
            <text x="210" y="277" fill="#ffffff" font-size="13" font-weight="800" text-anchor="middle">TOWER C</text>
            <text x="210" y="293" fill="#8b949e" font-size="9.5" text-anchor="middle">10 Floors &bull; 6 Flats</text>
            <text x="210" y="311" fill="#ff3366" font-size="9" font-weight="700" text-anchor="middle">🔴 1 TRAPPED (C-301)</text>
        </g>

        <!-- Tower D (South-East) -->
        <g onmousemove="showTip(evt, '{t_d_tip}')" onmouseout="hideTip()">
            <rect x="530" y="245" width="120" height="85" rx="6" class="tower-box"/>
            <text x="590" y="277" fill="#ffffff" font-size="13" font-weight="800" text-anchor="middle">TOWER D</text>
            <text x="590" y="293" fill="#8b949e" font-size="9.5" text-anchor="middle">10 Floors &bull; 6 Flats</text>
            <text x="590" y="311" fill="#00f59b" font-size="9" font-weight="700" text-anchor="middle">🟢 SEARCH SQUAD ACTIVE</text>
        </g>

        <!-- 5. MAIN NORTH SECURITY GATE (PRIMARY INGRESS) -->
        <g class="gate-marker" onmousemove="showTip(evt, '{gate_tip}')" onmouseout="hideTip()">
            <rect x="360" y="38" width="80" height="24" rx="4" fill="{gate_color}" opacity="0.25" stroke="{gate_color}" stroke-width="2"/>
            <text x="400" y="54" fill="{gate_color}" font-size="10" font-weight="800" text-anchor="middle">🚪 {gate_name.upper()}</text>
        </g>

        <!-- 6. SOUTH SERVICE / RESCUE GATE -->
        <g class="gate-marker" onmousemove="showTip(evt, '{south_gate_tip}')" onmouseout="hideTip()">
            <rect x="360" y="380" width="80" height="22" rx="4" fill="#00f59b" opacity="0.2" stroke="#00f59b" stroke-width="1.5"/>
            <text x="400" y="395" fill="#00f59b" font-size="9.5" font-weight="700" text-anchor="middle">🚪 SOUTH GATE (CLEAR)</text>
        </g>

        <!-- 7. UTILITY YARD & GAS MANIFOLD -->
        <g onmousemove="showTip(evt, '{util_tip}')" onmouseout="hideTip()">
            <rect x="680" y="195" width="60" height="50" rx="4" fill="{util_fill}" stroke="{util_stroke}" stroke-width="1.8"/>
            <text x="710" y="218" fill="{util_stroke}" font-size="10" font-weight="800" text-anchor="middle">⚡ UTILITY</text>
            <text x="710" y="233" fill="#8b949e" font-size="8" text-anchor="middle">Gas &amp; Power</text>
        </g>

        <!-- 8. ACTIVE SAR K9 UNIT -->
        <g onmousemove="showTip(evt, '<b>🐕 SEARCH K9 UNIT #1</b><br>Canine handler and search dog operating along Central Lawn perimeter.')" onmouseout="hideTip()">
            <circle cx="340" cy="180" r="10" fill="#a371f7" stroke="#ffffff" stroke-width="1.5"/>
            <text x="340" y="184" fill="#ffffff" font-size="10" font-weight="800" text-anchor="middle">🐾</text>
        </g>
    </svg>
</div>

<script>
    const tooltip = document.getElementById('tooltip');
    function showTip(evt, text) {{
        tooltip.innerHTML = text;
        tooltip.style.display = 'block';
        tooltip.style.left = (evt.clientX + 14) + 'px';
        tooltip.style.top = (evt.clientY - 20) + 'px';
    }}
    function hideTip() {{
        tooltip.style.display = 'none';
    }}
</script>

</body>
</html>
"""
    return html
