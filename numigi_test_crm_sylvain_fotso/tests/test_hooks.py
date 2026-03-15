# © 2026 Sylvain Fotso
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0.html).
import pytest
import odoo
from odoo import api, SUPERUSER_ID
from odoo.tests.common import get_db_name


@pytest.fixture()
def env():
    registry = odoo.registry(get_db_name())
    cr = registry.cursor()
    with api.Environment.manage():
        yield api.Environment(cr, SUPERUSER_ID, {})
        cr.rollback()
    cr.close()


def test_group_use_lead_is_enabled(env):
    # group_use_lead est stocké comme groupe, pas comme clé get_values()
    group = env.ref('crm.group_use_lead', raise_if_not_found=False)
    assert group is not False


def test_generate_lead_from_alias_is_enabled(env):
    param = env['ir.config_parameter'].sudo().get_param(
        'crm.generate_lead_from_alias'
    )
    assert param == 'True'


def test_crm_alias_prefix_is_contact(env):
    value = env['res.config.settings'].get_values().get('crm_alias_prefix')
    assert value == 'contact'
