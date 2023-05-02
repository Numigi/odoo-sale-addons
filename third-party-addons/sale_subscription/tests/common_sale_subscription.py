# -*- coding: utf-8 -*-
from odoo.addons.sale.tests.common import TestSaleCommon
from odoo.tests import tagged


@tagged('-at_install', 'post_install')
class TestSubscriptionCommon(TestSaleCommon):

    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        # disable most emails for speed
        context_no_mail = {'no_reset_password': True, 'mail_create_nosubscribe': True, 'mail_create_nolog': True}
        Analytic = cls.env['account.analytic.account'].with_context(context_no_mail)
        Subscription = cls.env['sale.subscription'].with_context(context_no_mail)
        SubTemplate = cls.env['sale.subscription.template'].with_context(context_no_mail)
        SaleOrder = cls.env['sale.order'].with_context(context_no_mail)
        Tax = cls.env['account.tax'].with_context(context_no_mail)
        ProductTmpl = cls.env['product.template'].with_context(context_no_mail)

        # Minimal CoA & taxes setup
        cls.account_payable = cls.company_data['default_account_payable']
        cls.account_receivable = cls.company_data['default_account_receivable']
        cls.account_income = cls.company_data['default_account_revenue']

        cls.tax_10 = Tax.create({
            'name': "10% tax",
            'amount_type': 'percent',
            'amount': 10,
        })
        cls.tax_20 = Tax.create({
            'name': "20% tax",
            'amount_type': 'percent',
            'amount': 20,
        })
        cls.journal = cls.company_data['default_journal_sale']

        # Test Subscription Template
        cls.subscription_tmpl = SubTemplate.create({
            'name': 'TestSubscriptionTemplate',
            'description': 'Test Subscription Template 1',
            'journal_id': cls.journal.id,
        })
        cls.subscription_tmpl_2 = SubTemplate.create({
            'name': 'TestSubscriptionTemplate2',
            'description': 'Test Subscription Template 2',
            'journal_id': cls.journal.id,
        })
        cls.subscription_tmpl_3 = SubTemplate.create({
            'name': 'TestSubscriptionTemplate3',
            'description': 'Test Subscription Template 3',
            'recurring_rule_boundary':'limited',
            'journal_id': cls.journal.id,
        })

        # Test products
        cls.product_tmpl = ProductTmpl.create({
            'name': 'TestProduct',
            'type': 'service',
            'recurring_invoice': True,
            'subscription_template_id': cls.subscription_tmpl.id,
            'uom_id': cls.env.ref('uom.product_uom_unit').id,
        })
        cls.product = cls.product_tmpl.product_variant_id
        cls.product.write({
            'price': 50.0,
            'taxes_id': [(6, 0, [cls.tax_10.id])],
            'property_account_income_id': cls.account_income.id,
        })

        cls.product_tmpl_2 = ProductTmpl.create({
            'name': 'TestProduct2',
            'type': 'service',
            'recurring_invoice': True,
            'subscription_template_id': cls.subscription_tmpl_2.id,
            'uom_id': cls.env.ref('uom.product_uom_unit').id,
        })
        cls.product2 = cls.product_tmpl_2.product_variant_id
        cls.product2.write({
            'price': 20.0,
            'taxes_id': [(6, 0, [cls.tax_10.id])],
            'property_account_income_id': cls.account_income.id,
        })

        cls.product_tmpl_3 = ProductTmpl.create({
            'name': 'TestProduct3',
            'type': 'service',
            'recurring_invoice': True,
            'subscription_template_id': cls.subscription_tmpl_2.id,
            'uom_id': cls.env.ref('uom.product_uom_unit').id,
        })
        cls.product3 = cls.product_tmpl_3.product_variant_id
        cls.product3.write({
            'price': 15.0,
            'taxes_id': [(6, 0, [cls.tax_10.id])],
            'property_account_income_id': cls.account_income.id,
        })

        cls.product_tmpl_4 = ProductTmpl.create({
            'name': 'TestProduct4',
            'type': 'service',
            'recurring_invoice': True,
            'subscription_template_id': cls.subscription_tmpl_3.id,
            'uom_id': cls.env.ref('uom.product_uom_unit').id,
        })
        cls.product4 = cls.product_tmpl_4.product_variant_id
        cls.product4.write({
            'price': 15.0,
            'taxes_id': [(6, 0, [cls.tax_20.id])],
            'property_account_income_id': cls.account_income.id,
        })

        # Test user
        TestUsersEnv = cls.env['res.users'].with_context({'no_reset_password': True})
        group_portal_id = cls.env.ref('base.group_portal').id
        cls.user_portal = TestUsersEnv.create({
            'name': 'Beatrice Portal',
            'login': 'Beatrice',
            'email': 'beatrice.employee@example.com',
            'groups_id': [(6, 0, [group_portal_id])],
            'property_account_payable_id': cls.account_payable.id,
            'property_account_receivable_id': cls.account_receivable.id,
            'company_id': cls.company_data['company'].id,
        })

        # Test analytic account
        cls.account_1 = Analytic.create({
            'partner_id': cls.user_portal.partner_id.id,
            'name': 'Test Account 1',
        })
        cls.account_2 = Analytic.create({
            'partner_id': cls.user_portal.partner_id.id,
            'name': 'Test Account 2',
        })

        # Test Subscription
        cls.subscription = Subscription.create({
            'name': 'TestSubscription',
            'partner_id': cls.user_portal.partner_id.id,
            'pricelist_id': cls.company_data['default_pricelist'].id,
            'template_id': cls.subscription_tmpl.id,
        })
        cls.sale_order = SaleOrder.create({
            'name': 'TestSO',
            'partner_id': cls.user_portal.partner_id.id,
            'partner_invoice_id': cls.user_portal.partner_id.id,
            'partner_shipping_id': cls.user_portal.partner_id.id,
            'order_line': [(0, 0, {'name': cls.product.name, 'product_id': cls.product.id, 'subscription_id': cls.subscription.id, 'product_uom_qty': 2, 'product_uom': cls.product.uom_id.id, 'price_unit': cls.product.list_price})],
            'pricelist_id': cls.company_data['default_pricelist'].id,
        })
        cls.sale_order_2 = SaleOrder.create({
            'name': 'TestSO2',
            'partner_id': cls.user_portal.partner_id.id,
            'order_line': [(0, 0, {'name': cls.product.name, 'product_id': cls.product.id, 'product_uom_qty': 1.0, 'product_uom': cls.product.uom_id.id, 'price_unit': cls.product.list_price})]
        })
        cls.sale_order_3 = SaleOrder.create({
            'name': 'TestSO3',
            'partner_id': cls.user_portal.partner_id.id,
            'order_line': [(0, 0, {'name': cls.product.name, 'product_id': cls.product.id, 'product_uom_qty': 1.0, 'product_uom': cls.product.uom_id.id, 'price_unit': cls.product.list_price, }), (0, 0, {'name': cls.product2.name, 'product_id': cls.product2.id, 'product_uom_qty': 1.0, 'product_uom': cls.product2.uom_id.id, 'price_unit': cls.product2.list_price})],
        })
        cls.sale_order_4 = SaleOrder.create({
            'name': 'TestSO4',
            'partner_id': cls.user_portal.partner_id.id,
            'order_line': [(0, 0, {'name': cls.product2.name, 'product_id': cls.product2.id, 'product_uom_qty': 1.0, 'product_uom': cls.product2.uom_id.id, 'price_unit': cls.product2.list_price}), (0, 0, {'name': cls.product3.name, 'product_id': cls.product3.id, 'product_uom_qty': 1.0, 'product_uom': cls.product3.uom_id.id, 'price_unit': cls.product3.list_price})],
        })
        cls.sale_order_5 = SaleOrder.create({
            'name': 'TestSO5',
            'partner_id': cls.user_portal.partner_id.id,
            'order_line': [(0, 0, {'name': cls.product4.name, 'product_id': cls.product4.id, 'product_uom_qty': 1.0, 'product_uom': cls.product4.uom_id.id, 'price_unit': cls.product4.list_price})]
        })

    def flush_tracking(self):
        self.env['base'].flush()
        self.cr.precommit.run()
