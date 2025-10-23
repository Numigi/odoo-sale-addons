# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Sales Warranty Lead On Expiry",
    "version": "14.0.1.0.1",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://numigi.com/r/home",
    "license": "LGPL-3",
    "category": "Sales",
    "summary": "Generate a lead when a sale warranty expires",
    "depends": ["sale_warranty", "crm", "queue_job_cron"],
    "data": [
        "data/ir_cron.xml",
        "views/config_settings.xml",
        "views/warranty_to_lead_link_message.xml",
        "views/warranty_type.xml",
    ],
    "installable": True,
}
