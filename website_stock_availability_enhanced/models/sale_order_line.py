# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    displayed_delay = fields.Char()

    def _update_displayed_delay(self):
        info = self.product_id._get_enhanced_availability_info(0)
        delay = info.get("replenishment_delay")
        if delay:
            self.displayed_delay = _("{} days").format(delay)
