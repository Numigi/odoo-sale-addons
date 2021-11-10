# © 2020 - today Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime
from odoo.http import request
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.addons.product_supplier_info_helpers.helpers import (
    get_supplier_info_from_product,
)


class ProductProduct__enhanced_availability(models.Model):

    _inherit = "product.product"

    replenishment_delay = fields.Integer(
        company_dependent=True,
    )
    replenishment_availability = fields.Float(
        digits=dp.get_precision("Product Unit of Measure"),
        company_dependent=True,
    )
    sale_availability = fields.Float(
        digits=dp.get_precision("Product Unit of Measure"),
        company_dependent=True,
    )

    def _compute_quantities(self):
        super()._compute_quantities()
        website = request and getattr(request, 'website', None)
        if website:
            for product in self:
                product.virtual_available = product.replenishment_availability

    def compute_availability(self):
        for product in self.sudo().__iter_products_per_company():
            sale_availability = product.__get_sale_availability()
            next_replenishment_qty = product.__get_next_replenishment_quantity()
            product.sale_availability = sale_availability
            product.replenishment_availability = (
                sale_availability + next_replenishment_qty
            )
            product.replenishment_delay = product.sudo().__get_replenishment_delay()

    def _get_enhanced_availability_info(self, add_qty):
        info = {
            "cart_qty": self.cart_qty,
            "product_template": self.product_tmpl_id.id,
            "product_type": self.type,
            "uom_name": self.uom_id.name,
        }

        if self.__show_availability():
            self.__set_availability(info, add_qty)

        if self.custom_message:
            info["custom_message"] = self.custom_message

        return info

    def __iter_products_per_company(self):
        all_companies = self.env["res.company"].search([])

        for product in self:
            companies = product.company_id or all_companies
            for company in companies:
                yield product.with_context(force_company=company.id)

    def __get_sale_availability(self):
        current_qty = self.__get_current_qty()
        out_qty = self.__get_outgoing_qty()
        return max(current_qty - out_qty, 0)

    def __get_replenishment_delay(self):
        picking = self.__get_next_receipt()
        if picking:
            delta = picking.scheduled_date - datetime.now()
            return max(delta.days, 0)
        else:
            return self.__get_standard_replenishment_delay()

    def __get_standard_replenishment_delay(self):
        company = self.__get_company()
        supplier_info = self.__get_main_supplier_info()
        return company.security_lead + company.po_lead + (supplier_info.delay or 0)

    def __get_main_supplier_info(self):
        company_id = self.__get_company_id()
        supplier_info = (
            get_supplier_info_from_product(self)
            .sorted(key=lambda s: (0 if s.product_id else 1, s.sequence))
            .filtered(lambda s: not s.company_id or s.company_id.id == company_id)
        )
        return supplier_info[:1]

    def __get_next_replenishment_quantity(self):
        picking = self.__get_next_receipt()
        moves = picking.mapped("move_lines").filtered(lambda m: m.product_id == self)
        return sum(m.product_qty for m in moves)

    def __set_availability(self, info, add_qty):
        info["show_availability"] = True

        if self.__show_available_qty():
            info["show_available_qty"] = True
            info["available_qty"] = self.__get_available_qty()

        elif self.__show_available_qty_warning(add_qty):
            info["show_available_qty_warning"] = True
            info["available_qty"] = self.__get_available_qty()

        elif self.__show_in_stock(add_qty):
            info["show_in_stock"] = True

        elif self.__show_replenishment_delay(add_qty):
            info["show_replenishment_delay"] = True
            info["replenishment_delay_message"] = self.__get_replenishment_message()
            info["replenishment_delay"] = self.replenishment_delay

    def __show_availability(self):
        return self.inventory_availability not in ("never", "custom")

    def __show_available_qty(self):
        return self.inventory_availability == "always"

    def __show_available_qty_warning(self, add_qty):
        available_qty = self.__get_available_qty()
        is_threshold = self.inventory_availability in ("threshold", "threshold_warning")
        qty_below_threshold = available_qty <= self.available_threshold
        enough_available = add_qty <= available_qty
        return is_threshold and qty_below_threshold and enough_available

    def __show_in_stock(self, add_qty):
        return self.__get_available_qty() >= add_qty

    def __show_replenishment_delay(self, add_qty):
        return self.__get_replenishment_qty() >= add_qty

    def __get_available_qty(self):
        return self.sale_availability - self.cart_qty

    def __get_replenishment_qty(self):
        return self.replenishment_availability - self.cart_qty

    def __get_replenishment_message(self):
        return _(
            "Unfortunately, the stock level is currently low for this product. "
            "We estimate a better availability of this product in a delay of "
            "{} days."
        ).format(self.replenishment_delay)

    def __get_next_receipt(self):
        domain = [
            *self.__get_pending_stock_move_domain(),
            ("location_id.usage", "=", "supplier"),
            ("location_dest_id.usage", "=", "internal"),
            ("location_dest_id.company_id", "=", self.__get_company_id()),
        ]
        move = self.env["stock.move"].search(domain, order="date_expected", limit=1)
        return move.picking_id

    def __get_current_qty(self):
        domain = [
            ("product_id", "=", self.id),
            ("location_id.usage", "=", "internal"),
            ("location_id.company_id", "=", self.__get_company_id()),
        ]
        field = "quantity"
        res = self.env["stock.quant"].read_group(domain, [field], [field])
        return res[0][field] if res else 0

    def __get_outgoing_qty(self):
        domain = [
            *self.__get_pending_stock_move_domain(),
            ("location_dest_id.usage", "=", "customer"),
            ("location_id.usage", "=", "internal"),
            ("location_id.company_id", "=", self.__get_company_id()),
        ]
        field = "product_qty"
        res = self.env["stock.move"].read_group(domain, [field], [field])
        return res[0][field] if res else 0

    def __get_pending_stock_move_domain(self):
        return [
            ("product_id", "=", self.id),
            ("state", "not in", ("done", "cancel", "done")),
        ]

    def __get_company(self):
        return self.env["res.company"].browse(self.__get_company_id())

    def __get_company_id(self):
        return self._context.get("force_company")
