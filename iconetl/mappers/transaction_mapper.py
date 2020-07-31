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


from iconetl.domain.transaction import IcxTransaction
from iconetl.utils import fix_tx_hash, hex_to_dec


class IcxTransactionMapper(object):
    def json_dict_to_transaction(
        self, json_dict, idx, block_hash, block_number, block_timestamp
    ):
        transaction = IcxTransaction()

        transaction.version = json_dict.get("version")
        transaction.from_address = json_dict.get("from")
        transaction.to_address = json_dict.get("to")
        transaction.value = hex_to_dec(json_dict.get("value", 0))
        transaction.step_limit = hex_to_dec(json_dict.get("stepLimit"))
        transaction.timestamp = json_dict.get("timestamp")
        transaction.nid = hex_to_dec(json_dict.get("nid"))
        transaction.nonce = hex_to_dec(json_dict.get("nonce"))
        if "txHash" in json_dict:
            transaction.hash = fix_tx_hash(json_dict.get("txHash"))

        if "tx_hash" in json_dict:
            transaction.hash = fix_tx_hash(json_dict.get("tx_hash"))

        if json_dict.get("txIndex"):
            transaction.transaction_index = hex_to_dec(json_dict.get("txIndex"))
        else:
            transaction.transaction_index = idx

        transaction.block_hash = block_hash
        transaction.block_number = block_number
        transaction.block_timestamp = block_timestamp
        transaction.fee = hex_to_dec(json_dict.get("fee"))
        transaction.signature = json_dict.get("signature")
        transaction.data_type = json_dict.get("dataType")
        transaction.data = json_dict.get("data")

        return transaction

    def transaction_to_dict(self, transaction):
        return {
            "type": "transaction",
            "version": transaction.version,
            "from_address": transaction.from_address,
            "to_address": transaction.to_address,
            "value": transaction.value,
            "step_limit": transaction.step_limit,
            "timestamp": transaction.timestamp,
            "block_timestamp": transaction.block_timestamp,
            "nid": transaction.nid,
            "nonce": transaction.nonce,
            "hash": transaction.hash,
            "transaction_index": transaction.transaction_index,
            "block_hash": transaction.block_hash,
            "block_number": transaction.block_number,
            "fee": transaction.fee,
            "signature": transaction.signature,
            "data_type": transaction.data_type,
            "data": transaction.data,
        }
