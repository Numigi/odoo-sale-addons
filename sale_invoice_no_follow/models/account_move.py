# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import logging
from odoo import api, models

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _name = "account.move"
    _inherit = ['account.move', 'mail.thread', 'mail.activity.mixin']

    @api.model
    def create(self, vals):
        return super(AccountMove, self.with_context(mail_create_nosubscribe=True)).create(vals)

    def _message_auto_subscribe_followers(self, updated_values, subtype_ids):
        updated_values = {k: v for k,
                          v in updated_values.items() if k != "user_id"}
        return super(AccountMove, self)._message_auto_subscribe_followers(
            updated_values, subtype_ids
        )
