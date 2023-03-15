# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    partner_id = fields.Many2one(related="move_id.partner_id", store=True)
    origin = fields.Char(store=True)
