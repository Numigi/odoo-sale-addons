from odoo import api, SUPERUSER_ID

from . import models


def _set_configuration(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    sales_team_id = env.ref("numigi_test_crm_hbentaleb.sales_team", raise_if_not_found=False)
    config = env["res.config.settings"].create(
        {
            "group_use_lead": True,
            "generate_lead_from_alias": True,
            "crm_alias_prefix": "contact",
            "crm_default_team_id": sales_team_id.id,
        }
    )
    config.execute()
