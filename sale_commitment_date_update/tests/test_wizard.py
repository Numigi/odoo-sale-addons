# © 2021 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import SavepointCase
from datetime import datetime, timedelta
from freezegun import freeze_time


class TestWizard(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.new_date = datetime(1990, 1, 25)
        cls.old_date = cls.new_date - timedelta(5)

        cls.product = cls.env["product.product"].create(
            {
                "name": "Product",
                "type": "product",
            }
        )

        cls.partner = cls.env["res.partner"].create(
            {
                "name": "william",
            }
        )

        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "pricelist_id": cls.env.ref("product.list0").id,
                "commitment_date": cls.old_date,
            }
        )

        cls.sale_order_line = cls.env["sale.order.line"].create(
            {
                "product_id": cls.product.id,
                "order_id": cls.sale_order.id,
                "product_uom": cls.product.uom_id.id,
                "product_uom_qty": 1,
                "name": "line",
            }
        )

        cls.wizard = cls.env["sale.commitment.date.update"].create(
            {
                "order_id": cls.sale_order.id,
                "date": cls.new_date,
            }
        )

    def test_propagates_date_to_sale_order(self):
        self.wizard.confirm()
        assert self.sale_order.commitment_date == self.new_date

    def test_propagates_date_to_stock_move(self):
        self.sale_order.action_confirm()
        self.wizard.confirm()
        move = self.sale_order_line.move_ids
        assert move.date_expected == self.new_date

    def test_respects_security_lead_time(self):
        self.sale_order.company_id.security_lead = 2
        self.sale_order.action_confirm()
        self.wizard.confirm()
        assert self.sale_order_line.move_ids.date_expected == self.new_date - timedelta(
            2
        )

    def test_two_steps(self):
        self.sale_order.warehouse_id.delivery_steps = "pick_ship"
        self.sale_order.action_confirm()
        self.wizard.confirm()
        ship_move = self.sale_order_line.move_ids
        pick_move = ship_move.move_orig_ids
        assert ship_move.date_expected == self.new_date
        assert pick_move.date_expected == self.new_date

    def test_two_sale_order_lines(self):
        new_line = self.sale_order_line.copy(
            {"product_id": self.product.copy().id, "order_id": self.sale_order.id}
        )
        self.sale_order.action_confirm()
        self.wizard.confirm()
        assert self.sale_order_line.move_ids.date_expected == self.new_date
        assert new_line.move_ids.date_expected == self.new_date

    def test_sale_order_without_date(self):
        self.sale_order.commitment_date = None
        with freeze_time(self.old_date):
            self.sale_order.action_confirm()
        self.wizard.confirm()
        assert self.sale_order_line.move_ids.date_expected == self.new_date

    def test_sale_order_with_customer_lead(self):
        self.sale_order.commitment_date = None
        self.sale_order_line.customer_lead = 3
        with freeze_time(self.old_date):
            self.sale_order.action_confirm()
        self.wizard.confirm()
        assert self.sale_order_line.move_ids.date_expected == self.new_date

    def test_two_sale_order_lines_with_two_steps(self):
        self.sale_order.warehouse_id.delivery_steps = "pick_ship"
        new_line = self.sale_order_line.copy(
            {"order_id": self.sale_order.id,}
        )
        self.sale_order.action_confirm()
        self.wizard.confirm()
        assert self.sale_order_line.move_ids.move_orig_ids.date_expected == self.new_date

    def test_stock_move_completed(self):
        self.sale_order.action_confirm()
        self.sale_order_line.move_ids.is_done = True
        self.wizard.confirm()
        assert self.sale_order_line.move_ids.date_expected == self.new_date