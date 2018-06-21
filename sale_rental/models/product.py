# © 2018 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models

from .product_template import (
    ProductTemplateWithIsRentalMustBeService,
    ProductTemplateWithIsRentalMustHaveDayUom,
    ProductTemplateWithRentalOKMustBeStockableProduct,
)


class ProductWithExtraOnchangeMethods(models.Model):
    """Copy onchange methods from product.template to product.product.

    Otherwise, the onchange methods are not triggered on the form view
    of product.product.
    """

    _inherit = 'product.product'

    _onchange_rental_ok_set_type_to_stockable_product = (
        ProductTemplateWithRentalOKMustBeStockableProduct
        ._onchange_rental_ok_set_type_to_stockable_product
    )

    _onchange_type_if_not_service_then_empty_is_rental = (
        ProductTemplateWithIsRentalMustBeService
        ._onchange_type_if_not_service_then_empty_is_rental
    )

    _onchange_is_rental_set_days_as_product_uom = (
        ProductTemplateWithIsRentalMustHaveDayUom
        ._onchange_is_rental_set_days_as_product_uom
    )
