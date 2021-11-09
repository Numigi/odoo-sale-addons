# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp


class StockMove(models.Model):

    _inherit = "stock.move"

    @api.multi
    def write(self, vals):
        super().write(vals)

        if "state" in vals:
            self.mapped("product_id").with_delay().compute_availability()

        return True
