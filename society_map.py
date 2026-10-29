import folium
from folium import plugins

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
    Renders an interactive GIS Tactical Aerial Layout Map for the Residential Society.
    Returns HTML string for embedding directly into Streamlit.
    """
    # Base coordinates for the simulated residential society campus
    center_lat, center_lon = 19.0760, 72.8777

    # Initialize map with OpenStreetMap tiles
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=18,
        tiles="OpenStreetMap",
        control_scale=True
    )

    # 1. Society Compound Perimeter Boundary (Dashed Cyan Line)
    compound_bounds = [
        [center_lat + 0.0018, center_lon - 0.0022],
        [center_lat + 0.0018, center_lon + 0.0022],
        [center_lat - 0.0018, center_lon + 0.0022],
        [center_lat - 0.0018, center_lon - 0.0022],
        [center_lat + 0.0018, center_lon - 0.0022]
    ]
    folium.PolyLine(
        compound_bounds,
        color="#00f0ff",
        weight=2.5,
        opacity=0.8,
        dash_array="6, 6",
        tooltip=f"{society_name} Campus Perimeter"
    ).add_to(m)

    # 2. Designated Safe Assembly Ground (Central Community Lawn) - Green Area
    safe_lawn_coords = [
        [center_lat + 0.0006, center_lon - 0.0007],
        [center_lat + 0.0006, center_lon + 0.0007],
        [center_lat - 0.0006, center_lon + 0.0007],
        [center_lat - 0.0006, center_lon - 0.0007]
    ]
    folium.Polygon(
        safe_lawn_coords,
        color="#2ea043",
        weight=2,
        fill=True,
        fill_color="#2ea043",
        fill_opacity=0.25,
        popup=f"<b>🟢 DESIGNATED SAFE ZONE</b><br>{safe_zone}<br>Open grass field free from falling glass/masonry.",
        tooltip=f"🟢 Safe Assembly Ground ({safe_zone})"
    ).add_to(m)

    # 3. Residential Towers (Tower A, Tower B, Tower C)
    towers = [
        {
            "name": "Tower 1 (A-Wing)",
            "lat": center_lat + 0.0012,
            "lon": center_lon - 0.0014,
            "floors": "14 Floors",
            "trapped": max(0, min(people_count, 2))
        },
        {
            "name": "Tower 2 (B-Wing)",
            "lat": center_lat + 0.0012,
            "lon": center_lon + 0.0014,
            "floors": "14 Floors",
            "trapped": max(0, people_count - 2) if people_count > 2 else 0
        },
        {
            "name": "Tower 3 (C-Wing)",
            "lat": center_lat - 0.0012,
            "lon": center_lon - 0.0014,
            "floors": "12 Floors",
            "trapped": 0
        }
    ]

    for t in towers:
        has_victims = t["trapped"] > 0
        icon_color = "red" if has_victims else "blue"
        popup_html = f"""
        <div style="font-family: sans-serif; font-size: 12px; min-width: 140px;">
            <b style="color: {'#cf222e' if has_victims else '#0969da'};">{t['name']}</b><br>
            Structure: {t['floors']}<br>
            Status: {'🔴 ' + str(t['trapped']) + ' Trapped Resident(s)' if has_victims else '🟢 Structural Clear'}
        </div>
        """
        folium.Marker(
            [t["lat"], t["lon"]],
            popup=popup_html,
            tooltip=f"{t['name']} ({t['trapped']} Trapped)" if has_victims else t['name'],
            icon=folium.Icon(color=icon_color, icon="home", prefix="fa")
        ).add_to(m)

    # 4. Main Security Access Gate
    gate_lat, gate_lon = center_lat + 0.0018, center_lon
    gate_color = "red" if obstacle_count > 0 else "green"
    gate_popup = f"""
    <div style="font-family: sans-serif; font-size: 12px; min-width: 150px;">
        <b>🚪 {gate_name}</b><br>
        Status: <b style="color: {'#cf222e' if obstacle_count > 0 else '#1a7f37'};">
        {'🔴 BLOCKED (' + str(obstacle_count) + ' Obstacles)' if obstacle_count > 0 else '🟢 CLEAR (Accessible)'}</b><br>
        Primary entrance for Fire Brigade & Ambulances.
    </div>
    """
    folium.Marker(
        [gate_lat, gate_lon],
        popup=gate_popup,
        tooltip=f"{gate_name}: {'🔴 BLOCKED' if obstacle_count > 0 else '🟢 CLEAR'}",
        icon=folium.Icon(color=gate_color, icon="road", prefix="fa")
    ).add_to(m)

    # 5. Utility Yard (Electrical Transformer & PNG Gas Manifold)
    util_lat, util_lon = center_lat - 0.0012, center_lon + 0.0014
    util_color = "red" if has_hazard else "gray"
    util_popup = f"""
    <div style="font-family: sans-serif; font-size: 12px; min-width: 150px;">
        <b>⚡ Utility Yard & Gas Manifold</b><br>
        Status: <b style="color: {'#cf222e' if has_hazard else '#1a7f37'};">
        {'🔥 CRITICAL HIGH HEAT / GAS FIRE ALERT' if has_hazard else '🟢 NORMAL'}</b><br>
        Electrical transformer yard & piped gas station.
    </div>
    """
    folium.Marker(
        [util_lat, util_lon],
        popup=util_popup,
        tooltip="⚡ Utility Yard & PNG Gas Station",
        icon=folium.Icon(color=util_color, icon="fire" if has_hazard else "bolt", prefix="fa")
    ).add_to(m)

    # 6. Active K9 Search Units
    if k9_count > 0:
        folium.Marker(
            [center_lat + 0.0003, center_lon + 0.0004],
            popup="<b>🐕 Active Search & Rescue K9</b><br>Canine scent tracking unit operating in sector.",
            tooltip="SAR K9 Unit #1",
            icon=folium.Icon(color="purple", icon="paw", prefix="fa")
        ).add_to(m)

    return m._repr_html_()
