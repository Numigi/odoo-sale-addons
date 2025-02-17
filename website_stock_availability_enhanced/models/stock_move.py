# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):

    _inherit = "stock.move"

    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            if "state" in vals or "date" in vals:
                rec.mapped("product_id").schedule_compute_availability()
        return res
