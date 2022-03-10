# © 2018 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import common


class TestResPartner(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.territory_1 = cls.env["res.territory"].create(
            {
                "name": "Territory 1",
            }
        )
        cls.territory_2 = cls.env["res.territory"].create(
            {
                "name": "Territory 2",
            }
        )

        cls.fsa_1 = cls.env["forward.sortation.area"].create(
            {
                "name": "A1A",
                "territory_ids": [(6, 0, [cls.territory_1.id, cls.territory_2.id])],
            }
        )
        cls.fsa_2 = cls.env["forward.sortation.area"].create(
            {
                "name": "A1B",
            }
        )

        cls.lead = cls.env["crm.lead"].create(
            {
                "name": "Partner",
                "zip": "A1AB2B",
            }
        )

        cls.lead_2 = cls.env["crm.lead"].create(
            {
                "name": "Partner",
                "zip": "A1CB2B",
            }
        )

    def test_compute_fsa_id(self):
        assert self.lead.fsa_id == self.fsa_1
        assert not self.lead_2.fsa_id

        self.lead.write({"zip": None})
        assert not self.lead.fsa_id
        assert not self.lead_2.fsa_id

    def test_field_related_territory_ids(self):
        assert self.territory_1 in self.lead.territory_ids
        assert self.territory_2 in self.lead.territory_ids

        self.fsa_1.write({"territory_ids": [(3, self.territory_1.id)]})
        assert self.territory_1 not in self.lead.territory_ids
        assert self.territory_2 in self.lead.territory_ids

        self.territory_1.write({"fsa_ids": [(6, 0, [self.fsa_1.id, self.fsa_2.id])]})
        assert self.territory_1 in self.lead.territory_ids
        assert self.territory_2 in self.lead.territory_ids

    def test_change_fsa_name_change_leads(self):
        assert self.lead.fsa_id == self.fsa_1
        assert self.lead in self.fsa_1.lead_ids

        self.fsa_1.write({"name": "A1C"})
        assert not self.lead.fsa_id
        assert self.lead_2.fsa_id == self.fsa_1
