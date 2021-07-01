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


import json
import logging
from datetime import datetime
from math import floor, log10, pow


class IcxItemTimestampCalculator:
    def calculate(self, item):
        if item is None or not isinstance(item, dict):
            return None

        item_type = item.get("type")

        if item_type == "block" and item.get("timestamp") is not None:
            return epoch_seconds_to_rfc3339(
                convert_unknown_resolution_to_epoch_seconds(item.get("timestamp"))
            )
        elif item.get("block_timestamp") is not None:
            return epoch_seconds_to_rfc3339(
                convert_unknown_resolution_to_epoch_seconds(item.get("block_timestamp"))
            )

        logging.warning("item_timestamp for item {} is None".format(json.dumps(item)))

        return None


def convert_unknown_resolution_to_epoch_seconds(timestamp):
    """
    Function to convert an epoch timestamp with unknown resolution to seconds.
    :param timestamp: Epoch timestamp of unknown resolution.
    :return: Epoch timestamp of seconds resolution.
    """

    digits = floor(log10(timestamp)) + 1
    delta = digits - 10

    if delta > 0:
        return int(timestamp / pow(10, delta))
    else:
        return timestamp


def epoch_seconds_to_rfc3339(timestamp):
    return datetime.utcfromtimestamp(int(timestamp)).isoformat() + "Z"
