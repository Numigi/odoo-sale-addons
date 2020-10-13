# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    property_purchase_currency_id = fields.Many2one(
        "res.currency",
        string="Customer Currency",
        company_dependent=True,
        help="This currency will be used, instead of the default one, for sales to this partner",
    )
