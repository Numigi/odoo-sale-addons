# © 2018 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Sale Rental',
    'version': '1.0.0',
    'author': 'Numigi',
    'maintainer': 'Numigi',
    'website': 'https://www.numigi.com',
    'license': 'LGPL-3',
    'category': 'Sale',
    'summary': 'Add rental sale type.',
    'depends': [
        'sale_stock',
        'sale_order_type',
        'web_timeline',
    ],
    'data': [
        'views/product_template.xml',
        'views/sale_order.xml',
        'views/sale_order_type.xml',
        'views/stock_move_line.xml',
        'views/stock_picking.xml',
        'wizard/rental_return.xml',
    ],
    'demo': [
        'demo/sale_order_type.xml',
    ],
    'installable': True,
}
