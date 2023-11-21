# © 2023 - Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.sale_product_pack.models.sale_order import SaleOrder


class SaleOrderOverride(SaleOrder):
    def copy(self, default=None):
        sale_copy = super(SaleOrder,
                          self.with_context(from_copy=True)).copy(default)
        return sale_copy


SaleOrder.copy = SaleOrderOverride.copy
