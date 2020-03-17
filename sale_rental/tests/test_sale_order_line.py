# © 2020 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

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
        self.add_kit_on_sale_order()
        service = self.get_rental_service_lines()
        assert service.price_unit == self.price_per_day

    def test_rental_service_readonly_fields(self):
        self.add_kit_on_sale_order()
        service = self.get_rental_service_lines()
        assert service.product_readonly
        assert not service.product_uom_qty_readonly
        assert service.product_uom_readonly
        assert service.handle_widget_invisible
        assert service.trash_widget_invisible
        assert service.rental_date_from_required
        assert service.rental_date_from_editable
        assert service.rental_date_to_editable


class TestNonKitRental(KitRentalCase):
    """Test the rental of a single product (instead of a kit)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.kit.is_kit = False
        cls.kit.kit_line_ids = None

    def test_if_not_rental_order__rental_service_not_added(self):
        self.order.is_rental = False
        self.add_kit_on_sale_order()
        assert len(self.order.order_line) == 1

    def test_one_line_added_for_the_rental_service(self):
        self.add_kit_on_sale_order()
        lines = self.order.order_line
        assert len(lines) == 2
        assert lines[1].product_id == self.rental_service
        assert lines[1].is_rental_service
