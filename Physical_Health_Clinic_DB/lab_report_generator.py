# lab_report_generator.py
import os
import json
from datetime import datetime
from database import connect_db

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, KeepTogether
    from reportlab.graphics.shapes import Drawing, Rect, String, Group, Line
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


def _get_medical_logo_drawing():
    """Generate a vector medical logo graphic for lab report header."""
    d = Drawing(44, 44)
    # Royal blue rounded background
    d.add(Rect(0, 0, 44, 44, fillColor=colors.HexColor('#1E3A8A'), strokeColor=None, rx=8, ry=8))
    # White cross
    d.add(Rect(18, 9, 8, 26, fillColor=colors.white, strokeColor=None))
    d.add(Rect(9, 18, 26, 8, fillColor=colors.white, strokeColor=None))
    # Red heart accent
    d.add(Rect(19, 19, 6, 6, fillColor=colors.HexColor('#EF4444'), strokeColor=None))
    return d


def _get_qr_matrix_drawing(text_val="VERIFIED-LAB-REPORT"):
    """Generate a vector QR code simulation block for authenticity verification."""
    d = Drawing(45, 45)
    d.add(Rect(0, 0, 45, 45, fillColor=colors.white, strokeColor=colors.HexColor('#CBD5E1'), strokeWidth=0.5, rx=4, ry=4))
    # Corner alignment boxes
    d.add(Rect(3, 3, 11, 11, fillColor=colors.HexColor('#0F172A'), strokeColor=None))
    d.add(Rect(5, 5, 7, 7, fillColor=colors.white, strokeColor=None))
    d.add(Rect(7, 7, 3, 3, fillColor=colors.HexColor('#0F172A'), strokeColor=None))

    d.add(Rect(31, 3, 11, 11, fillColor=colors.HexColor('#0F172A'), strokeColor=None))
    d.add(Rect(33, 5, 7, 7, fillColor=colors.white, strokeColor=None))
    d.add(Rect(35, 7, 3, 3, fillColor=colors.HexColor('#0F172A'), strokeColor=None))

    d.add(Rect(3, 31, 11, 11, fillColor=colors.HexColor('#0F172A'), strokeColor=None))
    d.add(Rect(5, 33, 7, 7, fillColor=colors.white, strokeColor=None))
    d.add(Rect(7, 35, 3, 3, fillColor=colors.HexColor('#0F172A'), strokeColor=None))

    # Inner data matrix pixels
    data_bits = [
        (16, 4, 3, 3), (22, 6, 4, 3), (26, 4, 3, 3),
        (16, 12, 4, 4), (22, 14, 3, 3), (26, 12, 4, 3),
        (4, 18, 4, 3), (10, 20, 3, 3), (16, 18, 4, 4), (22, 20, 3, 3), (28, 18, 4, 3), (34, 20, 3, 3),
        (4, 24, 3, 3), (10, 26, 4, 3), (16, 24, 3, 4), (24, 26, 4, 3), (30, 24, 3, 3), (36, 26, 4, 3),
        (16, 30, 4, 3), (22, 32, 3, 3), (28, 30, 4, 4), (34, 32, 3, 3),
        (16, 36, 3, 3), (22, 38, 4, 3), (26, 36, 3, 3), (32, 38, 4, 3)
    ]
    for x, y, w, h in data_bits:
        d.add(Rect(x, y, w, h, fillColor=colors.HexColor('#0F172A'), strokeColor=None))
    return d


