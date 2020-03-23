# © 2019 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _setup_warehouses_rental_routes(env)


def _setup_warehouses_rental_routes(env):
    warehouses = env["stock.warehouse"].search([])
    for warehouse in warehouses:
        warehouse._create_rental_location()
        warehouse._create_rental_route()
