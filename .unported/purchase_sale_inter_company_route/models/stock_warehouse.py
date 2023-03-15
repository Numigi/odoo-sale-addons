# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, _
import logging

_logger = logging.getLogger(__name__)


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    interco_rule_id = fields.Many2one("stock.rule", "Inter Company Rule")
    interco_type_id = fields.Many2one(
        "stock.picking.type", "InterCompany Type", check_company=True
    )

    def _get_picking_type_create_values(self, max_sequence):
        vals, max_sequence = super()._get_picking_type_create_values(max_sequence)
        customer_loc, supplier_loc = self._get_partner_locations()
        vals.update(
            {
                "interco_type_id": {
                    "name": _("Inter Company Delivery"),
                    "code": "outgoing",
                    "use_create_lots": True,
                    "use_existing_lots": False,
                    "default_location_src_id": customer_loc.id,
                    "sequence": max_sequence + 1,
                    "show_reserved": False,
                    "show_operations": False,
                    "sequence_code": "ICO",
                    "default_location_dest_id": supplier_loc.id,
                    "company_id": self.company_id.id,
                }
            }
        )
        return vals, max_sequence + 1

    def _get_picking_type_update_values(self):
        res = super()._get_picking_type_update_values()
        customer_loc, supplier_loc = self._get_partner_locations()
        res.update(
            {
                "interco_type_id": {
                    "default_location_dest_id": supplier_loc.id,
                    "barcode": self.code.replace(" ", "").upper() + "-INTERCO",
                }
            }
        )
        return res

    def _get_sequence_values(self):
        res = super()._get_sequence_values()
        res.update(
            {
                "interco_type_id": {
                    "name": self.name + " " + _("Sequence Inter Company Delivery"),
                    "prefix": "ICO",
                    "padding": 5,
                    "company_id": self.company_id.id,
                }
            }
        )
        return res

    def _get_global_route_rules_values(self):
        vals = super()._get_global_route_rules_values()

        customer_loc, supplier_loc = self._get_partner_locations()
        route = self.env.ref("purchase_sale_inter_company_route.inter_company_route")
        picking_type_id = self.interco_type_id
        _logger.info("====================picking_type_id: %s", picking_type_id)

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
                        "route_id": route.id,
                    },
                    "update_values": {
                        "name": self._format_rulename(
                            customer_loc, supplier_loc, "Inter Company Push"
                        ),
                        "location_src_id": customer_loc.id,
                        "location_id": supplier_loc.id,
                        "picking_type_id": picking_type_id.id,
                    },
                }
            }
        )

        return vals
