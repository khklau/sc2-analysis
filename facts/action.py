from enum import Enum
from pprint import PrettyPrinter


ACTION_TYPES = frozenset({
    'Build',
    'Train',
    'Upgrade',
    'Research',
    'Lift',
    'Land',
    'Lower',
    'Burrow',
    'Halt',
    'Cancel'
})


def parse_action_string(input):
    for action in ACTION_TYPES:
        if input.find(action) == 0:
            unit = input[len(action):]
            return (action, unit)
    return (None, None)
