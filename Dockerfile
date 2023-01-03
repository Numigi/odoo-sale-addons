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
COPY sale_invoice_group_by_order /mnt/extra-addons/sale_invoice_group_by_order
COPY sale_xmlrpc_compatible /mnt/extra-addons/sale_xmlrpc_compatible

COPY .docker_files/main /mnt/extra-addons/main
COPY .docker_files/odoo.conf /etc/odoo
