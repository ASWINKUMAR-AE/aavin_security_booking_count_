from django.core.management.base import BaseCommand, CommandError
from reports.models import GatePass
from reports.services.pdf_service import AavinGatePassPDFGenerator
from reports.services.email_service import GatePassEmailService


class Command(BaseCommand):
    help = "Generate PDF and/or dispatch gatepass to recipient email"

    def add_arguments(self, parser):
        parser.add_argument(
            '--gatepass-no',
            type=str,
            default='139914',
            help='Gate Pass number to process (default: 139914)'
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Recipient email address to dispatch the PDF report'
        )
        parser.add_argument(
            '--save-pdf',
            type=str,
            help='Optional local file path to save the generated PDF (e.g. gatepass.pdf)'
        )

    def handle(self, *args, **options):
        gatepass_no = options['gatepass_no']
        email = options.get('email')
        save_path = options.get('save_pdf')

        try:
            gate_pass = GatePass.objects.get(gate_pass_no=gatepass_no)
        except GatePass.DoesNotExist:
            raise CommandError(f"GatePass #{gatepass_no} does not exist in the database. Run 'python manage.py seed_aavin_slip' first.")

        self.stdout.write(f"Processing Gatepass #{gate_pass.gate_pass_no} ({gate_pass.vehicle_no})...")

        # Optional save to disk
        if save_path:
            pdf_bytes = AavinGatePassPDFGenerator.generate_pdf(gate_pass)
            with open(save_path, 'wb') as f:
                f.write(pdf_bytes)
            self.stdout.write(self.style.SUCCESS(f"Saved PDF to: {save_path}"))

        # Email dispatch
        if email:
            self.stdout.write(f"Sending email with PDF attachment to: {email}...")
            result = GatePassEmailService.send_gatepass_email(gate_pass, recipient_email=email)
            if result.get('success'):
                self.stdout.write(self.style.SUCCESS(f"Email sent successfully to {email}!"))
            else:
                self.stdout.write(self.style.ERROR(f"Failed to send email: {result.get('error')}"))
        elif not save_path:
            # If neither email nor save_pdf specified, default to saving a copy in the workspace
            default_path = f"Gatepass_{gate_pass.gate_pass_no}.pdf"
            pdf_bytes = AavinGatePassPDFGenerator.generate_pdf(gate_pass)
            with open(default_path, 'wb') as f:
                f.write(pdf_bytes)
            self.stdout.write(self.style.SUCCESS(f"No email specified. Generated PDF saved to: {default_path}"))
