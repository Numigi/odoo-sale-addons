# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class AccountInvoice(models.Model):

    _inherit = "account.invoice"

    def _message_auto_subscribe_followers(self, updated_values, default_subtype_ids):
        updated_values = {k: v for k, v in updated_values.items() if k != "user_id"}
        return super()._message_auto_subscribe_followers(
            updated_values, default_subtype_ids
        )
