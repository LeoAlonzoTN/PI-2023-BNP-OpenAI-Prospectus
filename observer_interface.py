from abc import ABC, abstractmethod

class ObserverInterface(ABC):
    @abstractmethod
    def initialize_metric(self):
        pass

    @abstractmethod
    def update_metric(self,input_token,output):
        pass

    @abstractmethod
    def get_metric(self):
        pass
