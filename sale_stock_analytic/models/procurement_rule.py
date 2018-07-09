# © 2018 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class ProcurementRuleWithAnalyticAccountPropagation(models.Model):

    _inherit = 'procurement.rule'

    def _get_stock_move_values(
        self, product_id, product_qty, product_uom, location_id, name, origin, values, group_id
    ):
        res = super()._get_stock_move_values(
            product_id, product_qty, product_uom, location_id, name, origin, values, group_id)
        group = self.env['procurement.group'].browse(group_id)

        analytic_account = group.mapped('sale_id.analytic_account_id')
        if analytic_account:
            res['analytic_account_id'] = analytic_account.id

        return res
