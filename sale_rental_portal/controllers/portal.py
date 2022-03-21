# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import (
    CustomerPortal,
    pager as portal_pager,
    get_records_pager,
)


class SaleRentalPortal(CustomerPortal):
    def _prepare_portal_layout_values_inherit(self, values):
        partner = request.env.user.partner_id
        partner_id = partner.commercial_partner_id.id
        SaleOrder = request.env["sale.order"]
        order_ids = SaleOrder.search(
            [
                ("message_partner_ids", "child_of", [partner_id]),
                ("state", "in", ["sale", "done"]),
            ]
        )
        rentals_ids = order_ids.filtered(lambda x: x.is_rental)
        sales_ids = order_ids - rentals_ids
        values.update(
            {
                "order_count": len(sales_ids),
                "rental_count": len(rentals_ids),
            }
        )
        return values

    def _prepare_portal_layout_values(self):
        values = super(SaleRentalPortal, self)._prepare_portal_layout_values()
        return self._prepare_portal_layout_values_inherit(values)

    @http.route(
        ["/my/orders", "/my/orders/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_orders(
        self, page=1, date_begin=None, date_end=None, sortby=None, **kw
    ):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        SaleOrder = request.env["sale.order"]

        domain = [
            ("message_partner_ids", "child_of", [partner.commercial_partner_id.id]),
            ("state", "in", ["sale", "done"]),
        ]

        searchbar_sortings = {
            "date": {"label": _("Order Date"), "order": "date_order desc"},
            "name": {"label": _("Reference"), "order": "name"},
            "stage": {"label": _("Stage"), "order": "state"},
        }
        # default sortby order
        if not sortby:
            sortby = "date"
        sort_order = searchbar_sortings[sortby]["order"]

        archive_groups = self._get_archive_groups("sale.order", domain)
        if date_begin and date_end:
            domain += [
                ("create_date", ">", date_begin),
                ("create_date", "<=", date_end),
            ]

        is_rental = kw.get("rental") and int(kw.get("rental")) == 1
        values["page_name"] = "rental" if is_rental else "order"
        domain += [("is_rental", "=", True if is_rental else False)]

        # count for pager
        order_count = SaleOrder.search_count(domain)

        # pager
        pager = portal_pager(
            url="/my/orders",
            url_args={"date_begin": date_begin, "date_end": date_end, "sortby": sortby},
            total=order_count,
            page=page,
            step=self._items_per_page,
        )
        # content according to pager and archive selected
        orders = SaleOrder.search(
            domain, order=sort_order, limit=self._items_per_page, offset=pager["offset"]
        )
        request.session["my_orders_history"] = orders.ids[:100]

        values.update(
            {
                "date": date_begin,
                "orders": orders.sudo(),
                "pager": pager,
                "archive_groups": archive_groups,
                "default_url": "/my/orders",
                "searchbar_sortings": searchbar_sortings,
                "sortby": sortby,
            }
        )
        return request.render("sale.portal_my_orders", values)
