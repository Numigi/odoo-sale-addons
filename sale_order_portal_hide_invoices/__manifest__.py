# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Order Portal Hide Invoices",
    "version": "1.0.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://numigi.com/r/home",
    "license": "AGPL-3",
    "category": "Sale",
    "depends": ["sale"],
    "summary": """Removes the section which displays the list of associated
    invoices and credit notes.""",
    "data": [
        "views/sale_portal_templates.xml",
    ],
    "installable": True,
}
