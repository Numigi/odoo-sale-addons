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

# To exclude module, add folder name to .dockerignore
COPY . /mnt/extra-addons

USER root

# Cleaning extra-addons after massive copy
RUN [ "/bin/bash", "-c", "\
    find /mnt/extra-addons/ -maxdepth 1 -type f -delete && \
    find /mnt/extra-addons/ -maxdepth 1 -type d -iname '.*' -print0 | xargs -I {} -0 rm -rvf '{}'\
    " ]

USER odoo

COPY .docker_files/main /mnt/extra-addons/main
COPY .docker_files/odoo.conf /etc/odoo
