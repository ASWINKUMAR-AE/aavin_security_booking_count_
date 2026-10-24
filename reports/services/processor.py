import logging
from decimal import Decimal, InvalidOperation
from typing import Dict, Any, List
from ..models import GatePass, GatePassItem

logger = logging.getLogger(__name__)


def clean_int(val: Any, default: int = 0) -> int:
    """Sanitize integers, converting hyphens, blanks, and nulls to 0."""
    if val is None:
        return default
    if isinstance(val, (int, float)):
        return int(val)
    s = str(val).strip().replace(',', '')
    if s in ('', '-', '--', 'null', 'None'):
        return default
    try:
        return int(float(s))
    except (ValueError, TypeError):
        return default


def clean_decimal(val: Any, default: str = "0.0") -> Decimal:
    """Sanitize decimal numbers, converting hyphens, blanks, and nulls to Decimal."""
    if val is None:
        return Decimal(default)
    if isinstance(val, Decimal):
        return val
    s = str(val).strip().replace(',', '')
    if s in ('', '-', '--', 'null', 'None'):
        return Decimal(default)
    try:
        return Decimal(s)
    except (InvalidOperation, ValueError, TypeError):
        return Decimal(default)


class GatePassProcessor:
    """
    Validates, sanitizes, and structures GatePass records.
    Can ingest raw OCR dictionaries or audit existing database records.
    """

    @classmethod
    def process_and_validate(cls, gate_pass: GatePass) -> Dict[str, Any]:
        """
        Calculates aggregates, validates line-item math and compares against recorded totals.
        Updates the gatepass status and validation notes.
        """
        items = list(gate_pass.items.all().order_by('item_no'))

        calc_cash_total = sum(i.cash_qty for i in items)
        calc_card_total = sum(i.card_qty for i in items)
        calc_pkts_total = sum(i.total_qty for i in items)
        calc_tubs_total = sum(i.tubs for i in items)
        calc_litres_total = sum(i.qty_litres for i in items)
        calc_leaks_total = sum(i.leak_qty for i in items)

        warnings: List[str] = []

        # Check line item internal math: Cash + Card == Total
        for item in items:
            expected_total = item.cash_qty + item.card_qty
            if item.total_qty != expected_total:
                warnings.append(
                    f"Item #{item.item_no} ({item.product_name}): Cash({item.cash_qty}) + Card({item.card_qty}) = {expected_total}, but Total is {item.total_qty}."
                )

        # Check document grand totals vs sum of items
        if gate_pass.total_litres > Decimal('0.000'):
            diff_litres = abs(calc_litres_total - gate_pass.total_litres)
            if diff_litres > Decimal('0.001'):
                warnings.append(
                    f"Milk Total Litres mismatch: Sum of lines is {calc_litres_total} L, but header total is {gate_pass.total_litres} L."
                )
        else:
            # If header total wasn't provided, use calculated
            gate_pass.total_litres = calc_litres_total

        if gate_pass.total_tubs > Decimal('0.00'):
            diff_tubs = abs(calc_tubs_total - gate_pass.total_tubs)
            if diff_tubs > Decimal('0.01'):
                warnings.append(
                    f"Tubs Total note: Sum of line tubs is {calc_tubs_total}, header total is {gate_pass.total_tubs}."
                )
        else:
            gate_pass.total_tubs = calc_tubs_total

        gate_pass.total_leaks = calc_leaks_total

        if warnings:
            gate_pass.validation_notes = "\n".join(warnings)
            # Non-blocking warning - keep PROCESSED but record notes
            gate_pass.status = 'PROCESSED'
        else:
            gate_pass.validation_notes = "All line items and totals verified successfully."
            gate_pass.status = 'PROCESSED'

        gate_pass.save()

        return {
            'gate_pass': gate_pass,
            'items': items,
            'calc_cash_total': calc_cash_total,
            'calc_card_total': calc_card_total,
            'calc_pkts_total': calc_pkts_total,
            'calc_tubs_total': calc_tubs_total,
            'calc_litres_total': calc_litres_total,
            'calc_leaks_total': calc_leaks_total,
            'warnings': warnings,
            'is_valid': len(warnings) == 0,
        }

    @classmethod
    def ingest_from_dict(cls, data: Dict[str, Any]) -> GatePass:
        """
        Creates or updates a GatePass and its items from a structured dictionary.
        Teammates can call this directly from the OCR engine!
        """
        header = data.get('header', {})
        gate_pass_no = str(header.get('gate_pass_no', 'UNKNOWN')).strip()

        gate_pass, _ = GatePass.objects.update_or_create(
            gate_pass_no=gate_pass_no,
            date=header.get('date'),
            defaults={
                'union_name': header.get('union_name', "THE MADURAI DISTRICT CO-OPERATIVE MILK PRODUCERS' UNION LTD."),
                'plant_location': header.get('plant_location', "SIVAGANGAI MAIN ROAD, MADURAI - 625 020"),
                'gatepass_type': header.get('gatepass_type', "1 DAIRY GATEPASS FOR MILK - 0"),
                'copy_type': header.get('copy_type', "In Original"),
                'shift': header.get('shift', 'Morning'),
                'route_name': header.get('route_name', ''),
                'vehicle_no': header.get('vehicle_no', ''),
                'route_supervisor': header.get('route_supervisor', ''),
                'departure_time': header.get('departure_time', ''),
                'total_tubs': clean_decimal(header.get('total_tubs', 0)),
                'total_litres': clean_decimal(header.get('total_litres', 0)),
                'total_leaks': clean_int(header.get('total_leaks', 0)),
                'status': 'PENDING',
            }
        )

        # Clear existing items if re-ingesting
        gate_pass.items.all().delete()

        # Ingest line items
        items_data = data.get('items', [])
        for idx, row in enumerate(items_data, start=1):
            GatePassItem.objects.create(
                gate_pass=gate_pass,
                item_no=clean_int(row.get('item_no', idx)),
                product_name=str(row.get('product_name', '')).strip(),
                cash_qty=clean_int(row.get('cash_qty', 0)),
                card_qty=clean_int(row.get('card_qty', 0)),
                total_qty=clean_int(row.get('total_qty', 0)),
                tubs=clean_decimal(row.get('tubs', 0)),
                qty_litres=clean_decimal(row.get('qty_litres', 0)),
                leak_qty=clean_int(row.get('leak_qty', 0)),
            )

        # Process and validate after ingestion
        cls.process_and_validate(gate_pass)
        return gate_pass
