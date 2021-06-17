FROM python:3.6 as compile
MAINTAINER Richard Mah <richard@geometrylabs.io>
ENV PROJECT_DIR=icon-etl

RUN useradd -ms /bin/bash iconetl && mkdir /$PROJECT_DIR && chown -R iconetl:iconetl /$PROJECT_DIR
WORKDIR /$PROJECT_DIR
USER iconetl
COPY --chown=iconetl:iconetl . .
RUN pip install --upgrade pip && pip install --user -e /$PROJECT_DIR/[streaming]

FROM python:3.6-slim AS base

ENV PROJECT_DIR=icon-etl
RUN useradd -ms /bin/bash iconetl && mkdir /$PROJECT_DIR && chown -R iconetl:iconetl /$PROJECT_DIR
COPY --from=compile --chown=iconetl:iconetl /home/iconetl/.local /home/iconetl/.local
WORKDIR /$PROJECT_DIR
COPY --chown=iconetl:iconetl . .
ENV PATH=/home/iconetl/.local/bin:$PATH

# Add Tini
ENV TINI_VERSION v0.19.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini

USER iconetl
ENTRYPOINT ["/tini", "--", "python", "iconetl"]

FROM base as prod


FROM base as test
USER iconetl
COPY requirements_dev.txt .
RUN pip3 install -r requirements_dev.txt
RUN python3 -m pytest
