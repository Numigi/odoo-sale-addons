# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime, timedelta
from odoo.addons.sale_warranty.tests.test_expired_warranties_cron import (
    ExpiredWarrantiesCronCase,
)


class TestExtensionOnWarrantyActivation(ExpiredWarrantiesCronCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        today = datetime.now().date()
        cls.activation_date = today - timedelta(120)
        cls.expiry_date = today - timedelta(90)
        cls.extension_start_date = today - timedelta(60)
        cls.warranty.write(
            {
                "use_warranty_extension": True,
                "activation_date": cls.activation_date,
                "expiry_date": cls.expiry_date,
                "extension_start_date": cls.extension_start_date,
            }
        )

    def test_if_expiration_date_after_today_then_warranty_active(self):
        self.warranty.extension_expiry_date = self.today + timedelta(1)
        self.run_cron()
        assert self.warranty.state == "active"

    def test_if_expiration_date_is_today_then_warranty_active(self):
        self.warranty.extension_expiry_date = self.today
        self.run_cron()
        assert self.warranty.state == "active"

    def test_if_expiration_date_before_today_then_warranty_expired(self):
        self.warranty.extension_expiry_date = self.today - timedelta(1)
        self.run_cron()
        assert self.warranty.state == "expired"

    def test_if_not_use_warranty_extension__then_activation_date_used(self):
        self.warranty.use_warranty_extension = False
        self.run_cron()
        assert self.warranty.state == "expired"
