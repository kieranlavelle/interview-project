FROM postgres:15.1-alpine


COPY ./docker/init.sql /docker-entrypoint-initdb.d/
