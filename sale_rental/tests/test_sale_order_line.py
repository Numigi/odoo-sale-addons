# © 2022 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytest
from odoo.exceptions import ValidationError
from odoo.addons.sale_kit.tests.common import SaleOrderLineCase


class KitRentalCase(SaleOrderLineCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.uom_day = cls.env.ref("uom.product_uom_day")
        cls.price_per_day = 30
        cls.rental_service = cls.env["product.product"].create(
            {
                "name": "My Rental Service",
                "type": "service",
                "uom_id": cls.uom_day.id,
                "uom_po_id": cls.uom_day.id,
                "list_price": cls.price_per_day,
            }
        )
        cls.kit.write(
            {"can_be_rented": True, "rental_service_id": cls.rental_service.id}
        )

    def setUp(self):
        super().setUp()
        self.order.is_rental = True

    def get_rental_service_lines(self):
        return self.order.order_line.filtered(
            lambda l: l.product_id == self.rental_service
        )


class TestKitRental(KitRentalCase):
    def test_if_not_rental_order__rental_service_not_added(self):
        self.order.is_rental = False
        self.add_kit_on_sale_order()
        assert len(self.order.order_line) == 4

    def test_one_line_added_for_the_rental_service(self):
        self.add_kit_on_sale_order()
        service = self.get_rental_service_lines()
        assert service.is_rental_service

    def test_rental_service_kit_reference(self):
        self.add_kit_on_sale_order()
        self.add_kit_on_sale_order()
        services = self.get_rental_service_lines()
        assert services.mapped("kit_reference") == ["K1", "K2"]

    def test_rental_service_is_not_important_component(self):
        self.add_kit_on_sale_order()
        service = self.get_rental_service_lines()
        assert not service.is_important_kit_component

    def test_rental_service_description_is_set(self):
        self.add_kit_on_sale_order()
        service = self.get_rental_service_lines()
        assert service.name

    def test_rental_service_is_in_days(self):
        self.add_kit_on_sale_order()
        service = self.get_rental_service_lines()
        assert service.product_uom == self.uom_day
        assert service.product_uom_qty == 1

    def test_rental_service_has_a_unit_price(self):
        self.env["res.currency.rate"].search([]).write({"rate": 1})
        self.add_kit_on_sale_order()
        service = self.get_rental_service_lines()
        assert service.price_unit == self.price_per_day

    def test_rental_service_readonly_fields(self):
        self.add_kit_on_sale_order()

        service = self.get_rental_service_lines()
        print ('-----------product_uom_readonly-----------------')
        print (service.is_kit)
        assert service.kit_reference_readonly
        assert service.product_readonly
        assert not service.product_uom_qty_readonly
        assert service.product_uom_readonly
        assert not service.handle_widget_invisible
        assert service.trash_widget_invisible
        assert service.rental_date_from_required
        assert service.rental_date_from_editable
        assert service.rental_date_to_editable

#     def test_component_unit_price_is_zero(self):
#         self.add_kit_on_sale_order()
#         components = self.get_component_lines()
#         assert not components[0].price_unit
#         assert not components[1].price_unit
#         assert not components[2].price_unit
#
#     def test_component_unit_price_readonly(self):
#         self.add_kit_on_sale_order()
#         components = self.get_component_lines()
#         assert components[0].price_unit_readonly
#         assert components[1].price_unit_readonly
#         assert components[2].price_unit_readonly
#
#     def test_onchange_qty__component_unit_price_is_zero(self):
#         self.add_kit_on_sale_order()
#         components = self.get_component_lines()
#         components[0].product_uom_change()
#         assert not components[0].price_unit
#
#     def test_component_taxes_readonly(self):
#         self.add_kit_on_sale_order()
#         components = self.get_component_lines()
#         assert components[0].taxes_readonly
#         assert components[1].taxes_readonly
#         assert components[2].taxes_readonly
#
#     def test_onchange_fiscal_position__component_taxes_empty(self):
#         self.add_kit_on_sale_order()
#         self.order._compute_tax_id()
#         components = self.get_component_lines()
#         assert not components[0].tax_id
#
#     def test_kit_unit_price_is_zero(self):
#         self.add_kit_on_sale_order()
#         kit = self.get_kit_lines()
#         assert not kit.price_unit
#
#     def test_kit_unit_price_readonly(self):
#         self.add_kit_on_sale_order()
#         kit = self.get_kit_lines()
#         assert kit.price_unit_readonly
#
#     def test_onchange_qty__kit_unit_price_is_zero(self):
#         self.add_kit_on_sale_order()
#         kit = self.get_kit_lines()
#         kit.product_uom_change()
#         assert not kit.price_unit
#
#     def test_kit_quantity_readonly(self):
#         self.add_kit_on_sale_order()
#         kit = self.get_kit_lines()
#         assert kit.product_uom_qty_readonly
#
#     def test_kit_taxes_readonly(self):
#         self.add_kit_on_sale_order()
#         kit = self.get_kit_lines()
#         assert kit.taxes_readonly
#
#     def test_kit_taxes_empty(self):
#         self.add_kit_on_sale_order()
#         kit = self.get_kit_lines()
#         assert not kit.tax_id
#
#     def test_onchange_fiscal_position__kit_taxes_empty(self):
#         self.add_kit_on_sale_order()
#         self.order._compute_tax_id()
#         kit = self.get_kit_lines()
#         assert not kit.tax_id
#
#     def test_if_kit_cannot_be_rented__raise_error(self):
#         self.kit.can_be_rented = False
#         with pytest.raises(ValidationError):
#             self.add_kit_on_sale_order()
#
#     def test_service_taxes_not_readonly(self):
#         self.add_kit_on_sale_order()
#         service = self.get_rental_service_lines()
#         assert not service.taxes_readonly
#
#     def test_service_taxes_not_empty(self):
#         self.add_kit_on_sale_order()
#         services = self.get_rental_service_lines()
#         assert services.tax_id
#
#     def test_onchange_fiscal_position__service_taxes_not_empty(self):
#         self.add_kit_on_sale_order()
#         self.order._compute_tax_id()
#         services = self.get_rental_service_lines()
#         assert services.tax_id
#
#
# class TestNonKitRental(KitRentalCase):
#     """Test the rental of a single product (instead of a kit)."""
#
#     @classmethod
#     def setUpClass(cls):
#         super().setUpClass()
#         cls.kit.is_kit = False
#         cls.kit.kit_line_ids = None
#
#     def test_if_not_rental_order__rental_service_not_added(self):
#         self.order.is_rental = False
#         self.add_kit_on_sale_order()
#         assert len(self.order.order_line) == 1
#
#     def test_one_line_added_for_the_rental_service(self):
#         self.add_kit_on_sale_order()
#         lines = self.order.order_line
#         assert len(lines) == 2
#         assert lines[1].product_id == self.rental_service
#         assert lines[1].is_rental_service
