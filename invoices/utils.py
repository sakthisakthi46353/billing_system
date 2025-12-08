def calculate_invoice_total(invoice):
    return sum(item.total_price for item in invoice.items.all())
