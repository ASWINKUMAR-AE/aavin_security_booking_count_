from datetime import date
from decimal import Decimal
from django.core.management.base import BaseCommand
from reports.services.processor import GatePassProcessor


class Command(BaseCommand):
    help = "Seeds the database with sample Aavin Gatepass data matching the real physical slip"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding sample Aavin Gatepass #139914..."))

        raw_data = {
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
                'route_supervisor': "",
                'departure_time': "",
                'total_tubs': Decimal('184.00'),
                'total_litres': Decimal('2168.500'),
                'total_leaks': 2,
            },
            'items': [
                {
                    'item_no': 1,
                    'product_name': "COW MILK 500 ML",
                    'cash_qty': 2098,
                    'card_qty': 39,
                    'total_qty': 2137,
                    'tubs': Decimal('89.01'),
                    'qty_litres': Decimal('1068.500'),
                    'leak_qty': 2,
                },
                {
                    'item_no': 2,
                    'product_name': "COW MILK 500 ML (STAFF)",
                    'cash_qty': 0,
                    'card_qty': 28,
                    'total_qty': 28,
                    'tubs': Decimal('1.04'),
                    'qty_litres': Decimal('14.000'),
                    'leak_qty': 0,
                },
                {
                    'item_no': 3,
                    'product_name': "CM 200 ML",
                    'cash_qty': 1945,
                    'card_qty': 0,
                    'total_qty': 1945,
                    'tubs': Decimal('38.45'),
                    'qty_litres': Decimal('389.000'),
                    'leak_qty': 0,
                },
                {
                    'item_no': 4,
                    'product_name': "AAVIN GOLD 500 ML",
                    'cash_qty': 1146,
                    'card_qty': 20,
                    'total_qty': 1166,
                    'tubs': Decimal('48.14'),
                    'qty_litres': Decimal('583.000'),
                    'leak_qty': 0,
                },
                {
                    'item_no': 5,
                    'product_name': "TEA MATE PLUS-1000ML",
                    'cash_qty': 105,
                    'card_qty': 0,
                    'total_qty': 105,
                    'tubs': Decimal('8.09'),
                    'qty_litres': Decimal('105.000'),
                    'leak_qty': 0,
                },
                {
                    'item_no': 6,
                    'product_name': "TEAMATE 500 ML",
                    'cash_qty': 18,
                    'card_qty': 0,
                    'total_qty': 18,
                    'tubs': Decimal('0.18'),
                    'qty_litres': Decimal('9.000'),
                    'leak_qty': 0,
                },
            ]
        }

        gate_pass = GatePassProcessor.ingest_from_dict(raw_data)
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully seeded Gatepass #{gate_pass.gate_pass_no} with {gate_pass.items.count()} items! "
                f"Total Litres: {gate_pass.total_litres} L, Status: {gate_pass.status}"
            )
        )
