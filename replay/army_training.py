from core.protocol import TopicProtocol
from facts.action import parse_action_string

from sc2reader.data import UnitType

import csv
from os.path import basename, join, splitext
from pprint import PrettyPrinter


class ArmyTraining(TopicProtocol):
    def __init__(self, opts):
        self.opts = opts
        self.fields = [
            'frame',
            'event_type',
            'player_id',
            'unit_name',
            'time_cost',
            'mineral_cost',
            'vespene_cost'
        ]
        self.module_name = splitext(basename(__file__))[0]
        output_file = self.module_name + '.csv'
        self.output_path = join(self.opts.output_dir, output_file)
        self.event_list = []
        self.pp = PrettyPrinter(indent=2)

    def generate(self, replay):
        for event in replay.events:
            if event.name == 'BasicCommandEvent' and event.ability:
                if event.ability.build_unit and isinstance(event.ability.build_unit, UnitType):
                    (action, unit) = parse_action_string(event.ability.name)
                    if event.ability.build_unit.is_army and action == 'Train':
                        details = {}
                        details['frame'] = event.frame
                        details['event_type'] = action
                        details['player_id'] = event.pid
                        details['unit_name'] = event.ability.build_unit.name
                        details['time_cost'] = event.ability.build_time
                        details['mineral_cost'] = event.ability.build_unit.minerals
                        details['vespene_cost'] = event.ability.build_unit.vespene
                        self.event_list.append(details)

    def publish(self, replay):
        with open(self.output_path, 'w') as handle:
            writer = csv.DictWriter(handle, fieldnames=self.fields)
            writer.writeheader()
            for event in self.event_list:
                writer.writerow(event)


def init(opts):
    return ArmyTraining(opts)
