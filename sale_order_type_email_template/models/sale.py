# Copyright 2024 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _find_mail_template(self, force_confirmation_template=False):
        self.ensure_one()
        if (self.type_id and self.type_id.mail_template
                and not force_confirmation_template):
            return self.type_id.mail_template.id
        return super(SaleOrder, self)._find_mail_template(
            force_confirmation_template=force_confirmation_template
        )
