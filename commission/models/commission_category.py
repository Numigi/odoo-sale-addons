# © 2021 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api
from odoo.exceptions import ValidationError


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
            ("my_sales", "My Sales"),
            ("my_team_commissions", "My Team's Commissions"),
        ],
        "Based On",
        default="my_sales",
    )
    child_ids = fields.Many2many("commission.category", "commission_category_child_rel", "parent_id", "child_id")
    included_tag_ids = fields.Many2one("account.analytic.tag")
    excluded_tag_ids = fields.Many2one("account.analytic.tag")

    def _sorted_by_dependencies(self):
        return self.sorted(lambda c: len(c._get_all_children()))
    
    def _get_all_children(self):
        children = self.mapped("child_ids")

        if children:
            children |= children._get_all_children()
        
        return children

    @api.constrains("child_ids")
    def _validate_slices(self):
        if self in self.child_ids:
            raise ValidationError(
                "You cannot assign a child category to itself."
            )
