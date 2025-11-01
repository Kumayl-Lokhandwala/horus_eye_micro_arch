from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch

# --- Define Simple Colors ---
COLOR_BODY_TEXT = colors.HexColor("#333333")
COLOR_LIGHT_GREY_BG = colors.HexColor("#F0F0F0")
COLOR_CONFIDENTIAL = colors.HexColor("#A8A8A8")

# --- Define Severity Colors ---
SEVERITY_COLORS = {
    'Critical': colors.HexColor("#D90429"),
    'High': colors.HexColor("#EF476F"),
    'Medium': colors.HexColor("#FCA311"),
    'Low': colors.HexColor("#2A9D8F"),
    'Informational': colors.HexColor("#457B9D"),
}

def draw_header_footer_and_watermark(canvas, doc, header_text="Consolidated Security Report"):
    """Draws the watermark, header, and footer on each page."""
    canvas.saveState() # Save the original state
    
    page_width = doc.width + doc.leftMargin + doc.rightMargin
    page_height = doc.height + doc.topMargin + doc.bottomMargin

    # --- 1. WATERMARK (DRAWN FIRST TO BE BEHIND) ---
    canvas.saveState() # Save state for watermark transforms
    
    canvas.setFont('Helvetica-Bold', 100)
    canvas.setFillColor(colors.Color(0.85, 0.85, 0.85, alpha=0.2)) 
    center_x = page_width / 2
    center_y = page_height / 2
    canvas.translate(center_x, center_y)
    canvas.rotate(45)
    canvas.drawCentredString(0, 0, "HORUSEYE")
    canvas.restoreState()
    # --- END WATERMARK ---

    # --- 2. HEADER (DRAWN ON TOP OF WATERMARK) ---
    canvas.setFont('Helvetica-Bold', 12)
    canvas.setFillColor(colors.black)
    canvas.drawString(doc.leftMargin, page_height - doc.topMargin + inch*0.5, header_text) # Use dynamic header
    
    canvas.setFont('Helvetica', 9)
    canvas.setFillColor(colors.darkgrey)
    canvas.drawRightString(page_width - doc.rightMargin, page_height - doc.topMargin + inch*0.5, f"Page {canvas.getPageNumber()}")
    
    canvas.setStrokeColor(colors.darkgrey)
    canvas.setLineWidth(1)
    canvas.line(doc.leftMargin, page_height - doc.topMargin + inch*0.35, page_width - doc.rightMargin, page_height - doc.topMargin + inch*0.35)

    # --- 3. FOOTER (DRAWN ON TOP OF WATERMARK) ---
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(COLOR_CONFIDENTIAL)
    canvas.drawString(doc.leftMargin, doc.bottomMargin - inch*0.3, "CONFIDENTIAL REPORT")
    
    canvas.setStrokeColor(COLOR_CONFIDENTIAL)
    canvas.setLineWidth(0.5)
    canvas.line(doc.leftMargin, doc.bottomMargin - inch*0.1, page_width - doc.rightMargin, doc.bottomMargin - inch*0.1)
    
    canvas.restoreState()

