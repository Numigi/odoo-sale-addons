# © 2021 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api
from odoo.exceptions import ValidationError


class CommissionCategory(models.Model):
    _name = "commission.category"
    _description = "Commission Category"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    name = fields.Char(translate=True, required=True, track_visibility="onchange")
    rate_type = fields.Selection(
        [
            ("fixed", "Fixed"),
            ("interval", "Interval"),
        ],
        default="fixed",
        required=True,
        track_visibility="onchange",
    )
    basis = fields.Selection(
        [
            ("my_sales", "My Sales"),
            ("my_team_commissions", "My Team's Commissions"),
        ],
        "Based On",
        default="my_sales",
        required=True,
        track_visibility="onchange",
    )
    rate_ids = fields.One2many("commission.category.rate", "category_id")
    fixed_rate = fields.Float(track_visibility="onchange")
    child_category_ids = fields.Many2many(
        "commission.category", "commission_category_child_rel", "parent_id", "child_id"
    )
    included_tag_ids = fields.Many2many(
        "sale.order.tag",
        "commission_category_included_tags_rel",
        "category_id",
        "tag_id",
        track_visibility="onchange",
    )
    excluded_tag_ids = fields.Many2many(
        "sale.order.tag",
        "commission_category_excluded_tags_rel",
        "category_id",
        "tag_id",
        track_visibility="onchange",
    )

    def _sorted_by_dependencies(self):
        return self.sorted(lambda c: len(c._get_all_children()))

    def _get_all_children(self):
        children = self.mapped("child_category_ids")

        if children:
            children |= children._get_all_children()

        return children

    @api.constrains("child_category_ids")
    def _validate_slices(self):
        for category in self:
            if category in category.child_category_ids:
                raise ValidationError("You cannot assign a child category to itself.")
