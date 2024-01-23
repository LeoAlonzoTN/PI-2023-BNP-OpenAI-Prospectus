from abc import ABC, abstractmethod

class ObserverInterface(ABC):
    @abstractmethod
    def initialize_metric(self):
        pass

    @abstractmethod
    def get_metric(self):
        pass
