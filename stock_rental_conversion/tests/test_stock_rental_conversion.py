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

<<<<<<< HEAD
        cls.rental_product = cls.env["product.product"].create(
            {"name": "Rentalable Product", "type": "product", "tracking": "serial"}
        )

        cls.sales_product = cls.env["product.product"].create(
            {
                "name": "Salable Product",
                "type": "product",
                "tracking": "serial",
                "rental_product_id": cls.rental_product.id,
            }
        )

        cls.number = "123456"
        cls.sales_serial = cls.env["stock.production.lot"].create(
            {"product_id": cls.sales_product.id, "name": cls.number}
=======
        cls.salable_product = cls.env["product.product"].create(
            {"name": "Salable Product", "type": "product", "tracking": "serial"}
        )

        cls.rentalable_product = cls.env["product.product"].create(
            {"name": "Rentalable Product", "type": "product", "tracking": "serial"}
        )

        cls.number = "123456"
        cls.serial = cls.env["stock.production.lot"].create(
            {"product_id": cls.salable_product.id, "name": cls.number}
>>>>>>> b06e56e... Add module stock_rental_conversion
        )

        cls.source_location = cls.warehouse.lot_stock_id
        cls.destination_location = cls.warehouse.rental_location_id

<<<<<<< HEAD
        cls.quant = cls.env["stock.quant"].create(
            {
                "location_id": cls.source_location.id,
                "lot_id": cls.sales_serial.id,
                "product_id": cls.sales_product.id,
=======
        cls.env["stock.quant"].create(
            {
                "location_id": cls.source_location.id,
                "lot_id": cls.serial.id,
                "product_id": cls.salable_product.id,
>>>>>>> b06e56e... Add module stock_rental_conversion
                "quantity": 1,
            }
        )


class TestWizardOnchange(StockRentalConversionCase):
<<<<<<< HEAD
    def test_automatically_set_rental_product(self):
        vals_before = {"sales_product_id": self.sales_product.id}
        vals_after = self.env["stock.rental.conversion.wizard"].play_onchanges(
            vals_before, ["sales_product_id"]
        )
        assert vals_after["rental_product_id"] == self.rental_product.id

    def test_source_default_values(self):
        vals_before = {
            "sales_product_id": self.sales_product.id,
            "sales_lot_id": self.sales_serial.id,
        }
        vals_after = self.env["stock.rental.conversion.wizard"].play_onchanges(
            vals_before, ["sales_lot_id"]
=======
    def test_source_default_values(self):
        vals_before = {"product_id": self.salable_product.id, "lot_id": self.serial.id}
        vals_after = self.env["stock.rental.conversion.wizard"].play_onchanges(
            vals_before, ["lot_id"]
>>>>>>> b06e56e... Add module stock_rental_conversion
        )
        assert vals_after["source_location_id"] == self.source_location.id
        assert vals_after["destination_location_id"] == self.destination_location.id


class TestWizardValidation(StockRentalConversionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wizard = cls.env["stock.rental.conversion.wizard"].create(
            {
<<<<<<< HEAD
                "sales_product_id": cls.sales_product.id,
                "sales_lot_id": cls.sales_serial.id,
                "rental_product_id": cls.rental_product.id,
                "source_location_id": cls.source_location.id,
                "destination_location_id": cls.destination_location.id,
            }
        )
        cls.wizard.validate()
        cls.rental_serial = cls.wizard.rental_lot_id

    def test_rental_serial_number(self):
        assert self.rental_serial.name == self.number
        assert self.rental_serial.product_id == self.rental_product
        assert self.rental_serial.sales_lot_id == self.sales_serial
        assert self.rental_serial.get_current_location() == self.destination_location

    def test_sales_serial_number(self):
        assert self.sales_serial.get_current_location().usage == "production"


class TestWizardWithNonSerializedProduct(StockRentalConversionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sales_product.tracking = "none"
        cls.rental_product.tracking = "none"
        cls.quant.lot_id = False
        cls.wizard = cls.env["stock.rental.conversion.wizard"].create(
            {
                "sales_product_id": cls.sales_product.id,
                "rental_product_id": cls.rental_product.id,
                "source_location_id": cls.source_location.id,
                "destination_location_id": cls.destination_location.id,
            }
        )
        cls.wizard.validate()

    def test_sales_product_moved_to_production(self):
        new_quant = self.env["stock.quant"].search(
            [("product_id", "=", self.sales_product.id), ("quantity", "!=", 0)]
        )
        assert new_quant.quantity == 1
        assert new_quant.location_id.usage == "production"

    def test_rental_product_moved_to_destination(self):
        new_quant = self.env["stock.quant"].search(
            [
                ("product_id", "=", self.rental_product.id),
                ("quantity", "!=", 0),
                ("location_id.usage", "!=", "production"),
            ]
        )
        assert new_quant.quantity == 1
        assert new_quant.location_id == self.destination_location
=======
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
>>>>>>> b06e56e... Add module stock_rental_conversion
