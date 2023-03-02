# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from ddt import ddt, data
from lxml import etree
from .common import TestCommissionCase


@ddt
class TestViews(TestCommissionCase):

    @data(
        "view_invoice_lines",
        "view_child_targets",
    )
    def test_buttons_is_visible_for_basic_users(self, button_name):
        form = self._get_commission_target_form(self.user)
        assert form.xpath(f"//button[@name='{button_name}']")

    def _get_commission_target_form(self, user):
        view = self.env.ref("commission.commission_target_form")
        arch = (
            self.env["commission.target"]
            .sudo(user)
            .fields_view_get(view_id=view.id)["arch"]
        )
        return etree.fromstring(arch)
