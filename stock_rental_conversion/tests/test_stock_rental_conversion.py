# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import SavepointCase


class StockRentalConversionCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.warehouse = cls.env["stock.warehouse"].create(
            {"name": "My Warehouse", "code": "W1"}
        )

        cls.salable_product = cls.env["product.product"].create(
            {"name": "Salable Product", "type": "product", "tracking": "serial"}
        )

        cls.rentalable_product = cls.env["product.product"].create(
            {"name": "Rentalable Product", "type": "product", "tracking": "serial"}
        )

        cls.number = "123456"
        cls.serial = cls.env["stock.production.lot"].create(
            {"product_id": cls.salable_product.id, "name": cls.number}
        )

        cls.source_location = cls.warehouse.lot_stock_id
        cls.destination_location = cls.warehouse.rental_location_id

        cls.env["stock.quant"].create(
            {
                "location_id": cls.source_location.id,
                "lot_id": cls.serial.id,
                "product_id": cls.salable_product.id,
                "quantity": 1,
            }
        )


class TestWizardOnchange(StockRentalConversionCase):
    def test_source_default_values(self):
        vals_before = {"product_id": self.salable_product.id, "lot_id": self.serial.id}
        vals_after = self.env["stock.rental.conversion.wizard"].play_onchanges(
            vals_before, ["lot_id"]
        )
        assert vals_after["source_location_id"] == self.source_location.id
        assert vals_after["destination_location_id"] == self.destination_location.id


class TestWizardValidation(StockRentalConversionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wizard = cls.env["stock.rental.conversion.wizard"].create(
            {
                "product_id": cls.salable_product.id,
                "source_location_id": cls.source_location.id,
                "destination_location_id": cls.destination_location.id,
                "lot_id": cls.serial.id,
            }
        )
        cls.wizard.validate()
        cls.new_serial = cls.wizard.new_lot_id

    def test_new_serial_number(self):
        assert self.new_serial.name == self.number
        assert self.new_serial.product_id == self.rentalable_product
        assert self.new_serial.sales_lot_id == self.serial
        assert self.new_serial.get_current_location() == self.destination_location

    def test_old_serial_number(self):
        assert self.serial.get_current_location().usage == "production"
