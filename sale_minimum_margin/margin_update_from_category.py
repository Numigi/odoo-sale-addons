# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models, _


class Product(models.Model):

    _inherit = 'product.product'

    def _update_margin_from_minimum_margin(self):
        rate_before = self.margin
        self.margin = self.minimum_margin
        self.update_sale_price_from_cost()
        message = _(
            'The margin rate of the product was revised from '
            '{rate_before:.2f}% to {rate_after:.2f}%, after a change in the '
            'minimum margin on the product category ({category}).'
        ).format(
            rate_before=rate_before * 100,
            rate_after=self.margin * 100,
            category=self.categ_id.display_name,
        )
        self.message_post(body=message)

        only_one_variant = (
            self.product_tmpl_id.product_variant_ids == self
        )
        if only_one_variant:
            self.product_tmpl_id.message_post(body=message)


class ProductCategory(models.Model):

    _inherit = 'product.category'

    def _update_products_with_minimum_margin(self):
        products_with_lower_margin = self.env['product.product'].search([
            ('categ_id', '=', self.id),
            ('margin', '<', self.minimum_margin),
            ('price_type', '=', 'dynamic'),
        ])
        for product in products_with_lower_margin:
            product._update_margin_from_minimum_margin()

    @api.multi
    def write(self, vals):
        super().write(vals)

        if vals.get('minimum_margin'):
            self._update_products_with_minimum_margin()

        return True
