from core.protocol import TopicProtocol
from facts.action import parse_action_string

import csv
from os.path import basename, join, splitext
from pprint import PrettyPrinter


class BuildingPos(TopicProtocol):
    def __init__(self, opts):
        self.opts = opts
        self.fields = [
            'frame',
            'event_type',
            'player_id',
            'x_pos',
            'y_pos',
            'z_pos',
            'building_name',
            'mineral_cost',
            'vespene_cost'
        ]
        self.module_name = splitext(basename(__file__))[0]
        output_file = self.module_name + '.csv'
        self.output_path = join(self.opts.output_dir, output_file)
        self.event_list = []
        self.pp = PrettyPrinter(indent=2)

    def generate(self, replay):
        event_names = set([event.name for event in replay.events])
        self.pp.pprint(event_names)
        for event in replay.events:
            if event.name == 'TargetPointCommandEvent':
                #self.pp.pprint(event.__dict__)
                #self.pp.pprint(event.ability.__dict__)
                if event.ability.build_unit:
                    if event.ability.build_unit.is_building:
                        (action, unit) = parse_action_string(event.ability.name)
                        details = {}
                        details['frame'] = event.frame
                        details['event_type'] = action
                        details['player_id'] = event.pid
                        details['x_pos'] = event.x
                        details['y_pos'] = event.y
                        details['z_pos'] = event.z
                        details['building_name'] = unit
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
    return BuildingPos(opts)
