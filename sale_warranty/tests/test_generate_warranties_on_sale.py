# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from .common import SaleWarrantyCase


class TestSaleOrderWithSingleProductAndWarranty(SaleWarrantyCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._confirm_sale_order()

    def test_on_sale_order_confirm_warranty_is_created(self):
        assert len(self.sale_order.warranty_ids) == 1

    def test_on_sale_order_confirm_warranty_state_is_pending(self):
        assert self.sale_order.warranty_ids.state == 'pending'

    def test_product_propagated_to_warranty(self):
        assert self.sale_order.warranty_ids.product_id == self.product_a

    def test_warranty_type_propagated_from_product(self):
        assert self.sale_order.warranty_ids.type_id == self.warranty_6_months

    def test_warranty_description_propagated_from_warranty_type(self):
        assert self.sale_order.warranty_ids.description == self.warranty_6_months.description

    def test_sale_line_propagated_to_warranty(self):
        assert self.sale_order.warranty_ids.sale_order_line_id == self.sale_order.order_line

    def test_commercial_partner_propagated_to_warranty(self):
        assert self.sale_order.warranty_ids.partner_id == self.customer_company

    def test_one_warranty_created_per_product_unit(self):
        self.sale_order.order_line.product_uom_qty = 3
        assert len(self.sale_order.warranty_ids) == 3

    def test_on_add_extra_order_line_extra_warranty_is_added(self):
        assert len(self.sale_order.warranty_ids) == 1

        self.sale_order.write({
            'order_line': [
                (0, 0, {
                    'product_id': self.product_b.id,
                    'name': self.product_b.name,
                    'product_uom': self.env.ref('uom.product_uom_unit').id,
                    'product_uom_qty': 1,
                })
            ]
        })

        warranties = self.sale_order.warranty_ids.sorted(key=lambda w: w.id)
        sale_lines = self.sale_order.order_line.sorted(key=lambda l: l.id)
        assert len(warranties) == 2
        assert warranties[0].sale_order_line_id == sale_lines[0]
        assert warranties[1].sale_order_line_id == sale_lines[1]

    def test_on_add_extra_quantity_then_extra_warranty_is_added(self):
        assert len(self.sale_order.warranty_ids) == 1
        self.sale_order.order_line.product_uom_qty = 2
        assert len(self.sale_order.warranty_ids) == 2


class TestSaleOrderWithCustomNumberOfWarranties(SaleWarrantyCase):

    def test_if_product_has_multiple_warranties_then_each_warranty_created(self):
        self.product_a.warranty_type_ids = self.warranty_6_months | self.warranty_2_years
        self.sale_order.order_line.product_uom_qty = 3
        self._confirm_sale_order()
        assert len(self.sale_order.warranty_ids) == 6

    def test_if_product_not_warranteed_no_warranty_created(self):
        self.product_a.warranty_type_ids = False
        self._confirm_sale_order()
        assert not self.sale_order.warranty_ids
