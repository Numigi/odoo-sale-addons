# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import logging
from odoo import api, models

_logger = logging.getLogger(__name__)

class MailMessage(models.Model):

    _inherit = "mail.message"

    @api.model
    def create(self, vals):
        message = super().create(vals)
        return message

