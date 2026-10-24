from django.db import models
from decimal import Decimal


class GatePass(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Processing'),
        ('PROCESSED', 'Processed & Ready'),
        ('SENT', 'Email Sent'),
        ('FAILED', 'Failed / Discrepancy Found'),
    ]

    # Organization & Document Info
    union_name = models.CharField(
        max_length=255,
        default="THE MADURAI DISTRICT CO-OPERATIVE MILK PRODUCERS' UNION LTD."
    )
    plant_location = models.CharField(
        max_length=255,
        default="SIVAGANGAI MAIN ROAD, MADURAI - 625 020"
    )
    gatepass_type = models.CharField(
        max_length=100,
        default="1 DAIRY GATEPASS FOR MILK - 0"
    )
    copy_type = models.CharField(
        max_length=50,
        default="In Original",
        help_text="e.g. In Original / In Duplicate"
    )

    # Route & Vehicle Details
    gate_pass_no = models.CharField(max_length=50, db_index=True)
    date = models.DateField(help_text="Date of gatepass")
    shift = models.CharField(max_length=30, default="Morning", help_text="Morning / Evening")
    route_name = models.CharField(max_length=100, help_text="e.g. 3-ANNA NAGAR 3")
    vehicle_no = models.CharField(max_length=50, help_text="e.g. TN69 BD 9208")
    route_supervisor = models.CharField(max_length=100, blank=True, default="")
    departure_time = models.CharField(max_length=50, blank=True, default="")

    # Grand Totals (as read from document or calculated)
    total_tubs = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_litres = models.DecimalField(max_digits=12, decimal_places=3, default=Decimal('0.000'))
    total_leaks = models.PositiveIntegerField(default=0)

    # Processing & Dispatch State
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    validation_notes = models.TextField(blank=True, default="", help_text="Audit remarks or discrepancy warnings")
    recipient_email = models.EmailField(blank=True, default="")
    sent_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = "Dairy Gatepass"
        verbose_name_plural = "Dairy Gatepasses"

    def __str__(self):
        return f"Gatepass #{self.gate_pass_no} ({self.vehicle_no} - {self.route_name})"


class GatePassItem(models.Model):
    gate_pass = models.ForeignKey(GatePass, related_name='items', on_delete=models.CASCADE)
    item_no = models.PositiveIntegerField(default=1)
    product_name = models.CharField(max_length=150)
    cash_qty = models.IntegerField(default=0)
    card_qty = models.IntegerField(default=0)
    total_qty = models.IntegerField(default=0)
    tubs = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))
    qty_litres = models.DecimalField(max_digits=10, decimal_places=3, default=Decimal('0.000'))
    leak_qty = models.IntegerField(default=0)

    class Meta:
        ordering = ['item_no']
        verbose_name = "Gatepass Item"
        verbose_name_plural = "Gatepass Items"

    def __str__(self):
        return f"{self.item_no}. {self.product_name} ({self.qty_litres} L)"
