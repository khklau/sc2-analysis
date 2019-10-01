import sc2reader
from importlib import import_module


class MapReport:
    @staticmethod
    def import_topics(args, topic_list):
        result = []
        for topic in topic_list:
            module = import_module(topic)
            if hasattr(module, 'init'):
                init_func = getattr(module, 'init')
                obj = init_func(args)
                result.append(obj)
        return result

    def __init__(self, args, topic_list):
        self.args = args
        self.topic_list = MapReport.import_topics(args, topic_list)
        if args.input_type == 'map':
            self.map = sc2reader.load_map(args.input_file)
        elif args.input_type == 'replay':
            replay = sc2reader.load_replay(args.input_file)
            self.map = replay.map

    def write(self):
        for topic in self.topic_list:
            topic.generate(self.map)
        for topic in self.topic_list:
            topic.publish(self.map)
