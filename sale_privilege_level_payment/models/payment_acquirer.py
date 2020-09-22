# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class PaymentAcquirer(models.Model):

    _inherit = "payment.acquirer"

    privilege_level_ids = fields.Many2many(
        "sale.privilege.level",
        "sale_privilege_level_payment_acquirer_rel",
        "acquirer_id",
        "privilege_level_id",
        "Privilege Levels",
    )

    def search(self, *args, **kwargs):
        res = super().search(*args, **kwargs)

        if "filter_payment_acquirer_ids" in self._context:
            available_ids = self._context["filter_payment_acquirer_ids"]
            res = res.filtered(lambda a: available_ids and a.id in available_ids)

        return res
