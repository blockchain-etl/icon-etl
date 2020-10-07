# Commands

All the commands accept `-h` parameter for help, e.g.:

```bash
> iconetl export_blocks_and_transactions -h

Usage: iconetl export_blocks_and_transactions [OPTIONS]

  Exports blocks and transactions.

Options:
  -s, --start-block INTEGER   Start block  [default: 0]
  -e, --end-block INTEGER     End block  [required]
  -b, --batch-size INTEGER    The number of blocks to export at a time.
                              [default: 100]
  -p, --provider-uri TEXT     The URI of the node endpoint  [default:
                              https://ctz.solidwallet.io/api/v3]
  -w, --max-workers INTEGER   The maximum number of workers.  [default: 5]
  --blocks-output TEXT        The output file for blocks. If not provided
                              blocks will not be exported. Use "-" for stdout
  --transactions-output TEXT  The output file for transactions. If not
                              provided transactions will not be exported. Use
                              "-" for stdout
  -h, --help                  Show this message and exit.
```

For the `--output` parameters the supported types are csv and json. The format type is inferred from the output file name.

#### export_blocks_and_transactions

```bash
> iconetl export_blocks_and_transactions --start-block 0 --end-block 500000 \
--provider-uri https://ctz.solidwallet.io/api/v3 \
--blocks-output blocks.csv --transactions-output transactions.csv
```

Omit `--blocks-output` or `--transactions-output` options if you want to export only transactions/blocks.

You can tune `--batch-size`, `--max-workers` for performance.

[Blocks and transactions schema](schema.md#blockscsv).

#### export_receipts_and_logs

First extract transaction hashes from `transactions.csv`
(Exported with [export_blocks_and_transactions](#export_blocks_and_transactions)):

```bash
> iconetl extract_csv_column --input transactions.csv --column hash --output transaction_hashes.txt
```

Then export receipts and logs:

```bash
> iconetl export_receipts_and_logs --transaction-hashes transaction_hashes.txt \
--provider-uri https://ctz.solidwallet.io/api/v3 --receipts-output receipts.csv --logs-output logs.csv
```

Omit `--receipts-output` or `--logs-output` options if you want to export only logs/receipts.

You can tune `--batch-size`, `--max-workers` for performance.

[Receipts and logs schema](schema.md#receiptscsv).
