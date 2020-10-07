# Quickstart

Install ICON ETL:

```bash
pip3 install icon-etl
```

Export blocks and transactions:

```bash
> iconetl export_blocks_and_transactions --start-block 0 --end-block 500000 \
--blocks-output blocks.csv --transactions-output transactions.csv
```

Export logs and receipts:

```bash
> iconetl export_receipts_and_logs --transaction-hashes hashes.txt \
--receipts-output receipts.csv --logs-output logs.csv
```


Find all commands [here](commands.md).

---

To run the latest version of ICON ETL, check out the repo and call
```bash
> pip3 install -e .
> python3 iconetl.py
```
