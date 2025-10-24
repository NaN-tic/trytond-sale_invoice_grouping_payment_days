import datetime
from dateutil.relativedelta import relativedelta
from trytond.pool import PoolMeta, Pool
from trytond.transaction import Transaction

def days_in_month(date):
        return (date + relativedelta(day=31)).day

class PaymentTermLine(metaclass=PoolMeta):
    __name__ = 'account.invoice.payment_term.line'

    @classmethod
    def previous_payment_day(cls, date, payment_days=None):
        if payment_days is None:
            payment_days = Transaction().context.get('account_payment_days')
        if payment_days:
            assert isinstance(payment_days, list)
            payment_days = sorted(payment_days)
            for day in reversed(payment_days):
                if day < date.day:
                    return date + relativedelta(day=day)
        return date + relativedelta(day=1)

class Sale(metaclass=PoolMeta):
    __name__ = 'sale.sale'

    def _get_invoice_dates(self, date, period):
        if period != 'customer_payment_days':
            return super()._get_invoice_dates(date, period)
        pool = Pool()
        PTline = pool.get('account.invoice.payment_term.line')

        today = date or datetime.date.today()
        month_first = today.replace(day=1)
        month_last = (month_first + relativedelta(months=1)) - relativedelta(days=1)

        raw = self.party.customer_payment_days or ""

        norm_days = sorted({
        min(max(int(d), 1), month_last.day)
        for d in raw.split()
        if d.isdigit()
        })
        if not norm_days:
            return month_first, month_last

        next_date = PTline.next_payment_day(today, norm_days)
        prev_date = PTline.previous_payment_day(today, norm_days)

        end = next_date if next_date.month == today.month else month_last
        start = (prev_date + relativedelta(days=1)) if prev_date.month == today.month and prev_date.day != 1 else month_first

        return start, end
