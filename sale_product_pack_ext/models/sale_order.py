# Copyright 2019 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.addons.sale_product_pack.models.sale_order import SaleOrder


def copy(self, default=None):
    sale_copy = super(SaleOrder, self.with_context(from_copy=True)).copy(default)
    return sale_copy

SaleOrder.copy = copy
