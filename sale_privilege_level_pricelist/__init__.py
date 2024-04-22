# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from . import models
from odoo import api, SUPERUSER_ID


def _post_init_hook(cr, registry):
    """
    Activate the pricelist feature in the settings.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    config = env["res.config.settings"].create({})
    config.group_product_pricelist = True
    config._onchange_group_sale_pricelist()
    config.execute()
