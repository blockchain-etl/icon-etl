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

from json import dumps

from confluent_kafka.admin import NewTopic
from confluent_kafka.schema_registry import Schema
from confluent_kafka.schema_registry.error import SchemaRegistryError

schemas = {
    "block": {
        "type": "object",
        "properties": {
            "type": {"type": "string"},
            "number": {"type": "integer"},
            "hash": {"type": "string"},
            "parent_hash": {"type": "string"},
            "merkle_root_hash": {"type": "string"},
            "timestamp": {"type": "integer"},
            "version": {"type": "string"},
            "transaction_count": {"type": "integer"},
            "peer_id": {"type": "string"},
            "signature": {"type": ["string", "null"]},
            "next_leader": {"type": ["string", "null"]},
            "item_id": {"type": "string"},
            "item_timestamp": {"type": "string"},
        },
    },
    "transaction_int": {
        "type": "object",
        "properties": {
            "type": {"type": "string"},
            "version": {"type": ["string", "null"]},
            "from_address": {"type": ["string", "null"]},
            "to_address": {"type": ["string", "null"]},
            "value": {"type": ["integer", "null"]},
            "step_limit": {"type": ["integer", "null"]},
            "timestamp": {"type": "string"},
            "block_timestamp": {"type": "integer"},
            "nid": {"type": ["integer", "null"]},
            "nonce": {"type": ["integer", "null"]},
            "hash": {"type": "string"},
            "transaction_index": {"type": "integer"},
            "block_hash": {"type": "string"},
            "block_number": {"type": "integer"},
            "fee": {"type": ["integer", "null"]},
            "signature": {"type": ["string", "null"]},
            "data_type": {"type": ["string", "null"]},
            "data": {"type": ["object", "string", "null"]},
            "receipt_cumulative_step_used": {
                "type": ["integer", "null"],
            },
            "receipt_step_used": {"type": ["integer", "null"]},
            "receipt_step_price": {"type": ["integer", "null"]},
            "receipt_score_address": {"type": ["string", "null"]},
            "receipt_logs": {"type": ["string", "null"]},
            "receipt_status": {"type": "integer"},
            "item_id": {"type": "string"},
            "item_timestamp": {"type": "string"},
        },
    },
    "transaction_hex": {
        "type": "object",
        "properties": {
            "type": {"type": "string"},
            "version": {"type": ["string", "null"]},
            "from_address": {"type": ["string", "null"]},
            "to_address": {"type": ["string", "null"]},
            "value": {"type": ["string", "null"]},
            "step_limit": {"type": ["string", "null"]},
            "timestamp": {"type": "string"},
            "block_timestamp": {"type": "integer"},
            "nid": {"type": ["integer", "null"]},
            "nonce": {"type": ["integer", "null"]},
            "hash": {"type": "string"},
            "transaction_index": {"type": "integer"},
            "block_hash": {"type": "string"},
            "block_number": {"type": "integer"},
            "fee": {"type": ["string", "null"]},
            "signature": {"type": ["string", "null"]},
            "data_type": {"type": ["string", "null"]},
            "data": {"type": ["object", "string", "null"]},
            "receipt_cumulative_step_used": {
                "type": ["string", "null"],
            },
            "receipt_step_used": {"type": ["string", "null"]},
            "receipt_step_price": {"type": ["string", "null"]},
            "receipt_score_address": {"type": ["string", "null"]},
            "receipt_logs": {"type": ["string", "null"]},
            "receipt_status": {"type": "integer"},
            "item_id": {"type": "string"},
            "item_timestamp": {"type": "string"},
        },
    },
    "log": {
        "type": "object",
        "properties": {
            "type": {"type": "string"},
            "log_index": {"type": "integer"},
            "transaction_hash": {"type": "string"},
            "transaction_index": {"type": "integer"},
            "address": {"type": "string"},
            "data": {
                "type": ["array", "null"],
                "items": {"type": "string"},
            },
            "indexed": {
                "type": ["array", "null"],
                "items": {"type": "string"},
            },
            "block_number": {"type": "integer"},
            "block_timestamp": {"type": "integer"},
            "block_hash": {"type": "string"},
            "item_id": {"type": "string"},
            "item_timestamp": {"type": "string"},
        },
    },
}


def topic_exist(admin_client, topic):

    res = admin_client.create_topics([NewTopic(topic, 1, 1)], validate_only=True)

    # no exception returned, connection is fine, topic DNE
    if not res[topic].exception():
        return False

    # exception returned, topic exists
    if res[topic].exception().args[0].code() == 36:
        return True


def create_topic(admin_client, topic):
    admin_client.create_topics([NewTopic(topic, 1, 1)])


def schema_exist(registry_client, topic_name, topic_type):
    try:
        registry_client.lookup_schema(
            topic_name + "-value",
            Schema(get_schema(topic_name, topic_type), schema_type="JSON"),
        )
    except SchemaRegistryError as e:
        if e.error_code == 40403 or e.error_code == 40401:
            return False
        else:
            raise

    return True


def register_schema(registry_client, topic_name, topic_type):
    schema = Schema(get_schema(topic_name, topic_type), schema_type="JSON")
    return registry_client.register_schema(topic_name + "-value", schema)


def get_schema(topic_name, topic_type):
    schema = schemas[topic_type]
    schema["title"] = topic_name + "-value"
    return dumps(schema)
