# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class SalePrivilegeLevel(models.Model):

    _inherit = "sale.privilege.level"

    payment_acquirer_ids = fields.Many2many(
        "payment.acquirer",
        "sale_privilege_level_payment_acquirer_rel",
        "privilege_level_id",
        "acquirer_id",
        "Payment Acquirers",
    )
