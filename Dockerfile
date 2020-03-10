FROM quay.io/numigi/odoo-public:12.0
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

COPY sale_default_term_on_company /mnt/extra-addons/sale_default_term_on_company
COPY sale_delivery_completion /mnt/extra-addons/sale_delivery_completion
COPY sale_dynamic_price /mnt/extra-addons/sale_dynamic_price
COPY sale_minimum_margin /mnt/extra-addons/sale_minimum_margin
COPY sale_order_available_qty_popover /mnt/extra-addons/sale_order_available_qty_popover
COPY sale_order_margin_percent /mnt/extra-addons/sale_order_margin_percent
COPY sale_persistent_product_warning /mnt/extra-addons/sale_persistent_product_warning
COPY sale_warranty /mnt/extra-addons/sale_warranty
COPY sale_warranty_extension /mnt/extra-addons/sale_warranty_extension
COPY sale_warranty_lead_on_expiry /mnt/extra-addons/sale_warranty_lead_on_expiry
COPY sale_whole_order_invoiced /mnt/extra-addons/sale_whole_order_invoiced

COPY .docker_files/main /mnt/extra-addons/main
COPY .docker_files/odoo.conf /etc/odoo
