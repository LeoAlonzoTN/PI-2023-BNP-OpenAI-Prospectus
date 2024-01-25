import time
from observer_interface import ObserverInterface

class TimeObserver(ObserverInterface):
    def initialize_metric(self):
        self.name = "Durée"
        self.debut = time.time()
        self.fin = 0
        self.metric = 0

    def update_metric(self,input_token,output):
        self.fin = time.time()
        self.metric = self.fin - self.debut

    def get_metric(self):
        return self.metric