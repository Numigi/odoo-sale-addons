# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from lxml import etree
from .common import TestCommissionCase


class TestViews(TestCommissionCase):
    def test_compute_button_is_visible_for_basic_users(self):
        form = self._get_commission_target_form(self.user)
        assert form.xpath("//button[@name='compute']")

    def _get_commission_target_form(self, user):
        view = self.env.ref("commission.commission_target_form")
        arch = (
            self.env["commission.target"]
            .sudo(user)
            .fields_view_get(view_id=view.id)["arch"]
        )
        return etree.fromstring(arch)
