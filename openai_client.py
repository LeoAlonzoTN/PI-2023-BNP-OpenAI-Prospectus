import openai

class OpenAI_Client:
    def __init__(self):
        with open('openaikey.txt', 'r') as file:
            self.api_key = file.read().strip()

    def get_client(self):
        return openai.OpenAI(api_key=self.api_key)
