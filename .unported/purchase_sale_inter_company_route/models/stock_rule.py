# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _run_push(self, move):
        interco_route = self.env.ref(
            "purchase_sale_inter_company_route.inter_company_route"
        )

        if self.route_id == interco_route:
            move.is_intercompany_delivery = True

        return super()._run_push(move)
