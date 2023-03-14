# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _prepare_sale_order_data(self, name, partner, company,
                                 direct_delivery_address):
        vals = super()._prepare_sale_order_data(name, partner, company,
                                                direct_delivery_address)
        vals["route_id"] = self.env.ref(
            "purchase_sale_inter_company_route.inter_company_route"
        ).id
        return vals
