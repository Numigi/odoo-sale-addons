# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    is_rental = fields.Boolean()

    def _group_by_sale(self, groupby=""):
        res = super()._group_by_sale(groupby)
        res += """,s.is_rental"""
        return res

    def _select_additional_fields(self, fields):
        fields["is_rental"] = ", s.is_rental as is_rental"
        return super()._select_additional_fields(fields)