def build_lab_test_report_elements(request_id, test_id):
    """Build ReportLab flowable elements for a single lab test A4 page."""
    if not PDF_AVAILABLE:
        raise RuntimeError("ReportLab library is required for PDF generation.")

    conn = connect_db()
    cursor = conn.cursor()

    # 1. Fetch Request & Patient & Doctor details
    cursor.execute("""
        SELECT 
            lr.RequestID, lr.RequestDate, p.PatientID, p.FullName, p.Gender, p.DateOfBirth, p.PhoneNumber,
            doc.FullName AS DoctorName, doc.WorkerID AS DoctorWorkerID
        FROM Laboratory_Requests lr
        JOIN Patients p ON lr.PatientID = p.PatientID
        LEFT JOIN Health_Workers doc ON lr.DoctorID = doc.WorkerID
        WHERE lr.RequestID = %s
    """, (request_id,))
    req_row = cursor.fetchone()
    if not req_row:
        conn.close()
        raise ValueError(f"Laboratory Request #{request_id} not found.")

    req_id, req_date, pat_id, pat_name, pat_gender, pat_dob, pat_phone, doc_name, doc_id = req_row

    # 2. Fetch Result details & Technician details
    cursor.execute("""
        SELECT 
            res.ResultID, res.ResultDetails, res.TestDate, lt.TestName, lt.TestID,
            tech.FullName AS TechName, tech.WorkerID AS TechWorkerID
        FROM Laboratory_Results res
        JOIN Laboratory_Tests lt ON res.TestID = lt.TestID
        LEFT JOIN Health_Workers tech ON res.TechnicianID = tech.WorkerID
        WHERE res.RequestID = %s AND res.TestID = %s
    """, (request_id, test_id))
    res_row = cursor.fetchone()
    if not res_row:
        conn.close()
        raise ValueError(f"No result found for Request #{request_id}, Test #{test_id}.")

    res_id, raw_details, test_date, test_name, t_id, tech_name, tech_id = res_row

    # 3. Fetch active Template for this test
    cursor.execute("""
        SELECT TemplateName, TemplateDescription, TemplateFields, ReferenceRanges, MeasurementUnits, DefaultComments
        FROM laboratory_templates
        WHERE TestID = %s AND Status = 'Active'
        ORDER BY TemplateID DESC LIMIT 1
    """, (test_id,))
    tpl_row = cursor.fetchone()

    tpl_name = tpl_row[0] if tpl_row else f"{test_name} Template"
    tpl_desc = tpl_row[1] if tpl_row else ""
    tpl_fields = json.loads(tpl_row[2]) if (tpl_row and tpl_row[2]) else []
    tpl_ranges = json.loads(tpl_row[3]) if (tpl_row and tpl_row[3]) else {}
    tpl_units = json.loads(tpl_row[4]) if (tpl_row and tpl_row[4]) else {}
    default_comments = tpl_row[5] if (tpl_row and tpl_row[5]) else ""

    conn.close()

    # Parse Result Details JSON
    patient_values = {}
    tech_notes = ""
    if raw_details:
        try:
            parsed = json.loads(raw_details)
            if isinstance(parsed, dict):
                patient_values = parsed.get("values", parsed)
                tech_notes = parsed.get("notes", "")
            else:
                tech_notes = str(raw_details)
        except Exception:
            tech_notes = str(raw_details)

    # Styles Setup
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'HeaderTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=14, leading=16,
        textColor=colors.HexColor('#1E3A8A')
    )
    motto_style = ParagraphStyle(
        'HeaderMotto', parent=styles['Normal'],
        fontName='Helvetica-Oblique', fontSize=8.5, leading=11,
        textColor=colors.HexColor('#2563EB')
    )
    meta_style = ParagraphStyle(
        'MetaText', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8.5, leading=12,
        textColor=colors.HexColor('#0F172A')
    )
    banner_style = ParagraphStyle(
        'BannerText', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=12, leading=14,
        alignment=TA_CENTER, textColor=colors.HexColor('#1E3A8A')
    )
    table_header_style = ParagraphStyle(
        'TableHeader', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=9, leading=11,
        textColor=colors.white
    )
    cell_style = ParagraphStyle(
        'TableCell', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8.5, leading=11,
        textColor=colors.HexColor('#1E293B')
    )
    cell_bold_style = ParagraphStyle(
        'TableCellBold', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8.5, leading=11,
        textColor=colors.HexColor('#0F172A')
    )
    comment_style = ParagraphStyle(
        'CommentText', parent=styles['Normal'],
        fontName='Helvetica-Oblique', fontSize=8.5, leading=12,
        textColor=colors.HexColor('#334155')
    )

    elements = []

    # 1. Clinic Header
    logo = _get_medical_logo_drawing()
    header_para = Paragraph(
        "<b>PHYSICAL HEALTH CLINIC — LABORATORY SERVICES</b><br/>"
        "<i>“Quality Healthcare, Trusted Care”</i><br/>"
        "📍 123 Hospital Road, Freetown, Sierra Leone  |  📞 +232 76 123 456  |  🌐 physicalhealthclinic.sl",
        title_style
    )
    header_table = Table([[logo, header_para]], colWidths=[50, 465])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 2),
        ('LINEBELOW', (0,0), (-1,-1), 1.5, colors.HexColor('#1E3A8A')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 6))

    # 2. Report Title Banner
    banner_table = Table([[Paragraph(f"••• {test_name.upper()} REPORT •••", banner_style)]], colWidths=[515])
    banner_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#EFF6FF')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(banner_table)
    elements.append(Spacer(1, 6))

    # 3. Patient & Request Metadata Panel
    spec_date_str = test_date.strftime("%Y-%m-%d %H:%M") if isinstance(test_date, datetime) else str(test_date or datetime.now().strftime("%Y-%m-%d %H:%M"))
    doc_str = f"Dr. {doc_name} (ID: HW-{doc_id:03d})" if doc_id else (doc_name or "N/A")
    tech_str = f"{tech_name} (ID: HW-{tech_id:03d})" if tech_id else (tech_name or "Lab Technician")

    meta_left = (
        f"<b>Patient Name:</b> {pat_name}<br/>"
        f"<b>Patient ID:</b> PAT-{pat_id:05d}<br/>"
        f"<b>Gender / DOB:</b> {pat_gender or 'N/A'} | {pat_dob or 'N/A'}<br/>"
        f"<b>Phone:</b> {pat_phone or 'N/A'}"
    )
    meta_right = (
        f"<b>Lab Request ID:</b> LAB-REQ-{req_id:06d}<br/>"
        f"<b>Requesting Doctor:</b> {doc_str}<br/>"
        f"<b>Specimen Date:</b> {spec_date_str}<br/>"
        f"<b>Laboratory Technician:</b> {tech_str}"
    )
    meta_table = Table([[Paragraph(meta_left, meta_style), Paragraph(meta_right, meta_style)]], colWidths=[255, 260])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 8))

    # 4. Parameter Results Table
    t_headers = [
        Paragraph("<b>Test Parameter</b>", table_header_style),
        Paragraph("<b>Patient Result</b>", table_header_style),
        Paragraph("<b>Unit</b>", table_header_style),
        Paragraph("<b>Reference Range</b>", table_header_style),
        Paragraph("<b>Status / Flag</b>", table_header_style)
    ]
    table_data = [t_headers]

    if tpl_fields:
        for f in tpl_fields:
            p_name = f.get("name", "")
            unit = f.get("unit", "")
            ref_range = f.get("range", "")
            val = str(patient_values.get(p_name, f.get("default", "N/A")))
            
            # Basic status flag evaluation
            flag_text = "NORMAL"
            flag_color = colors.HexColor('#16A34A')
            if val.lower() in ["positive", "reactive", "high", "abnormal"]:
                flag_text = "ABNORMAL"
                flag_color = colors.HexColor('#DC2626')

            flag_style = ParagraphStyle(
                'FlagStyle', parent=styles['Normal'],
                fontName='Helvetica-Bold', fontSize=8, leading=10,
                alignment=TA_CENTER, textColor=flag_color
            )

            table_data.append([
                Paragraph(p_name, cell_bold_style),
                Paragraph(f"<b>{val}</b>", cell_style),
                Paragraph(unit, cell_style),
                Paragraph(ref_range, cell_style),
                Paragraph(flag_text, flag_style)
            ])
    else:
        # Fallback if raw text result
        table_data.append([
            Paragraph(test_name, cell_bold_style),
            Paragraph(str(patient_values or raw_details or "Completed"), cell_style),
            Paragraph("Clinical", cell_style),
            Paragraph("Standard", cell_style),
            Paragraph("NORMAL", cell_style)
        ])

    results_table = Table(table_data, colWidths=[165, 110, 75, 105, 60])
    results_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A8A')),
        ('ALIGN', (0,0), (-1,0), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')])
    ]))
    elements.append(results_table)
    elements.append(Spacer(1, 8))

    # 5. Lab Comments & Interpretation Box
    comments_body = []
    if default_comments:
        comments_body.append(f"<b>Standard Interpretation:</b> {default_comments}")
    if tech_notes:
        comments_body.append(f"<b>Technician Notes:</b> {tech_notes}")
    if not comments_body:
        comments_body.append("<i>Result verified and released by Physical Health Clinic Laboratory.</i>")

    comment_para = Paragraph("<br/>".join(comments_body), comment_style)
    comment_table = Table([[comment_para]], colWidths=[515])
    comment_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FEFCE8')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#FEF08A')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(comment_table)
    elements.append(Spacer(1, 10))

    # 6. Footer Signatures & QR Verification
    qr = _get_qr_matrix_drawing(f"LAB-{req_id}-{test_id}")
    sig_left = (
        f"<b>Reported By:</b> {tech_str}<br/>"
        f"<b>Designation:</b> Medical Laboratory Technician<br/>"
        f"<b>Signature:</b> ___________________________"
    )
    sig_right = (
        f"<b>Verified By:</b> Head of Laboratory Services<br/>"
        f"<b>Status:</b> ✅ APPROVED & RELEASED<br/>"
        f"<b>Signature:</b> ___________________________"
    )
    footer_table = Table([[qr, Paragraph(sig_left, meta_style), Paragraph(sig_right, meta_style)]], colWidths=[55, 230, 230])
    footer_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 2),
    ]))
    elements.append(footer_table)

    return elements


def generate_single_lab_report_pdf(request_id, test_id, output_path):
    """Generate a single A4 lab report PDF file."""
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    elements = build_lab_test_report_elements(request_id, test_id)
    doc.build(elements)
    return output_path


def generate_combined_lab_report_pdf(request_id, output_path):
    """Generate a multi-page combined A4 PDF report for all tests in a request."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT TestID FROM Laboratory_Results WHERE RequestID = %s", (request_id,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        raise ValueError(f"No completed tests found for Request #{request_id}.")

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    all_elements = []
    for idx, (t_id,) in enumerate(rows):
        if idx > 0:
            all_elements.append(PageBreak())
        elems = build_lab_test_report_elements(request_id, t_id)
        all_elements.extend(elems)

    doc.build(all_elements)
    return output_path
