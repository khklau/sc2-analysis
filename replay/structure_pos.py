from core.protocol import TopicProtocol

class StructurePos(TopicProtocol):
    def __init__(self, opts):
        self.opts = opts

    def generate(self, replay):
        print(replay.__dict__)
        pass

    def publish(self, replay):
        pass


def init(opts):
    return StructurePos(opts)
