# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    sale_authorized_company_ids = fields.Many2many(
        "res.company",
        "res_partner_sale_authorized_company_rel",
        "partner_id",
        "company_id",
        "Authorized Companies For Sales",
    )
