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

import json
import logging

from blockchainetl_common.jobs.exporters.console_item_exporter import (
    ConsoleItemExporter,
)
from blockchainetl_common.jobs.exporters.in_memory_item_exporter import (
    InMemoryItemExporter,
)
from blockchainetl_common.thread_local_proxy import ThreadLocalProxy

from iconetl.enumeration.entity_type import EntityType
from iconetl.jobs.export_blocks_job import ExportBlocksJob
from iconetl.jobs.export_receipts_job import ExportReceiptsJob
from iconetl.json_rpc_requests import generate_json_rpc
from iconetl.streaming.enrich import enrich_logs, enrich_transactions
from iconetl.streaming.icx_item_id_calculator import IcxItemIdCalculator
from iconetl.streaming.icx_item_timestamp_calculator import IcxItemTimestampCalculator
from iconetl.utils import rpc_response_batch_to_results


class IcxStreamerAdapter:
    def __init__(
        self,
        batch_web3_provider,
        item_exporter=ConsoleItemExporter(),
        batch_size=100,
        max_workers=5,
        entity_types=tuple(EntityType.ALL_FOR_STREAMING),
    ):
        self.batch_web3_provider = batch_web3_provider
        self.item_exporter = item_exporter
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.entity_types = entity_types
        self.item_id_calculator = IcxItemIdCalculator()
        self.item_timestamp_calculator = IcxItemTimestampCalculator()

    def open(self):
        self.item_exporter.open()

    def get_current_block_number(self):
        blocks_rpc = generate_json_rpc("icx_getLastBlock", {}, 1)
        response = self.batch_web3_provider.make_batch_request(json.dumps(blocks_rpc))
        return response["result"]["height"]

    def export_all(self, start_block, end_block):
        # Export blocks and transactions
        blocks, transactions = [], []
        if self._should_export(EntityType.BLOCK) or self._should_export(
            EntityType.TRANSACTION
        ):
            blocks, transactions = self._export_blocks_and_transactions(
                start_block, end_block
            )

        # Export receipts and logs
        receipts, logs = [], []
        if self._should_export(EntityType.RECEIPT) or self._should_export(
            EntityType.LOG
        ):
            receipts, logs = self._export_receipts_and_logs(transactions)

        enriched_blocks = blocks if EntityType.BLOCK in self.entity_types else []
        enriched_transactions = (
            enrich_transactions(transactions, receipts)
            if EntityType.TRANSACTION in self.entity_types
            else []
        )
        enriched_logs = (
            enrich_logs(blocks, logs, transactions)
            if EntityType.LOG in self.entity_types
            else []
        )

        logging.info("Exporting with " + type(self.item_exporter).__name__)

        all_items = enriched_blocks + enriched_transactions + enriched_logs

        self.calculate_item_ids(all_items)
        self.calculate_item_timestamps(all_items)

        self.item_exporter.export_items(all_items)

    def _export_blocks_and_transactions(self, start_block, end_block):
        blocks_and_transactions_item_exporter = InMemoryItemExporter(
            item_types=["block", "transaction"]
        )
        blocks_and_transactions_job = ExportBlocksJob(
            start_block=start_block,
            end_block=end_block,
            batch_size=self.batch_size,
            batch_web3_provider=self.batch_web3_provider,
            max_workers=self.max_workers,
            item_exporter=blocks_and_transactions_item_exporter,
            export_blocks=self._should_export(EntityType.BLOCK),
            export_transactions=self._should_export(EntityType.TRANSACTION),
        )
        blocks_and_transactions_job.run()
        blocks = blocks_and_transactions_item_exporter.get_items("block")
        transactions = blocks_and_transactions_item_exporter.get_items("transaction")
        return blocks, transactions

    def _export_receipts_and_logs(self, transactions):
        exporter = InMemoryItemExporter(item_types=["receipt", "log"])
        job = ExportReceiptsJob(
            transaction_hashes_iterable=(
                transaction["hash"] for transaction in transactions
            ),
            batch_size=self.batch_size,
            batch_web3_provider=self.batch_web3_provider,
            max_workers=self.max_workers,
            item_exporter=exporter,
            export_receipts=self._should_export(EntityType.RECEIPT),
            export_logs=self._should_export(EntityType.LOG),
        )
        job.run()
        receipts = exporter.get_items("receipt")
        logs = exporter.get_items("log")
        return receipts, logs

    def _should_export(self, entity_type):
        if entity_type == EntityType.BLOCK:
            return True

        if entity_type == EntityType.TRANSACTION:
            return EntityType.TRANSACTION in self.entity_types or self._should_export(
                EntityType.LOG
            )

        if entity_type == EntityType.RECEIPT:
            return EntityType.TRANSACTION in self.entity_types

        if entity_type == EntityType.LOG:
            return EntityType.LOG in self.entity_types

        raise ValueError("Unexpected entity type " + entity_type)

    def calculate_item_ids(self, items):
        for item in items:
            item["item_id"] = self.item_id_calculator.calculate(item)

    def calculate_item_timestamps(self, items):
        for item in items:
            item["item_timestamp"] = self.item_timestamp_calculator.calculate(item)

    def close(self):
        self.item_exporter.close()
