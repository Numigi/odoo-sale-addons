# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytest
from ddt import ddt, data
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


@ddt
class TestProductSearch(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create({"name": "My Rented Product"})

    @data(
        (True, False, False),
        (True, True, True),
        (False, False, True),
        (False, True, False),
    )
    def test_filter_on_sales_orders_activated(self, args):
        self.env["ir.config_parameter"].set_param(
            FILTER_PRODUCTS_ON_ORDERS, "True",
        )
        self.product.can_be_rented = args[0]
        context = {"is_rental_sale_order": args[1]}
        product = self._search(context)
        assert bool(product) is args[2]

    @data(
        (True, False, True),
        (True, True, True),
        (False, False, True),
        (False, True, False),
    )
    def test_filter_on_sales_orders_deactivated(self, args):
        self.env["ir.config_parameter"].set_param(
            FILTER_PRODUCTS_ON_ORDERS, "False",
        )
        self.product.can_be_rented = args[0]
        context = {"is_rental_sale_order": args[1]}
        product = self._search(context)
        assert bool(product) is args[2]

    def _search(self, context):
        return (
            self.env["product.product"]
            .with_context(**context)
            .name_search(self.product.name)
        )