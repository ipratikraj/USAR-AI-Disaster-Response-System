import io
import time
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_society_pdf_report(
    society_name: str,
    safe_zone: str,
    gate_name: str,
    model_name: str,
    counts: dict,
    gate_blocked: bool,
    thermal_hazard: bool,
    detections: list
) -> bytes:
    """
    Generates an official PDF Incident Report for Residential Society Earthquake Response.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        textColor=colors.HexColor('#0d1117'),
        leading=20,
        spaceAfter=3
    )
    sub_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        textColor=colors.HexColor('#57606a'),
        spaceAfter=10
    )
    cell_bold = ParagraphStyle(
        'CellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        textColor=colors.HexColor('#24292f')
    )
    cell_norm = ParagraphStyle(
        'CellNorm',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        textColor=colors.HexColor('#24292f')
    )

    story = []

    # Title & Header
    story.append(Paragraph('RESIDENTIAL SOCIETY DISASTER RESPONSE & USAR INCIDENT REPORT', title_style))
    story.append(Paragraph('Tactical Aerial Reconnaissance • Trapped Resident Triage • Gate Obstacle Assessment', sub_style))
    story.append(HRFlowable(width='100%', thickness=2.5, color=colors.HexColor('#cf222e'), spaceAfter=12))

    # Meta Table
    recon_time = time.strftime('%Y-%m-%d %H:%M:%S')
    meta_data = [
        [Paragraph('Residential Society:', cell_bold), Paragraph(str(society_name), cell_norm),
         Paragraph('Recon Timestamp:', cell_bold), Paragraph(recon_time, cell_norm)],
        [Paragraph('Safe Assembly Point:', cell_bold), Paragraph(str(safe_zone), cell_norm),
         Paragraph('Vision Payload:', cell_bold), Paragraph(str(model_name)[:28], cell_norm)],
        [Paragraph('Main Access Gate:', cell_bold), Paragraph(str(gate_name), cell_norm),
         Paragraph('Operational Edge:', cell_bold), Paragraph('Apple Silicon MPS (Offline)', cell_norm)]
    ]
    t_meta = Table(meta_data, colWidths=[115, 155, 115, 155])
    t_meta.setStyle(TableStyle([
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LINEBELOW', (0,-1), (-1,-1), 0.5, colors.HexColor('#d0d7de')),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 10))

    # Tactical Summary Table
    story.append(Paragraph('<b>1. EXECUTIVE TRIAGE & COMMUNITY SAFETY AUDIT</b>', styles['Heading2']))
    
    p_count = counts.get('Person', 0)
    d_count = counts.get('Dog', 0)
    c_count = counts.get('Car', 0)

    gate_status_str = f"BLOCKED ({c_count} Obstacle{'s' if c_count != 1 else ''})" if gate_blocked else "CLEAR (Accessible)"
    gate_action_str = "Dispatch Security / Towing to clear gate for fire engines" if gate_blocked else "Maintain clear lane for emergency vehicles"
    hazard_status_str = "CRITICAL HIGH-HEAT ANOMALY (>300°C)" if thermal_hazard else "NORMAL (Safe)"
    hazard_action_str = "Isolate gas mains / DG sets; dispatch foam suppression" if thermal_hazard else "No active gas or transformer fire flares detected"

    triage_data = [
        ['Assessment Category', 'Count / Status', 'Action Required'],
        ['Trapped Residents (Persons)', f"{p_count} Confirmed", 'Immediate Void Extraction & Heavy Shoring Squad' if p_count > 0 else 'Sector clear of confirmed human heat signatures'],
        ['Search & Rescue K9s', f"{d_count} Active", 'Canine search grid active' if d_count > 0 else 'K9 teams on standby'],
        [f'Society Gate & Driveway ({gate_name})', gate_status_str, gate_action_str],
        ['Utility Corridors (Gas/Transformer)', hazard_status_str, hazard_action_str]
    ]
    t_triage = Table(triage_data, colWidths=[175, 135, 230])
    t_triage.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#161b22')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#d0d7de')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#f6f8fa'), colors.white]),
        ('TEXTCOLOR', (1,3), (1,3), colors.HexColor('#cf222e') if gate_blocked else colors.HexColor('#1a7f37')),
        ('TEXTCOLOR', (1,4), (1,4), colors.HexColor('#cf222e') if thermal_hazard else colors.HexColor('#1a7f37')),
    ]))
    story.append(t_triage)
    story.append(Spacer(1, 12))

    # Target Detections Roster
    story.append(Paragraph('<b>2. CONFIRMED TARGET DETECTIONS ROSTER</b>', styles['Heading2']))
    if detections:
        det_headers = ['Target ID', 'Classification', 'Confidence', 'Bounding Box (x1, y1, x2, y2)', 'USAR Priority']
        det_rows = [det_headers]
        for idx, d in enumerate(detections[:15]):  # Up to 15 entries
            cid_name = d.get('Category', 'Unknown')
            conf_str = d.get('Confidence', '0%')
            coords = d.get('Coordinates', [0,0,0,0])
            coord_str = f"[{coords[0]}, {coords[1]}, {coords[2]}, {coords[3]}]"
            
            if cid_name == 'Person':
                prio = 'Priority 1 (Extraction)'
            elif cid_name == 'Dog':
                prio = 'Priority 3 (SAR K9)'
            else:
                prio = 'Priority 4 (Gate Obstacle)'
            
            det_rows.append([
                d.get('Target ID', f"TRG-{idx+1:02d}"),
                cid_name,
                conf_str,
                coord_str,
                prio
            ])
        
        t_det = Table(det_rows, colWidths=[70, 90, 75, 175, 130])
        t_det.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#24292f')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#d0d7de')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f6f8fa')])
        ]))
        story.append(t_det)
    else:
        story.append(Paragraph('<i>No confirmed thermal or optical targets detected in current reconnaissance sweep.</i>', styles['Normal']))
    
    story.append(Spacer(1, 16))

    # Official Sign-off section
    story.append(KeepTogether([
        Paragraph('<b>3. INCIDENT COMMAND VERIFICATION & SIGN-OFF</b>', styles['Heading2']),
        Spacer(1, 6),
        Table([
            [
                Paragraph('___________________________________<br/><b>RWA Emergency Controller</b><br/>Residential Society Management', styles['Normal']),
                Paragraph('___________________________________<br/><b>USAR Incident Commander</b><br/>Fire & Rescue Services', styles['Normal']),
                Paragraph('___________________________________<br/><b>Chief Security Officer</b><br/>Access Gate & Perimeter Control', styles['Normal'])
            ]
        ], colWidths=[180, 180, 180])
    ]))

    doc.build(story)
    return buffer.getvalue()
