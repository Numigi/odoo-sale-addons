# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class Company(models.Model):

    _inherit = "res.company"

    rental_buffer = fields.Integer(string="Rental Buffer", default=6)
