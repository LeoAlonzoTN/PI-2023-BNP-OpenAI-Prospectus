import openai
import requests
from io import BytesIO
import time
import json

with open('openaikey.txt', 'r') as file:
    openai_api_key = file.read().strip()

# Création de l'assistant avec Retrieval
client = openai.OpenAI(api_key=openai_api_key)
def save_assistant_id(assistant_id):
    with open('assistant_id.json', 'w') as file:
        json.dump({'assistant_id': assistant_id}, file)

def load_assistant_id():
    try:
        with open('assistant_id.json', 'r') as file:
            data = json.load(file)
            return data.get('assistant_id')
    except FileNotFoundError:
        return None

# Charger l'ID de l'assistant s'il existe déjà
assistant_id = load_assistant_id()

if not assistant_id:
    # Créer un nouvel assistant si aucun ID n'est enregistré
    assistant = client.beta.assistants.create(
        name="BNP-ChatBot",
        instructions="Answer the questions using the documents provided. Indicate the source of answers by citing the part of the documents containing the information (in the form of a page or section number).",
        model="gpt-4-1106-preview",
        tools=[{"type": "retrieval"}],
    )
    assistant_id = assistant.id
    save_assistant_id(assistant_id)
else:
    # Charger l'assistant existant par son ID
    assistant = client.beta.assistants.retrieve(assistant_id)

def get_uploaded_files():
    try:
        with open('uploaded_files.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_uploaded_file(file_name, file_id):
    uploaded_files = get_uploaded_files()
    uploaded_files[file_name] = file_id
    with open('uploaded_files.json', 'w') as file:
        json.dump(uploaded_files, file)

def upload_documents(file_paths):
    file_ids = []
    uploaded_files = get_uploaded_files()

    for file_path in file_paths:
        file_name = file_path.split('/')[-1]

        if file_name in uploaded_files:
            file_ids.append(uploaded_files[file_name])  # Utiliser l'ID existant
        else:
            with open(file_path, 'rb') as file:
                file_object = client.files.create(file=file, purpose="assistants")
                file_id = file_object.id
                file_ids.append(file_id)
                save_uploaded_file(file_name, file_id)  # Sauvegarder le nouvel ID

    return file_ids

def ask_question(file_ids, question):
    thread = client.beta.threads.create()
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=question,
        file_ids=file_ids
    )
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )

    while True:
        time.sleep(5)
        run_status = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        ).status
        if run_status == 'completed':
            break

    messages = client.beta.threads.messages.list(thread_id=thread.id)
        
    assistant_messages = [m for m in messages if m.role == 'assistant']

    if assistant_messages:
        last_message = assistant_messages[-1]
        if last_message.content and last_message.content[0].text:
            return last_message.content[0].text.value
    return "Aucune réponse trouvée."


if __name__ == "__main__":
    file_paths = ["prospectus/prospectus_exemple_3.pdf"]
    print("Uploading...")
    file_ids = upload_documents(file_paths)
    print("Done\nAsking assistant...")
    response = ask_question(file_ids, "What are the liquidation strategy ?")
    print()
    print(response)
