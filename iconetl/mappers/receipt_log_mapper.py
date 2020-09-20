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

from iconetl.domain.receipt_log import IcxReceiptLog


class IcxReceiptLogMapper(object):
    def json_dict_to_receipt_log(
        self, json_dict, log_idx, tx_hash, tx_idx, blk_hash, blk_num
    ):
        receipt_log = IcxReceiptLog()

        receipt_log.log_index = log_idx
        receipt_log.transaction_hash = tx_hash
        receipt_log.transaction_index = tx_idx
        receipt_log.block_hash = blk_hash
        receipt_log.block_number = blk_num
        receipt_log.address = json_dict.get("scoreAddress")
        unsanitized_data = json_dict.get("data")
        sanitized_data = []
        for item in unsanitized_data:
            if item:
                sanitized_data.append(item.replace("\n", "").replace('"', "'"))
        receipt_log.data = sanitized_data
        receipt_log.indexed = json_dict.get("indexed")

        return receipt_log

    def receipt_log_to_dict(self, receipt_log):
        return {
            "type": "log",
            "log_index": receipt_log.log_index,
            "transaction_hash": receipt_log.transaction_hash,
            "transaction_index": receipt_log.transaction_index,
            "block_hash": receipt_log.block_hash,
            "block_number": receipt_log.block_number,
            "address": receipt_log.address,
            "data": receipt_log.data,
            "indexed": receipt_log.indexed,
        }

    def dict_to_receipt_log(self, dict):
        receipt_log = IcxReceiptLog()

        receipt_log.log_index = dict.get("log_index")
        receipt_log.transaction_hash = dict.get("transaction_hash")
        receipt_log.transaction_index = dict.get("transaction_index")
        receipt_log.block_hash = dict.get("block_hash")
        receipt_log.block_number = dict.get("block_number")
        receipt_log.address = dict.get("address")
        receipt_log.data = dict.get("data")
        receipt_log.indexed = dict.get("indexed")

        return receipt_log
