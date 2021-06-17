FROM python:3.6 as compile
MAINTAINER Richard Mah <richard@geometrylabs.io>
ENV PROJECT_DIR=icon-etl

WORKDIR /$PROJECT_DIR
COPY --chown=iconetl:iconetl . .
RUN cd /usr/local/lib/python3.6/site-packages && python /$PROJECT_DIR/setup.py develop && pip install -e /$PROJECT_DIR/[streaming]

FROM python:3.6-slim AS base

ENV PROJECT_DIR=icon-etl
RUN useradd -ms /bin/bash iconetl && mkdir /$PROJECT_DIR && chown -R iconetl:iconetl /$PROJECT_DIR
COPY --from=compile /usr/local/lib/python3.6/site-packages /usr/local/lib/python3.6/site-packages
WORKDIR /$PROJECT_DIR
USER iconetl
COPY --chown=iconetl:iconetl . .
ENV PATH=/$PROJECT_DIR:$PATH

ENTRYPOINT ["python", "iconetl"]

FROM base as prod


FROM base as test
USER iconetl
COPY requirements_dev.txt .
RUN pip3 install -r requirements_dev.txt
RUN python3 -m pytest
