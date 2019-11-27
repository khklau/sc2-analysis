from core.protocol import TopicProtocol
from facts.action import parse_action_string
from facts.unit_event import parse_unit_event_string

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
            'unit_id',
            'building_name',
            'x_pos',
            'y_pos',
            'mineral_cost',
            'vespene_cost'
        ]
        self.module_name = splitext(basename(__file__))[0]
        output_file = self.module_name + '.csv'
        error_file = self.module_name + '.err'
        self.output_path = join(self.opts.output_dir, output_file)
        self.error_path = join(self.opts.output_dir, error_file)
        self.event_list = []
        self.error_list = []
        self.active_units = {}
        self.pp = PrettyPrinter(indent=2)

    def generate(self, replay):
        event_names = set([event.name for event in replay.events])
        for event in replay.events:
            if event.name == 'UnitInitEvent':
                self.process_init_event(event)
            elif event.name == 'UnitDoneEvent' or event.name == 'UnitTypeChangeEvent':
                self.process_unit_event(event)
            elif event.name == 'UnitDiedEvent':
                self.process_died_event(event)
            elif event.name == 'TargetPointCommandEvent' and event.ability:
                if event.ability.build_unit and isinstance(event.ability.build_unit, UnitType):
                    (action, unit) = parse_action_string(event.ability.name)
                    # TODO handle Terran specific LIFT and LAND events
                    if event.ability.build_unit.is_building and action == 'Build':
                        self.process_build_event(event, action)

    def process_init_event(self, event):
        if not event.unit._type_class.is_building:
            return
        event_type = parse_unit_event_string(event.name)
        details = {}
        details['frame'] = event.frame
        details['event_type'] = event_type
        details['player_id'] = event.control_pid
        details['unit_id'] = event.unit_id
        details['building_name'] = event.unit._type_class.name
        details['x_pos'] = event.x
        details['y_pos'] = event.y
        details['mineral_cost'] = event.unit._type_class.minerals
        details['vespene_cost'] = event.unit._type_class.vespene
        self.event_list.append(details)
        self.active_units[event.unit_id] = details

    def process_unit_event(self, event):
        if not event.unit._type_class.is_building:
            return
        if event.unit_id in self.active_units:
            active_unit = self.active_units[event.unit_id]
            event_type = parse_unit_event_string(event.name)
            details = {}
            details['frame'] = event.frame
            details['event_type'] = event_type
            details['player_id'] = active_unit['player_id']
            details['unit_id'] = event.unit_id
            details['building_name'] = active_unit['building_name']
            details['x_pos'] = active_unit['x_pos']
            details['y_pos'] = active_unit['y_pos']
            details['mineral_cost'] = active_unit['mineral_cost']
            details['vespene_cost'] = active_unit['vespene_cost']
            self.event_list.append(details)
        else:
            self.error_list.append(f'Unit {event.unit.name} has changed but has an unknown ID {event.unit_id}')

    def process_died_event(self, event):
        if not event.unit._type_class.is_building:
            return
        self.process_unit_event(event)
        if event.unit_id in self.active_units:
            del self.active_units[event.unit_id]

    def process_build_event(self, event, action):
        details = {}
        details['frame'] = event.frame
        details['event_type'] = action
        details['player_id'] = event.pid
        details['unit_id'] = 0
        details['building_name'] = event.ability.build_unit.name
        details['x_pos'] = event.x
        details['y_pos'] = event.y
        details['mineral_cost'] = event.ability.build_unit.minerals
        details['vespene_cost'] = event.ability.build_unit.vespene
        self.event_list.append(details)

    def publish(self, replay):
        with open(self.output_path, 'wt') as handle:
            writer = csv.DictWriter(handle, fieldnames=self.fields)
            writer.writeheader()
            for event in self.event_list:
                writer.writerow(event)
        if len(self.error_list) > 0:
            with open(self.error_path, 'wt') as handle:
                handle.writelines(self.error_list)


def init(opts):
    return BuildingPos(opts)
