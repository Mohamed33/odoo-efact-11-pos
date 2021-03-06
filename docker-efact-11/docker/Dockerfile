FROM debian:stretch-slim
LABEL maintainer="Facturacion VIP <ingvcueva@gmail.com>"

# Generate locale C.UTF-8 for postgres and general locale data
ENV LANG C.UTF-8

RUN echo "America/Lima" > /etc/timezone
ENV TZ=America/Lima
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
# Install some deps, lessc and less-plugin-clean-css, and wkhtmltopdf
RUN set -x; \
        apt-get update \
        && apt-get install -y --no-install-recommends \
            ca-certificates \
            curl \
            dirmngr \
            fonts-noto-cjk \
            gnupg \
            libssl1.0-dev \
            node-less \
            python3-pip \
            python3-pyldap \
            python3-qrcode \
            python3-renderpm \
            python3-setuptools \
            python3-vobject \
            python3-watchdog \
            xz-utils \
            unoconv \
            subversion \
        && curl -o wkhtmltox.deb -sSL https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.5/wkhtmltox_0.12.5-1.stretch_amd64.deb \
        && echo '7e35a63f9db14f93ec7feeb0fce76b30c08f2057 wkhtmltox.deb' | sha1sum -c - \
        && dpkg --force-depends -i wkhtmltox.deb\
        && apt-get -y install -f --no-install-recommends \
        && rm -rf /var/lib/apt/lists/* wkhtmltox.deb

# install latest postgresql-client

RUN set -x; \
        echo 'deb http://apt.postgresql.org/pub/repos/apt/ stretch-pgdg main' >  /etc/apt/sources.list.d/pgdg.list \
        && curl -o key.asc https://www.postgresql.org/media/keys/ACCC4CF8.asc && apt-key add key.asc && rm key.asc \
        && apt-get update  \
        && apt-get install -y postgresql-client-10 \
        && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest-odoo
#RUN set -x; \
#        echo 'deb http://apt.postgresql.org/pub/repos/apt/ stretch-pgdg main' > etc/apt/sources.list.d/pgdg.list \
#        && export GNUPGHOME="$(mktemp -d)" \
#        && repokey='B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8' \
#        && gpg --batch --keyserver keyserver.ubuntu.com --recv-keys "${repokey}" \
#        && gpg --batch --armor --export "${repokey}" > /etc/apt/trusted.gpg.d/pgdg.gpg.asc \
#        && gpgconf --kill all \
#        && rm -rf "$GNUPGHOME" \
#        && apt-get update  \
#        && apt-get install -y postgresql-client \
#        && rm -rf /var/lib/apt/lists/*

# Install Odoo

ENV ODOO_VERSION 11.0
ARG ODOO_RELEASE=20200826
ARG ODOO_SHA=cf5c3c766ba42861ede4ec9b4027dfc910818a01

RUN set -x; \
        curl -o odoo.deb -SL http://nightly.odoo.com/${ODOO_VERSION}/nightly/deb/odoo_${ODOO_VERSION}.${ODOO_RELEASE}_all.deb \
        && echo "${ODOO_SHA} odoo.deb" | sha1sum -c - \
        && dpkg --force-depends -i odoo.deb \
        && apt-get update \
        && apt-get -y install -f --no-install-recommends \
        && rm -rf /var/lib/apt/lists/* odoo.deb

# Aditional libraries
COPY requirements.txt /
RUN pip3 install -U pip
RUN pip3 install -U -r /requirements.txt \
        && rm requirements.txt
        
# Copy entrypoint script and Odoo configuration file
COPY ./entrypoint.sh /
COPY ./odoo.conf /etc/odoo/
RUN chown -R odoo:odoo /etc/odoo

# Mount /var/lib/odoo to allow restoring filestore and /mnt/extra-addons for users addons
RUN mkdir -p /mnt/extra-addons \
        && chown -R odoo /mnt/extra-addons
VOLUME ["/var/lib/odoo", "/mnt/extra-addons"]

# Expose Odoo services
EXPOSE 8069 8071

# Set the default config file
ENV ODOO_RC /etc/odoo/odoo.conf


COPY wait-for-psql.py /usr/local/bin/wait-for-psql.py

# Set default user when running the container
USER odoo

ENTRYPOINT ["/entrypoint.sh"]
CMD ["odoo"]
