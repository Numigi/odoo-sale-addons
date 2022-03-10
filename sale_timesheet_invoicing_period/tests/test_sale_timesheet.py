# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from contextlib import contextmanager
from datetime import date
from ddt import ddt, data, unpack
from odoo.tests import Form
from odoo.tests.common import SavepointCase


@ddt
class TestSaleTimesheet(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.project = cls.env["project.project"].create(
            {
                "name": "My Project",
            }
        )

        cls.product = cls.env["product.product"].create(
            {
                "name": "My Product",
                "type": "service",
                "service_type": "timesheet",
                "service_tracking": "task_global_project",
                "invoice_policy": "delivery",
                "project_id": cls.project.id,
            }
        )

        cls.partner = cls.env["res.partner"].create(
            {
                "name": "My Partner",
            }
        )

        line_vals = {
            "product_id": cls.product.id,
            "product_uom_qty": 1,
            "product_uom_id": cls.product.uom_id.id,
        }

        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "pricelist_id": cls.env.ref("product.list0").id,
                "order_line": [(0, 0, line_vals)],
            }
        )

        cls.order.action_confirm()
        cls.order_line = cls.order.order_line
        cls.task = cls.order.tasks_ids

    @data(
        (date(2021, 1, 2), date(2021, 1, 2)),
        (date(2021, 1, 1), date(2021, 1, 3)),
        (date(2021, 1, 1), False),
        (False, date(2021, 1, 3)),
        (False, False),
    )
    @unpack
    def test_invoice__line_not_filtered(self, date_from, date_to):
        line = self._make_timesheet(date=date(2021, 1, 2))
        self._invoice_order(date_from, date_to)
        assert line.timesheet_invoice_id
        assert self.order_line.qty_invoiced == 1

    @data(
        (date(2021, 1, 3), False),
        (False, date(2021, 1, 1)),
    )
    @unpack
    def test_invoice__line_filtered(self, date_from, date_to):
        line = self._make_timesheet(date=date(2021, 1, 2))
        self._invoice_order(date_from, date_to)
        assert not line.timesheet_invoice_id
        assert not self.order_line.qty_invoiced

    def _invoice_order(self, date_from, date_to):
        with self.open_wizard() as wizard:
            wizard.timesheet_date_from = date_from
            wizard.timesheet_date_to = date_to
            wizard.save().create_invoices()

    def _make_timesheet(self, **kwargs):
        vals = {
            "name": "/",
            "project_id": self.project.id,
            "task_id": self.task.id,
            "amount": 100,
            "unit_amount": 1,
            "user_id": self.env.user.id,
            **kwargs,
        }
        return self.env["account.analytic.line"].create(vals)

    @contextmanager
    def open_wizard(self):
        wizard_obj = self.env["sale.advance.payment.inv"].with_context(
            active_ids=[self.order.id]
        )
        with Form(wizard_obj) as wizard:
            yield wizard
