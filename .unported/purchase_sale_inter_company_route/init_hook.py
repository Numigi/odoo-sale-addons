# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})

    _update_warehouses(env)


def _update_warehouses(env):
    warehouses = env["stock.warehouse"].search([])
    for warehouse in warehouses:
        new_vals = warehouse._create_or_update_sequences_and_picking_types()
        if new_vals:
            warehouse.write(new_vals)
        warehouse._create_or_update_global_routes_rules()

    env["ir.model.data"]._update_xmlids(
        [
            {
                "xml_id": "purchase_sale_inter_company_route.interco_picking_type",
                "record": env.ref("stock.warehouse0").interco_type_id,
                "noupdate": True,
            }
        ]
    )
