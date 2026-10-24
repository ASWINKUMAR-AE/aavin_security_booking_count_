import logging
from typing import Dict, Any, Optional
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone

from ..models import GatePass
from .pdf_service import AavinGatePassPDFGenerator

logger = logging.getLogger(__name__)


class GatePassEmailService:
    """
    Handles PDF generation and dispatching gatepass documents via email.
    """

    @classmethod
    def send_gatepass_email(cls, gate_pass: GatePass, recipient_email: Optional[str] = None) -> Dict[str, Any]:
        """
        Generates the PDF report for gate_pass and emails it as an attachment.
        Updates gate_pass status and timestamp.
        """
        target_email = recipient_email or gate_pass.recipient_email or getattr(settings, 'DEFAULT_RECIPIENT_EMAIL', None)

        if not target_email:
            raise ValueError(
                f"No recipient email specified for Gatepass #{gate_pass.gate_pass_no}. "
                "Provide a recipient email address."
            )

        # 1. Generate PDF document bytes
        pdf_bytes = AavinGatePassPDFGenerator.generate_pdf(gate_pass)
        clean_vehicle = gate_pass.vehicle_no.replace(" ", "_")
        filename = f"Aavin_GatePass_{gate_pass.gate_pass_no}_{clean_vehicle}.pdf"

        # 2. Prepare Subject and Body
        date_str = gate_pass.date.strftime("%d-%b-%Y") if gate_pass.date else ""
        subject = f"[Aavin Dispatch] Gate Pass #{gate_pass.gate_pass_no} | {gate_pass.vehicle_no} | {gate_pass.route_name}"

        plain_text = f"""
Aavin Security Gatepass Dispatch Report
======================================
Gate Pass No : {gate_pass.gate_pass_no}
Vehicle No   : {gate_pass.vehicle_no}
Route        : {gate_pass.route_name}
Date / Shift : {date_str} / {gate_pass.shift}

Summary of Booking:
-------------------
Total Milk Litres : {gate_pass.total_litres} L
Total Tubs/Crates : {gate_pass.total_tubs}
Total Leaks       : {gate_pass.total_leaks}

Please find the detailed security gatepass attached as a PDF.

Regards,
Madurai District Co-operative Milk Producers' Union Ltd.
Security Booking System
"""

        html_content = f"""
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; color: #1e293b; line-height: 1.5; background-color: #f8fafc; padding: 20px;">
  <div style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 8px; border: 1px solid #e2e8f0; overflow: hidden;">
    <div style="background-color: #0b3c68; color: #ffffff; padding: 20px 24px;">
      <h2 style="margin: 0; font-size: 18px; letter-spacing: 0.5px;">THE MADURAI DISTRICT CO-OPERATIVE MILK PRODUCERS' UNION LTD.</h2>
      <p style="margin: 4px 0 0 0; font-size: 13px; color: #bae6fd;">Security Booking & Dispatch Verification</p>
    </div>

    <div style="padding: 24px;">
      <p style="font-size: 15px; margin-top: 0;">
        Hello,
        <br/><br/>
        The security gatepass for <strong>{gate_pass.vehicle_no}</strong> on route <strong>{gate_pass.route_name}</strong> has been processed.
      </p>

      <table style="width: 100%; border-collapse: collapse; margin: 20px 0; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px;">
        <tr>
          <td style="padding: 10px 14px; border-bottom: 1px solid #e2e8f0; font-weight: bold; width: 40%; color: #475569;">Gate Pass No.</td>
          <td style="padding: 10px 14px; border-bottom: 1px solid #e2e8f0; font-weight: bold; color: #0b3c68;">{gate_pass.gate_pass_no}</td>
        </tr>
        <tr>
          <td style="padding: 10px 14px; border-bottom: 1px solid #e2e8f0; font-weight: bold; color: #475569;">Vehicle No.</td>
          <td style="padding: 10px 14px; border-bottom: 1px solid #e2e8f0;">{gate_pass.vehicle_no}</td>
        </tr>
        <tr>
          <td style="padding: 10px 14px; border-bottom: 1px solid #e2e8f0; font-weight: bold; color: #475569;">Route</td>
          <td style="padding: 10px 14px; border-bottom: 1px solid #e2e8f0;">{gate_pass.route_name}</td>
        </tr>
        <tr>
          <td style="padding: 10px 14px; border-bottom: 1px solid #e2e8f0; font-weight: bold; color: #475569;">Date / Shift</td>
          <td style="padding: 10px 14px; border-bottom: 1px solid #e2e8f0;">{date_str} ({gate_pass.shift})</td>
        </tr>
        <tr>
          <td style="padding: 10px 14px; border-bottom: 1px solid #e2e8f0; font-weight: bold; color: #475569;">Total Milk Litres</td>
          <td style="padding: 10px 14px; border-bottom: 1px solid #e2e8f0; font-weight: bold; color: #0284c7;">{gate_pass.total_litres} L</td>
        </tr>
        <tr>
          <td style="padding: 10px 14px; border-bottom: 1px solid #e2e8f0; font-weight: bold; color: #475569;">Total Tubs / Crates</td>
          <td style="padding: 10px 14px; border-bottom: 1px solid #e2e8f0;">{gate_pass.total_tubs}</td>
        </tr>
        <tr>
          <td style="padding: 10px 14px; font-weight: bold; color: #475569;">Leaks Recorded</td>
          <td style="padding: 10px 14px; color: {'#dc2626' if gate_pass.total_leaks > 0 else '#16a34a'}; font-weight: bold;">{gate_pass.total_leaks}</td>
        </tr>
      </table>

      <p style="font-size: 14px; color: #64748b; margin-bottom: 0;">
        &bull; <i>The complete official Gatepass is attached as <strong>{filename}</strong>.</i>
      </p>
    </div>

    <div style="background-color: #f1f5f9; padding: 14px 24px; font-size: 12px; color: #64748b; border-top: 1px solid #e2e8f0;">
      Aavin Security Dispatch Automated System &bull; Madurai Dairy
    </div>
  </div>
</body>
</html>
"""

        # 3. Create EmailMessage and attach PDF
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'aavin.security.dispatch@gmail.com')
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_text.strip(),
            from_email=from_email,
            to=[target_email],
        )
        email.attach_alternative(html_content, "text/html")
        email.attach(filename, pdf_bytes, "application/pdf")

        # 4. Dispatch Email
        try:
            email.send(fail_silently=False)
            gate_pass.recipient_email = target_email
            gate_pass.sent_at = timezone.now()
            gate_pass.status = 'SENT'
            gate_pass.save()

            return {
                'success': True,
                'recipient': target_email,
                'gate_pass_no': gate_pass.gate_pass_no,
                'sent_at': gate_pass.sent_at,
                'filename': filename
            }
        except Exception as e:
            logger.exception("Failed to send Gatepass email: %s", str(e))
            gate_pass.status = 'FAILED'
            gate_pass.validation_notes += f"\nEmail dispatch error: {str(e)}"
            gate_pass.save()
            return {
                'success': False,
                'error': str(e),
                'recipient': target_email
            }
