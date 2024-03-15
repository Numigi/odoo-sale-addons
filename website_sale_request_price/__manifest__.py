# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Website Sale Request Price",
    "summary": """Hide the price of a product when it reaches a threshold and allows
    the user to request for price""",
    "version": "14.0.1.1.0",
    "website": "https://bit.ly/numigi-com",
    "author": "Numigi",
    "maintainer": "Numigi",
    "license": "LGPL-3",
    "depends": [
        "crm_brand",
        "crm_lead_product",
        "sale_product_configurator",
        "website_sale",

    ],
    "data": [
        "views/res_config_settings.xml",
        "views/templates.xml"
    ],
    "installable": True,
}
