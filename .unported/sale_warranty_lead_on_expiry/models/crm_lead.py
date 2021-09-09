# © 2020 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class CrmLead(models.Model):

    _inherit = 'crm.lead'

    generated_from_warranty = fields.Boolean(copy=False)
