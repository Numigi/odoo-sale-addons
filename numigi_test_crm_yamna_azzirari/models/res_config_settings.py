from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    group_use_lead = fields.Boolean(
        string="Leads", implied_group="crm.group_use_lead", default=True
    )

    @api.model
    def default_get(self, fields):
        result = super(ResConfigSettings, self).default_get(fields)
        result.update(
            {"crm_alias_prefix": (result.get("crm_alias_prefix") or "contact")}
        )
        return result
