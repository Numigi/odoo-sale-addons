# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models, _
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


def _get_minimum_margin_error_message(product: models.Model, context: dict) -> str:
    """Get the message to display when the margin constraint is raised.

    When a user changes the margin for a value below the minimum margin,
    this message is displayed.

    :param product: the product
    :param context: the odoo context, required for translations
    :return: the message content
    """
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


def _get_minimum_margin_bypass_message(product: models.Model, context: dict) -> str:
    """Get the message to display when bypassing the margin constraint.

    When a sale manager bypasses the minimum margin constraint,
    this message is displayed.

    :param product: the product
    :param context: the odoo context, required for translations
    :return: the message content
    """
    return _(
        'The margin rate ({margin:.2f}%) was saved even though '
        'it is lower than the minimum margin ({minimum_margin:.2f}%) of the product category '
        '({category}).'
    ).format(
        margin=product.margin * 100,
        minimum_margin=product.minimum_margin * 100,
        category=product.categ_id.name,
    )


def _is_product_margin_lower_than_minimum_margin(product: models.Model) -> bool:
    """Evaluate whether the product as a margin below its minimum margin.

    The comparison is done with a precision of 4 decimals.
    For example, if the margin on the product is 29.99% (0.2999) and the
    minimum margin is 30.00% (0.3000), the returned value will be True.

    :param product: the product
    """
    if product.margin is None or product.minimum_margin is None:
        return False

    return float_compare(product.margin, product.minimum_margin, 4) == -1


class Product(models.Model):

    _inherit = 'product.product'

    @api.onchange('margin')
    def _check_margin_is_not_lower_than_minimum_margin(self):
        """Check whether the margin is not lower than the minimum margin.

        If the constraint is not filled, raise a non-blocking message.
        If the user is not member of Sales / Manager, he will be blocked
        when saving the record.
        """
        if _is_product_margin_lower_than_minimum_margin(self):
            message = _get_minimum_margin_error_message(self, self._context)
            return {
                'warning': {
                    'title': _('Minimum Margin Rate'),
                    'message': message,
                }
            }

    @api.constrains('margin', 'categ_id')
    def _constraint_margin_not_lower_than_minimum_margin(self):
        """Apply the constraint when saving the margin.

        If the margin is below the minimum margin AND
        the user is NOT member of `Sales / Manager`, a blocking message
        will be displayed.

        If the margin is below the minimum margin AND
        the user is member of `Sales / Manager`, a non-blocking message
        will be displayed in the mail thread of the record.
        """
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
