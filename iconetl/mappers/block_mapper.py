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


from iconetl.domain.block import IcxBlock
from iconetl.mappers.transaction_mapper import IcxTransactionMapper
from iconetl.utils import hex_to_dec


class IcxBlockMapper(object):
    def __init__(self, transaction_mapper=None):
        if transaction_mapper is None:
            self.transaction_mapper = IcxTransactionMapper()
        else:
            self.transaction_mapper = transaction_mapper

    def json_dict_to_block(self, json_dict):
        block = IcxBlock()

        block.number = json_dict.get("height")
        block.hash = json_dict.get("block_hash")
        block.parent_hash = json_dict.get("prev_block_hash")
        block.merkle_root_hash = json_dict.get("merkle_tree_root_hash")
        block.timestamp = json_dict.get("time_stamp")
        block.version = json_dict.get("version")
        block.peer_id = json_dict.get("peer_id")
        block.signature = json_dict.get("signature")
        block.next_leader = json_dict.get("next_leader")

        if "confirmed_transaction_list" in json_dict:
            block.transactions = [
                self.transaction_mapper.json_dict_to_transaction(
                    tx, idx, block.hash, block.number, block.timestamp
                )
                for idx, tx in enumerate(json_dict["confirmed_transaction_list"])
                if isinstance(tx, dict)
            ]

        return block

    def block_to_dict(self, block):
        return {
            "type": "block",
            "number": block.number,
            "hash": block.hash,
            "parent_hash": block.parent_hash,
            "merkle_root_hash": block.merkle_root_hash,
            "timestamp": block.timestamp,
            "version": block.version,
            "transactions": block.transactions,
            "peer_id": block.peer_id,
            "signature": block.signature,
            "next_leader": block.next_leader,
        }
