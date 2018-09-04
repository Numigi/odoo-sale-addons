# © 2018 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'MRP Repair Analytic',
    'version': '1.0.0',
    'author': 'Numigi',
    'maintainer': 'Numigi',
    'website': 'https://www.numigi.com',
    'license': 'LGPL-3',
    'category': 'MRP',
    'summary': 'Generate analytic lines from a repair order.',
    'depends': [
        'mrp_repair',
        'stock_analytic',
    ],
    'data': [
        'views/mrp_repair.xml',
    ],
    'installable': True,
}
