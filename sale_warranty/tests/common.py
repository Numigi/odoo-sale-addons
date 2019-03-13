# © 2019 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import SavepointCase


class SaleWarrantyCase(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.salesman = cls.env['res.users'].create({
            'name': 'Salesman',
            'login': 'test_salesman',
            'email': 'test_salesman@test.com',
            'groups_id': [(4, cls.env.ref('sales_team.group_sale_salesman').id)]
        })

        cls.stock_user = cls.env['res.users'].create({
            'name': 'Stock User',
            'login': 'test_stock_user',
            'email': 'test_stock_user@test.com',
            'groups_id': [(4, cls.env.ref('stock.group_stock_user').id)]
        })

        cls.warranty_6_months = cls.env['sale.warranty.type'].create({
            'name': '6 Months Parts',
            'duration_in_months': 6,
            'description': 'Warranted 6 months on parts'
        })

        cls.warranty_2_years = cls.env['sale.warranty.type'].create({
            'name': '2 Years Parts',
            'duration_in_months': 24,
            'description': 'Warranted 2 years on parts'
        })

        cls.product_a = cls.env['product.product'].create({
            'name': 'My Product',
            'tracking': 'serial',
            'type': 'product',
            'warranty_type_ids': [(4, cls.warranty_6_months.id)]
        })

        cls.product_b = cls.env['product.product'].create({
            'name': 'My Product B',
            'tracking': 'serial',
            'type': 'product',
            'warranty_type_ids': [(4, cls.warranty_2_years.id)]
        })

        cls.customer_company = cls.env['res.partner'].create({
            'name': 'Customer Company',
            'customer': True,
            'is_company': True,
        })

        cls.customer = cls.env['res.partner'].create({
            'name': 'My Customer',
            'customer': True,
            'parent_id': cls.customer_company.id,
        })

        cls.sale_order = cls.env['sale.order'].create({
            'partner_id': cls.customer.id,
            'user_id': cls.salesman.id,
            'order_line': [
                (0, 0, {
                    'product_id': cls.product_a.id,
                    'name': cls.product_a.name,
                    'product_uom': cls.env.ref('uom.product_uom_unit').id,
                    'product_uom_qty': 1,
                })
            ]
        })

    @classmethod
    def _confirm_sale_order(cls):
        cls.sale_order.sudo(cls.salesman).action_confirm()

    @classmethod
    def _generate_serial_number(cls, product, number):
        serial = cls.env['stock.production.lot'].create({
            'number': number,
            'product_id': product.id,
        })
        inventory = cls.env['stock.inventory'].create({
            'name': 'Add serial number',
        })
        inventory.action_start()

        warehouse = cls.env['stock.warehouse'].search([
            ('company_id', '=', cls.env.user.company_id.id),
        ])
        inventory.write({
            'line_ids': [(0, 0, {
                'product_id': product.id,
                'product_qty': 1,
                'prod_lot_id': serial.id,
                'location_id': warehouse.lot_stock_id.id,
            })]
        })
        inventory.action_validate()
        return serial


class WarrantyActivationCase(SaleWarrantyCase):

    @classmethod
    def _select_serial_number_on_stock_picking(cls, serial_number, picking):
        move = next(m for m in picking.move_lines if m.product_id == serial_number.product_id)
        move_line_vals = {
            'location_dest_id': move.location_dest_id.id,
            'location_id': move.location_id.id,
            'lot_id': serial_number.id,
            'product_id': move.product_id.id,
            'product_uom_id': cls.env.ref('uom.product_uom_unit').id,
            'qty_done': 1,
        }
        line_without_serial = next((l for l in move.move_line_ids if not l.lot_id), None)
        if line_without_serial:
            line_without_serial.write(move_line_vals)
        else:
            move.write({'move_line_ids': [(0, 0, move_line_vals)]})

    @classmethod
    def _deliver_products(cls, picking, serial_numbers):
        for serial in serial_numbers:
            cls._select_serial_number_on_stock_picking(serial, picking)
        picking.sudo(cls.stock_user).action_done()

        # Verify that the stock.picking was properly processed.
        assert picking.state == 'done'
        move_lines = picking.mapped('move_lines.move_line_ids')
        assert len(move_lines) == len(serial_numbers)
        assert move_lines.mapped('lot_id') == serial_numbers
        for line in move_lines:
            assert line.qty_done == 1
