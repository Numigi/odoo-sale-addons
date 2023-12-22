# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import SavepointCase


class TestSaleProductPackModifiable(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.parent_pack = cls.env.ref(
            "product_pack.product_pack_cpu_detailed_totalized"
        )
        cls.parent_pack.pack_modifiable = True

        # Create new child pack
        cls.child_pack = cls.env["product.product"].create(
            {
                "name": "Numigi Child Pack Test",
                "categ_id": cls.env.ref("product.product_category_4").id,
                "pack_ok": True,
                "pack_type": "detailed",
                "pack_component_price": "totalized",
                "pack_modifiable": True,
                "standard_price": 10.5,
                "list_price": 13.0,
                "type": "service",
            }
        )

        # Update list price of child pack components
        cls.product_16 = cls.env.ref("product.product_product_16")
        cls.product_16.list_price = 40.0

        cls.product_24 = cls.env.ref("product.product_product_24")
        cls.product_24.list_price = 11.0

        cls.child_pack.write(
            {
                "pack_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_16.id,
                            "quantity": 1.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_24.id,
                            "quantity": 3.0,
                        },
                    ),
                ]
            }
        )

        # Associate parent pack to child pack
        # and unlink previous demo components
        cls.parent_pack.write(
            {
                "pack_line_ids": [
                    (6, 0, []),
                ]
            }
        )
        cls.child_pack_component = cls.env["product.pack.line"].create(
            {
                "parent_product_id": cls.parent_pack.id,
                "product_id": cls.child_pack.id,
                "quantity": 1,
            }
        )

        cls.sale_order = cls.env["sale.order"].create(
            {
                "company_id": cls.env.company.id,
                "partner_id": cls.env.ref("base.res_partner_12").id,
            }
        )

    def test_compute_main_parent_unit_price_remove_component_then_pack(self):
        self._generate_sale_order_line()

        # Must have 6 lines created (packs + their components)
        # Parent pack : 1 pack => Total : 1
        # Child pack : 1 pack contains 2 components => Total : 3
        self.assertEqual(len(self.sale_order.order_line), 4)

        # Parent pack price: total of price on child pack
        # Child pack price: (40.0 * 1.0) + (11.0 * 3.0)=> Total : 73.0
        self.assertEqual(self._get_parent_pack_price_unit(), 73.0)

        component_2_line = self.sale_order.order_line.filtered(
            lambda line: line.product_id == self.product_24
        )

        # Removing one line of component
        self.sale_order.write({"order_line": [(2, component_2_line.id, False)]})

        # Now, number of order lines will be 3
        self.assertEqual(len(self.sale_order.order_line), 3)

        # Main pack price unit : 73.0 - 33.0
        self.assertEqual(self._get_parent_pack_price_unit(), 40.0)

        # Then removing the whole child pack
        child_pack_line = self.sale_order.order_line.filtered(
            lambda line: line.product_id == self.child_pack
        )
        self.sale_order.write({"order_line": [(2, child_pack_line.id, False)]})

        # Main pack price unit must be 0.0
        self.assertEqual(self._get_parent_pack_price_unit(), 0.0)

    def test_compute_main_parent_unit_price_remove_pack_only(self):
        self._generate_sale_order_line()
        # Removing the whole child pack
        child_pack_line = self.sale_order.order_line.filtered(
            lambda line: line.product_id == self.child_pack
        )
        self.sale_order.write({"order_line": [(2, child_pack_line.id, False)]})

        # Main pack price unit must be 0.0
        self.assertEqual(self._get_parent_pack_price_unit(), 0.0)

    def test_pricelist_applied(self):
        """
        This function will fail if the dependeny product_pack_ext is not fixed.
        Curreny for conversion must be the right one if using pricelist.
        """
        my_currency = self.env["res.currency"].create(
            {"name": "Another currency", "symbol": "other"}
        )
        self.env["res.currency.rate"].create(
            {
                "name": "2020-12-10",
                "rate": 2,  # 1.30813
                "currency_id": my_currency.id,
                "company_id": self.env.company.id,
            }
        )
        new_simple_pricelist = self.env["product.pricelist"].create(
            {
                "name": "New pricelist",
                "currency_id": my_currency.id,
            }
        )
        self.sale_order.pricelist_id = new_simple_pricelist.id

        self.sale_order._onchange_pricelist_id()
        self.sale_order._compute_currency_rate()

        self.sale_order.refresh()
        self._generate_sale_order_line()

        self.assertEqual(self.sale_order.currency_id, my_currency)

        self.assertEqual(len(self.sale_order.order_line), 4)

        # Parent pack price: total of price on child pack
        # Child pack price with currency rate linked to order pricelist
        self.assertEqual(self._get_parent_pack_price_unit(), 95.5)

        component_2_line = self.sale_order.order_line.filtered(
            lambda line: line.product_id == self.product_24
        )

        # Removing one line of component
        self.sale_order.write({"order_line": [(2, component_2_line.id, False)]})

        # Main pack price unit with pricelist currency
        self.assertEqual(self._get_parent_pack_price_unit(), 52.33)

        # Then removing the whole child pack
        child_pack_line = self.sale_order.order_line.filtered(
            lambda line: line.product_id == self.child_pack
        )
        self.sale_order.write({"order_line": [(2, child_pack_line.id, False)]})

        # Main pack price unit must be 0.0
        self.assertEqual(self._get_parent_pack_price_unit(), 0.0)

    def _get_parent_pack_price_unit(self):
        # Main pack price unit : 73.0 - 33.0
        parent_pack_line = self.sale_order.order_line.filtered(
            lambda line: line.product_id == self.parent_pack
        )
        return parent_pack_line.price_unit

    def _generate_sale_order_line(self):
        self.env["sale.order.line"].create(
            {
                "order_id": self.sale_order.id,
                "name": self.parent_pack.name,
                "product_id": self.parent_pack.id,
                "product_uom_qty": 2,
            }
        )
