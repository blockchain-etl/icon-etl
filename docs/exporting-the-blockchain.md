## Exporting the Blockchain

1. Install python 3.6+ https://www.python.org/downloads/

1. Install ICON ETL: `> pip3 install icon-etl`

1. Export all:

```bash
> iconetl export_all --help
> iconetl export_all -s 0 -e 10000000 -b 100000 -o output
```

In case `iconetl` command is not available in PATH, use `python3 -m iconetl` instead.

The result will be in the `output` subdirectory, partitioned in Hive style:
```bash
output/blocks/start_block=00000000/end_block=00099999/blocks_00000000_00099999.csv
output/blocks/start_block=00100000/end_block=00199999/blocks_00100000_00199999.csv
...
output/transactions/start_block=00000000/end_block=00099999/transactions_00000000_00099999.csv
...
```
