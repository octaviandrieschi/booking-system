from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from datetime import datetime

def generate_receipt_pdf(receipt_data, output_path):
    """
    Generează un PDF pentru chitanță
    
    Args:
        receipt_data (dict): Datele chitanței
        output_path (str): Calea unde va fi salvat PDF-ul
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )

    # Creează lista de elemente pentru PDF
    elements = []
    styles = getSampleStyleSheet()
    
    # Adaugă titlul
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    elements.append(Paragraph("Confirmare Rezervare", title_style))
    elements.append(Spacer(1, 20))

    # Informații chitanță
    elements.append(Paragraph(f"Număr: {receipt_data['receipt_number']}", styles['Normal']))
    elements.append(Paragraph(f"Data emiterii: {format_date(receipt_data['date_issued'])}", styles['Normal']))
    elements.append(Spacer(1, 20))

    # Detalii client și serviciu
    data = [
        ['Client', 'Serviciu'],
        [
            Paragraph(f"{receipt_data['client_name']}<br/>{receipt_data['client_email']}", styles['Normal']),
            Paragraph(f"{receipt_data['service_name']}<br/>Data: {format_date(receipt_data['date_time'])}", styles['Normal'])
        ]
    ]

    table = Table(data, colWidths=[doc.width/2.0]*2)
    table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('TOPPADDING', (0, 1), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 12),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 30))

    # Total
    elements.append(Paragraph(
        f"Total: {receipt_data['total']} RON",
        ParagraphStyle(
            'CustomTotal',
            parent=styles['Normal'],
            fontSize=16,
            alignment=2  # Right alignment
        )
    ))

    # Generează PDF-ul
    doc.build(elements)

def format_date(date_string):
    """Formatează data pentru afișare în PDF"""
    date = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
    return date.strftime("%d %B %Y, %H:%M") 