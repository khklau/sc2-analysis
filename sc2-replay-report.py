from core.protocol import TopicProtocol
from core.replay_report import ReplayReport

import argparse
import os


def find_topics(dir):
    result = {}
    topic_dir = os.path.join(os.path.dirname(__file__), dir)
    for module in os.listdir(topic_dir):
        if module[0:2] == '__':
            continue
        elif module[-3:] == '.py':
            name = module[0:-3]
            full_qualification = dir + '.' + name
            result[name] = full_qualification
    return result


def main():
    parser = argparse.ArgumentParser(
            description='Create a report for a StarCraft 2 replay')
    parser.add_argument(
            'input_file',
            type=str,
            help='the input file path')
    parser.add_argument(
            'output_dir',
            type=str,
            help='the output directory path')
    available_topics = find_topics('replay')
    parser.add_argument(
            '--topic',
            choices=available_topics.keys(),
            action='append',
            help='a topic to include in the report')
    args = parser.parse_args()
    chosen_topics = [ available_topics[chosen] for chosen in args.topic ]
    report = ReplayReport(args, chosen_topics)
    report.write()


if __name__ == '__main__':
    main()
