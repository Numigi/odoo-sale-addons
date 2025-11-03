# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.addons.base.models.res_users import parse_m2m


class CrmTeam(models.Model):
    _inherit = "crm.team"

    emails = fields.Text(string="Emails", compute="_compute_members_email", store=True)

    @api.depends("member_ids", "member_ids.email")
    def _compute_members_email(self):
        for t in self:
            t.emails = ", ".join(
                t.member_ids.filtered(lambda m: m.email).mapped("email")
            )

    @api.onchange("user_id")
    def _onchange_member_ids(self):
        if self.user_id and self.user_id not in self.member_ids:
            self.member_ids = [(4, self.user_id.id)]

    @api.model
    def create(self, vals):
        if "user_id" in vals and vals["user_id"]:
            members_values = set(parse_m2m(vals.get("member_ids") or []))
            if vals["user_id"] not in members_values:
                vals["member_ids"] += [(4, vals["user_id"])]
        return super(CrmTeam, self).create(vals)

    def write(self, vals):
        if "user_id" in vals and vals["user_id"]:
            if "member_ids" not in vals or not vals["member_ids"]:
                for ct in self:
                    if vals["user_id"] not in ct.member_ids.ids:
                        vals["member_ids"] = [(4, vals["user_id"])]

            else:
                members_values = set(parse_m2m(vals.get("member_ids") or []))
                if vals["user_id"] not in members_values:
                    vals["member_ids"] += [(4, vals["user_id"])]
        return super(CrmTeam, self).write(vals)
