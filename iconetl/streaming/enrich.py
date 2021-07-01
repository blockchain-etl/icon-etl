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


import itertools
from collections import defaultdict


def join(left, right, join_fields, left_fields, right_fields):
    left_join_field, right_join_field = join_fields

    def field_list_to_dict(field_list):
        result_dict = {}
        for field in field_list:
            if isinstance(field, tuple):
                result_dict[field[0]] = field[1]
            else:
                result_dict[field] = field
        return result_dict

    left_fields_as_dict = field_list_to_dict(left_fields)
    right_fields_as_dict = field_list_to_dict(right_fields)

    left_map = defaultdict(list)
    for item in left:
        left_map[item[left_join_field]].append(item)

    right_map = defaultdict(list)
    for item in right:
        right_map[item[right_join_field]].append(item)

    for key in left_map.keys():
        for left_item, right_item in itertools.product(left_map[key], right_map[key]):
            result_item = {}
            for src_field, dst_field in left_fields_as_dict.items():
                result_item[dst_field] = left_item.get(src_field)
            for src_field, dst_field in right_fields_as_dict.items():
                result_item[dst_field] = right_item.get(src_field)

            yield result_item


def enrich_transactions(transactions, receipts):
    result = list(
        join(
            transactions,
            receipts,
            ("hash", "transaction_hash"),
            left_fields=[
                "type",
                "version",
                "from_address",
                "to_address",
                "value",
                "step_limit",
                "timestamp",
                "block_timestamp",
                "nid",
                "nonce",
                "hash",
                "transaction_index",
                "block_hash",
                "block_number",
                "fee",
                "signature",
                "data_type",
                "data",
            ],
            right_fields=[
                ("cumulative_step_used", "receipt_cumulative_step_used"),
                ("step_used", "receipt_step_used"),
                ("step_price", "receipt_step_price"),
                ("score_address", "receipt_score_address"),
                ("logs", "receipt_logs"),
                ("status", "receipt_status"),
            ],
        )
    )

    if len(result) != len(transactions):
        raise ValueError("The number of transactions is wrong " + str(result))

    return result


def enrich_logs(blocks, logs, transactions):
    result = list(
        join(
            join(
                logs,
                blocks,
                ("block_number", "number"),
                [
                    "type",
                    "log_index",
                    "transaction_hash",
                    "transaction_index",
                    "address",
                    "data",
                    "indexed",
                    "block_number",
                ],
                [
                    ("timestamp", "block_timestamp"),
                    ("hash", "block_hash"),
                ],
            ),
            transactions,
            ("transaction_hash", "hash"),
            [
                "type",
                "log_index",
                "transaction_hash",
                "transaction_index",
                "address",
                "data",
                "indexed",
                "block_number",
                "block_timestamp",
                "block_hash",
            ],
            ["from_address"],
        )
    )

    if len(result) != len(logs):
        raise ValueError("The number of logs is wrong " + str(result))

    return result
