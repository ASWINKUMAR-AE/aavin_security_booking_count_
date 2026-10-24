import io
from datetime import datetime
from decimal import Decimal
from typing import Optional
from django.utils import timezone

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
)

from ..models import GatePass
from .processor import GatePassProcessor


class AavinGatePassPDFGenerator:
    """
    Generates high-quality, professional Aavin Security Gatepass PDF documents.
    """

    # Brand Colors
    PRIMARY = colors.HexColor('#0B3C68')      # Aavin Dark Navy
    SECONDARY = colors.HexColor('#0284C7')    # Sky Blue
    DARK = colors.HexColor('#1E293B')         # Slate 800
    LIGHT_BG = colors.HexColor('#F8FAFC')     # Slate 50
    ZEBRA_BG = colors.HexColor('#F1F5F9')     # Slate 100
    BORDER = colors.HexColor('#CBD5E1')       # Slate 300
    SUCCESS = colors.HexColor('#16A34A')      # Green 600
    ALERT = colors.HexColor('#DC2626')        # Red 600
    TEXT_MUTED = colors.HexColor('#64748B')   # Slate 500

    @classmethod
    def generate_pdf(cls, gate_pass: GatePass) -> bytes:
        """
        Builds the PDF in-memory and returns raw PDF bytes.
        """
        # Ensure aggregates are up to date
        processed_data = GatePassProcessor.process_and_validate(gate_pass)
        items = processed_data['items']

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=12 * mm,
            rightMargin=12 * mm,
            topMargin=10 * mm,
            bottomMargin=10 * mm,
            title=f"Aavin_GatePass_{gate_pass.gate_pass_no}",
            author="Aavin Security Booking Dispatch System"
        )

        styles = getSampleStyleSheet()

        # Custom Typography Styles
        title_style = ParagraphStyle(
            'AavinTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=11,
            leading=14,
            alignment=1, # Center
            textColor=cls.PRIMARY
        )
        subtitle_style = ParagraphStyle(
            'AavinSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8,
            leading=10,
            alignment=1,
            textColor=cls.DARK
        )
        badge_style = ParagraphStyle(
            'AavinBadge',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=10,
            leading=13,
            alignment=1,
            textColor=cls.PRIMARY
        )
        meta_label = ParagraphStyle(
            'MetaLabel',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8,
            leading=10,
            textColor=cls.DARK
        )
        meta_val = ParagraphStyle(
            'MetaVal',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8,
            leading=10,
            textColor=cls.DARK
        )
        table_hdr = ParagraphStyle(
            'TableHdr',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=7.5,
            leading=9,
            alignment=1,
            textColor=colors.white
        )
        table_cell = ParagraphStyle(
            'TableCell',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=7.5,
            leading=9,
            textColor=cls.DARK
        )
        table_cell_bold = ParagraphStyle(
            'TableCellBold',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=7.5,
            leading=9,
            textColor=cls.DARK
        )
        table_cell_center = ParagraphStyle(
            'TableCellCenter',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=7.5,
            leading=9,
            alignment=1,
            textColor=cls.DARK
        )
        table_cell_right = ParagraphStyle(
            'TableCellRight',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=7.5,
            leading=9,
            alignment=2,
            textColor=cls.DARK
        )
        table_cell_right_bold = ParagraphStyle(
            'TableCellRightBold',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=7.5,
            leading=9,
            alignment=2,
            textColor=cls.PRIMARY
        )

        elements = []

        # -------------------------------------------------------------
        # 1. HEADER SECTION
        # -------------------------------------------------------------
        elements.append(Paragraph(gate_pass.union_name.upper(), title_style))
        elements.append(Paragraph(gate_pass.plant_location, subtitle_style))
        elements.append(Spacer(1, 1.5 * mm))
        elements.append(Paragraph(f"- {gate_pass.gatepass_type} -", badge_style))
        elements.append(Paragraph(f"( {gate_pass.copy_type} )", subtitle_style))
        elements.append(Spacer(1, 2.5 * mm))

        # -------------------------------------------------------------
        # 2. METADATA INFO GRID (2-column layout)
        # -------------------------------------------------------------
        date_str = gate_pass.date.strftime("%d.%m.%Y") if gate_pass.date else ""
        meta_table_data = [
            [
                Paragraph("<b>VEHICLE NO. :</b>", meta_label),
                Paragraph(gate_pass.vehicle_no, meta_val),
                Paragraph("<b>ROUTE :</b>", meta_label),
                Paragraph(gate_pass.route_name, meta_val),
            ],
            [
                Paragraph("<b>ROUTE SUPERVISOR :</b>", meta_label),
                Paragraph(gate_pass.route_supervisor or "-", meta_val),
                Paragraph("<b>DATE / SHIFT :</b>", meta_label),
                Paragraph(f"{date_str} / {gate_pass.shift}", meta_val),
            ],
            [
                Paragraph("<b>DEPT TIME :</b>", meta_label),
                Paragraph(gate_pass.departure_time or "-", meta_val),
                Paragraph("<b>GATE PASS NO. :</b>", meta_label),
                Paragraph(f"<b>{gate_pass.gate_pass_no}</b>", meta_label),
            ]
        ]

        meta_table = Table(
            meta_table_data,
            colWidths=[38 * mm, 50 * mm, 38 * mm, 60 * mm]
        )
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), cls.LIGHT_BG),
            ('BOX', (0, 0), (-1, -1), 0.5, cls.BORDER),
            ('INNERGRID', (0, 0), (-1, -1), 0.3, cls.BORDER),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(meta_table)
        elements.append(Spacer(1, 3.5 * mm))

        # -------------------------------------------------------------
        # 3. KPI STATS BANNER
        # -------------------------------------------------------------
        kpi_data = [
            [
                Paragraph(f"<font color='#0B3C68'><b>TOTAL LITRES</b></font><br/><font size=12><b>{gate_pass.total_litres} L</b></font>", subtitle_style),
                Paragraph(f"<font color='#0B3C68'><b>TOTAL TUBS / CRATES</b></font><br/><font size=12><b>{gate_pass.total_tubs}</b></font>", subtitle_style),
                Paragraph(f"<font color='#0B3C68'><b>TOTAL PACKETS</b></font><br/><font size=12><b>{processed_data['calc_pkts_total']}</b></font>", subtitle_style),
                Paragraph(f"<font color='{'#DC2626' if gate_pass.total_leaks > 0 else '#16A34A'}'><b>LEAKS DETECTED</b></font><br/><font size=12><b>{gate_pass.total_leaks}</b></font>", subtitle_style),
            ]
        ]
        kpi_table = Table(kpi_data, colWidths=[46.5 * mm, 46.5 * mm, 46.5 * mm, 46.5 * mm])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#E0F2FE')),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#BAE6FD')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#BAE6FD')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(kpi_table)
        elements.append(Spacer(1, 4 * mm))

        # -------------------------------------------------------------
        # 4. MAIN LINE ITEMS TABLE
        # -------------------------------------------------------------
        # Column headers (with nested Cash / Card / Total under Quantity)
        headers_row1 = [
            Paragraph("No.", table_hdr),
            Paragraph("PRODUCT DESCRIPTION", table_hdr),
            Paragraph("QUANTITY (PACKETS)", table_hdr),
            "", # Span placeholder
            "", # Span placeholder
            Paragraph("TUBS", table_hdr),
            Paragraph("QTY (LTR)", table_hdr),
            Paragraph("LEAK", table_hdr)
        ]
        headers_row2 = [
            "",
            "",
            Paragraph("CASH", table_hdr),
            Paragraph("CARD", table_hdr),
            Paragraph("TOTAL", table_hdr),
            "",
            "",
            ""
        ]

        table_rows = [headers_row1, headers_row2]

        for idx, item in enumerate(items, start=1):
            row_bg = cls.LIGHT_BG if idx % 2 == 0 else colors.white
            leak_cell = Paragraph(str(item.leak_qty), table_cell_center) if item.leak_qty > 0 else Paragraph("-", table_cell_center)

            table_rows.append([
                Paragraph(str(item.item_no), table_cell_center),
                Paragraph(item.product_name, table_cell_bold),
                Paragraph(str(item.cash_qty) if item.cash_qty > 0 else "-", table_cell_right),
                Paragraph(str(item.card_qty) if item.card_qty > 0 else "-", table_cell_right),
                Paragraph(str(item.total_qty), table_cell_right_bold),
                Paragraph(f"{item.tubs:.2f}", table_cell_right),
                Paragraph(f"{item.qty_litres:.3f}", table_cell_right_bold),
                leak_cell
            ])

        # Totals Row
        table_rows.append([
            "",
            Paragraph("<b>MILK TOTAL</b>", table_cell_bold),
            Paragraph(f"<b>{processed_data['calc_cash_total']}</b>", table_cell_right_bold),
            Paragraph(f"<b>{processed_data['calc_card_total']}</b>", table_cell_right_bold),
            Paragraph(f"<b>{processed_data['calc_pkts_total']}</b>", table_cell_right_bold),
            Paragraph(f"<b>{gate_pass.total_tubs}</b>", table_cell_right_bold),
            Paragraph(f"<b>{gate_pass.total_litres}</b>", table_cell_right_bold),
            Paragraph(f"<b>{gate_pass.total_leaks}</b>", table_cell_center)
        ])

        col_widths = [
            10 * mm,  # No.
            58 * mm,  # Product
            18 * mm,  # Cash
            18 * mm,  # Card
            20 * mm,  # Total
            20 * mm,  # Tubs
            27 * mm,  # Qty(Ltr)
            15 * mm   # Leak
        ]

        main_table = Table(table_rows, colWidths=col_widths, repeatRows=2)

        total_row_idx = len(table_rows) - 1

        t_style = [
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 1), cls.PRIMARY),
            ('SPAN', (0, 0), (0, 1)), # No.
            ('SPAN', (1, 0), (1, 1)), # Product
            ('SPAN', (2, 0), (4, 0)), # Quantity (Packets)
            ('SPAN', (5, 0), (5, 1)), # Tubs
            ('SPAN', (6, 0), (6, 1)), # Qty(Ltr)
            ('SPAN', (7, 0), (7, 1)), # Leak
            ('ALIGN', (0, 0), (-1, 1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 0.5, cls.BORDER),
            ('INNERGRID', (0, 0), (-1, -1), 0.3, cls.BORDER),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),

            # Totals row styling
            ('BACKGROUND', (0, total_row_idx), (-1, total_row_idx), colors.HexColor('#FEF3C7')),
            ('LINEABOVE', (0, total_row_idx), (-1, total_row_idx), 1, cls.PRIMARY),
            ('LINEBELOW', (0, total_row_idx), (-1, total_row_idx), 1, cls.PRIMARY),
        ]

        # Apply zebra shading to data rows
        for r in range(2, total_row_idx):
            if r % 2 == 1:
                t_style.append(('BACKGROUND', (0, r), (-1, r), cls.ZEBRA_BG))

        main_table.setStyle(TableStyle(t_style))
        elements.append(main_table)
        elements.append(Spacer(1, 4 * mm))

        # -------------------------------------------------------------
        # 5. AUDIT / VALIDATION REMARKS (if any warnings)
        # -------------------------------------------------------------
        if gate_pass.validation_notes:
            notes_p = Paragraph(
                f"<b>Audit & Verification Status:</b> {gate_pass.validation_notes.replace(chr(10), '<br/>')}",
                subtitle_style
            )
            notes_table = Table([[notes_p]], colWidths=[186 * mm])
            notes_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
                ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(notes_table)
            elements.append(Spacer(1, 5 * mm))

        # -------------------------------------------------------------
        # 6. SIGNATURE SECTION
        # -------------------------------------------------------------
        sig_data = [
            [
                Paragraph("<b>Indent</b>", subtitle_style),
                Paragraph("<b>Security</b>", subtitle_style),
                Paragraph("<b>B.Checker</b>", subtitle_style),
                Paragraph("<b>Dairy</b>", subtitle_style),
                Paragraph("<b>QC</b>", subtitle_style),
                Paragraph("<b>Driver</b>", subtitle_style),
            ],
            ["\n\n\n", "\n\n\n", "\n\n\n", "\n\n\n", "\n\n\n", "\n\n\n"]
        ]
        sig_col_w = 31 * mm
        sig_table = Table(sig_data, colWidths=[sig_col_w] * 6)
        sig_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), cls.ZEBRA_BG),
            ('BOX', (0, 0), (-1, -1), 0.5, cls.BORDER),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, cls.BORDER),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))

        elements.append(KeepTogether([sig_table]))
        elements.append(Spacer(1, 3 * mm))

        # -------------------------------------------------------------
        # 7. FOOTER
        # -------------------------------------------------------------
        gen_time = timezone.localtime(timezone.now()).strftime("%d-%b-%Y %I:%M %p")
        footer_p = Paragraph(
            f"Generated digitally by Aavin Security Dispatch System &bull; Timestamp: {gen_time} IST &bull; Page 1 of 1",
            subtitle_style
        )
        elements.append(footer_p)

        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
