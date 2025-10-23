# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from .common import SaleWarrantyCase


class TestCancelWarrantiesOnSaleCancel(SaleWarrantyCase):

    def test_on_cancel_order_then_warranties_cancelled(self):
        self.confirm_sale_order()
        assert self.sale_order.warranty_ids.state == 'pending'
        self.sale_order.action_cancel()
        assert self.sale_order.warranty_ids.state == 'cancelled'
