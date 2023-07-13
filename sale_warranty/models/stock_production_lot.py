# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"

    warranty_count = fields.Integer(
        string="Warranty count",
        compute="_compute_warranty_count",
    )

    def _compute_warranty_count(self):
        for rec in self:
            rec.warranty_count = len(rec.get_warranties())

    def get_warranties(self):
        return self.env["sale.warranty"].search(
            [
                ("lot_id", "=", self.id),
            ]
        )

    def action_view_warranty(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "sale_warranty.action_warranty_list_from_sale_order"
        )
        warranty = self.get_warranties()
        if len(warranty) == 1:
            action.update(
                res_id=warranty.id,
                view_mode="form",
                view_id=False,
                views=False,
            )
        else:
            action["domain"] = [("id", "in", warranty.ids)]
            action["context"] = {}
        return action
