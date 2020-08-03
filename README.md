# ICON ETL

[![Build Status](https://travis-ci.org/insight-icon/icon-etl.svg?branch=master)](https://travis-ci.org/github/insight-icon/icon-etl)
[![Pypi Version](https://img.shields.io/pypi/v/icon-etl)](https://pypi.org/project/icon-etl/)
[![Pypi Version](https://img.shields.io/pypi/l/icon-etl)](https://pypi.org/project/icon-etl/)



## Quickstart

Install ICON ETL:

```bash
pip3 install icon-etl
```

Export blocks and transactions:

```bash
> iconetl export_blocks_and_transactions --start-block 0 --end-block 500000 \
--blocks-output blocks.csv --transactions-output transactions.csv
```

## Running Tests

```bash
> pip3 install -e .[dev,streaming]
> export ICON_ETL_RUN_SLOW_TESTS=True
> pytest -vv
```

### Running Tox Tests

```bash
> pip3 install tox
> tox
```
