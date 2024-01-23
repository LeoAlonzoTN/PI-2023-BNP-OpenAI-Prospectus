import time
import json

class AssistantManager:
    @staticmethod
    def save_assistant_id(assistant_id):
        with open('assistant_id.json', 'w') as file:
            json.dump({'assistant_id': assistant_id}, file)

    @staticmethod
    def load_assistant_id():
        try:
            with open('assistant_id.json', 'r') as file:
                data = json.load(file)
                return data.get('assistant_id')
        except FileNotFoundError:
            return None

    def ask_question(self, client, assistant_id, file_ids, question):
        thread = client.beta.threads.create()
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=question,
            file_ids=file_ids
        )
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id,
        )

        while True:
            time.sleep(1)
            run_status = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            if run_status.status == 'completed':
                break

        messages = client.beta.threads.messages.list(thread_id=thread.id)
        assistant_messages = [m for m in messages if m.role == 'assistant']

        if assistant_messages:
            last_message = assistant_messages[-1]
            if last_message.content and last_message.content[0].text:
                message_content = last_message.content[0].text
                response = message_content
                annotations = message_content.annotations
                citations = []

                # Iterate over the annotations and add footnotes
                for index, annotation in enumerate(annotations):
                    # Replace the text with a footnote
                    message_content.value = message_content.value.replace(annotation.text, f' [{index}]')

                    # Gather citations based on annotation attributes
                    if (file_citation := getattr(annotation, 'file_citation', None)):
                        cited_file = client.files.retrieve(file_citation.file_id)
                        citations.append(f'[{index}] {file_citation.quote[:50]+"..."} from {cited_file.filename}')
                    elif (file_path := getattr(annotation, 'file_path', None)):
                        cited_file = client.files.retrieve(file_path.file_id)
                        citations.append(f'[{index}] Click <here> to download {cited_file.filename}')
                        # Note: File download functionality not implemented above for brevity
                
                message_content.value += '\n Source document:'
                message_content.value += '\n' + '\n'.join(citations)

                return message_content.value,run_status.usage.total_tokens,response
        return "Aucune réponse trouvée."
