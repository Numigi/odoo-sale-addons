FROM quay.io/numigi/odoo-public:14.latest
LABEL maintainer="contact@numigi.com"

USER root

COPY .docker_files/test-requirements.txt .
RUN pip3 install -r test-requirements.txt

# Variable used for fetching private git repositories.
ARG GIT_TOKEN

ENV THIRD_PARTY_ADDONS /mnt/third-party-addons
RUN mkdir -p "${THIRD_PARTY_ADDONS}" && chown -R odoo "${THIRD_PARTY_ADDONS}"
COPY ./gitoo.yml /gitoo.yml
RUN gitoo install-all --conf_file /gitoo.yml --destination "${THIRD_PARTY_ADDONS}"

USER odoo

COPY crm_assign_by_area /mnt/extra-addons/crm_assign_by_area
COPY crm_assign_in_house /mnt/extra-addons/crm_assign_in_house
COPY crm_brand /mnt/extra-addons/crm_brand
COPY crm_kanban_prorated_revenue /mnt/extra-addons/crm_kanban_prorated_revenue
COPY crm_lead_product /mnt/extra-addons/crm_lead_product
COPY crm_team_by_industry /mnt/extra-addons/crm_team_by_industry
COPY delivery_carrier_fixed_over /mnt/extra-addons/delivery_carrier_fixed_over
COPY event_sale_order_status /mnt/extra-addons/event_sale_order_status
COPY partner_sale_target /mnt/extra-addons/partner_sale_target
COPY partner_sale_target_change_parent_binding /mnt/extra-addons/partner_sale_target_change_parent_binding
COPY payment_auto_confirm_sale_order /mnt/extra-addons/payment_auto_confirm_sale_order
COPY product_configurator_sale_ext /mnt/extra-addons/product_configurator_sale_ext
COPY product_pack_ext /mnt/extra-addons/product_pack_ext
COPY sale_commitment_date_update /mnt/extra-addons/sale_commitment_date_update
COPY sale_commitment_date_update_mrp /mnt/extra-addons/sale_commitment_date_update_mrp
COPY sale_coupon_apply_on_domain /mnt/extra-addons/sale_coupon_apply_on_domain
COPY sale_default_analytic_tag /mnt/extra-addons/sale_default_analytic_tag
COPY sale_default_term_on_company /mnt/extra-addons/sale_default_term_on_company
COPY sale_delivery_completion /mnt/extra-addons/sale_delivery_completion
COPY sale_delivery_completion_rental /mnt/extra-addons/sale_delivery_completion_rental
COPY sale_display_qty_widget_secondary_unit /mnt/extra-addons/sale_display_qty_widget_secondary_unit
COPY sale_double_validation /mnt/extra-addons/sale_double_validation
COPY sale_double_validation_extend /mnt/extra-addons/sale_double_validation_extend
COPY sale_dynamic_price /mnt/extra-addons/sale_dynamic_price
COPY sale_intercompany_service /mnt/extra-addons/sale_intercompany_service
COPY sale_invoice_email_warning /mnt/extra-addons/sale_invoice_email_warning
COPY sale_invoice_group_by_order /mnt/extra-addons/sale_invoice_group_by_order
COPY sale_invoice_no_follow /mnt/extra-addons/sale_invoice_no_follow
COPY sale_kit /mnt/extra-addons/sale_kit
COPY sale_minimum_margin /mnt/extra-addons/sale_minimum_margin
COPY sale_order_default_taxes /mnt/extra-addons/sale_order_default_taxes
COPY sale_order_groupby_parent_affiliate /mnt/extra-addons/sale_order_groupby_parent_affiliate
COPY sale_order_line_checkbox /mnt/extra-addons/sale_order_line_checkbox
COPY sale_order_line_margin_amount /mnt/extra-addons/sale_order_line_margin_amount
COPY sale_order_line_readonly_conditions /mnt/extra-addons/sale_order_line_readonly_conditions
COPY sale_order_margin_percent /mnt/extra-addons/sale_order_margin_percent
COPY sale_order_partner_restrict_affiliates /mnt/extra-addons/sale_order_partner_restrict_affiliates
COPY sale_order_portal_hide_invoices /mnt/extra-addons/sale_order_portal_hide_invoices
COPY sale_order_type_email_template /mnt/extra-addons/sale_order_type_email_template
COPY sale_order_url_tracking /mnt/extra-addons/sale_order_url_tracking
COPY sale_order_weight /mnt/extra-addons/sale_order_weight
COPY sale_partner_authorized_company /mnt/extra-addons/sale_partner_authorized_company
COPY sale_persistent_product_warning /mnt/extra-addons/sale_persistent_product_warning
COPY sale_privilege_level /mnt/extra-addons/sale_privilege_level
COPY sale_privilege_level_delivery /mnt/extra-addons/sale_privilege_level_delivery
COPY sale_privilege_level_payment /mnt/extra-addons/sale_privilege_level_payment
COPY sale_privilege_level_pricelist /mnt/extra-addons/sale_privilege_level_pricelist
COPY sale_privilege_level_rental_pricelist /mnt/extra-addons/sale_privilege_level_rental_pricelist
COPY sale_privilege_level_website /mnt/extra-addons/sale_privilege_level_website
COPY sale_product_configurator_img_width /mnt/extra-addons/sale_product_configurator_img_width
COPY sale_product_pack_configurator_binding /mnt/extra-addons/sale_product_pack_configurator_binding
COPY sale_product_pack_ext /mnt/extra-addons/sale_product_pack_ext
COPY sale_product_pack_modifiable /mnt/extra-addons/sale_product_pack_modifiable
COPY sale_project_description /mnt/extra-addons/sale_project_description
COPY sale_project_milestone /mnt/extra-addons/sale_project_milestone
COPY sale_qweb_report_website_desc /mnt/extra-addons/sale_qweb_report_website_desc
COPY sale_rental /mnt/extra-addons/sale_rental
COPY sale_rental_app /mnt/extra-addons/sale_rental_app
COPY sale_rental_order_swap_variant /mnt/extra-addons/sale_rental_order_swap_variant
COPY sale_rental_portal /mnt/extra-addons/sale_rental_portal
COPY sale_rental_pricelist /mnt/extra-addons/sale_rental_pricelist
COPY sale_rental_status /mnt/extra-addons/sale_rental_status
COPY sale_report_partner /mnt/extra-addons/sale_report_partner
COPY sale_stock_availability_popover /mnt/extra-addons/sale_stock_availability_popover
COPY sale_stock_move_no_merge /mnt/extra-addons/sale_stock_move_no_merge
COPY sale_subscription_extended /mnt/extra-addons/sale_subscription_extended
COPY sale_target_margin /mnt/extra-addons/sale_target_margin
COPY sale_warranty /mnt/extra-addons/sale_warranty
COPY sale_warranty_groupby_parent_affiliate /mnt/extra-addons/sale_warranty_groupby_parent_affiliate
COPY sale_whole_order_invoiced /mnt/extra-addons/sale_whole_order_invoiced
COPY sale_xmlrpc_compatible /mnt/extra-addons/sale_xmlrpc_compatible
COPY sales_team_account_journal /mnt/extra-addons/sales_team_account_journal
COPY web_view_google_map_itinerary /mnt/extra-addons/web_view_google_map_itinerary
COPY website_payment_message_enhanced /mnt/extra-addons/website_payment_message_enhanced
COPY website_sale_request_price /mnt/extra-addons/website_sale_request_price
COPY website_sale_request_price_wishlist /mnt/extra-addons/website_sale_request_price_wishlist
COPY website_stock_availability_enhanced /mnt/extra-addons/website_stock_availability_enhanced



COPY .docker_files/main /mnt/extra-addons/main
COPY .docker_files/odoo.conf /etc/odoo
