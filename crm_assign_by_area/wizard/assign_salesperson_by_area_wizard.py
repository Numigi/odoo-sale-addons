# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class AssignSalespersonByAreaWizard(models.Model):
    _name = "assign.salesperson.by.area.wizard"
    _description = "Assign Salesperson By Area Wizard"

    available_territory_ids = fields.Many2many(comodel_name="res.territory")
    available_salesperson_ids = fields.Many2many(comodel_name="res.users")
    is_several_salespersons = fields.Boolean()
    wizard_msg = fields.Text(readonly=1)
    salesperson_id = fields.Many2one(comodel_name="res.users")

    @api.model
    def default_get(self, fields):
        res = super(AssignSalespersonByAreaWizard, self).default_get(fields)
        territory_ids = self._context.get("territory_ids", [])
        territories = self.env["res.territory"].browse(territory_ids)
        salespersons = territories.mapped("salesperson_id")
        vals = {
            "available_territory_ids": [(6, 0, territory_ids)],
            "available_salesperson_ids": [(6, 0, salespersons.ids)],
            "is_several_salespersons": len(salespersons) > 1,
            "wizard_msg": self.get_wizard_msg(territories, salespersons),
        }
        if len(salespersons) == 1:
            vals["salesperson_id"] = salespersons.id
        res.update(vals)
        return res

    @api.onchange("available_salesperson_ids")
    def _onchange_available_salesperson_ids(self):
        return {
            "domain": {
                "salesperson_id": [("id", "in", self.available_salesperson_ids.ids)]
            }
        }

    @api.multi
    def action_confirm(self):
        self.ensure_one()
        if not self.salesperson_id:
            raise AssertionError("There is no salesperson")

        # Get active record
        active_record = self.get_active_record()

        # Get salesperson field
        salesperson_field_name = self.get_salesperson_field_name(active_record)

        # Set salesperson
        active_record[salesperson_field_name] = self.salesperson_id

    @api.multi
    def get_active_record(self):
        self.ensure_one()
        # Get active context
        context = self._context
        active_model = context.get("active_model")
        active_id = context.get("active_id")
        if not (active_model and active_id):
            raise AssertionError("Missing active_model or active_id context.")

        # Get active record
        active_record = self.env[context.get("active_model")].browse(
            context.get("active_id")
        )
        if not active_record:
            raise AssertionError(
                "Cannot find any record with model '%s' and id '%s'." % active_model,
                active_id,
            )
        return active_record

    @api.model
    def get_salesperson_field_name(self, active_record):
        salesperson_field_name_mapping = self.get_salesperson_field_name_mapping()
        salesperson_field_name = ""
        for model_name, field_name in salesperson_field_name_mapping.items():
            if (
                model_name == active_record._name
                and field_name in active_record._fields
            ):
                salesperson_field_name = field_name
                break
        if not salesperson_field_name:
            raise AssertionError(
                "There is no mapping to get salesperson field for model '%s'.\n"
                "Check function get_salesperson_field_name_mapping()"
                % active_record._name
            )
        return salesperson_field_name

    @api.model
    def get_salesperson_field_name_mapping(self):
        return {"crm.lead": "user_id", "res.partner": "user_id"}

    @api.model
    def get_wizard_msg(self, territories, salespersons):
        if len(salespersons) == 1:
            related_territories = territories.filtered(
                lambda r: r.salesperson_id == salespersons
            )
            related_territories_names = ", ".join(
                related_territories.mapped("display_name")
            )
            wizard_msg = _(
                "%s will be assigned to the record. Do you want to continue?"
            ) % (
                "{} ({})".format(
                    salespersons[0].display_name, related_territories_names
                )
            )
        elif len(salespersons) > 1:
            wizard_msg = _(
                "Several salespersons could be assigned depending on the partner's "
                "territories. Please choose the right seller."
            )
        else:
            wizard_msg = _(
                "There is no salesperson to assign. The partner's territories "
                "might not be linked to any salesperson."
            )
        return wizard_msg
