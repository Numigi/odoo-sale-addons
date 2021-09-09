# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import TestCommissionCase


class TestAccountInvoiceLine(TestCommissionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.invoice = cls._create_invoice(amount=1)
        cls.target = cls._create_target(target_amount=1)
        cls.target.set_confirmed_state()
        cls.target.compute()

    def test_commission_target_count(self):
        invoice_line = self.invoice.invoice_line_ids
        assert invoice_line.commission_target_count == 1

    def test_commission_target_count__cancelled_target(self):
        self.target.set_cancelled_state()
        invoice_line = self.invoice.invoice_line_ids
        assert invoice_line.commission_target_count == 0

    def test_commission_target_count__draft_target(self):
        self.target.set_draft_state()
        invoice_line = self.invoice.invoice_line_ids
        assert invoice_line.commission_target_count == 0
