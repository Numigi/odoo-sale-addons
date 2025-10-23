# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResCompany(models.Model):

    _inherit = "res.company"

    sale_order_partner_restrict = fields.Selection(
        selection_add=[
            ('affiliate_contact',
             'Only Children (including affiliates companies and contacts')
        ]
    )
