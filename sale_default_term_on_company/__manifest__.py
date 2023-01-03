# © 2022 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Sale Persistent Sale Warning",
    'version': '14.0.1.0.0',
    'author': 'Numigi',
    'maintainer': 'Numigi',
    'website': 'https://bit.ly/numigi-com',
    'license': 'LGPL-3',
    "category": "Sales",
    "summary": "Add default terms and conditions on the form view of companies",
    "depends": [
        'account',
    ],
    "data": [
        "data/ir_config_parameter.xml",
        "views/res_company.xml",
    ],
    "installable": True,
}
