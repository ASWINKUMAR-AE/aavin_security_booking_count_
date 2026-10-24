from django.contrib import admin
from .models import GatePass, GatePassItem


class GatePassItemInline(admin.TabularInline):
    model = GatePassItem
    extra = 0


@admin.register(GatePass)
class GatePassAdmin(admin.ModelAdmin):
    list_display = ('gate_pass_no', 'vehicle_no', 'route_name', 'date', 'shift', 'total_litres', 'total_tubs', 'status', 'sent_at')
    list_filter = ('status', 'shift', 'date')
    search_fields = ('gate_pass_no', 'vehicle_no', 'route_name')
    inlines = [GatePassItemInline]


@admin.register(GatePassItem)
class GatePassItemAdmin(admin.ModelAdmin):
    list_display = ('gate_pass', 'item_no', 'product_name', 'cash_qty', 'card_qty', 'total_qty', 'qty_litres', 'leak_qty')
    list_filter = ('product_name',)
