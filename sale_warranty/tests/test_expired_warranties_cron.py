# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.tests.common import SavepointCase


class TestExpiredWarrantiesCron(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.customer = cls.env['res.partner'].create({
            'name': 'My Customer',
            'customer': True,
        })

        cls.warranty_6_months = cls.env['sale.warranty.type'].create({
            'name': '6 Months Parts',
            'duration_in_months': 6,
            'description': 'Warranted 6 months on parts'
        })

        cls.product_a = cls.env['product.product'].create({
            'name': 'My Product',
            'tracking': 'serial',
            'type': 'product',
            'warranty_type_ids': [(4, cls.warranty_6_months.id)]
        })

        cls.today = datetime.now().date()

        cls.warranty = cls.env['sale.warranty'].create({
            'partner_id': cls.customer.id,
            'product_id': cls.product_a.id,
            'type_id': cls.warranty_6_months.id,
            'state': 'active',
            'activation_date': cls.today,
        })

    def run_cron(self):
        self.env.ref('sale_warranty.expired_warranties_cron').method_direct_trigger()

    def test_if_expiration_date_after_today_then_warranty_active(self):
        self.warranty.expiry_date = self.today + timedelta(1)
        self.run_cron()
        assert self.warranty.state == 'active'

    def test_if_expiration_date_is_today_then_warranty_active(self):
        self.warranty.expiry_date = self.today
        self.run_cron()
        assert self.warranty.state == 'active'

    def test_if_expiration_date_before_today_then_warranty_expired(self):
        self.warranty.expiry_date = self.today - timedelta(1)
        self.run_cron()
        assert self.warranty.state == 'expired'
