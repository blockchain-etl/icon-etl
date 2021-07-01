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

from sqlalchemy import (
    TIMESTAMP,
    BigInteger,
    Column,
    Integer,
    MetaData,
    Numeric,
    String,
    Table,
)

metadata = MetaData()

BLOCKS = Table(
    "blocks",
    metadata,
    Column("number", BigInteger, primary_key=True),
    Column("hash", String),
    Column("parent_hash", String),
    Column("merkle_root_hash", String),
    Column("timestamp", TIMESTAMP),
    Column("version", String),
    Column("peer_id", String),
    Column("signature", String),
    Column("next_leader", String),
)

TRANSACTIONS = Table(
    "transactions",
    metadata,
    Column("version", String),
    Column("from_address", String),
    Column("to_address", String),
    Column("value", Numeric(38, 0, asdecimal=True)),
    Column("step_limit", Numeric(38, 0, asdecimal=True)),
    Column("timestamp", TIMESTAMP),
    Column("block_timestamp", TIMESTAMP),
    Column("nid", Integer),
    Column("nonce", Numeric(100, 0, asdecimal=False)),
    Column("hash", String, primary_key=True),
    Column("transaction_index", BigInteger),
    Column("block_hash", String),
    Column("block_number", BigInteger),
    Column("fee", Numeric(38, 0, asdecimal=True)),
    Column("signature", String),
    Column("data_type", String),
    Column("data", String),
    Column("receipt_cumulative_step_used", Numeric(38, 0, asdecimal=True)),
    Column("receipt_step_used", Numeric(38, 0, asdecimal=True)),
    Column("receipt_step_price", Numeric(38, 0, asdecimal=True)),
    Column("receipt_score_address", String),
    Column("receipt_status", String),
)

LOGS = Table(
    "logs",
    metadata,
    Column("log_index", Integer, primary_key=True),
    Column("transaction_hash", String, primary_key=True),
    Column("transaction_index", Integer, primary_key=True),
    Column("address", String),
    Column("data", String),
    Column("indexed", String),
    Column("block_number", Integer),
    Column("block_timestamp", TIMESTAMP),
    Column("block_hash", String),
)
