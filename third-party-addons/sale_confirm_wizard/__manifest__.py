# Copyright 2017-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Sale Confirm Wizard',
    'version': '14.0.1.0.0',
    'category': 'Sales',
    'license': 'AGPL-3',
    'summary': 'Open a wizard when you confirm a sale order to update important info',
    'description': """
Sale Confirm Wizard
===================

When you confirm a quotation, Odoo will open a small wizard where you will be able to check and update important information:

* customer PO number,
* delivery address,
* invoicing address,
* payment terms.

It will also display the sale warning if the customer's company has one. And it is a blocker warning, the user won't be able to confirm the quotation.

This module has been developped because the experience has shown, when a sales assistant confirms a quotation in Odoo, it overlooks the important information written in the customer PO that may be different from the information of the quotation in Odoo, which causes many errors in delivery and invoicing.

This module has been written by Alexis de Lattre from Akretion
<alexis.delattre@akretion.com>.
    """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com',
    'depends': ['sale'],
    'data': [
        'wizard/sale_confirm_view.xml',
        'views/sale_order.xml',
        'security/ir.model.access.csv',
        ],
    'installable': True,
}
