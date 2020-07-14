#  MIT License
#
#  Copyright (c) 2020 Richard Mah (richard@richardmah.com) & Insight Infrastructure
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


import pytest
import tests.resources
from blockchainetl_common.thread_local_proxy import ThreadLocalProxy
from iconetl.jobs.export_blocks_job import ExportBlocksJob
from iconetl.jobs.exporters.blocks_and_transactions_item_exporter import \
    blocks_and_transactions_item_exporter
from tests.iconetl.job.utils import get_web3_provider
from tests.utils import (compare_lines_ignore_order, read_file,
                         skip_if_slow_tests_disabled)

RESOURCE_GROUP = "test_export_blocks_job"


def read_resource(resource_group, file_name):
    return tests.resources.read_resource([RESOURCE_GROUP, resource_group], file_name)


@pytest.mark.parametrize(
    "start_block,end_block,batch_size,resource_group,web3_provider_type",
    [
        (10324748, 10324748, 1, "version_01a_block", "mock"),
        (12640760, 12640760, 1, "version_03_block", "mock"),
        (14473621, 14473621, 1, "version_04_block", "mock"),
        (14473622, 14473622, 1, "version_05_block", "mock"),
        skip_if_slow_tests_disabled(
            (10324748, 10324748, 1, "version_01a_block", "public_endpoint")
        ),
        skip_if_slow_tests_disabled(
            (12640760, 12640760, 1, "version_03_block", "public_endpoint")
        ),
        skip_if_slow_tests_disabled(
            (14473621, 14473621, 1, "version_04_block", "public_endpoint")
        ),
        skip_if_slow_tests_disabled(
            (14473622, 14473622, 1, "version_05_block", "public_endpoint")
        ),
    ],
)
def test_export_blocks_job(
    tmpdir, start_block, end_block, batch_size, resource_group, web3_provider_type
):
    blocks_output_file = str(tmpdir.join("actual_blocks.csv"))
    transactions_output_file = str(tmpdir.join("actual_transactions.csv"))

    job = ExportBlocksJob(
        start_block=start_block,
        end_block=end_block,
        batch_size=batch_size,
        batch_web3_provider=ThreadLocalProxy(
            lambda: get_web3_provider(
                web3_provider_type,
                lambda file: read_resource(resource_group, file),
                batch=True,
            )
        ),
        max_workers=5,
        item_exporter=blocks_and_transactions_item_exporter(
            blocks_output_file, transactions_output_file
        ),
        export_blocks=blocks_output_file is not None,
        export_transactions=transactions_output_file is not None,
    )
    job.run()

    compare_lines_ignore_order(
        read_resource(resource_group, "expected_blocks.csv"),
        read_file(blocks_output_file),
    )

    compare_lines_ignore_order(
        read_resource(resource_group, "expected_transactions.csv"),
        read_file(transactions_output_file),
    )
