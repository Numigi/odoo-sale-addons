# © 2022 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    rental_status = fields.Selection(
        selection=[
            ("rented", "Rented"),
            ("partially_delivered", "Partially Delivered"),
            ("delivered", "Delivered"),
            ("partially_returned", "Partially Returned"),
            ("returned", "Returned"),
        ],
        compute="_compute_rental_status",
        store=True,
    )

    @api.depends("is_rental", "completion_rate", "return_rate")
    def _compute_rental_status(self):
        for rec in self:
            if not rec.is_rental or (
                rec.is_rental and rec.state not in ("sale", "done")
            ):
                rec.rental_status = None
                continue
            completion_percent = (
                rec.completion_rate and int(rec.completion_rate.replace("%", "")) or 0
            )
            return_percent = (
                rec.return_rate and int(rec.return_rate.replace("%", "")) or 0
            )
            print("return_percent", return_percent)
            if completion_percent == 0:
                rec.rental_status = "rented"
            elif 0 < completion_percent < 100:
                rec.rental_status = "partially_delivered"
            elif completion_percent == 100 and return_percent == 0:
                rec.rental_status = "delivered"
            elif 0 < return_percent < 100:
                rec.rental_status = "partially_returned"
            elif return_percent == 100:
                rec.rental_status = "returned"
