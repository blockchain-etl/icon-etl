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

from iconetl.utils import dec_to_hex


class KafkaItemExporter:
    def __init__(
        self,
        producer,
        item_type_to_topic_mapping,
        serializers,
        values_as_hex,
    ):
        self.producer = producer
        self.item_type_to_topic_mapping = item_type_to_topic_mapping
        self.serializers = serializers
        self.values_as_hex = values_as_hex

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
                        key = bytes(str(item["number"]), "utf-8")
                        headers.append(("hash", bytes(item["hash"], "utf-8")))

                    elif item["type"] == "log":
                        key = bytes(item["address"], "utf-8")
                        headers.append(
                            ("hash", bytes(item["transaction_hash"], "utf-8"))
                        )

                    else:
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

                    if item["type"] == "transaction" and self.values_as_hex:
                        item["value"] = dec_to_hex(item["value"])
                        item["step_limit"] = dec_to_hex(item["step_limit"])
                        item["fee"] = dec_to_hex(item["fee"])
                        item["receipt_cumulative_step_used"] = dec_to_hex(
                            item["receipt_cumulative_step_used"]
                        )
                        item["receipt_step_used"] = dec_to_hex(
                            item["receipt_step_used"]
                        )
                        item["receipt_step_price"] = dec_to_hex(
                            item["receipt_step_price"]
                        )

                    if self.serializers:
                        self.producer.produce(
                            topic=topic,
                            value=self.serializers[item_type](
                                item, serialization_context
                            ),
                            key=key,
                            headers=headers,
                        )
                    else:
                        self.producer.produce(
                            topic,
                            value=dumps(item),
                            key=key,
                            headers=headers,
                        )

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
