from observer_interface import ObserverInterface
import tiktoken

class creditManager(ObserverInterface):
    def initialize_metric(self):
        self.name = "Credit_used"
        self.metric = 0
        self.encoding = tiktoken.get_encoding("cl100k_base") #Tokennizer de GPT4
        self.credit_per_token_input = 0.00001
        self.credit_per_token_output = 0.00003

    def update_metric(self,input_token,output):
        if not isinstance(output, str):
            output = str(output)
        number_of_token = input_token
        self.metric += number_of_token * self.credit_per_token_input
        number_of_token = len(self.encoding.encode(output))
        self.metric += number_of_token * self.credit_per_token_output

    def get_metric(self):
        return self.metric
    
    