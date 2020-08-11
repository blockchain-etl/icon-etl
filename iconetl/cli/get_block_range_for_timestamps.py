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
from blockchainetl_common.file_utils import smart_open
from blockchainetl_common.logging_utils import logging_basic_config
from iconetl.providers.auto import get_provider_from_uri
from iconetl.service.icx_service import IcxService
from iconsdk.icon_service import IconService
from iconsdk.providers.http_provider import HTTPProvider

logging_basic_config()


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.option(
    "-p",
    "--provider-uri",
    default="https://ctz.solidwallet.io/api/v3",
    show_default=True,
    type=str,
    help="The URI of the node endpoint",
)
@click.option(
    "-s",
    "--start-timestamp",
    required=True,
    type=int,
    help="Start unix timestamp, in seconds.",
)
@click.option(
    "-e",
    "--end-timestamp",
    required=True,
    type=int,
    help="End unix timestamp, in seconds.",
)
@click.option(
    "-o",
    "--output",
    default="-",
    type=str,
    help="The output file. If not specified stdout is used.",
)
def get_block_range_for_timestamps(
    provider_uri, start_timestamp, end_timestamp, output
):
    """Outputs start and end blocks for given timestamps."""
    provider = get_provider_from_uri(provider_uri)
    svc = IconService(HTTPProvider(provider))
    icx_service = IcxService(svc)

    start_block, end_block = icx_service.get_block_range_for_timestamps(
        start_timestamp, end_timestamp
    )

    with smart_open(output, "w") as output_file:
        output_file.write("{},{}\n".format(start_block, end_block))
