# © 2023 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime
from odoo.tests.common import SavepointCase


class IntercoCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selling_company = cls._create_company("Selling Company2")
        cls.selling_company.so_from_po = True

        cls.purchasing_company = cls._create_company("Purchasing Company")

        cls.route = cls.env.ref("purchase_sale_inter_company_route.inter_company_route")
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")

        cls._set_user_company(cls.selling_company)
        cls.category = cls.env.ref("product.product_category_all")
        cls.category = cls.category.copy(
            {"name": "New category", "property_valuation": "real_time"}
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "My Product",
                "type": "product",
                "standard_price": 50,
                "categ_id": cls.category.id,
                "company_id": False,
                "tracking": "serial",
            }
        )

        cls.serial = cls.env["stock.production.lot"].create(
            {
                "name": "123",
                "product_id": cls.product.id,
                "company_id": cls.selling_company.id,
            }
        )
        cls.env["stock.quant"].create(
            {
                "product_id": cls.product.id,
                "location_id": cls.selling_company.warehouse_id.lot_stock_id.id,
                "quantity": 1,
                "lot_id": cls.serial.id,
            }
        )

        cls._set_user_company(cls.purchasing_company)
        cls.purchase_order = cls._create_purchase_order()
        cls.purchase_order.button_confirm()

        cls._set_user_company(cls.selling_company)
        cls.sale_order = cls._get_related_sale_order(cls.purchase_order)
        cls.sale_order_line = cls.sale_order.order_line
        cls.picking = cls.sale_order.picking_ids

    @classmethod
    def _create_company(cls, name):
        company = cls.env["res.company"].create({"name": name})
        cls._set_user_company(company)
        account_chart = cls.env.ref("l10n_ca.ca_en_chart_template_en")
        account_chart.try_loading(company=company)

        interco_user_name = f"{company.id}-interco@example.com"
        interco_user = cls.env["res.users"].create(
            {
                "email": interco_user_name,
                "login": interco_user_name,
                "name": interco_user_name,
                "company_id": company.id,
                "company_ids": [(4, company.id)],
            }
        )
        company.intercompany_user_id = interco_user

        company.warehouse_id = (
            cls.env["stock.warehouse"]
            .sudo()
            .search([("company_id", "=", company.id)], limit=1)
        )

        return company

    @classmethod
    def _set_user_company(cls, company):
        cls.env.user.company_ids |= company
        cls.env.user.company_id = company

    @classmethod
    def _create_purchase_order(cls):
        order_line_vals = cls._make_purchase_order_line_vals()
        return cls.env["purchase.order"].create(
            {
                "partner_id": cls.selling_company.partner_id.id,
                "order_line": [(0, 0, order_line_vals)],
            }
        )

    @classmethod
    def _make_purchase_order_line_vals(cls):
        return {
            "name": cls.product.display_name,
            "product_id": cls.product.id,
            "product_uom": cls.product.uom_id.id,
            "product_qty": 1,
            "price_unit": 100,
            "date_planned": datetime.now(),
        }

    @classmethod
    def _get_related_sale_order(cls, purchase_order):
        return cls.env["sale.order"].search(
            [("auto_purchase_order_id", "=", purchase_order.id)], limit=1
        )

    @classmethod
    def _process_picking(cls, picking):
        picking.picking_type_id.use_existing_lots = True

        for line in picking.move_line_ids:
            line.qty_done = 1
            line.lot_id = cls.serial
            line.company_id = False

        picking.action_assign()
        picking.button_validate()

    @classmethod
    def create_return_picking(cls, picking, to_refund=False):
        wizard_obj = cls.env["stock.return.picking"].with_context(active_id=picking.id)
        values = wizard_obj.default_get(list(wizard_obj._fields))
        wizard = wizard_obj.create(values)
        wizard.product_return_moves.quantity = 1
        wizard.product_return_moves.to_refund = to_refund
        return_picking_id = wizard.create_returns()["res_id"]
        return cls.env["stock.picking"].browse(return_picking_id)


class TestIntercoSaleOrder(IntercoCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.picking = cls.sale_order.picking_ids
        cls._process_picking(cls.picking)

        cls.stock_move = cls.picking.move_lines
        cls.account_move = cls.stock_move.account_move_ids

    def test_route_selected_on_sale_order(self):
        assert self.sale_order.route_id == self.route
        assert self.sale_order_line.route_id == self.route

    def test_delivers_to_customers(self):
        assert self.stock_move.location_dest_id == self.supplier_location

    def test_proper_transit_account_used(self):
        debit_line = self.account_move.line_ids.filtered("debit")
        assert "Stock Delivered" in debit_line.account_id.name

    def test_return_picking__proper_transit_account_used(self):
        return_picking = self.create_return_picking(self.picking)
        self._process_picking(return_picking)

        stock_move = return_picking.move_lines
        account_move = stock_move.account_move_ids
        credit_line = account_move.line_ids.filtered("credit")
        assert "Stock Delivered" in credit_line.account_id.name

    def test_sale_orders_serial_number_relation(self):
        self._set_user_company(self.selling_company)
        self.serial.refresh()
        assert self.sale_order in self.serial.sale_order_ids

        self._set_user_company(self.purchasing_company)
        self.serial.refresh()
        assert self.sale_order not in self.serial.sale_order_ids

    def test_purchase_orders_serial_number_relation(self):
        self._process_picking(self.purchase_order.picking_ids)

        self._set_user_company(self.selling_company)
        self.serial.refresh()
        assert self.purchase_order not in self.serial.purchase_order_ids

        self._set_user_company(self.purchasing_company)
        self.serial.refresh()
        assert self.purchase_order in self.serial.purchase_order_ids

    def test_delivered_quantity(self):
        assert self.sale_order_line.qty_delivered == 1

    def test_returned_quantity_not_refunded(self):
        return_picking = self.create_return_picking(self.picking, to_refund=False)
        self._process_picking(return_picking)
        assert self.sale_order_line.qty_delivered == 1

    def test_refunded_quantity(self):
        return_picking = self.create_return_picking(self.picking, to_refund=True)
        self._process_picking(return_picking)
        assert self.sale_order_line.qty_delivered == 0


class TestStandardSaleOrder(IntercoCase):
    """Test a case of a normal (non-interco) sale order.

    This checks that the module does not break standard behavior of sale orders.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.picking.do_unreserve()

        cls.sale_order = cls.sale_order.copy()
        cls.sale_order.route_id = False
        cls.sale_order_line = cls.sale_order.order_line
        cls.sale_order_line.route_id = False
        cls.sale_order.action_confirm()

        cls.picking = cls.sale_order.picking_ids
        cls._process_picking(cls.picking)

        cls.stock_move = cls.picking.move_lines
        cls.account_move = cls.stock_move.account_move_ids

    def test_delivers_to_customers(self):
        assert self.stock_move.location_dest_id == self.customer_location

    def test_proper_transit_account_used(self):
        debit_line = self.account_move.line_ids.filtered("debit")
        assert "Stock Delivered" in debit_line.account_id.name
