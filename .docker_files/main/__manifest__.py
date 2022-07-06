# © 2019 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Main Module",
    "version": "1.0.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://www.numigi.com",
    "license": "LGPL-3",
    "category": "Other",
    "summary": "Install all addons required for testing.",
    "depends": [
        "l10n_ca",  # for testing sale_intercompany_service
        "stock_dropshipping",  # for testing purchase_sale_inter_company_route
        "commission",
        "commission_intercompany_service",
        "commission_payroll_preparation",
        "crm_assign_by_area",
        "crm_assign_in_house",
        "crm_brand",
        "crm_filter_no_activity",
        "crm_forward_sorting_area",
        "crm_industry_parent_filter",
        "crm_team_by_industry",
        "delivery_carrier_fixed_over",
        "event_sale_order_status",
        "commission",
        "commission_payroll_preparation",
        "commission_prorata",
        "contract_invoice_offset",
        "payment_auto_confirm_sale_order",
        "purchase_sale_inter_company_route",
        "sale_commitment_date_update",
        "sale_commitment_date_update_mrp",
        "sale_default_analytic_tag",
        "sale_default_term_on_company",
        "sale_delivery_completion",
        "sale_dynamic_price",
        "sale_intercompany_service",
        "sale_invoice_email_warning",
        "sale_invoice_no_follow",
        "sale_kit",
        "sale_minimum_margin",
        "sale_order_available_qty_popover",
        "sale_order_available_qty_popover_rental",
        "sale_order_default_taxes",
        "sale_order_line_margin_amount",
        "sale_order_line_readonly_conditions",
        "sale_order_margin_percent",
        "sale_order_url_tracking",
        "sale_order_weight",
        "sale_partner_authorized_company",
        "sale_persistent_product_warning",
        "sale_privilege_level",
        "sale_privilege_level_delivery",
        "sale_privilege_level_payment",
        "sale_privilege_level_pricelist",
        "sale_privilege_level_rental_pricelist",
        "sale_privilege_level_website",
        "sale_project_milestone",
        "sale_rental",
        "sale_rental_app",
        "sale_rental_order_swap_variant",
        "sale_rental_portal",
        "sale_rental_pricelist",
        "sale_stock_move_no_merge",
        "sale_timesheet_invoicing_period",
        "sale_warranty",
        "sale_warranty_extension",
        "sale_warranty_lead_on_expiry",
        "sale_whole_order_invoiced",
        "web_view_google_map_itinerary",
        "website_event_message_unpublished",
        "website_payment_message_enhanced",
        "website_sale_request_price",
        "website_sale_request_price_wishlist",
        "website_stock_availability_enhanced",
    ],
    "installable": True,
}
