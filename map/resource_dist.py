from core.protocol import TopicProtocol

class ResourceDist(TopicProtocol):
    def __init__(self, opts):
        self.opts = opts

    def generate(self, map):
        print(map.archive.__dict__)
        pass

    def publish(self, map):
        pass


def init(opts):
    return ResourceDist(opts)
