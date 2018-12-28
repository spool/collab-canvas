FROM mdillon/postgis:10
# FROM postgres:11

# Postgis capabilities
# https://github.com/appropriate/docker-postgis/blob/master/11-2.5/Dockerfile
#
# ENV POSTGIS_MAJOR 2.5
# ENV POSTGIS_VERSION 2.5.1+dfsg-1.pgdg90+1
#
# RUN apt-get update \
#       && apt-cache showpkg postgresql-$PG_MAJOR-postgis-$POSTGIS_MAJOR \
#       && apt-get install -y --no-install-recommends \
#            postgresql-$PG_MAJOR-postgis-$POSTGIS_MAJOR=$POSTGIS_VERSION \
#            postgresql-$PG_MAJOR-postgis-$POSTGIS_MAJOR-scripts=$POSTGIS_VERSION \
#            postgis=$POSTGIS_VERSION \
#       && rm -rf /var/lib/apt/lists/*
#
# RUN mkdir -p /docker-entrypoint-initdb.d
# COPY ./initdb-postgis.sh /docker-entrypoint-initdb.d/postgis.sh
# COPY ./update-postgis.sh /usr/local/bin

#End of copied postgis components


COPY ./compose/production/postgres/maintenance /usr/local/bin/maintenance
RUN chmod +x /usr/local/bin/maintenance/*
RUN mv /usr/local/bin/maintenance/* /usr/local/bin \
    && rmdir /usr/local/bin/maintenance
