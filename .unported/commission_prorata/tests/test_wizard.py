# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.exceptions import ValidationError
from .common import ProrataCase


class TestWizard(ProrataCase):
    def test_create_payroll_default_prorata(self):
        self.wizard.confirm()

        created_payroll = self.env["payroll.preparation.line"].search(
            [("company_id", "=", self.target.company_id.id)]
        )

        assert created_payroll.amount == self.invoiced_amount * self.fixed_rate
        assert self.target.prorata_days_worked == 1
        assert self.target.eligible_amount == self.invoiced_amount * self.fixed_rate

    def test_create_payroll_prorata(self):
        prorata = 0.5
        self.wizard.prorata_days_worked = prorata
        self.wizard.confirm()

        created_payroll = self.env["payroll.preparation.line"].search(
            [("company_id", "=", self.target.company_id.id)]
        )

        prorata_invoiced_amount = (
            self.invoiced_amount * self.fixed_rate * self.wizard.prorata_days_worked
        )

        assert created_payroll.amount == prorata_invoiced_amount
        assert self.target.prorata_days_worked == prorata
        assert self.target.eligible_amount == prorata_invoiced_amount
