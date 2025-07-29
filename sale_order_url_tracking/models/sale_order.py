# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    tracking_url = fields.Char("Tracking", tracking=True)
