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

#  MIT License
#
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of
#  this software and associated documentation files (the "Software"), to deal in
#  the Software without restriction, including without limitation the rights to
#  use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
#  the Software, and to permit persons to whom the Software is furnished to do so,
#  subject to the following conditions:
#
#
import collections
from json import dumps

from confluent_kafka.serialization import MessageField, SerializationContext
from google.protobuf.json_format import MessageToJson

from iconetl.schemas.protobuf_compiled import blocks_raw_pb2 as blocks_raw
from iconetl.schemas.protobuf_compiled import logs_raw_pb2 as logs_raw
from iconetl.schemas.protobuf_compiled import transactions_raw_pb2 as transactions_raw
from iconetl.utils import dec_to_hex


class KafkaItemExporter:
    def __init__(
        self,
        producer,
        item_type_to_topic_mapping,
        serializers,
    ):
        self.producer = producer
        self.item_type_to_topic_mapping = item_type_to_topic_mapping
        self.serializers = serializers

    def open(self):
        pass

    def export_items(self, items):
        items_grouped_by_type = group_by_item_type(items)

        for item_type, topic in self.item_type_to_topic_mapping.items():
            item_group = items_grouped_by_type.get(item_type)

            if item_group:
                serialization_context = SerializationContext(topic, MessageField.VALUE)
                for item in item_group:
                    headers = []
                    if item["type"] == "block":
                        # Configure header & key
                        key = bytes(str(item["number"]), "utf-8")
                        headers.append(("hash", bytes(item["hash"], "utf-8")))
                        # Create blocks_raw object
                        value_object = blocks_raw.blocks_raw(
                            type=str(item["type"]),
                            number=item["number"],
                            hash=str(item["hash"]),
                            parent_hash=str(item["parent_hash"]),
                            merkle_root_hash=str(item["merkle_root_hash"]),
                            timestamp=item["timestamp"],
                            version=str(item["version"]),
                            transaction_count=item["transaction_count"],
                            peer_id=str(item["peer_id"]),
                            signature=str(item["signature"]),
                            next_leader=str(item["next_leader"]),
                            item_id=str(item["item_id"]),
                            item_timestamp="",
                        )
                    elif item["type"] == "log":
                        # Configure header & key
                        key = bytes(item["address"], "utf-8")
                        headers.append(
                            ("hash", bytes(item["transaction_hash"], "utf-8"))
                        )
                        # Create logs_raw object
                        value_object = logs_raw.logs_raw(
                            type=str(item["type"]),
                            log_index=item["log_index"],
                            transaction_hash=str(item["transaction_hash"]),
                            transaction_index=item["transaction_index"],
                            address=str(item["address"]),
                            data=dumps(item["data"]),
                            indexed=dumps(item["indexed"]),
                            block_number=item["block_number"],
                            block_timestamp=item["block_timestamp"],
                            block_hash=str(item["block_hash"]),
                            item_id=str(item["item_id"]),
                            item_timestamp="",
                        )
                    else:
                        # Configure header & key
                        headers.append(("hash", bytes(item["hash"], "utf-8")))
                        if item["to_address"]:
                            headers.append(("to", bytes(item["to_address"], "utf-8")))
                            key = bytes(item["to_address"], "utf-8")
                        else:
                            headers.append(("to", bytes("None", "utf-8")))
                            key = bytes("None", "utf-8")
                        if item["from_address"]:
                            headers.append(
                                ("from", bytes(item["from_address"], "utf-8"))
                            )
                        else:
                            headers.append(("from", bytes("None", "utf-8")))
                        value_object = transactions_raw.transactions_raw(
                            type=str(item["type"]),
                            version=str(item["version"]),
                            from_address=str(item["from_address"]),
                            to_address=str(item["to_address"]),
                            value=dec_to_hex(item["value"]),
                            step_limit=item["step_limit"],
                            timestamp=str(item["timestamp"]),
                            block_timestamp=item["block_timestamp"],
                            nid=item["nid"],
                            nonce=item["nonce"],
                            hash=str(item["hash"]),
                            transaction_index=item["transaction_index"],
                            block_hash=str(item["block_hash"]),
                            block_number=item["block_number"],
                            fee=item["fee"],
                            signature=str(item["signature"]),
                            data_type=str(item["data_type"]),
                            data=dumps(item["data"]),
                            receipt_cumulative_step_used=item[
                                "receipt_cumulative_step_used"
                            ],
                            receipt_step_used=item["receipt_step_used"],
                            receipt_step_price=item["receipt_step_price"],
                            receipt_score_address=str(item["receipt_score_address"]),
                            receipt_logs=str(item["receipt_logs"]),
                            receipt_status=item["receipt_status"],
                            item_id=str(item["item_id"]),
                            item_timestamp=str(item["item_timestamp"]),
                        )

                    if self.serializers:
                        self.producer.produce(
                            topic=topic,
                            value=self.serializers[item_type](
                                value_object, serialization_context
                            ),
                            key=key,
                            headers=headers,
                        )
                    else:
                        self.producer.produce(
                            topic,
                            value=MessageToJson(value_object),
                            key=key,
                            headers=headers,
                        )
                    self.producer.poll(0)

                self.producer.flush()

    def convert_items(self, items):
        pass

    def close(self):
        pass


def group_by_item_type(items):
    result = collections.defaultdict(list)
    for item in items:
        result[item.get("type")].append(item)

    return result
