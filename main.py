from openai_client import OpenAI_Client
from file_management import FileManager
from assistant_functions import AssistantManager

class MainApplication:
    def __init__(self):
        self.openai_client = OpenAI_Client()
        self.file_manager = FileManager()
        self.assistant_manager = AssistantManager()
        self.observers = []

    def add_observer(self, observer):
        self.observers.append(observer)

    def initialize_observers(self):
        for observer in self.observers:
            observer.initialize_metric()

    def update_metric(self,input_token,output):
        for observer in self.observers:
            observer.update_metric(input_token,output)
    
    def get_metrics(self):
        metrics = {}
        for observer in self.observers:
            metrics[observer.name] = observer.metric
        return metrics

if __name__ == '__main__':
    app = MainApplication()
