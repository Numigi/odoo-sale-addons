# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.addons.sale_warranty.tests.common import WarrantyActivationCase


class TestExtensionOnWarrantyActivation(WarrantyActivationCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.extension_template = cls.env['sale.subscription.template'].create({
            'name': 'Warranty extension on parts',
        })
        cls.stage_draft = cls.env.ref('sale_subscription.sale_subscription_stage_draft')
        cls.stage_in_progress = cls.env.ref('sale_subscription.sale_subscription_stage_in_progress')
        cls.stage_closed = cls.env.ref('sale_subscription.sale_subscription_stage_closed')
        cls.subscription = cls.env['sale.subscription'].create({
            'partner_id': cls.customer.id,
            'template_id': cls.extension_template.id,
            'stage_id': cls.stage_in_progress.id,
        })
        cls.warranty_6_months.write({
            'use_warranty_extension': True,
            'extension_duration_in_months': 3,
            'extension_template_id': cls.extension_template.id,
        })

        cls.confirm_sale_order()
        cls.warranty = cls.sale_order.warranty_ids

        cls.extension_start_date = (
            datetime.now().date() + relativedelta(months=6)
        )
        cls.extension_expiry_date = (
            cls.warranty.activation_date + relativedelta(months=9) - timedelta(1)
        )

    def _trigger_warranty_activation(self):
        serial = self.generate_serial_number(self.product_a, '000001')
        picking = self.sale_order.picking_ids
        self.select_serial_numbers_on_picking(picking, serial)
        self.validate_picking(picking)

    def test_if_subscription_in_progress__extension_is_applied(self):
        self._trigger_warranty_activation()
        assert self.warranty.use_warranty_extension

    def test_if_draft_subscription__extension_is_not_applied(self):
        self.subscription.stage_id = self.stage_draft
        self._trigger_warranty_activation()
        assert not self.warranty.use_warranty_extension

    def test_if_subscription_closed__extension_is_not_applied(self):
        self.subscription.stage_id = self.stage_closed
        self._trigger_warranty_activation()
        assert not self.warranty.use_warranty_extension

    def test_if_not_use_warranty_extension__extension_is_not_applied(self):
        self.warranty_6_months.use_warranty_extension = False
        self._trigger_warranty_activation()
        assert not self.warranty.use_warranty_extension

    def test_if_not_same_subscription_template__extension_is_not_applied(self):
        other_template = self.env['sale.subscription.template'].create({
            'name': 'Other Subscription Template',
        })
        self.subscription.template_id = other_template
        self._trigger_warranty_activation()
        assert not self.warranty.use_warranty_extension

    def test_if_multiple_active_subscription__extension_is_applied(self):
        self.subscription.copy()
        self._trigger_warranty_activation()
        assert self.warranty.use_warranty_extension

    def test_if_contact_has_same_parent_company__extension_is_applied(self):
        contact_in_same_company = self.customer.copy()
        self.subscription.partner_id = contact_in_same_company
        self._trigger_warranty_activation()
        assert self.warranty.use_warranty_extension

    def test_if_contact_in_other_company__extension_is_not_applied(self):
        other_company = self.customer_company.copy()
        contact_other_company = self.customer.copy({
            'parent_id': other_company.id,
        })
        self.subscription.partner_id = contact_other_company
        self._trigger_warranty_activation()
        assert not self.warranty.use_warranty_extension

    def test_if_customer_is_the_commercial_partner__extension_is_applied(self):
        self.subscription.partner_id = self.customer_company
        self._trigger_warranty_activation()
        assert self.warranty.use_warranty_extension

    def test_warranty_extension_start_date(self):
        self._trigger_warranty_activation()
        assert self.warranty.extension_start_date == self.extension_start_date

    def test_warranty_extension_end_date(self):
        self._trigger_warranty_activation()
        assert self.warranty.extension_expiry_date == self.extension_expiry_date

    def test_warranty_extension_subscription(self):
        self._trigger_warranty_activation()
        assert self.warranty.extension_subscription_id == self.subscription
