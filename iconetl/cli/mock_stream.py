#  MIT License
#
#  Copyright (c) 2021 Richard Mah (richard@richardmah.com) & Insight Infrastructure
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of
#  this software and associated documentation files (the "Software"), to deal in
#  the Software without restriction, including without limitation the rights to
#  use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
#  the Software, and to permit persons to whom the Software is furnished to do so,
#  subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
#  FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
#  COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
#  IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
#  CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


import os

import click
from blockchainetl_common.streaming.streaming_utils import (
    configure_logging,
    configure_signals,
)
from blockchainetl_common.thread_local_proxy import ThreadLocalProxy

from iconetl.enumeration.entity_type import EntityType


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.option(
    "-i",
    "--input_directory",
    type=str,
    help="Path to directory containing files to be mocked.",
)
@click.option(
    "-o",
    "--output",
    type=str,
    help="Either Google PubSub topic path e.g. projects/your-project/topics/crypto_icon; "
    "a Postgres connection url e.g. postgresql+pg8000://postgres:admin@127.0.0.1:5432/icon. "
    "or a Kafka node url e.g. kafka.node.example[:1234]"
    "If not specified will print to console",
)
@click.option("-s", "--start-block", required=True, type=int, help="Start block")
@click.option(
    "--end-block",
    required=True,
    type=int,
    help="End block",
)
@click.option(
    "-e",
    "--entity-types",
    default=",".join(EntityType.ALL_FOR_STREAMING),
    show_default=True,
    type=str,
    help="The list of entity types to export.",
)
@click.option("--log-file", default=None, show_default=True, type=str, help="Log file")
@click.option(
    "--kafka-blocks-topic",
    default="blocks",
    show_default=True,
    type=str,
    envvar="ICONETL_KAFKA_TOPIC_BLOCKS",
    help="Name of Kafka topic for block data",
)
@click.option(
    "--kafka-transactions-topic",
    default="transactions",
    show_default=True,
    type=str,
    envvar="ICONETL_KAFKA_TOPIC_TRANSACTIONS",
    help="Name of Kafka topic for transaction data",
)
@click.option(
    "--kafka-logs-topic",
    default="logs",
    show_default=True,
    type=str,
    envvar="ICONETL_KAFKA_TOPIC_LOGS",
    help="Name of Kafka topic for log data",
)
@click.option(
    "--kafka-compression-type",
    default="gzip",
    show_default=True,
    type=str,
    envvar="ICONETL_KAFKA_COMPRESSION_TYPE",
    help="Type/level of compression for Kafka: either 'gzip', 'snappy', or None",
)
@click.option(
    "--kafka-schema-registry-url",
    default=None,
    show_default=True,
    type=str,
    envvar="ICONETL_KAFKA_SCHEMA_REGISTRY_URL",
    help="URL for Kafka schema registry. Must use 'http://'. If not specified, schema registry will not be used.",
)
@click.option(
    "--values-as-hex",
    default=False,
    show_default=True,
    type=bool,
    envvar="ICONETL_VALUES_AS_HEX",
    help="Export ICX (loop) values as hex rather than int.",
)
def mock_stream(
    input_directory,
    output,
    start_block,
    end_block,
    entity_types,
    kafka_blocks_topic,
    kafka_transactions_topic,
    kafka_logs_topic,
    kafka_compression_type,
    kafka_schema_registry_url,
    values_as_hex,
    batch_size=2,
    max_workers=5,
    log_file=None,
):
    """Streams all data types to console or Google Pub/Sub."""
    configure_logging(log_file)
    configure_signals()
    entity_types = parse_entity_types(entity_types)
    validate_entity_types(entity_types, output)

    from blockchainetl_common.streaming.streamer import Streamer

    from iconetl.streaming.icx_streamer_adapter import IcxStreamerAdapter
    from iconetl.streaming.item_exporter_creator import create_item_exporter
    from tests.iconetl.job.utils import get_web3_provider

    kafka_settings = {
        "topic_map": {
            "block": kafka_blocks_topic,
            "transaction": kafka_transactions_topic,
            "log": kafka_logs_topic,
        },
        "compression_type": kafka_compression_type,
        "schema_registry_url": kafka_schema_registry_url,
        "values_as_hex": values_as_hex,
    }

    streamer_adapter = IcxStreamerAdapter(
        batch_web3_provider=ThreadLocalProxy(
            lambda: get_web3_provider(
                provider_type="mock",
                read_resource_lambda=lambda file: read_resource(input_directory, file),
                batch=True,
            )
        ),
        item_exporter=create_item_exporter(output, kafka_settings),
        batch_size=batch_size,
        max_workers=max_workers,
        entity_types=entity_types,
    )
    streamer = Streamer(
        blockchain_streamer_adapter=streamer_adapter,
        start_block=start_block,
        end_block=end_block,
        retry_errors=False,
    )
    streamer.stream()


def parse_entity_types(entity_types):
    entity_types = [c.strip() for c in entity_types.split(",")]

    # validate passed types
    for entity_type in entity_types:
        if entity_type not in EntityType.ALL_FOR_STREAMING:
            raise click.BadOptionUsage(
                "--entity-type",
                "{} is not an available entity type. Supply a comma separated list of types from {}".format(
                    entity_type, ",".join(EntityType.ALL_FOR_STREAMING)
                ),
            )

    return entity_types


def validate_entity_types(entity_types, output):
    from iconetl.streaming.item_exporter_creator import (
        ItemExporterType,
        determine_item_exporter_type,
    )

    item_exporter_type = determine_item_exporter_type(output)
    if item_exporter_type == ItemExporterType.POSTGRES and (
        EntityType.CONTRACT in entity_types or EntityType.TOKEN in entity_types
    ):
        raise ValueError(
            "contract and token are not yet supported entity types for postgres item exporter."
        )


def read_resource(path, file_name):
    fixture_file_name = os.path.join(path, file_name)

    if not os.path.exists(fixture_file_name):
        raise ValueError("File does not exist: " + fixture_file_name)

    with open(fixture_file_name, encoding="utf-8") as file_handle:
        return file_handle.read()
