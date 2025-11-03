import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    _logger.info("hook start")

    env = api.Environment(cr, SUPERUSER_ID, {})

    try:
        settings = env["res.config.settings"].create(
            {
                "group_use_lead": True,
                "generate_lead_from_alias": True,
            }
        )
        _logger.info("record created")
        settings.execute()
        _logger.info("good end")

    except Exception as e:
        _logger.error("Error", e)

    _logger.info("hook end")
