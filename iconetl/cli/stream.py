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


import logging
import random

import click
from blockchainetl_common.streaming.streaming_utils import (
    configure_logging,
    configure_signals,
)
from blockchainetl_common.thread_local_proxy import ThreadLocalProxy
from iconsdk.icon_service import IconService
from iconsdk.providers.http_provider import HTTPProvider

from iconetl.enumeration.entity_type import EntityType
from iconetl.providers.auto import get_provider_from_uri


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.option(
    "-l",
    "--last-synced-block-file",
    default="last_synced_block.txt",
    show_default=True,
    type=str,
    help="",
)
@click.option(
    "--lag",
    default=0,
    show_default=True,
    type=int,
    help="The number of blocks to lag behind the network.",
)
@click.option(
    "-p",
    "--provider-uri",
    default="https://ctz.solidwallet.io/api/v3",
    show_default=True,
    type=str,
    help="The URI of the node endpoint",
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
@click.option(
    "-s", "--start-block", default=None, show_default=True, type=int, help="Start block"
)
@click.option(
    "--start-at-head",
    default=False,
    show_default=True,
    type=bool,
    help="Start syncing at chain head",
)
@click.option(
    "-e",
    "--entity-types",
    default=",".join(EntityType.ALL_FOR_STREAMING),
    show_default=True,
    type=str,
    help="The list of entity types to export.",
)
@click.option(
    "--period-seconds",
    default=10,
    show_default=True,
    type=int,
    help="How many seconds to sleep between syncs",
)
@click.option(
    "-b",
    "--batch-size",
    default=10,
    show_default=True,
    type=int,
    help="How many blocks to batch in single request",
)
@click.option(
    "-B",
    "--block-batch-size",
    default=1,
    show_default=True,
    type=int,
    help="How many blocks to batch in single sync round",
)
@click.option(
    "-w",
    "--max-workers",
    default=5,
    show_default=True,
    type=int,
    help="The number of workers",
)
@click.option("--log-file", default=None, show_default=True, type=str, help="Log file")
@click.option("--pid-file", default=None, show_default=True, type=str, help="pid file")
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
def stream(
    last_synced_block_file,
    lag,
    provider_uri,
    output,
    start_block,
    start_at_head,
    entity_types,
    kafka_blocks_topic,
    kafka_transactions_topic,
    kafka_logs_topic,
    kafka_compression_type,
    kafka_schema_registry_url,
    values_as_hex,
    period_seconds=10,
    batch_size=2,
    block_batch_size=10,
    max_workers=5,
    log_file=None,
    pid_file=None,
):
    """Streams all data types to console or Google Pub/Sub."""
    configure_logging(log_file)
    configure_signals()
    entity_types = parse_entity_types(entity_types)
    validate_entity_types(entity_types, output)
    start_block = determine_start_block(start_block, start_at_head, provider_uri)

    from blockchainetl_common.streaming.streamer import Streamer

    from iconetl.streaming.icx_streamer_adapter import IcxStreamerAdapter
    from iconetl.streaming.item_exporter_creator import create_item_exporter

    provider_uri = pick_random_provider_uri(provider_uri)
    logging.info("Using " + provider_uri)

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
            lambda: get_provider_from_uri(provider_uri, batch=True)
        ),
        item_exporter=create_item_exporter(output, kafka_settings),
        batch_size=batch_size,
        max_workers=max_workers,
        entity_types=entity_types,
    )
    streamer = Streamer(
        blockchain_streamer_adapter=streamer_adapter,
        last_synced_block_file=last_synced_block_file,
        lag=lag,
        start_block=start_block,
        period_seconds=period_seconds,
        block_batch_size=block_batch_size,
        pid_file=pid_file,
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


def pick_random_provider_uri(provider_uri):
    provider_uris = [uri.strip() for uri in provider_uri.split(",")]
    return random.choice(provider_uris)


def determine_start_block(start_block, start_at_head, provider_uri):
    if start_block and start_at_head:
        raise ValueError(
            "A start block value, {}, should not be specified if the --start-at-head option is enabled.".format(
                start_block
            )
        )

    if not start_at_head:
        return start_block

    if start_at_head:
        svc = IconService(HTTPProvider(provider_uri))
        head = svc.get_block("latest")["height"]
        return head
