# Copyright 2019 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api
from odoo.addons.sale_product_pack.models.sale_order_line import SaleOrderLine


@api.model
def create(self, vals):
    record = super(SaleOrderLine, self).create(vals)
    if not self._context.get('from_copy', False):
        record.expand_pack_line()
    return record

SaleOrderLine.create = create
