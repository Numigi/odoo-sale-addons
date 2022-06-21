# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytest
from odoo.tests import common
from odoo.exceptions import ValidationError
from ..models.product_product import FILTER_PRODUCTS_ON_ORDERS


class TestProduct(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.uom_day = cls.env.ref("uom.product_uom_day")
        cls.uom_hour = cls.env.ref("uom.product_uom_hour")
        cls.rental_service = cls.env["product.product"].create(
            {
                "name": "My Rental Service",
                "type": "service",
                "uom_id": cls.uom_day.id,
                "uom_po_id": cls.uom_day.id,
            }
        )
        cls.rented_product = cls.env["product.product"].create(
            {
                "name": "My Rented Product",
                "type": "service",
                "can_be_rented": True,
                "rental_service_id": cls.rental_service.id,
            }
        )

    def test_rental_service_must_be_in_days(self):
        with pytest.raises(ValidationError):
            self.rental_service.uom_id = self.uom_hour


class TestProductSearch(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env["ir.config_parameter"].set_param(
            FILTER_PRODUCTS_ON_ORDERS, "True"
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "My Rented Product",
                "can_be_rented": True,
            }
        )

    def test_search__rental_order(self):
        context = {"is_rental_sale_order": True}
        assert self._search(context)

    def test_search__rental_order__not_rental_product(self):
        context = {"is_rental_sale_order": True}
        self.product.can_be_rented = False
        assert not self._search(context)

    def test_search__not_rental_order(self):
        context = {"is_rental_sale_order": False}
        assert self._search(context)

    def test_search__not_rental_order__not_rental_product(self):
        context = {"is_rental_sale_order": False}
        self.product.can_be_rented = False
        assert self._search(context)

    def test_search__context_variable_not_defined(self):
        assert self._search({})

    def test_system_parameter_deactivated(self):
        self.env["ir.config_parameter"].set_param(
            FILTER_PRODUCTS_ON_ORDERS, "False"
        )
        context = {"is_rental_sale_order": False}
        assert self._search(context)

    def _search(self, context):
        return (
            self.env["product.product"]
            .with_context(**context)
            .name_search(self.product.name)
        )
