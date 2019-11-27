from core.protocol import TopicProtocol

from datetime import datetime
import json
from os.path import basename, join, splitext 
from pprint import PrettyPrinter


class MatchInfo(TopicProtocol):
    def __init__(self, opts):
        self.opts = opts
        self.module_name = splitext(basename(__file__))[0]
        output_file = self.module_name + '.json'
        self.output_path = join(self.opts.output_dir, output_file)
        self.match_info = {}
        self.pp = PrettyPrinter(indent=2)

    def generate_replay_metadata(self, replay):
        self.match_info['metadata'] = {}
        self.match_info['metadata']['replay_release'] = replay.release_string

    def generate_match_settings(self, replay):
        description = replay.raw_data['replay.initData.backup']['game_description']
        game_options = description['game_options']
        self.match_info['settings'] = {}
        self.match_info['settings']['is_private'] = replay.is_private
        self.match_info['settings']['is_ladder'] = game_options['amm'] != 0
        self.match_info['settings']['is_battle_net'] = game_options['battle_net'] != 0
        self.match_info['settings']['is_competitive'] = game_options['competitive'] != 0
        self.match_info['settings']['is_cooperative'] = game_options['cooperative'] != 0
        self.match_info['settings']['is_practice'] = game_options['practice'] != 0
        self.match_info['settings']['has_locked_teams'] = game_options['lock_teams'] != 0
        self.match_info['settings']['speed'] = description['game_speed']
        self.match_info['settings']['is_realtime'] = description['is_realtime_mode'] != 0
        lobby_state = replay.raw_data['replay.initData.backup']['lobby_state']
        self.match_info['settings']['duration'] = lobby_state['game_duration']

    def generate_map_details(self, replay):
        self.match_info['map'] = {}
        self.match_info['map']['name'] = replay.map_name
        self.match_info['map']['hash'] = replay.map_hash
        description = replay.raw_data['replay.initData.backup']['game_description']
        self.match_info['map']['author'] = description['map_author_name']
        self.match_info['map']['size_x'] = description['map_size_x']
        self.match_info['map']['size_y'] = description['map_size_y']

    def generate_time_details(self, replay):
        self.match_info['time'] = {}
        self.match_info['time']['game_fps'] = replay.game_fps
        self.match_info['time']['total_frames'] = replay.frames
        self.match_info['time']['start'] = replay.start_time.strftime('%Y%m%dT%H%M%S')
        self.match_info['time']['end'] = replay.end_time.strftime('%Y%m%dT%H%M%S')
        self.match_info['time']['time_zone'] = replay.time_zone

    def generate_team_details(self, replay):
        self.match_info['result'] = {}
        self.match_info['teams'] = {}
        for team in replay.teams:
            self.match_info['teams'][team.number] = []
            for player in team.players:
                self.match_info['result'][team.number] = player.result
                player_detail = {}
                player_detail['player_id'] = player.pid
                player_detail['name'] = player.detail_data['name']
                player_detail['race'] = player.detail_data['race']
                player_detail['battle_net'] = {}
                player_detail['battle_net']['name'] = player.detail_data['bnet']['program_id'].decode("utf-8")
                player_detail['battle_net']['id'] = player.detail_data['bnet']['uid']
                player_detail['battle_net']['region'] = player.detail_data['bnet']['region']
                player_detail['battle_net']['subregion'] = player.detail_data['bnet']['subregion']
                self.match_info['teams'][team.number].append(player_detail)

    def generate(self, replay):
        self.generate_replay_metadata(replay)
        self.generate_match_settings(replay)
        self.generate_map_details(replay)
        self.generate_time_details(replay)
        self.generate_team_details(replay)

    def publish(self, replay):
        with open(self.output_path, 'w') as handle:
            handle.write(json.dumps(self.match_info, indent=2))


def init(opts):
    return MatchInfo(opts)
