# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = "sale.order"

    partner_highest_parent_id = fields.Many2one(
        "res.partner",
        string="Parent company",
        related="partner_id.highest_parent_id",
        store=True,
    )
