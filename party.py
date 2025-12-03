from trytond.pool import PoolMeta
from trytond.i18n import gettext
from trytond.exceptions import UserError

class Party(metaclass=PoolMeta):
    __name__ = "party.party"

    @classmethod
    def __setup__(cls):
        super().__setup__()
        payment_days = ('customer_payment_days', 'Customer Payment Days')
        if payment_days not in cls.sale_invoice_grouping_period.selection:
            cls.sale_invoice_grouping_period.selection.append(payment_days)

    @classmethod
    def validate(cls, parties):
        super().validate(parties)
        for p in parties:
            if p.sale_invoice_grouping_period != 'customer_payment_days':
                return
            if not p.customer_payment_days:
                raise UserError(
                    gettext(
                        'sale_invoice_grouping_payment_days.msg_customer_payment_days_required',
                        party=p.rec_name
                    )
                )

class PartySaleInvoiceGroupingMethod(metaclass=PoolMeta):
    __name__ = 'party.party.sale_invoice_grouping_method'

    @classmethod
    def __setup__(cls):
        super().__setup__()
        payment_days = ('customer_payment_days', 'Customer Payment Days')
        if payment_days not in cls.sale_invoice_grouping_period.selection:
            cls.sale_invoice_grouping_period.selection.append(payment_days)