def create_pdf_report(report_data, report_type):
    """Generates a clean, well-formatted PDF report with watermark and type-specific headings."""
    
    print(f"Generating {report_type} PDF report with watermark...")
    buffer = BytesIO()
    
    doc = SimpleDocTemplate(buffer, pagesize=letter, 
                            rightMargin=0.75*inch, leftMargin=0.75*inch, 
                            topMargin=1.2*inch, bottomMargin=1.0*inch)
    
    styles = getSampleStyleSheet()
    
    # --- Clean, Professional Styles ---
    styles.add(ParagraphStyle(name='TitleStyle', 
                              fontSize=20, 
                              fontName='Helvetica-Bold', 
                              alignment=1,
                              spaceAfter=24,
                              spaceBefore=10))
    
    styles.add(ParagraphStyle(name='H1', 
                              fontSize=16, 
                              fontName='Helvetica-Bold', 
                              spaceAfter=12, 
                              spaceBefore=18,
                              underlineWidth=1,
                              underlineColor=colors.black,
                              underlineOffset=-6))
    
    styles.add(ParagraphStyle(name='H2', 
                              fontSize=14, 
                              fontName='Helvetica-Bold', 
                              spaceAfter=8, 
                              spaceBefore=14))
    
    styles.add(ParagraphStyle(name='H3_Label', 
                              fontSize=11, 
                              fontName='Helvetica-Bold', 
                              spaceAfter=4, 
                              spaceBefore=10))
    
    styles.add(ParagraphStyle(name='Body', 
                              fontSize=10, 
                              fontName='Helvetica', 
                              leading=14,
                              spaceAfter=8,
                              alignment=4))
    
    styles.add(ParagraphStyle(name='Evidence', 
                              fontSize=9, 
                              fontName='Courier', 
                              leading=12,
                              leftIndent=12,
                              spaceAfter=10,
                              backColor=colors.HexColor("#f8f8f8")))
    
    styles.add(ParagraphStyle(name='Severity', 
                              fontSize=10, 
                              fontName='Helvetica-Bold', 
                              spaceAfter=6, 
                              spaceBefore=10))
    
    styles.add(ParagraphStyle(name='Disclaimer', 
                              fontSize=9, 
                              fontName='Helvetica-Oblique', 
                              leading=12,
                              spaceAfter=8,
                              alignment=4))

    # Determine report type and set appropriate headings
    if report_type.lower() == 'vulnr':
        main_title = "Vulnerability Assessment Report"
        critical_section_title = "Critical Vulnerabilities"
        analysis_section_title = "Vulnerability Analysis"
        header_text = "Vulnerability Assessment Report"
    else:  # Default to reconnaissance
        main_title = "Reconnaissance Intelligence Report"
        critical_section_title = "Key Intelligence Findings"
        analysis_section_title = "Technical Reconnaissance Analysis"
        header_text = "Reconnaissance Report"

    flowables = []

    # 1. Title (Dynamic based on report type)
    flowables.append(Paragraph(main_title, styles['TitleStyle']))
    flowables.append(Spacer(1, 0.3 * inch))

    # 2. Executive Summary
    flowables.append(Paragraph("Executive Summary", styles['H1']))
    exec_summary = report_data.get('executive_summary', 'No executive summary provided.')
    summary_paragraphs = exec_summary.split('\n\n')
    for para in summary_paragraphs:
        if para.strip():
            flowables.append(Paragraph(para.strip(), styles['Body']))
            flowables.append(Spacer(1, 0.1 * inch))
    flowables.append(Spacer(1, 0.25 * inch))

    # 3. Critical Findings Section (Dynamic title)
    flowables.append(Paragraph(critical_section_title, styles['H1']))
    correlated_findings = report_data.get('correlated_findings', [])
    
    if not correlated_findings:
        if report_type.lower() == 'vulnr':
            no_findings_text = "No critical vulnerabilities were identified."
        else:
            no_findings_text = "No critical reconnaissance findings were identified."
        flowables.append(Paragraph(no_findings_text, styles['Body']))
        flowables.append(Spacer(1, 0.1 * inch))
    else:
        for i, finding in enumerate(correlated_findings, 1):
            if report_type.lower() == 'vulnr':
                flowables.append(Paragraph(f"Vulnerability {i}", styles['H2']))
            else:
                flowables.append(Paragraph(f"Finding {i}", styles['H2']))
            
            flowables.append(Paragraph("Description:", styles['H3_Label']))
            flowables.append(Paragraph(finding.get('correlated_finding', 'No description'), styles['Body']))
            
            flowables.append(Paragraph("Impact:", styles['H3_Label']))
            flowables.append(Paragraph(finding.get('impact', 'No impact assessment'), styles['Body']))
            
            flowables.append(Paragraph("Recommendation:", styles['H3_Label']))
            flowables.append(Paragraph(finding.get('recommendation', 'No recommendation'), styles['Body']))
            
            if i < len(correlated_findings):
                flowables.append(Spacer(1, 0.15 * inch))
    
    flowables.append(Spacer(1, 0.3 * inch))

    # 4. Detailed Analysis Section (Dynamic title)
    flowables.append(Paragraph(analysis_section_title, styles['H1']))
    
    for tool in report_data.get('detailed_analysis', []):
        tool_name = tool.get('tool_name', 'Unknown Tool').upper()
        flowables.append(Paragraph(f"Tool: {tool_name}", styles['H2']))
        
        tool_findings = tool.get('findings', [])
        if not tool_findings:
            flowables.append(Paragraph("No findings reported for this tool.", styles['Body']))
            flowables.append(Spacer(1, 0.2 * inch))
        else:
            for finding in tool_findings:
                # Severity
                sev = finding.get('severity', 'Informational')
                sev_color = SEVERITY_COLORS.get(sev.capitalize(), colors.darkgrey)
                sev_text = f"<b>Severity:</b> <font color='{sev_color.hexval()}'>{sev}</font>"
                flowables.append(Paragraph(sev_text, styles['Severity']))
                
                # Description
                flowables.append(Paragraph("Description:", styles['H3_Label']))
                flowables.append(Paragraph(finding.get('description', 'No description'), styles['Body']))
                
                # Evidence
                evidence = finding.get('evidence', 'No evidence')
                if evidence and evidence != 'No evidence':
                    flowables.append(Paragraph("Evidence:", styles['H3_Label']))
                    flowables.append(Paragraph(evidence.replace('\n', '<br/>'), styles['Evidence']))
                
                # Recommendation
                flowables.append(Paragraph("Recommendation:", styles['H3_Label']))
                flowables.append(Paragraph(finding.get('recommendation', 'No recommendation'), styles['Body']))
                
                flowables.append(Spacer(1, 0.2 * inch))
        
        flowables.append(Spacer(1, 0.2 * inch))
    
    # 5. Disclaimer Section
    flowables.append(Spacer(1, 0.3 * inch))
    flowables.append(Paragraph("Disclaimer", styles['H2']))
    
    disclaimer_text = """
    <i>This report is generated automatically by the HorusEye Automated Pen-testing Platform. 
    The findings and recommendations provided are based on automated security scans and 
    should be reviewed by qualified security professionals. The platform is not responsible 
    for any damages or liabilities arising from the use of this report. It is recommended 
    to validate all findings manually and consider the specific context of your environment 
    before implementing any security changes. This report is intended for authorized 
    security assessment purposes only.</i>
    """
    
    flowables.append(Paragraph(disclaimer_text, styles['Disclaimer']))
    flowables.append(Spacer(1, 0.2 * inch))
        
    # Build PDF with header, footer and watermark
    # We pass the dynamic header_text to the draw function
    doc.build(flowables, onFirstPage=lambda c, d: draw_header_footer_and_watermark(c, d, header_text=header_text), 
              onLaterPages=lambda c, d: draw_header_footer_and_watermark(c, d, header_text=header_text))
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    print(f"{report_type.capitalize()} PDF report with watermark generation complete.")
    return pdf_bytes
