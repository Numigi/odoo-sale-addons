# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytest
from odoo.tests import common
from odoo.exceptions import ValidationError


class TestWarehouse(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env["res.company"].create({"name": "My Company"})

        cls.warehouse = cls.env["stock.warehouse"].create(
            {"name": "My Warehouse", "code": "WH2", "company_id": cls.company.id}
        )

        cls.customer_location = cls.env.ref("sale_rental.customer_location")

    def test_rental_stock_location(self):
        assert self.warehouse.rental_location_id

    def test_rental_route(self):
        assert self.warehouse.rental_route_id

    def test_one_pull_from_rental_stock_to_client(self):
        pull = self.warehouse.rental_route_id.rule_ids.filtered(
            lambda r: r.action == "pull"
        )
        assert pull.location_src_id == self.warehouse.rental_location_id
        assert pull.location_id == self.customer_location
        assert pull.picking_type_id == self.warehouse.out_type_id

    def test_one_push_from_client_to_rental_stock(self):
        pull = self.warehouse.rental_route_id.rule_ids.filtered(
            lambda r: r.action == "push"
        )
        assert pull.location_src_id == self.customer_location
        assert pull.location_id == self.warehouse.rental_location_id
        assert pull.picking_type_id == self.warehouse.in_type_id

    def test_main_warehouse_has_rental_route(self):
        warehouse = self.env.ref("stock.warehouse0")
        assert warehouse.rental_route_id
