# © 2021 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.addons.sale_commitment_date_update.tests.common import SaleCommitmentDateCase


class TestSaleCommitmentDateMrp(SaleCommitmentDateCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        
        cls.route_mrp = cls.env.ref("mrp.route_warehouse0_manufacture")
        cls.route_mto = cls.env.ref("stock.route_warehouse0_mto")
        cls.product.route_ids = cls.route_mto | cls.route_mrp
        cls.env["mrp.bom"].create({
            "product_id": cls.product.id,
            "product_tmpl_id": cls.product.product_tmpl_id.id,
        }
        )
        cls.sale_order.action_confirm()

    def test_propagates_date_to_mrp(self):
        self.wizard.confirm()
        mrp_order = self.env["mrp.production"].search([('procurement_group_id', '=', self.sale_order.procurement_group_id.id)])
        
        assert mrp_order
        assert mrp_order.date_planned_finished == self.new_date