FROM ubuntu:20.04

RUN apt-get -qq update \
    && apt-get -qq install -y --no-install-recommends ca-certificates \
    && apt-get -qq install -y --no-install-recommends curl \
    && apt-get -qq install -y --no-install-recommends postgresql-client

RUN curl -fsSL -o /bin/dbmate https://github.com/amacneil/dbmate/releases/download/v1.12.0/dbmate-linux-amd64 \
    && chmod +x /bin/dbmate

COPY ./*.sql /db/migrations/
COPY ./entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]
