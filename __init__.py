# This file is part sale_invoice_grouping_payment_days module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool
from .party import Party, PartySaleInvoiceGroupingMethod
from .sale import Sale, PaymentTermLine

def register():
    Pool.register(
        Party,
        PartySaleInvoiceGroupingMethod,
        Sale,
        PaymentTermLine,
        module='sale_invoice_grouping_payment_days', type_='model')
    Pool.register(
        module='sale_invoice_grouping_payment_days', type_='wizard')
    Pool.register(
        module='sale_invoice_grouping_payment_days', type_='report')
