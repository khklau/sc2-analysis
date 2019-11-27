from enum import Enum
from pprint import PrettyPrinter


PREFIX = 'Unit'
SUFIX = 'Event'


def parse_unit_event_string(input):
    min_length = len(PREFIX) + len(SUFIX)
    if len(input) > min_length:
        begin = len(PREFIX)
        end = len(input) - len(SUFIX)
        return input[begin:end]
    else:
        return None
