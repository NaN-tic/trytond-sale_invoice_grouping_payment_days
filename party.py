from trytond.pool import PoolMeta, Pool
from trytond.i18n import gettext
from trytond.exceptions import UserError, UserWarning
from trytond.model import fields

class Party(metaclass=PoolMeta):
    __name__ = "party.party"

    @classmethod
    def __setup__(cls):
        super().__setup__()
        payment_days = ('customer_payment_days', 'Customer Payment Days')
        if payment_days not in cls.sale_invoice_grouping_period.selection:
            cls.sale_invoice_grouping_period.selection.append(payment_days)

    # @fields.depends('sale_invoice_grouping_period', 'customer_payment_days')
    # def on_change_sale_invoice_grouping_period(self):
    #     try:
    #         super().on_change_sale_invoice_grouping_period()
    #     except AttributeError:
    #         pass
    #     if (self.sale_invoice_grouping_period == 'customer_payment_days' and
    #         not self.customer_payment_days):
    #         raise UserError(gettext(
    #             'sale_invoice_grouping_payment_days.msg_customer_payment_days_required',
    #             party=self.rec_name))

    # @fields.depends('sale_invoice_grouping_period', 'customer_payment_days')
    # def on_change_customer_payment_days(self):
    #     pool = Pool()
    #     Warning = pool.get('res.user.warning')
    #     try:
    #         super().on_change_customer_payment_days()
    #     except AttributeError:
    #         pass
    #     if (self.sale_invoice_grouping_period == 'customer_payment_days' and
    #         not self.customer_payment_days):
    #         key = Warning.format('no_customer_payment_days', [self])
    #         if Warning.check(key):
    #             raise UserWarning(key,gettext(
    #                 'sale_invoice_grouping_payment_days.msg_no_customer_payment_days_warning',
    #                 party=self.rec_name))
    #         self.sale_invoice_grouping_period = None


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
