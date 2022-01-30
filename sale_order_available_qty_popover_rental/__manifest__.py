# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': "Sale Order Available Qty Popover Rental",
    'summary': "",
    'author': "Numigi",
    'maintener': "Numigi",
    'website': "https://bit.ly/numigi-com",
    "license": "LGPL-3",
    'category': 'Sales',
    'version': '0.1',
    'depends': ['stock_rental', 'sale_rental', 'sale_order_available_qty_popover'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    "installable": True,
}
