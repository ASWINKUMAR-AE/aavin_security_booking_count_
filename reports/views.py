from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST

from .models import GatePass
from .services.processor import GatePassProcessor
from .services.pdf_service import AavinGatePassPDFGenerator
from .services.email_service import GatePassEmailService


def gatepass_list(request):
    """Dashboard listing all recorded gatepasses."""
    gatepasses = GatePass.objects.all().prefetch_related('items')
    total_litres_sum = sum(gp.total_litres for gp in gatepasses)
    total_tubs_sum = sum(gp.total_tubs for gp in gatepasses)
    total_leaks_sum = sum(gp.total_leaks for gp in gatepasses)

    context = {
        'gatepasses': gatepasses,
        'total_passes': gatepasses.count(),
        'total_litres_sum': total_litres_sum,
        'total_tubs_sum': total_tubs_sum,
        'total_leaks_sum': total_leaks_sum,
    }
    return render(request, 'reports/dashboard.html', context)


def gatepass_detail(request, pk):
    """Detailed view for a single gatepass and its line items."""
    gate_pass = get_object_or_404(GatePass, pk=pk)
    processed_data = GatePassProcessor.process_and_validate(gate_pass)

    context = {
        'gate_pass': gate_pass,
        'items': processed_data['items'],
        'calc_pkts_total': processed_data['calc_pkts_total'],
        'calc_cash_total': processed_data['calc_cash_total'],
        'calc_card_total': processed_data['calc_card_total'],
        'warnings': processed_data['warnings'],
        'is_valid': processed_data['is_valid'],
    }
    return render(request, 'reports/detail.html', context)


def gatepass_pdf_preview(request, pk):
    """Streams the generated PDF directly in the browser."""
    gate_pass = get_object_or_404(GatePass, pk=pk)
    pdf_bytes = AavinGatePassPDFGenerator.generate_pdf(gate_pass)

    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    filename = f"Aavin_GatePass_{gate_pass.gate_pass_no}.pdf"
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response


@require_POST
def gatepass_send_email_view(request, pk):
    """Dispatches the gatepass PDF report via email."""
    gate_pass = get_object_or_404(GatePass, pk=pk)
    recipient_email = request.POST.get('recipient_email', '').strip()

    if not recipient_email:
        messages.error(request, "Please enter a valid recipient email address.")
        return redirect('gatepass_detail', pk=pk)

    result = GatePassEmailService.send_gatepass_email(gate_pass, recipient_email=recipient_email)

    if result.get('success'):
        messages.success(request, f"Gatepass PDF successfully sent to {recipient_email}!")
    else:
        messages.error(request, f"Failed to send email: {result.get('error')}")

    return redirect('gatepass_detail', pk=pk)


def seed_sample_view(request):
    """Quick one-click button from UI to seed the sample slip #139914."""
    from datetime import date
    from decimal import Decimal

    sample_data = {
        'header': {
            'union_name': "THE MADURAI DISTRICT CO-OPERATIVE MILK PRODUCERS' UNION LTD.",
            'plant_location': "SIVAGANGAI MAIN ROAD, MADURAI - 625 020",
            'gatepass_type': "1 DAIRY GATEPASS FOR MILK - 0",
            'copy_type': "In Original",
            'gate_pass_no': "139914",
            'date': date(2026, 10, 24),
            'shift': "Morning",
            'route_name': "3-ANNA NAGAR 3",
            'vehicle_no': "TN69 BD 9208",
            'total_tubs': Decimal('184.00'),
            'total_litres': Decimal('2168.500'),
            'total_leaks': 2,
        },
        'items': [
            {'item_no': 1, 'product_name': "COW MILK 500 ML", 'cash_qty': 2098, 'card_qty': 39, 'total_qty': 2137, 'tubs': Decimal('89.01'), 'qty_litres': Decimal('1068.500'), 'leak_qty': 2},
            {'item_no': 2, 'product_name': "COW MILK 500 ML (STAFF)", 'cash_qty': 0, 'card_qty': 28, 'total_qty': 28, 'tubs': Decimal('1.04'), 'qty_litres': Decimal('14.000'), 'leak_qty': 0},
            {'item_no': 3, 'product_name': "CM 200 ML", 'cash_qty': 1945, 'card_qty': 0, 'total_qty': 1945, 'tubs': Decimal('38.45'), 'qty_litres': Decimal('389.000'), 'leak_qty': 0},
            {'item_no': 4, 'product_name': "AAVIN GOLD 500 ML", 'cash_qty': 1146, 'card_qty': 20, 'total_qty': 1166, 'tubs': Decimal('48.14'), 'qty_litres': Decimal('583.000'), 'leak_qty': 0},
            {'item_no': 5, 'product_name': "TEA MATE PLUS-1000ML", 'cash_qty': 105, 'card_qty': 0, 'total_qty': 105, 'tubs': Decimal('8.09'), 'qty_litres': Decimal('105.000'), 'leak_qty': 0},
            {'item_no': 6, 'product_name': "TEAMATE 500 ML", 'cash_qty': 18, 'card_qty': 0, 'total_qty': 18, 'tubs': Decimal('0.18'), 'qty_litres': Decimal('9.000'), 'leak_qty': 0},
        ]
    }
    gp = GatePassProcessor.ingest_from_dict(sample_data)
    messages.success(request, f"Loaded Gatepass #{gp.gate_pass_no} ({gp.vehicle_no}) from sample data!")
    return redirect('gatepass_detail', pk=gp.pk)
