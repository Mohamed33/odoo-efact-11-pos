FROM postgres:10-alpine
ENV TZ=America/Lima
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
COPY ./postgresql.conf /var/lib/postgresql/data/pgdata/postgresql.conf 