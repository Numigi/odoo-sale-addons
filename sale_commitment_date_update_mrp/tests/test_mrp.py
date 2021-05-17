# © 2021 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.addons.sale_commitment_date_update.tests.common import SaleCommitmentDateCase
from datetime import timedelta


class TestSaleCommitmentDateMrp(SaleCommitmentDateCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.route_mrp = cls.env.ref("mrp.route_warehouse0_manufacture")
        cls.route_mto = cls.env.ref("stock.route_warehouse0_mto")
        cls.product.route_ids = cls.route_mto | cls.route_mrp
        cls.env["mrp.bom"].create(
            {
                "product_id": cls.product.id,
                "product_tmpl_id": cls.product.product_tmpl_id.id,
            }
        )
        cls.sale_order.action_confirm()
        cls.mrp_order = cls.sale_order_line.move_ids.created_production_id

    def test_propagates_date_to_mrp(self):
        self.wizard.confirm()
        assert self.mrp_order.date_planned_finished == self.new_date
        assert self.mrp_order.date_planned_start == self.new_date

    def test_company_manufacturing_lead(self):
        self.sale_order.company_id.manufacturing_lead = 3
        self.wizard.confirm()
        assert self.mrp_order.date_planned_start == self.new_date - timedelta(3)

    def test_company_product_delay(self):
        self.product.produce_delay = 3
        self.wizard.confirm()
        assert self.mrp_order.date_planned_start == self.new_date - timedelta(3)
