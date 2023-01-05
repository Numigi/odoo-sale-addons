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

COPY crm_brand /mnt/extra-addons/crm_brand
COPY delivery_carrier_fixed_over /mnt/extra-addons/delivery_carrier_fixed_over
COPY event_sale_order_status /mnt/extra-addons/event_sale_order_status
COPY payment_auto_confirm_sale_order /mnt/extra-addons/payment_auto_confirm_sale_order
COPY sale_default_term_on_company /mnt/extra-addons/sale_default_term_on_company
COPY sale_delivery_completion /mnt/extra-addons/sale_delivery_completion
COPY sale_delivery_completion_rental /mnt/extra-addons/sale_delivery_completion_rental
COPY sale_dynamic_price /mnt/extra-addons/sale_dynamic_price
COPY sale_invoice_email_warning /mnt/extra-addons/sale_invoice_email_warning
COPY sale_invoice_group_by_order /mnt/extra-addons/sale_invoice_group_by_order
COPY sale_kit /mnt/extra-addons/sale_kit
COPY sale_minimum_margin /mnt/extra-addons/sale_minimum_margin
COPY sale_order_available_qty_popover /mnt/extra-addons/sale_order_available_qty_popover
COPY sale_order_available_qty_popover_rental /mnt/extra-addons/sale_order_available_qty_popover_rental
COPY sale_order_line_readonly_conditions /mnt/extra-addons/sale_order_line_readonly_conditions
COPY sale_order_margin_percent /mnt/extra-addons/sale_order_margin_percent
COPY sale_order_weight /mnt/extra-addons/sale_order_weight
COPY sale_persistent_product_warning /mnt/extra-addons/sale_persistent_product_warning
COPY sale_privilege_level /mnt/extra-addons/sale_privilege_level
COPY sale_privilege_level_delivery /mnt/extra-addons/sale_privilege_level_delivery
COPY sale_privilege_level_payment /mnt/extra-addons/sale_privilege_level_payment
COPY sale_privilege_level_pricelist /mnt/extra-addons/sale_privilege_level_pricelist
COPY sale_privilege_level_website /mnt/extra-addons/sale_privilege_level_website
COPY sale_rental /mnt/extra-addons/sale_rental
COPY sale_xmlrpc_compatible /mnt/extra-addons/sale_xmlrpc_compatible

COPY .docker_files/main /mnt/extra-addons/main
COPY .docker_files/odoo.conf /etc/odoo
