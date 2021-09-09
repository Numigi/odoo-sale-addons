# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytest
from odoo.tests import common
from odoo.exceptions import ValidationError


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
