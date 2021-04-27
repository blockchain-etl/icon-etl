# Testing Mocks

There is a command that can be used to mock the output from the ICON ETL streaming output, and is typically used as such:

```bash
> iconetl  etltest mock_stream -o kafka:9092 -i /files -s 21388823 --end-block 21388824 --values-as-hex True
```

## Options

| Short flag | Long flag                   | Type    | Description                                                                                                                                                                                                                                                      |
|------------|-----------------------------|---------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| -i         | --input_directory           | TEXT    | Path to directory containing files to be mocked.                                                                                                                                                                                                                 |
| -o         | --output                    | TEXT    | Either Google PubSub topic path e.g. projects/your-project/topics/crypto_icon; a Postgres connection url e.g. postgresql+pg8000://postgres:admin@127.0.0.1:5432/icon. or a Kafka node url e.g. kafka.node.example[:1234]. If not specified will print to console |
| -s         | --start-block               | INTEGER | Start block  [required]                                                                                                                                                                                                                                          |
|            | --end-block                 | INTEGER | End block  [required]                                                                                                                                                                                                                                            |
| -e         | --entity-types              | TEXT    | The list of entity types to export. [default: block, transaction, log, receipt]                                                                                                                                                                                  |
|            | --log-file                  | TEXT    | Log file                                                                                                                                                                                                                                                         |
|            | --kafka-blocks-topic        | TEXT    | Name of Kafka topic for block data [default: blocks]                                                                                                                                                                                                             |
|            | --kafka-transactions-topic  | TEXT    | Name of Kafka topic for transaction data [default: transactions]                                                                                                                                                                                                 |
|            | --kafka-logs-topic          | TEXT    | Name of Kafka topic for log data  [default: logs]                                                                                                                                                                                                                |
|            | --kafka-compression-type    | TEXT    | Type/level of compression for Kafka: either 'gzip', snappy, or None  [default: gzip]                                                                                                                                                                             |
|            | --kafka-schema-registry-url | TEXT    | URL for Kafka schema registry. Must use 'http://'. If not specified, schema registry will not be used.                                                                                                                                                           |
|            | --values-as-hex             | BOOLEAN | Export ICX (loop) values as hex rather than int.  [default: False]                                                                                                                                                                                               |

## Notes

- If using in a Docker container, ensure you've mounted the volume containing the files to be mocked.
- You **must** specify the start and end blocks based on the files to be mocked
- Mocked files **must** have the appropriate name provided to them, as below

```text
web3_response.{rpc_method_name}_{item_hash}.json
```
