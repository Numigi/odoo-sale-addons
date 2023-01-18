# © 2022 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, _


class Event(models.Model):

    _inherit = "event.event"

    confirmed_attendees_count = fields.Integer(
        compute="_compute_confirmed_attendees_count"
    )

    def _compute_confirmed_attendees_count(self):
        for event in self:
            event.confirmed_attendees_count = len(
                event.registration_ids.filtered(
                    lambda r: r.sale_order_id.state in ("sale", "done")
                    and r.state != "cancel"
                )
            )
