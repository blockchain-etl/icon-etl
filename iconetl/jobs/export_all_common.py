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

import csv
import logging
import os
import shutil
from time import time

from blockchainetl_common.file_utils import smart_open
from blockchainetl_common.thread_local_proxy import ThreadLocalProxy

from iconetl.csv_utils import set_max_field_size_limit
from iconetl.jobs.export_blocks_job import ExportBlocksJob
from iconetl.jobs.export_receipts_job import ExportReceiptsJob
from iconetl.jobs.exporters.blocks_and_transactions_item_exporter import (
    blocks_and_transactions_item_exporter,
)
from iconetl.jobs.exporters.receipts_and_logs_item_exporter import (
    receipts_and_logs_item_exporter,
)
from iconetl.providers.auto import get_provider_from_uri

logger = logging.getLogger("export_all")


def extract_csv_column_unique(input, output, column):
    set_max_field_size_limit()

    with smart_open(input, "r") as input_file, smart_open(output, "w") as output_file:
        reader = csv.DictReader(input_file)
        seen = set()
        for row in reader:
            if row[column] in seen:
                continue
            seen.add(row[column])
            output_file.write(row[column] + "\n")


def export_all_common(partitions, output_dir, provider_uri, max_workers, batch_size):
    for batch_start_block, batch_end_block, partition_dir in partitions:

        start_time = time()

        padded_batch_start_block = str(batch_start_block).zfill(8)
        padded_batch_end_block = str(batch_end_block).zfill(8)
        block_range = "{padded_batch_start_block}-{padded_batch_end_block}".format(
            padded_batch_start_block=padded_batch_start_block,
            padded_batch_end_block=padded_batch_end_block,
        )
        file_name_suffix = "{padded_batch_start_block}_{padded_batch_end_block}".format(
            padded_batch_start_block=padded_batch_start_block,
            padded_batch_end_block=padded_batch_end_block,
        )

        blocks_output_dir = "{output_dir}/blocks{partition_dir}".format(
            output_dir=output_dir, partition_dir=partition_dir,
        )
        os.makedirs(os.path.dirname(blocks_output_dir), exist_ok=True)

        transactions_output_dir = "{output_dir}/transactions{partition_dir}".format(
            output_dir=output_dir, partition_dir=partition_dir,
        )
        os.makedirs(os.path.dirname(transactions_output_dir), exist_ok=True)

        blocks_file = "{blocks_output_dir}/blocks_{file_name_suffix}.csv".format(
            blocks_output_dir=blocks_output_dir, file_name_suffix=file_name_suffix,
        )
        transactions_file = "{transactions_output_dir}/transactions_{file_name_suffix}.csv".format(
            transactions_output_dir=transactions_output_dir,
            file_name_suffix=file_name_suffix,
        )
        logger.info(
            "Exporting blocks {block_range} to {blocks_file}".format(
                block_range=block_range, blocks_file=blocks_file,
            )
        )
        logger.info(
            "Exporting transactions from blocks {block_range} to {transactions_file}".format(
                block_range=block_range, transactions_file=transactions_file,
            )
        )

        job = ExportBlocksJob(
            start_block=batch_start_block,
            end_block=batch_end_block,
            batch_size=batch_size,
            batch_web3_provider=ThreadLocalProxy(
                lambda: get_provider_from_uri(provider_uri, batch=True)
            ),
            max_workers=max_workers,
            item_exporter=blocks_and_transactions_item_exporter(
                blocks_file, transactions_file
            ),
            export_blocks=blocks_file is not None,
            export_transactions=transactions_file is not None,
        )
        job.run()

        cache_output_dir = "{output_dir}/.tmp{partition_dir}".format(
            output_dir=output_dir, partition_dir=partition_dir,
        )
        os.makedirs(os.path.dirname(cache_output_dir), exist_ok=True)

        transaction_hashes_file = "{cache_output_dir}/transaction_hashes_{file_name_suffix}.csv".format(
            cache_output_dir=cache_output_dir, file_name_suffix=file_name_suffix,
        )
        logger.info(
            "Extracting hash column from transaction file {transactions_file}".format(
                transactions_file=transactions_file,
            )
        )
        extract_csv_column_unique(transactions_file, transaction_hashes_file, "hash")

        receipts_output_dir = "{output_dir}/receipts{partition_dir}".format(
            output_dir=output_dir, partition_dir=partition_dir,
        )
        os.makedirs(os.path.dirname(receipts_output_dir), exist_ok=True)

        logs_output_dir = "{output_dir}/logs{partition_dir}".format(
            output_dir=output_dir, partition_dir=partition_dir,
        )
        os.makedirs(os.path.dirname(logs_output_dir), exist_ok=True)

        receipts_file = "{receipts_output_dir}/receipts_{file_name_suffix}.csv".format(
            receipts_output_dir=receipts_output_dir, file_name_suffix=file_name_suffix,
        )
        logs_file = "{logs_output_dir}/logs_{file_name_suffix}.csv".format(
            logs_output_dir=logs_output_dir, file_name_suffix=file_name_suffix,
        )
        logger.info(
            "Exporting receipts and logs from blocks {block_range} to {receipts_file} and {logs_file}".format(
                block_range=block_range,
                receipts_file=receipts_file,
                logs_file=logs_file,
            )
        )

        with smart_open(transaction_hashes_file, "r") as transaction_hashes:
            job = ExportReceiptsJob(
                transaction_hashes_iterable=(
                    transaction_hash.strip() for transaction_hash in transaction_hashes
                ),
                batch_size=batch_size,
                batch_web3_provider=ThreadLocalProxy(
                    lambda: get_provider_from_uri(provider_uri, batch=True)
                ),
                max_workers=max_workers,
                item_exporter=receipts_and_logs_item_exporter(receipts_file, logs_file),
                export_receipts=receipts_file is not None,
                export_logs=logs_file is not None,
            )
            job.run()

        shutil.rmtree(os.path.dirname(cache_output_dir))
        end_time = time()
        time_diff = round(end_time - start_time, 5)
        logger.info(
            "Exporting blocks {block_range} took {time_diff} seconds".format(
                block_range=block_range, time_diff=time_diff,
            )
        )
