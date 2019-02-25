
from odoo.tests import TransactionCase


class TestModules(TransactionCase):
    """Test that Odoo modules are installed.

    To prevent ci to fail if no module was installed.
    """

    def setUp(self):
        super(TestModules, self).setUp()
        self.modules = self.env['ir.module.module']

    def test_main(self):
        """Main is installed."""
        self.assertTrue(self.modules.search([('name', '=', 'main')]))
