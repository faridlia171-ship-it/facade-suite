"""Générateur de PDF pour les devis."""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
from typing import List


def generate_quote_pdf(
    company_name: str,
    customer_name: str,
    customer_city: str,
    project_name: str,
    version: int,
    lines: List,
    total: float,
    is_trial: bool = False
) -> bytes:
    """Génère un PDF de devis."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30
    )
    
    elements = []
    
    # En-tête verrouillé
    header_data = [
        [Paragraph(f"<b>{company_name}</b>", styles['Heading1'])],
        [Paragraph("Devis de façade", title_style)],
        [Paragraph(f"Version {version}", styles['Normal'])]
    ]
    header_table = Table(header_data, colWidths=[15*cm])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 1*cm))
    
    # Informations client
    client_data = [
        ["Client:", customer_name],
        ["Ville:", customer_city or ""],
        ["Chantier:", project_name]
    ]
    client_table = Table(client_data, colWidths=[4*cm, 11*cm])
    client_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(client_table)
    elements.append(Spacer(1, 1*cm))
    
    # Lignes du devis
    line_data = [["Description", "Quantité", "Prix unitaire", "Total"]]
    for line in lines:
        line_data.append([
            line.label,
            f"{float(line.quantity):.2f}",
            f"{float(line.unit_price):.2f} €",
            f"{float(line.total):.2f} €"
        ])
    
    # Ligne total
    line_data.append(["", "", "TOTAL", f"{total:.2f} €"])
    
    lines_table = Table(line_data, colWidths=[8*cm, 2*cm, 3*cm, 3*cm])
    lines_table.setStyle(TableStyle([
        # En-tête
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#333333')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        # Corps
        ('ALIGN', (0, 1), (0, -2), 'LEFT'),
        ('ALIGN', (1, 1), (-1, -2), 'RIGHT'),
        ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
        # Total
        ('FONTNAME', (2, -1), (-1, -1), 'Helvetica-Bold'),
        ('ALIGN', (2, -1), (-1, -1), 'RIGHT'),
        ('BACKGROUND', (2, -1), (-1, -1), colors.HexColor('#f0f0f0')),
        ('LINEABOVE', (2, -1), (-1, -1), 2, colors.black),
    ]))
    elements.append(lines_table)
    elements.append(Spacer(1, 1*cm))
    
    # Filigrane TRIAL si nécessaire
    if is_trial:
        watermark = Paragraph(
            "<b>TRIAL - Document non contractuel</b>",
            ParagraphStyle(
                'Watermark',
                parent=styles['Normal'],
                fontSize=14,
                textColor=colors.HexColor('#ff0000'),
                alignment=1
            )
        )
        elements.append(watermark)
    
    # Mentions légales
    elements.append(Spacer(1, 2*cm))
    footer = Paragraph(
        "Développé par El Bennouni Farid pour SARL Plein Sud Crépis - RCS 50113927300020",
        ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=1
        )
    )
    elements.append(footer)
    
    # Générer le PDF
    doc.build(elements)
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes
