import os
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from app.core.config import settings

class CertificateGenerator:
    def __init__(self):
        self.output_dir = settings.OUTPUT_DIRECTORY
        
    def _ensure_dir(self, job_id: str) -> str:
        job_dir = os.path.join(self.output_dir, job_id)
        os.makedirs(job_dir, exist_ok=True)
        return job_dir
        
    def generate(self, job_id: str, certificate_id: str, recipient_name: str, event_name: str, event_date: str, issuer_name: str) -> str:
        job_dir = self._ensure_dir(job_id)
        file_path = os.path.join(job_dir, f"{certificate_id}.pdf")
        
        c = canvas.Canvas(file_path, pagesize=landscape(A4))
        width, height = landscape(A4)
        
        # Draw Ivory Background
        c.setFillColor(HexColor("#F9F6F0"))
        c.rect(0, 0, width, height, fill=1, stroke=0)
        
        # Draw Outer Gold Border
        c.setStrokeColor(HexColor("#D4AF37"))
        c.setLineWidth(12)
        c.rect(0.5 * inch, 0.5 * inch, width - 1 * inch, height - 1 * inch)
        
        # Draw Inner Fine Gold Border
        c.setLineWidth(1.5)
        c.rect(0.7 * inch, 0.7 * inch, width - 1.4 * inch, height - 1.4 * inch)
        
        # Draw Header Ribbon
        c.setFillColor(HexColor("#1e293b")) # Dark Slate
        c.rect(0.7 * inch, height - 2.5 * inch, width - 1.4 * inch, 1.8 * inch, fill=1, stroke=0)
        
        c.setFillColor(HexColor("#FFFFFF"))
        c.setFont("Times-BoldItalic", 42)
        c.drawCentredString(width / 2.0, height - 1.8 * inch, "CERTIFICATE OF EXCELLENCE")
        
        # Sub-header
        c.setFillColor(HexColor("#555555"))
        c.setFont("Helvetica", 14)
        c.drawCentredString(width / 2.0, height - 3.2 * inch, "THIS IS PROUDLY PRESENTED TO")
        
        # Recipient Name
        c.setFillColor(HexColor("#D4AF37"))
        c.setFont("Times-BoldItalic", 38)
        c.drawCentredString(width / 2.0, height - 4.2 * inch, recipient_name)
        
        # Divider Line
        c.setStrokeColor(HexColor("#D4AF37"))
        c.setLineWidth(1)
        c.line(width / 2.0 - 2.5 * inch, height - 4.4 * inch, width / 2.0 + 2.5 * inch, height - 4.4 * inch)
        
        # Description
        c.setFillColor(HexColor("#333333"))
        c.setFont("Helvetica", 12)
        c.drawCentredString(width / 2.0, height - 4.9 * inch, "For outstanding achievement and participation in")
        
        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(width / 2.0, height - 5.5 * inch, event_name.upper())
        
        # Signatures
        c.setFillColor(HexColor("#333333"))
        c.setFont("Helvetica-Bold", 12)
        c.drawString(1.5 * inch, 1.8 * inch, event_date)
        c.setStrokeColor(HexColor("#888888"))
        c.line(1.5 * inch, 1.6 * inch, 3.5 * inch, 1.6 * inch)
        c.setFont("Helvetica", 10)
        c.drawString(1.5 * inch, 1.35 * inch, "DATE")
        
        c.setFont("Helvetica-Bold", 12)
        c.drawRightString(width - 1.5 * inch, 1.8 * inch, issuer_name)
        c.line(width - 4.0 * inch, 1.6 * inch, width - 1.5 * inch, 1.6 * inch)
        c.setFont("Helvetica", 10)
        c.drawRightString(width - 1.5 * inch, 1.35 * inch, "ISSUER")
        
        c.save()
        return file_path
