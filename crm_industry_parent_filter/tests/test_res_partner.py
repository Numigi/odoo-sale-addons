# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests import Form
from odoo.tests.common import SavepointCase


class TestPartner(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Partner"})
        cls.main_industry = cls.env["res.partner.industry"].create(
            {
                "name": "Main",
            }
        )

        cls.secondary_industry_a = cls.env["res.partner.industry"].create(
            {
                "name": "Secondary A",
                "parent_id": cls.main_industry.id,
            }
        )

        cls.secondary_industry_b = cls.env["res.partner.industry"].create(
            {
                "name": "Secondary B",
            }
        )

    def test_set_main_industry(self):
        self.partner.secondary_industry_ids = (
            self.secondary_industry_a | self.secondary_industry_b
        )
        with Form(self.partner) as form:
            form.industry_id = self.main_industry
            assert self.secondary_industry_a in form.secondary_industry_ids
            assert self.secondary_industry_b not in form.secondary_industry_ids

    def test_empty_main_industry(self):
        self.partner.secondary_industry_ids = (
            self.secondary_industry_a | self.secondary_industry_b
        )
        with Form(self.partner) as form:
            form.industry_id = self.env["res.partner.industry"]
            assert not form.secondary_industry_ids
