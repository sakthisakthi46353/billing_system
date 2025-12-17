def calculate_invoice_total(invoice):
    return sum(item.total_price for item in invoice.items.all())
from decimal import Decimal

def recalculate_invoice(invoice):
    items = invoice.items.all()

    subtotal = sum(item.line_total for item in items)
    tax = subtotal * Decimal('0.18')   # 18% tax
    total = subtotal + tax

    invoice.subtotal = subtotal
    invoice.tax = tax
    invoice.total = total
    invoice.save()
