from . import models
from . import controllers


def post_init_hook(cr, registry):
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})

    config = env["res.config.settings"].create(
        {
            "group_use_lead": True,
            "generate_lead_from_alias": True,
        }
    )
    config.execute()
