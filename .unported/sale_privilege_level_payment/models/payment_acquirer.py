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

        partner_id = self._context.get("sale_privilege_level_partner_id")
        if partner_id:
            partner = (
                self.env["res.partner"]
                .browse(partner_id)
                .with_context(sale_privilege_level_partner_id=False)
            )
            available_acquirers = partner.sudo().get_available_payment_acquirers()
            res &= available_acquirers

        return res
