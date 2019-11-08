from core.protocol import TopicProtocol
from facts.action import parse_action_string

from sc2reader.data import UnitType

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
        event_names = set([event.name for event in replay.events])
        self.pp.pprint(event_names)
        #self.pp.pprint(replay.__dict__)
        for event in replay.events:
            if (event.name == 'TargetPointCommandEvent'
                    or event.name == 'TargetUnitCommandEvent'
                    or event.name == 'BasicCommandEvent'
                    or event.name == 'UpdateTargetPointCommandEvent'
                    or event.name == 'UpdateTargetUnitCommandEvent') and event.ability:
                #self.pp.pprint(event.__dict__)
                #self.pp.pprint(event.ability.__dict__)
                if event.ability.build_unit and isinstance(event.ability.build_unit, UnitType):
                    #self.pp.pprint(event.ability.build_unit.__dict__)
                    (action, unit) = parse_action_string(event.ability.name)
                    if event.ability.build_unit.is_building and action == 'Build':
                        details = {}
                        details['frame'] = event.frame
                        details['event_type'] = action
                        details['player_id'] = event.pid
                        details['x_pos'] = event.x
                        details['y_pos'] = event.y
                        details['z_pos'] = event.z
                        details['building_name'] = event.ability.build_unit.name
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
    return BuildingPos(opts)
