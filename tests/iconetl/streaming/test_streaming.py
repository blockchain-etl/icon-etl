#  MIT License
#
#  Copyright (c) 2021 Richard Mah (richard@geometrylabs.io) & Geometry Labs (geometrylabs.io)
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

import pytest
from blockchainetl_common.jobs.exporters.composite_item_exporter import (
    CompositeItemExporter,
)
from blockchainetl_common.streaming.streamer import Streamer
from blockchainetl_common.thread_local_proxy import ThreadLocalProxy

import tests.resources
from iconetl.enumeration.entity_type import EntityType
from iconetl.streaming.icx_streamer_adapter import IcxStreamerAdapter
from tests.iconetl.job.utils import get_web3_provider
from tests.utils import (
    compare_lines_ignore_order,
    read_file,
    skip_if_slow_tests_disabled,
)

RESOURCE_GROUP = "test_stream"


def read_resource(resource_group, file_name):
    return tests.resources.read_resource([RESOURCE_GROUP, resource_group], file_name)


@pytest.mark.parametrize(
    "start_block, end_block, batch_size, resource_group, entity_types, provider_type",
    [
        (
            21388823,
            21388824,
            1,
            "blocks_21388823_21388824",
            EntityType.ALL_FOR_STREAMING,
            "mock",
        ),
        skip_if_slow_tests_disabled(
            [
                21388823,
                21388824,
                1,
                "blocks_21388823_21388824",
                EntityType.ALL_FOR_STREAMING,
                "public_endpoint",
            ]
        ),
    ],
)
def test_stream(
    tmpdir,
    start_block,
    end_block,
    batch_size,
    resource_group,
    entity_types,
    provider_type,
):
    try:
        os.remove("last_synced_block.txt")
    except OSError:
        pass

    blocks_output_file = str(tmpdir.join("actual_blocks.json"))
    transactions_output_file = str(tmpdir.join("actual_transactions.json"))
    logs_output_file = str(tmpdir.join("actual_logs.json"))

    streamer_adapter = IcxStreamerAdapter(
        batch_web3_provider=ThreadLocalProxy(
            lambda: get_web3_provider(
                provider_type,
                read_resource_lambda=lambda file: read_resource(resource_group, file),
                batch=True,
            )
        ),
        batch_size=batch_size,
        item_exporter=CompositeItemExporter(
            filename_mapping={
                "block": blocks_output_file,
                "transaction": transactions_output_file,
                "log": logs_output_file,
            }
        ),
        entity_types=entity_types,
    )
    streamer = Streamer(
        blockchain_streamer_adapter=streamer_adapter,
        start_block=start_block,
        end_block=end_block,
        retry_errors=False,
    )
    streamer.stream()

    if "block" in entity_types:
        print("=====================")
        print(read_file(blocks_output_file))
        compare_lines_ignore_order(
            read_resource(resource_group, "expected_blocks.json"),
            read_file(blocks_output_file),
        )

    if "transaction" in entity_types:
        print("=====================")
        print(read_file(transactions_output_file))
        compare_lines_ignore_order(
            read_resource(resource_group, "expected_transactions.json"),
            read_file(transactions_output_file),
        )

    if "log" in entity_types:
        print("=====================")
        print(read_file(logs_output_file))
        compare_lines_ignore_order(
            read_resource(resource_group, "expected_logs.json"),
            read_file(logs_output_file),
        )
