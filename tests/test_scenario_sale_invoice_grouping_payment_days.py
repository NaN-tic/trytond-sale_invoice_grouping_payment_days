import datetime
import unittest
from decimal import Decimal

from dateutil.relativedelta import relativedelta
from proteus import Model
from trytond.modules.account.tests.tools import (
    create_chart,
    create_fiscalyear,
    get_accounts)
from trytond.modules.account_invoice.tests.tools import \
    set_fiscalyear_invoice_sequences
from trytond.modules.company.tests.tools import create_company, get_company
from trytond.tests.test_tryton import drop_db
from trytond.tests.tools import activate_modules


class Test(unittest.TestCase):

    def setUp(self):
        drop_db()
        super().setUp()

    def tearDown(self):
        drop_db()
        super().tearDown()

    def test(self):

        # Install sale_invoice_grouping_payment_days
        config = activate_modules('sale_invoice_grouping_payment_days')

        # Compute dates
        today = datetime.date.today()

        # Create company
        _ = create_company()
        company = get_company()

        # Create sale user
        User = Model.get('res.user')
        Group = Model.get('res.group')
        sale_user = User()
        sale_user.name = 'Sale'
        sale_user.login = 'sale'
        sale_group, = Group.find([('name', '=', 'Sales')])
        sale_user.groups.append(sale_group)
        sale_user.save()

        # Create stock user
        stock_user = User()
        stock_user.name = 'Stock'
        stock_user.login = 'stock'
        stock_group, = Group.find([('name', '=', 'Stock')])
        stock_user.groups.append(stock_group)
        stock_user.save()

        # Create account user
        account_user = User()
        account_user.name = 'Account'
        account_user.login = 'account'
        account_group, = Group.find([('name', '=', 'Account')])
        account_user.groups.append(account_group)
        account_user.save()

        # Create fiscal year
        fiscalyear = set_fiscalyear_invoice_sequences(
            create_fiscalyear(company))
        fiscalyear.click('create_period')

        # Create chart of accounts
        _ = create_chart(company)
        accounts = get_accounts(company)
        revenue = accounts['revenue']
        expense = accounts['expense']

        # Set sale configuration
        SaleConfig = Model.get('sale.configuration')
        sale_config = SaleConfig(1)
        sale_config.fill_grouping_invoice_date = True
        sale_config.save()

        # Create parties
        Party = Model.get('party.party')
        customer_payment_days = Party(name='Customer Payment Days')
        customer_payment_days.sale_invoice_grouping_method = 'standard'
        customer_payment_days.sale_invoice_grouping_period = 'customer_payment_days'
        customer_payment_days.customer_payment_days = '20'
        customer_payment_days.save()

        # Create account category
        ProductCategory = Model.get('product.category')
        account_category = ProductCategory(name="Account Category")
        account_category.accounting = True
        account_category.account_expense = expense
        account_category.account_revenue = revenue
        account_category.save()

        # Create product
        ProductUom = Model.get('product.uom')
        unit, = ProductUom.find([('name', '=', 'Unit')])
        ProductTemplate = Model.get('product.template')
        template = ProductTemplate()
        template.name = 'product'
        template.default_uom = unit
        template.type = 'goods'
        template.salable = True
        template.list_price = Decimal('10')
        template.account_category = account_category
        template.save()
        product, = template.products

        # Create an Inventory
        Inventory = Model.get('stock.inventory')
        Location = Model.get('stock.location')
        storage, = Location.find([
            ('code', '=', 'STO'),
        ])
        inventory = Inventory()
        inventory.location = storage
        inventory_line = inventory.lines.new(product=product)
        inventory_line.quantity = 100.0
        inventory_line.expected_quantity = 0.0
        inventory.click('confirm')
        self.assertEqual(inventory.state, 'done')

        # Sale some products before payment day
        config.user = sale_user.id
        Sale = Model.get('sale.sale')
        sale1 = Sale()
        # Sale some products before payment day
        config.user = sale_user.id
        Sale = Model.get('sale.sale')
        sale1 = Sale()
        sale1.party = customer_payment_days
        sale1.sale_date = today.replace(day=10)
        sale1.invoice_method = 'order'
        sale_line = sale1.lines.new()
        sale_line.product = product
        sale_line.unit = unit
        sale_line.unit_price = Decimal('10')
        sale_line.quantity = 1.0
        sale1.click('quote')
        sale1.click('confirm')

        # Another sale before payment day
        sale2 = Sale()
        sale2.party = customer_payment_days
        sale2.sale_date = today.replace(day=15)
        sale2.invoice_method = 'order'
        sale_line = sale2.lines.new()
        sale_line.product = product
        sale_line.unit = unit
        sale_line.unit_price = Decimal('10')
        sale_line.quantity = 2.0
        sale2.click('quote')
        sale2.click('confirm')

        # Sale after payment day
        sale3 = Sale()
        sale3.party = customer_payment_days
        sale3.sale_date = today.replace(day=25)
        sale3.invoice_method = 'order'
        sale_line = sale3.lines.new()
        sale_line.product = product
        sale_line.unit = unit
        sale_line.unit_price = Decimal('10')
        sale_line.quantity = 3.0
        sale3.click('quote')
        sale3.click('confirm')
        Invoice = Model.get('account.invoice')
        invoices = Invoice.find([
            ('party', '=', customer_payment_days.id),
            ('state', '=', 'draft'),
        ])
        self.assertEqual(len(invoices), 2)

        # Find the invoice for the first period (1-20)
        invoice1 = None
        invoice2 = None
        for inv in invoices:
            if inv.start_date == today.replace(day=1) and inv.end_date == today.replace(day=20):
                invoice1 = inv
            elif inv.start_date == today.replace(day=21) and inv.end_date == (today + relativedelta(months=1)).replace(day=1) - relativedelta(days=1):
                invoice2 = inv

        self.assertIsNotNone(invoice1)
        self.assertIsNotNone(invoice2)
        self.assertEqual(len(invoice1.lines), 2)
        self.assertEqual(invoice1.lines[0].quantity, 1.0)
        self.assertEqual(invoice1.lines[1].quantity, 2.0)
        self.assertEqual(len(invoice2.lines), 1)
        self.assertEqual(invoice2.lines[0].quantity, 3.0)

        # Check invoice dates
        self.assertEqual(invoice1.invoice_date, today.replace(day=20))
        self.assertEqual(invoice2.invoice_date, (today + relativedelta(months=1)).replace(day=1) - relativedelta(days=1))