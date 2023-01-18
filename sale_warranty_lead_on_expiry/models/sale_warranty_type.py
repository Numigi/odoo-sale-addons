# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class WarrantyType(models.Model):

    _inherit = 'sale.warranty.type'

    automated_action = fields.Boolean(
        'Automated Warranty End Action',
        help="If active, an opportunity is created for each "
        "expired warranty or warranty extension, if applicable."
    )

    sales_team_id = fields.Many2one(
        'crm.team', 'Sales Team', ondelete='restrict',
    )

    automated_action_delay = fields.Integer(
        'Days To Trigger Action',
        help="Number of days before triggering a follow up action."
    )
