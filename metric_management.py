from observer_interface import ObserverInterface
import tiktoken

class Credit_Manager(ObserverInterface):
    def initialize_metric(self):
        self.credit_count = 1000
        self.encoding = tiktoken.get_encoding("cl100k_base")
        self.credit_per_token_input = 0.00003
        self.credit_per_token_output = 0.00006

    def update_metric_input(self,input):
        number_of_token = len(self.encoding.encode(input))
        self.credit_count -= number_of_token * self.credit_per_token_input

    def update_metric_output(self,output):
        number_of_token = len(self.encoding.encode(output))
        self.credit_count -= number_of_token * self.credit_per_token_output

    def get_metric(self):
        return self.credit_count
    
    