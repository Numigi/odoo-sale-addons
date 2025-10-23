# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class EventRegistration(models.Model):

    _inherit = "event.registration"

    sale_order_state = fields.Selection(
        string="Sale Order Status", related="sale_order_id.state"
    )
