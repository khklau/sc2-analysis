from core.protocol import TopicProtocol
from core.map_report import MapReport

import argparse
import os


def find_topics():
    result = {}
    topic_dir = os.path.join(os.path.dirname(__file__), 'map')
    for module in os.listdir(topic_dir):
        if module[0:2] == '__':
            continue
        elif module[-3:] == '.py':
            name = module[0:-3]
            full_qualification = 'map.' + name
            result[name] = full_qualification
    return result


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
    available_topics = find_topics();
    parser.add_argument(
            '--topic',
            choices=available_topics.keys(),
            action='append',
            help='a topic to include in the report')
    args = parser.parse_args()
    chosen_topics = [ available_topics[chosen] for chosen in args.topic ]
    report = MapReport(args, chosen_topics)
    report.write()


if __name__ == '__main__':
    main()
