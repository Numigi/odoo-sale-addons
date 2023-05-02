# Copyright 2015-2020 Akretion France (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    'name': 'Product Usability',
    'version': '14.0.1.0.0',
    'category': 'Product',
    'license': 'AGPL-3',
    'summary': 'Small usability enhancements to the product module',
    'description': """
Product Usability
=================

The usability enhancements include:

* show the object product.price.history in the product template form view

* wider name field in product form view

* hide description field on product (description_sale must be use instead of description)

* add a field barcode_type in product form view

This module has been written by Alexis de Lattre from Akretion <alexis.delattre@akretion.com>.
    """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com',
    'depends': ['product'],
    "external_dependencies": {"python": ["stdnum"]},
    'data': [
        'views/product_supplierinfo_view.xml',
        'views/product_pricelist_view.xml',
        'views/product_pricelist_item.xml',
        'views/product_template_view.xml',
        'views/product_product.xml',
        'views/product_config_menu.xml',
        'views/product_category_view.xml',
    ],
    'installable': True,
}
