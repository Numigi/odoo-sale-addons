# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    init_settings(env)


def init_settings(env):
    """
    Activate the pricelist feature in the settings.
    """
    config = env["res.config.settings"].create({})
    config.multi_sales_price = True
    config._onchange_sale_price()
    config.execute()
