# © 2023 - Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api
from odoo.addons.product_configurator_sale.models.sale import SaleOrderLine


@api.onchange("product_uom", "product_uom_qty")
def product_uom_change(self):
    # Rewrite the onchange of product configurator to add the condition related to the pack
    # When the product is a pack with price totalized in the pack we don't nead to calculate 
    # the price from the config_session
    is_pack_totalised_price = self.product_id.pack_ok and\
        self.product_id.pack_type == 'detailed' and\
            self.product_id.pack_component_price in ['totalized', 'ignored']
    if self.config_session_id and not is_pack_totalised_price:
        account_tax_obj = self.env["account.tax"]
        self.price_unit = account_tax_obj._fix_tax_included_price_company(
            self.config_session_id.price,
            self.product_id.taxes_id,
            self.tax_id,
            self.company_id,
        )
    else:
        super(SaleOrderLine, self).product_uom_change()

SaleOrderLine.product_uom_change = product_uom_change
