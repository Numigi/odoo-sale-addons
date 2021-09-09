# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models
from .common import DEFAULT_DELAY_BETWEEN_LEADS


class Company(models.Model):

    _inherit = 'res.company'

    warranty_delay_between_leads = fields.Integer(
        string="Warranty Delay Between Leads", default=DEFAULT_DELAY_BETWEEN_LEADS)
