# -*- coding: utf-8 -*-
# License AGPL-3.0 (https://www.gnu.org/licenses/agpl-3.0).

from . import models
from . import controllers

from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    crm_settings = env["res.config.settings"].create(
        {
            "group_use_lead": True,
            "generate_lead_from_alias": True,
            "crm_alias_prefix": "contact",
        }
    )

    crm_settings.execute()
