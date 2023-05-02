# Copyright 2020 Akretion France (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Service Line Qty Update Sale',
    'version': '12.0.1.0.0',
    'category': 'Tools',
    'license': 'AGPL-3',
    'summary': 'Update delivery qty on service lines - Sale module',
    'author': 'Akretion',
    'website': 'http://www.akretion.com',
    'depends': [
        'sale',
        'service_line_qty_update_base',
        # 'purchase_reception_status',
        ],
    'data': [
        'views/sale_order.xml',
        ],
    'installable': False,
}
