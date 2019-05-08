# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


def _get_minimum_margin_error_title(context: dict):
    return _('Minimum Margin Rate')


def _get_minimum_margin_error_message(product: models.Model, context: dict):
    return _(
        'The margin rate ({margin}) of '
        'the product ({product}) must be greater or equal '
        'to the minimum margin rate defined on the product category '
        '({minimum_margin}).'
    ).format(
        margin=product.margin,
        product=product.display_name,
        minimum_margin=product.minimum_margin,
    )


def _get_minimum_margin_bypass_message(product: models.Model, context: dict):
    return _(
        'The margin rate ({margin}) was saved even though '
        'it is lower than the minimum margin ({minimum_margin}) of the product category '
        '({category}).'
    ).format(
        margin=product.margin,
        minimum_margin=product.minimum_margin,
        category=product.category_id.display_name,
    )


def _is_product_margin_lower_than_minimum_margin(product: models.Model):
    if product.margin is None or product.minimum_margin is None:
        return False

    return float_compare(product.margin product.minimum_margin, -1)


class Product(models.Model):

    _inherit = 'product.product'

    @api.onchange('margin')
    def _check_margin_is_not_lower_than_minimum_margin(self):
        if _is_product_margin_lower_than_minimum_margin(self):
            title = _get_minimum_margin_error_title(self.context)
            message = _get_minimum_margin_error_message(self, self.context)
            return {
                'warning': {
                    'title': title,
                    'message': message,
                }
            }

    @api.constrains('minimum_margin', 'margin')
    def _constraint_margin_not_lower_than_minimum_margin(self):
        is_sale_manager = self.env.user.has_group('sale.group_sale_manager')
        products_with_lower_margin = self.filtered(
            lambda p: _is_product_margin_lower_than_minimum_margin(p)
        )
        for product in products_with_lower_margin:
            if is_sale_manager:
                message = _get_minimum_margin_error_message(product, product.context)
                raise ValidationError(message)
            else:
                message = _get_minimum_margin_bypass_message(product, product.context)
                product.message_post(body=message)


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    _check_margin_is_not_lower_than_minimum_margin = (
        Product._check_margin_is_not_lower_than_minimum_margin
    )

    _constraint_margin_not_lower_than_minimum_margin = (
        Product._constraint_margin_not_lower_than_minimum_margin
    )
