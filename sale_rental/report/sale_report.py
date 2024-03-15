# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    is_rental = fields.Boolean()

    def _query(self, with_clause, fields, groupby, from_clause):
        fields["is_rental"] = ", s.is_rental as is_rental"
        groupby += ", s.is_rental"
        return super()._query(with_clause, fields, groupby, from_clause)
