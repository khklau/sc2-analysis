from core.protocol import TopicProtocol
from facts.action import parse_action_string
from facts.unit_event import parse_unit_event_string

from sc2reader.data import UnitType

import csv
from os.path import basename, join, splitext


class WorkerDist(TopicProtocol):
    def __init__(self, opts):
        self.opts = opts
        self.fields = [
            'frame',
            'event_type',
            'player_id',
            'unit_id',
            'unit_name',
            'unit_x_pos',
            'unit_y_pos',
            'target_id',
            'target_name',
            'target_x_pos',
            'target_y_pos'
        ]
        self.module_name = splitext(basename(__file__))[0]
        output_file = self.module_name + '.csv'
        error_file = self.module_name + '.err'
        self.output_path = join(self.opts.output_dir, output_file)
        self.error_path = join(self.opts.output_dir, error_file)
        self.event_list = []
        self.error_list = []
        self.active_units = {}
        self.active_resources = {}
        self.active_selections = {}
        self.game_control_groups = {}

    def generate(self, replay):
        for event in replay.events:
            if event.name == 'UnitBornEvent':
                unit_name = event.unit._type_class.name
                if event.unit._type_class.is_worker:
                    self.on_born_event(event)
                elif unit_name == 'MineralField' or unit_name == 'VespeneGeyser':
                    self.on_resource_creation(event)
            elif event.name == 'UnitDiedEvent':
                if event.unit._type_class.is_worker:
                    self.on_died_event(event)
            elif event.name == 'SelectionEvent':
                self.on_selection_event(event)
            elif event.name == 'SetControlGroupEvent':
                self.set_control_group(event)
            elif event.name == 'AddToControlGroupEvent':
                self.add_to_control_group(event)
            elif event.name == 'GetControlGroupEvent':
                self.get_control_group(event)
            elif event.name == 'TargetUnitCommandEvent':
                target_name = event.target._type_class.name
                if target_name == 'MineralField' or target_name == 'VespeneGeyser':
                    self.on_issue_target_event(event)
            elif event.name == 'UpdateTargetUnitCommandEvent':
                target_name = event.target._type_class.name
                if target_name == 'MineralField' or target_name == 'VespeneGeyser':
                    self.on_update_target_event(event)

    def on_born_event(self, event):
        event_type = parse_unit_event_string(event.name)
        details = {}
        details['frame'] = event.frame
        details['event_type'] = event_type
        details['player_id'] = event.control_pid
        details['unit_id'] = event.unit_id
        details['unit_name'] = event.unit._type_class.name
        details['unit_x_pos'] = event.x
        details['unit_y_pos'] = event.y
        self.event_list.append(details)
        self.active_units[event.unit_id] = details

    def on_died_event(self, event):
        if event.unit_id in self.active_units:
            active_unit = self.active_units[event.unit_id]
            event_type = parse_unit_event_string(event.name)
            details = {}
            details['frame'] = event.frame
            details['event_type'] = event_type
            details['player_id'] = active_unit['player_id']
            details['unit_id'] = event.unit_id
            details['unit_name'] = active_unit['unit_name']
            details['unit_x_pos'] = event.x
            details['unit_y_pos'] = event.y
            self.event_list.append(details)
            del self.active_units[event.unit_id]
        else:
            self.error_list.append(f'Unit {event.unit.name} has changed but has an unknown ID {event.unit_id}')

    def on_resource_creation(self, event):
        details = {}
        details['frame'] = event.frame
        details['event_type'] = 'Resource'
        details['player_id'] = event.control_pid
        details['unit_id'] = event.unit_id
        details['unit_name'] = event.unit._type_class.name
        details['unit_x_pos'] = event.x
        details['unit_y_pos'] = event.y
        self.event_list.append(details)
        self.active_resources[event.unit_id] = details

    def on_selection_event(self, event):
        player_selection = self.find_or_make_player_selection(event.pid)
        player_selection.clear()
        unit_index = 0
        for unit_id in event.new_unit_ids:
            unit = event.new_units[unit_index]
            if unit._type_class.is_worker:
                if unit_id in self.active_units:
                    player_selection[unit_id] = self.active_units[unit_id]
                else:
                    self.error_list.append('Worker {} selected by player {} is not alive'.format(
                            unit_id,
                            event.pid))
            unit_index += 1

    def find_or_make_player_selection(self, player_id):
        if player_id not in self.active_selections:
            self.active_selections[player_id] = {}
        return self.active_selections[player_id]

    def set_control_group(self, event):
        # The cached active selection might be empty because non-worker units were selected
        control_group = self.find_or_make_control_group(event.pid, event.control_group)
        control_group.clear()
        player_selection = self.find_or_make_player_selection(event.pid)
        if len(player_selection) > 0:
            control_group.update(player_selection)

    def add_to_control_group(self, event):
        # The cached active selection might be empty because non-worker units were selected
        control_group = self.find_or_make_control_group(event.pid, event.control_group)
        player_selection = self.find_or_make_player_selection(event.pid)
        if len(player_selection) > 0:
            control_group.update(player_selection)

    def get_control_group(self, event):
        # The cached control group might be empty because non-worker units are in the group
        player_selection = self.find_or_make_player_selection(event.pid)
        player_selection.clear()
        control_group = self.find_or_make_control_group(event.pid, event.control_group)
        if len(player_selection) > 0:
            player_selection.update(control_group)

    def find_or_make_control_group(self, player_id, group_id):
        if player_id not in self.game_control_groups:
            self.game_control_groups[player_id] = {}
        player_control_groups = self.game_control_groups[player_id]
        if group_id not in player_control_groups:
            player_control_groups[group_id] = {}
        return player_control_groups[group_id]

    def on_issue_target_event(self, event):
        player_selection = self.find_or_make_player_selection(event.pid)
        if event.target_unit_id not in self.active_resources:
            self.error_list.append('Frame {}: player {} issued target cmd at unknown resource {}'.format(
                    event.frame,
                    event.player.pid,
                    event.target_unit_id))
        elif len(player_selection) == 0:
            self.error_list.append('Frame {}: player {} issued target cmd at {} with empty selection'.format(
                    event.frame,
                    event.player.pid,
                    event.target_unit_id))
        else:
            for unit_id in player_selection.keys():
                if unit_id not in self.active_units:
                    continue
                else:
                    details = {}
                    details['frame'] = event.frame
                    details['event_type'] = 'TargetUnit'
                    details['player_id'] = event.player.pid
                    details['unit_id'] = unit_id
                    details['unit_name'] = self.active_units[unit_id]['unit_name']
                    details['target_id'] = event.target_unit_id
                    details['target_name'] = self.active_resources[event.target_unit_id]['unit_name']
                    details['target_x_pos'] = self.active_resources[event.target_unit_id]['unit_x_pos']
                    details['target_y_pos'] = self.active_resources[event.target_unit_id]['unit_y_pos']
                    self.event_list.append(details)

    def on_update_target_event(self, event):
        player_selection = self.find_or_make_player_selection(event.pid)
        if event.target_unit_id not in self.active_resources:
            self.error_list.append('Frame {}: player {} updated target cmd at unknown resource {}'.format(
                    event.frame,
                    event.player.pid,
                    event.target_unit_id))
        elif len(player_selection) == 0:
            self.error_list.append('Frame {}: player {} updated target cmd at {} with empty selection'.format(
                    event.frame,
                    event.player.pid,
                    event.target_unit_id))
        else:
            for unit_id in player_selection.keys():
                if unit_id not in self.active_units:
                    continue
                else:
                    details = {}
                    details['frame'] = event.frame
                    details['event_type'] = 'UpdateTargetUnit'
                    details['player_id'] = event.player.pid
                    details['unit_id'] = unit_id
                    details['unit_name'] = self.active_units[unit_id]['unit_name']
                    details['target_id'] = event.target_unit_id
                    details['target_name'] = self.active_resources[event.target_unit_id]['unit_name']
                    details['target_x_pos'] = self.active_resources[event.target_unit_id]['unit_x_pos']
                    details['target_y_pos'] = self.active_resources[event.target_unit_id]['unit_y_pos']
                    self.event_list.append(details)

    def publish(self, replay):
        with open(self.output_path, 'wt') as handle:
            writer = csv.DictWriter(handle, fieldnames=self.fields)
            writer.writeheader()
            for event in self.event_list:
                writer.writerow(event)
        if len(self.error_list) > 0:
            with open(self.error_path, 'wt') as handle:
                handle.writelines(err + '\n' for err in self.error_list)


def init(opts):
    return WorkerDist(opts)
