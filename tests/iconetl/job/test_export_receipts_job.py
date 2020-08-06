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
from iconetl.jobs.export_receipts_job import ExportReceiptsJob
from iconetl.jobs.exporters.receipts_and_logs_item_exporter import \
    receipts_and_logs_item_exporter
from tests.iconetl.job.utils import get_web3_provider
from tests.utils import (compare_lines_ignore_order, read_file,
                         skip_if_slow_tests_disabled)

RESOURCE_GROUP = "test_export_receipts_job"


def read_resource(resource_group, file_name):
    return tests.resources.read_resource([RESOURCE_GROUP, resource_group], file_name)


DEFAULT_TX_HASHES = [
    "0x3680f3262fed98a4bc169c11b6ac66778da43c889d47a673d252362138715da9",
    "0xaec1f999ec61c80e23701229a33ec3b471c073e721d0a4096f37f2e1ea6bfa19",
    "0x3ce26161a89e0747b87df969ce76af1c275237f0e95a7415cca8e578ed7372d7",
    "0xcd159d87e580c51a770017a813dd451bed6cbe587ff6c84bc43a95efe9ea7c61",
    "0xe87509d050cd172b1ca8129b3ba2028c5ff84b53684f56401d01d09934777039",
    "0x341884ab68c291df94ca9ce8e4948b06ed80652519f0a228b30ec7bda64d001c",
]

HTML_TX_HASHES = [
    "0x16dbc932b601821b08450ad6f228a6a8e1bfd9cf5a361f0bf42ccf4b0b29be7b",
    "0x1a94bf51895fc4112ccd17f17a382fbe2cc5c0f787595256c98e0669b572c52e",
]


@pytest.mark.parametrize(
    "batch_size,transaction_hashes,output_format,resource_group,web3_provider_type",
    [
        (1, DEFAULT_TX_HASHES, "csv", "receipts_with_logs", "mock"),
        (2, DEFAULT_TX_HASHES, "csv", "receipts_with_logs", "mock"),
        (2, DEFAULT_TX_HASHES, "json", "receipts_with_logs", "mock"),
        skip_if_slow_tests_disabled(
            (1, DEFAULT_TX_HASHES, "csv", "receipts_with_logs", "public_endpoint")
        ),
        skip_if_slow_tests_disabled(
            (2, DEFAULT_TX_HASHES, "json", "receipts_with_logs", "public_endpoint")
        ),
        (2, HTML_TX_HASHES, "csv", "html_sanitize", "mock"),
        (2, HTML_TX_HASHES, "json", "html_sanitize", "mock"),
        skip_if_slow_tests_disabled(
            (2, HTML_TX_HASHES, "csv", "html_sanitize", "mock")
        ),
    ],
)
def test_export_receipts_job(
    tmpdir,
    batch_size,
    transaction_hashes,
    output_format,
    resource_group,
    web3_provider_type,
):
    receipts_output_file = str(tmpdir.join("actual_receipts." + output_format))
    logs_output_file = str(tmpdir.join("actual_logs." + output_format))

    job = ExportReceiptsJob(
        transaction_hashes_iterable=transaction_hashes,
        batch_size=batch_size,
        batch_web3_provider=ThreadLocalProxy(
            lambda: get_web3_provider(
                web3_provider_type,
                lambda file: read_resource(resource_group, file),
                batch=True,
            )
        ),
        max_workers=5,
        item_exporter=receipts_and_logs_item_exporter(
            receipts_output_file, logs_output_file
        ),
        export_receipts=receipts_output_file is not None,
        export_logs=logs_output_file is not None,
    )
    job.run()

    compare_lines_ignore_order(
        read_resource(resource_group, "expected_receipts." + output_format),
        read_file(receipts_output_file),
    )

    compare_lines_ignore_order(
        read_resource(resource_group, "expected_logs." + output_format),
        read_file(logs_output_file),
    )
