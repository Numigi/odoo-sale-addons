# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from ddt import data, ddt
from odoo.tests.common import SavepointCase


@ddt
class TestSaleOrder(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {"name": "Product A", "invoice_policy": "order"}
        )

        cls.customer = cls.env["res.partner"].create({"name": "My Customer"})

        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.customer.id,
                "pricelist_id": cls.env.ref("product.list0").id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product.id,
                            "name": cls.product.name,
                            "product_uom": cls.env.ref("uom.product_uom_unit").id,
                            "product_uom_qty": 10,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product.id,
                            "name": cls.product.name,
                            "product_uom": cls.env.ref("uom.product_uom_unit").id,
                            "product_uom_qty": 20,
                        },
                    ),
                ],
            }
        )
        cls.sale_order.action_confirm()

    def _process_invoicing_wizard(self, option):
        wizard_obj = self.env["sale.advance.payment.inv"].with_context(
            active_ids=[self.sale_order.id]
        )
        wizard = wizard_obj.create(wizard_obj.default_get(list(wizard_obj._fields)))
        wizard.advance_payment_method = option
        return wizard.create_invoices()

    def test_if_whole_order__order_status_invoiced(self):
        self._process_invoicing_wizard("whole_order")
        assert self.sale_order.whole_order_invoiced

    @data("delivered")
    def test_if_not_whole_order__order_status_not_invoiced(self, option):
        self._process_invoicing_wizard(option)
        assert not self.sale_order.whole_order_invoiced

    @data("delivered", "whole_order")
    def test_after_wizard_processed__invoice_created(self, option):
        assert not self.sale_order.invoice_ids
        self._process_invoicing_wizard("whole_order")
        assert self.sale_order.invoice_ids

    def test_on_set_whole_order_invoiced__status_set_to_invoiced(self):
        assert self.sale_order.invoice_status == "to invoice"
        self.sale_order.whole_order_invoiced = True
        assert self.sale_order.invoice_status == "invoiced"

    def test_on_set_whole_order_invoiced__line_status_set_to_invoiced(self):
        assert self.sale_order.mapped("order_line.invoice_status") == [
            "to invoice",
            "to invoice",
        ]
        self.sale_order.whole_order_invoiced = True
        assert self.sale_order.mapped("order_line.invoice_status") == [
            "invoiced",
            "invoiced",
        ]

    def test_on_copy__whole_order_invoiced_not_propagated(self):
        self.sale_order.whole_order_invoiced = True
        new_order = self.sale_order.copy()
        assert not new_order.whole_order_invoiced

    def test_wizard_default_whole_order_invoiced(self):
        def check_advance_payment_method(order_ids):
            wizard_obj = self.env["sale.advance.payment.inv"].with_context(
                active_ids=order_ids
            )
            wizard = wizard_obj.create(wizard_obj.default_get(list(wizard_obj._fields)))
            assert wizard.advance_payment_method == "whole_order"

        # Check on one record
        check_advance_payment_method([self.sale_order.id])

        # Check on more than one record
        new_order = self.sale_order.copy()
        check_advance_payment_method([self.sale_order.id, new_order.id])
