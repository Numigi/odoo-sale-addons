# © 2021 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class CommissionCategory(models.Model):
    _name = "commission.category"
    _description = "Commission Category"

    name = fields.Char()
    rate_type = fields.Selection(
        [
            ("fixed", "Fixed"),
            ("interval", "Interval"),
        ],
        "Rate Type",
        default="fixed",
    )
    basis = fields.Selection(
        [
            ("personal", "My Sales"),
            ("team", "My team sales"),
        ],
        "Based On",
        default="personal",
    )
    # field attribution, quel type?
