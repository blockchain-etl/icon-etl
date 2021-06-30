all: blocks_raw transactions_raw logs_raw

blocks_raw: blocks_raw.proto
	protoc -I=. --python_out=../protobuf_compiled/ ./blocks_raw.proto;

transactions_raw: blocks_raw.proto
	protoc -I=. --python_out=../protobuf_compiled/ ./transactions_raw.proto;

logs_raw: blocks_raw.proto
	protoc -I=. --python_out=../protobuf_compiled/. ./logs_raw.proto;
