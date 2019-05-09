# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import float_compare, float_round


def _get_minimum_margin_error_title(context: dict):
    return _('Minimum Margin Rate')


def _get_minimum_margin_error_message(product: models.Model, context: dict):
    return _(
        'The margin rate ({margin:.2f}%) of '
        'the product ({product}) must be greater or equal '
        'to the minimum margin rate defined on the product category '
        '({minimum_margin:.2f}%).'
    ).format(
        margin=product.margin * 100,
        product=product.name,
        minimum_margin=product.minimum_margin * 100,
    )


def _get_minimum_margin_bypass_message(product: models.Model, context: dict):
    return _(
        'The margin rate ({margin:.2f}%) was saved even though '
        'it is lower than the minimum margin ({minimum_margin:.2f}%) of the product category '
        '({category}).'
    ).format(
        margin=product.margin * 100,
        minimum_margin=product.minimum_margin * 100,
        category=product.categ_id.name,
    )


def _is_product_margin_lower_than_minimum_margin(product: models.Model):
    if product.margin is None or product.minimum_margin is None:
        return False

    return float_compare(product.margin, product.minimum_margin, 4) == -1


class Product(models.Model):

    _inherit = 'product.product'

    @api.onchange('margin')
    def _check_margin_is_not_lower_than_minimum_margin(self):
        if _is_product_margin_lower_than_minimum_margin(self):
            title = _get_minimum_margin_error_title(self._context)
            message = _get_minimum_margin_error_message(self, self._context)
            return {
                'warning': {
                    'title': title,
                    'message': message,
                }
            }

    @api.constrains('minimum_margin', 'margin', 'categ_id')
    def _constraint_margin_not_lower_than_minimum_margin(self):
        is_sale_manager = self.env.user.has_group('sales_team.group_sale_manager')
        products_with_lower_margin = self.filtered(
            lambda p: _is_product_margin_lower_than_minimum_margin(p)
        )
        for product in products_with_lower_margin:
            if is_sale_manager:
                message = _get_minimum_margin_bypass_message(product, product._context)
                product.message_post(body=message)
            else:
                message = _get_minimum_margin_error_message(product, product._context)
                raise ValidationError(message)


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    _check_margin_is_not_lower_than_minimum_margin = (
        Product._check_margin_is_not_lower_than_minimum_margin
    )

    _constraint_margin_not_lower_than_minimum_margin = (
        Product._constraint_margin_not_lower_than_minimum_margin
    )
