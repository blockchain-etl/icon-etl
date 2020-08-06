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


from iconetl.domain.receipt import IcxReceipt
from iconetl.mappers.receipt_log_mapper import IcxReceiptLogMapper
from iconetl.utils import hex_to_dec, to_normalized_address


class IcxReceiptMapper(object):
    def __init__(self, receipt_log_mapper=None):
        if receipt_log_mapper is None:
            self.receipt_log_mapper = IcxReceiptLogMapper()
        else:
            self.receipt_log_mapper = receipt_log_mapper

    def json_dict_to_receipt(self, json_dict):
        receipt = IcxReceipt()

        receipt.transaction_hash = json_dict.get("txHash")
        receipt.transaction_index = hex_to_dec(json_dict.get("txIndex"))
        receipt.block_hash = json_dict.get("blockHash")
        receipt.block_number = hex_to_dec(json_dict.get("blockHeight"))
        receipt.cumulative_step_used = hex_to_dec(json_dict.get("cumulativeStepUsed"))
        receipt.step_used = hex_to_dec(json_dict.get("stepUsed"))
        receipt.step_price = hex_to_dec(json_dict.get("stepPrice"))
        receipt.score_address = to_normalized_address(json_dict.get("scoreAddress"))
        receipt.status = hex_to_dec(json_dict.get("status"))

        if "eventLogs" in json_dict:
            receipt.logs = [
                self.receipt_log_mapper.json_dict_to_receipt_log(
                    log,
                    idx,
                    receipt.transaction_hash,
                    receipt.transaction_index,
                    receipt.block_hash,
                    receipt.block_number,
                )
                for idx, log in enumerate(json_dict["eventLogs"])
            ]

        return receipt

    def receipt_to_dict(self, receipt):
        return {
            "type": "receipt",
            "transaction_hash": receipt.transaction_hash,
            "transaction_index": receipt.transaction_index,
            "block_hash": receipt.block_hash,
            "block_number": receipt.block_number,
            "cumulative_step_used": receipt.cumulative_step_used,
            "step_used": receipt.step_used,
            "step_price": receipt.step_price,
            "score_address": receipt.score_address,
            "status": receipt.status,
        }
