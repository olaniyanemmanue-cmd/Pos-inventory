import os
from datetime import datetime
from fpdf import FPDF


class ReceiptGenerator:
    @staticmethod
    def format_currency(value: float) -> str:
        return f"${value:,.2f}"

    @staticmethod
    def create_pdf_receipt(order: dict, items: list, filename: str):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, "Inventory POS Receipt", ln=True, align="C")
        pdf.set_font("Helvetica", size=11)
        pdf.ln(4)
        pdf.cell(0, 8, f"Order Code: {order['order_code']}", ln=True)
        pdf.cell(0, 8, f"Customer: {order.get('customer_name', 'Walk-in')}", ln=True)
        pdf.cell(0, 8, f"Email: {order.get('customer_email', 'N/A')}", ln=True)
        pdf.cell(0, 8, f"Date: {order['created_at']}", ln=True)
        pdf.cell(0, 8, f"Payment: {order.get('payment_method', 'Pending')} ({order.get('payment_status', 'Pending')})", ln=True)
        pdf.ln(6)

        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(80, 8, "Product", border=1)
        pdf.cell(30, 8, "Qty", border=1, align="C")
        pdf.cell(30, 8, "Unit", border=1, align="R")
        pdf.cell(40, 8, "Total", border=1, align="R")
        pdf.ln()
        pdf.set_font("Helvetica", size=11)

        for item in items:
            pdf.cell(80, 8, item["name"][:28], border=1)
            pdf.cell(30, 8, str(item["quantity"]), border=1, align="C")
            pdf.cell(30, 8, ReceiptGenerator.format_currency(item["unit_price"]), border=1, align="R")
            pdf.cell(40, 8, ReceiptGenerator.format_currency(item["line_total"]), border=1, align="R")
            pdf.ln()

        pdf.ln(4)
        pdf.cell(0, 8, f"Subtotal: {ReceiptGenerator.format_currency(order['subtotal'])}", ln=True, align="R")
        pdf.cell(0, 8, f"Tax: {ReceiptGenerator.format_currency(order['tax'])}", ln=True, align="R")
        pdf.cell(0, 8, f"Discount: {ReceiptGenerator.format_currency(order['discount'])}", ln=True, align="R")
        pdf.cell(0, 8, f"Total: {ReceiptGenerator.format_currency(order['total'])}", ln=True, align="R")
        pdf.output(filename)
        return filename
