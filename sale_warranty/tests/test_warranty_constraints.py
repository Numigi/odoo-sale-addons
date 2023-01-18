# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytest
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from odoo.addons.sale_warranty.tests.common import SaleWarrantyCase


class TestWarrantyConstraints(SaleWarrantyCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        today = datetime.now().date()
        cls.warranty = cls.env['sale.warranty'].create({
            'partner_id': cls.customer.id,
            'product_id': cls.product_a.id,
            'type_id': cls.warranty_6_months.id,
            'activation_date': today,
            'expiry_date': today + timedelta(30),
        })

    def test_extension_start_must_be_prior_to_expiry(self):
        with pytest.raises(ValidationError):
            self.warranty.activation_date = self.warranty.expiry_date + timedelta(1)
