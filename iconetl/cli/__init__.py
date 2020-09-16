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


import click

from iconetl.cli.export_blocks_and_transactions import export_blocks_and_transactions
from iconetl.cli.export_receipts_and_logs import export_receipts_and_logs
from iconetl.cli.extract_csv_column import extract_csv_column
from iconetl.cli.get_block_range_for_date import get_block_range_for_date
from iconetl.cli.get_block_range_for_timestamps import get_block_range_for_timestamps


@click.group()
@click.version_option(version="0.0.1-beta.5")
@click.pass_context
def cli(ctx):
    pass


cli.add_command(export_receipts_and_logs, "export_receipts_and_logs")
cli.add_command(export_blocks_and_transactions, "export_blocks_and_transactions")

cli.add_command(get_block_range_for_date, "get_block_range_for_date")
cli.add_command(get_block_range_for_timestamps, "get_block_range_for_timestamps")
cli.add_command(extract_csv_column, "extract_csv_column")
