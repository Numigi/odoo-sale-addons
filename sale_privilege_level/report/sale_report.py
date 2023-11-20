# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class SaleReport(models.Model):
    _inherit = 'sale.report'

    privilege_level_id = fields.Many2one(
        "sale.privilege.level",
        "Privilege Level",
        readonly=True
    )

    def _group_by_sale(self, groupby=''):
        res = super()._group_by_sale(groupby)
        res += """,partner.privilege_level_id"""
        return res

    def _select_additional_fields(self, fields):
        fields['privilege_level_id'] =\
            ", partner.privilege_level_id as privilege_level_id"
        return super()._select_additional_fields(fields)
