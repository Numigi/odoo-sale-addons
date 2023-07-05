# © 2020 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from ddt import ddt, data
from odoo.tests.common import SavepointCase


@ddt
class TestSaleOrderLine(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.message = "Some warning message"

        cls.product = cls.env["product.product"].create(
            {
                "name": "My Product",
                "sale_line_warn": "warning",
                "sale_line_warn_msg": cls.message,
            }
        )

        cls.partner = cls.env.ref("base.res_partner_1")

        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "pricelist_id": cls.env.ref("product.list0").id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product.id,
                            "name": cls.product.name,
                            "product_uom": cls.env.ref("uom.product_uom_unit").id,
                            "product_uom_qty": 1,
                        },
                    )
                ],
            }
        )

        cls.line = cls.sale_order.order_line

    def test_if_no_message__so_line_message_is_empty(self):
        self.product.sale_line_warn = "no-message"
        assert not self.line.product_warning

    @data("warning", "block")
    def test_if_message_enabled__so_line_message_is_displayed(self, warning_config):
        self.product.sale_line_warn = warning_config
        assert self.line.product_warning == self.message
