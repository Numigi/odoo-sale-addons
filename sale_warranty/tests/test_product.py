# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytest
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from odoo.addons.sale_warranty.tests.common import SaleWarrantyCase


class TestProduct(SaleWarrantyCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_a.warranty_type_ids = False
        cls.product_a.tracking = "none"

    def test_if_serialized_only__warranty_type_not_selectable(self):
        self.warranty_2_years.allow_non_serialized_products = False
        with pytest.raises(ValidationError):
            self.product_a.warranty_type_ids |= self.warranty_2_years

    def test_if_non_serialized_product_allowed__warranty_type_selectable(self):
        self.warranty_2_years.allow_non_serialized_products = True
        self.product_a.warranty_type_ids |= self.warranty_2_years
