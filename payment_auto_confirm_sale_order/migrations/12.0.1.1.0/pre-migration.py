# © 2021 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openupgradelib.openupgrade import logged_query


def migrate(cr, version):
    if not version:
        return

    logged_query(
        cr, "SELECT id FROM payment_acquirer WHERE auto_confirm_sale_order is true"
    )
    checked_acquired_ids = [r[0] for r in cr.fetchall()]

    logged_query(cr, "ALTER TABLE payment_acquirer DROP COLUMN auto_confirm_sale_order")

    logged_query(
        cr, "ALTER TABLE payment_acquirer ADD COLUMN auto_confirm_sale_order TEXT"
    )

    if checked_acquired_ids:
        logged_query(
            cr,
            "UPDATE payment_acquirer SET auto_confirm_sale_order = 'confirm_order' WHERE id in %s",
            (tuple(checked_acquired_ids),),
        )
