import sc2reader
from importlib import import_module


class ReplayReport:
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
        self.topic_list = ReplayReport.import_topics(args, topic_list)
        self.replay = sc2reader.load_replay(args.input_file, load_level=4)

    def write(self):
        for topic in self.topic_list:
            topic.generate(self.replay)
        for topic in self.topic_list:
            topic.publish(self.replay)
