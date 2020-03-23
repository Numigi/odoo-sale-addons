# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _


class Warehouse(models.Model):

    _inherit = "stock.warehouse"

    rental_location_id = fields.Many2one(
        "stock.location",
        "Rental Stock Location",
        help="This location contains the stock available for rental.",
    )

    rental_route_id = fields.Many2one(
        "stock.location.route", "Rental Route", ondelete="restrict"
    )

    @api.model
    def create(self, vals):
        warehouse = super().create(vals)
        warehouse._create_rental_location()
        warehouse._create_rental_route()
        return warehouse

    def _create_rental_location(self):
        self.rental_location_id = self.env["stock.location"].create(
            {
                "name": _("Rental Stock"),
                "usage": "internal",
                "location_id": self.lot_stock_id.id,
                "company_id": self.company_id.id,
            }
        )

    def _create_rental_route(self):
        vals = self._get_rental_route_values()
        vals["rule_ids"] = [
            (0, 0, self._get_rental_pull_values()),
            (0, 0, self._get_rental_return_push_values()),
        ]
        self.rental_route_id = self.env["stock.location.route"].create(vals)

    def _get_rental_route_values(self):
        return {
            "name": "{warehouse}: Rental".format(warehouse=self.name),
            "active": True,
            "company_id": self.company_id.id,
            "product_categ_selectable": False,
            "warehouse_selectable": False,
            "product_selectable": False,
            "sequence": 10,
            "warehouse_ids": [(4, self.id)],
        }

    def _get_rental_pull_values(self):
        source_location = self.rental_location_id
        destination_location = self.env.ref("sale_rental.customer_location")
        return {
            "name": self._format_rulename(source_location, destination_location, ""),
            "location_src_id": source_location.id,
            "location_id": destination_location.id,
            "picking_type_id": self.out_type_id.id,
            "action": "pull",
            "active": True,
            "company_id": self.company_id.id,
            "sequence": 1,
            "propagate": True,
            "procure_method": "make_to_stock",
            "group_propagation_option": "propagate",
        }

    def _get_rental_return_push_values(self):
        source_location = self.env.ref("sale_rental.customer_location")
        destination_location = self.rental_location_id
        return {
            "name": self._format_rulename(source_location, destination_location, ""),
            "location_src_id": source_location.id,
            "location_id": destination_location.id,
            "picking_type_id": self.in_type_id.id,
            "action": "push",
            "active": True,
            "company_id": self.company_id.id,
            "sequence": 100,
            "propagate": True,
            "group_propagation_option": "propagate",
            "auto": "manual",
        }
