import sc2reader

import argparse


class Report:
    def __init__(self, args):
        self.map = None
        if args.input_type == 'map':
            self.map = sc2reader.load_map(args.input_file)
        elif args.input_type == 'replay':
            replay = sc2reader.load_replay(args.input_file)
            self.map = replay.map
        if self.map is None:
            raise ValueError('A map or replay input file is required')


def main():
    parser = argparse.ArgumentParser(
            description='Create a report for a StarCraft 2 map')
    parser.add_argument(
            'input_type',
            choices=['map', 'replay'],
            help='the input file type')
    parser.add_argument(
            'input_file',
            type=str,
            help='the input file path')
    parser.add_argument(
            'output_dir',
            type=str,
            help='the output directory path')
    args = parser.parse_args()
    report = Report(args)

if __name__ == '__main__':
    main()