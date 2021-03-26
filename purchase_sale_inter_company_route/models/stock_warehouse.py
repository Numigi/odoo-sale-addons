# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockWarehouse(models.Model):

    _inherit = "stock.warehouse"

    interco_rule_id = fields.Many2one("stock.rule", "Inter Company Rule")

    def _get_global_route_rules_values(self):
        vals = super()._get_global_route_rules_values()

        customer_loc, supplier_loc = self._get_partner_locations()
        route = self.env.ref("purchase_sale_inter_company_route.inter_company_route")
        picking_type = self.env.ref(
            "purchase_sale_inter_company_route.inter_company_picking_type"
        )

        vals.update(
            {
                "interco_rule_id": {
                    "depends": ["delivery_steps"],
                    "create_values": {
                        "active": True,
                        "company_id": self.company_id.id,
                        "action": "push",
                        "auto": "transparent",
                        "group_propagation_option": "propagate",
                        "propagate": True,
                        "route_id": route.id,
                    },
                    "update_values": {
                        "name": self._format_rulename(
                            customer_loc, supplier_loc, "Inter Company Push"
                        ),
                        "location_src_id": customer_loc.id,
                        "location_id": supplier_loc.id,
                        "picking_type_id": picking_type.id,
                    },
                }
            }
        )

        return vals
