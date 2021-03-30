# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _


class PaymentAcquirer(models.Model):

    _inherit = "payment.acquirer"

    auto_confirm_sale_order = fields.Boolean("Automatic Order Confirmation")
