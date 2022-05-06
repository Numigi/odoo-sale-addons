# © 2022 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging
from openupgradelib import openupgrade


_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    xml_ids = (
        "sale.portal_my_home_sale",
        "sale.portal_my_home_menu_sale",
    )

    for xml_id in xml_ids:
        _logger.info(f"Reactivating the view {xml_id}")
        env.ref(xml_id).active = True
