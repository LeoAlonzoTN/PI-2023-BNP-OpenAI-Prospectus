from abc import ABC, abstractmethod

class ObserverInterface(ABC):
    @abstractmethod
    def initialize_metric(self):
        pass

    @abstractmethod
    def update_metric_input(self,input):
        pass

    @abstractmethod
    def update_metric_output(self,output):
        pass

    @abstractmethod
    def get_metric(self):
        pass
