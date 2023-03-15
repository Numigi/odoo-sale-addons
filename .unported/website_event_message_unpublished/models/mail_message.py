# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models


class MailMessage(models.Model):
    _inherit = "mail.message"

    @api.model
    def create(self, vals):
        message = super().create(vals)

        # if message.model == "event.event":
        #     message.website_published = False

        return message
