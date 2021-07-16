# © 2021 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from .common import ProrataCase


class TestWizard(ProrataCase):
    def test_compute_updates_eligible_amount(self):
        prorata = 0.5
        self.target.prorata_days_worked = prorata
        self._create_invoice(amount=1000)

        self.target.compute()

        assert self.target.eligible_amount == self.target.total_amount * self.target.prorata_days_worked
