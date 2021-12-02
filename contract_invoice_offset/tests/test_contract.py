# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import date
from dateutil.relativedelta import relativedelta
from ddt import ddt, data, unpack
from odoo.tests.common import SavepointCase


@ddt
class TestContract(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "My Customer",
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "My Product",
                "type": "service",
            }
        )
        cls.contract = cls.env["contract.contract"].create(
            {
                "name": "Contract",
                "partner_id": cls.partner.id,
                "contract_type": "sale",
            }
        )

        cls.date_start = date(2021, 12, 1)

        cls.line = cls.env["contract.line"].create(
            {
                "contract_id": cls.contract.id,
                "product_id": cls.product.id,
                "name": "/",
                "quantity": 1,
                "uom_id": cls.product.uom_id.id,
                "price_unit": 100,
                "recurring_invoicing_type": "pre-paid",
                "recurring_interval": 1,
                "recurring_rule_type": "monthly",
                "date_start": cls.date_start,
            }
        )

    def test_no_offset(self):
        self.line._onchange_invoicing_offset()
        assert self.line.recurring_next_date == self.date_start

    @data(
        (0, date(2021, 12, 1)),
        (1, date(2021, 11, 30)),
        (2, date(2021, 11, 29)),
    )
    @unpack
    def test_daily_offset(self, interval, invoicing_date):
        self.line.invoicing_offset_interval = interval
        self.line.invoicing_offset_rule_type = "daily"
        self.line._onchange_invoicing_offset()
        assert self.line.recurring_next_date == invoicing_date

    @data(
        (0, date(2021, 12, 1)),
        (1, date(2021, 11, 24)),
        (2, date(2021, 11, 17)),
    )
    @unpack
    def test_weekly_offset(self, interval, invoicing_date):
        self.line.invoicing_offset_interval = interval
        self.line.invoicing_offset_rule_type = "weekly"
        self.line._onchange_invoicing_offset()
        assert self.line.recurring_next_date == invoicing_date

    @data(
        (0, date(2021, 12, 1)),
        (1, date(2021, 11, 1)),
        (2, date(2021, 10, 1)),
    )
    @unpack
    def test_month_offset(self, interval, invoicing_date):
        self.line.invoicing_offset_interval = interval
        self.line.invoicing_offset_rule_type = "monthly"
        self.line._onchange_invoicing_offset()
        assert self.line.recurring_next_date == invoicing_date
