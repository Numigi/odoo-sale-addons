# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrderTypology(models.Model):
    _inherit = "sale.order.type"

    mail_template = fields.Many2one("mail.template", "Email Template")
