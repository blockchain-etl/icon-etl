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


import pytest
from dateutil.parser import parse
from iconetl.service.graph_operations import OutOfBoundsError
from iconetl.service.icx_service import IcxService
from iconsdk.icon_service import IconService
from iconsdk.providers.http_provider import HTTPProvider
from tests.utils import skip_if_slow_tests_disabled


@pytest.mark.parametrize(
    "date,expected_start_block,expected_end_block",
    [
        skip_if_slow_tests_disabled(["2018-02-07", 2, 18]),
        skip_if_slow_tests_disabled(["2018-12-31", 155728, 156584]),
        skip_if_slow_tests_disabled(["2019-01-01", 156585, 157566]),
        skip_if_slow_tests_disabled(["2019-12-31", 12975470, 13018226]),
        skip_if_slow_tests_disabled(["2020-01-01", 13018228, 13061082]),
        skip_if_slow_tests_disabled(["2020-01-02", 13061084, 13103934]),
    ],
)
def test_get_block_range_for_date(date, expected_start_block, expected_end_block):
    icx_service = get_new_icx_service()
    parsed_date = parse(date)
    blocks = icx_service.get_block_range_for_date(parsed_date)
    assert blocks == (expected_start_block, expected_end_block)


@pytest.mark.parametrize(
    "date",
    [
        skip_if_slow_tests_disabled(["2015-07-29"]),
        skip_if_slow_tests_disabled(["2030-01-01"]),
    ],
)
def test_get_block_range_for_date_fail(date):
    icx_service = get_new_icx_service()
    parsed_date = parse(date)
    with pytest.raises(OutOfBoundsError):
        icx_service.get_block_range_for_date(parsed_date)


@pytest.mark.parametrize(
    "start_timestamp,end_timestamp,expected_start_block,expected_end_block",
    [skip_if_slow_tests_disabled([1517999935, 1517999936, 16, 16]),],
)
def test_get_block_range_for_timestamps(
    start_timestamp, end_timestamp, expected_start_block, expected_end_block
):
    icx_service = get_new_icx_service()
    blocks = icx_service.get_block_range_for_timestamps(start_timestamp, end_timestamp)
    assert blocks == (expected_start_block, expected_end_block)


@pytest.mark.parametrize(
    "start_timestamp,end_timestamp",
    [skip_if_slow_tests_disabled([1517999934, 1517999935])],
)
def test_get_block_range_for_timestamps_fail(start_timestamp, end_timestamp):
    icx_service = get_new_icx_service()
    with pytest.raises(ValueError):
        icx_service.get_block_range_for_timestamps(start_timestamp, end_timestamp)


def get_new_icx_service():
    svc = IconService(HTTPProvider("https://ctz.solidwallet.io/api/v3"))
    return IcxService(svc)
