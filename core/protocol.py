from abc import ABC, abstractmethod


class TopicProtocol(ABC):

    @abstractmethod
    def generate(self, map):
        pass

    @abstractmethod
    def publish(self, map):
        pass