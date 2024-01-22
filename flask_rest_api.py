from flask import Flask, request, jsonify,Response
import openai
import json
import time

# Initialisation de l'application Flask
app = Flask(__name__)

# Création de l'assistant avec Retrieval
def initialize_openai_client():
    with open('openaikey.txt', 'r') as file:
        openai_api_key = file.read().strip()
    return openai.OpenAI(api_key=openai_api_key)

# Fonctions pour gérer l'assistant
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

def upload_documents(client, file_paths):
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

def ask_question(client, assistant_id, file_ids, question):
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
            return last_message.content[0].text.value
    return "Aucune réponse trouvée."

@app.route('/ask_question', methods=['POST'])
def handle_question():
    # Extrait les données de la requête avant d'entrer dans le générateur
    request_data = request.get_json()
    question = request_data.get('question')
    file_names = request_data.get('file_names')

    if not question or not file_names:
        def error_generator():
            yield json.dumps({"response": "Question ou noms de fichiers manquants"})
        return Response(error_generator(), status=400, mimetype='application/json')

    try:
        client = initialize_openai_client()
        assistant_id = load_assistant_id()

        if not assistant_id:
            def error_generator():
                yield json.dumps({"response": "Assistant ID introuvable"})
            return Response(error_generator(), status=500, mimetype='application/json')

        file_paths = [f"{name}" for name in file_names]
        file_ids = upload_documents(client, file_paths)

        def generate():
            response = ask_question(client, assistant_id, file_ids, question)
            yield json.dumps({"response": response})

        return Response(generate(), mimetype='application/json')
    except Exception as e:
        def error_generator():
            yield json.dumps({"response": str(e)})
        return Response(error_generator(), status=500, mimetype='application/json')



@app.route('/hello', methods=["POST"])
def hello_world():
    def generate():
        yield json.dumps({"response": "hello_world"})
    return Response(generate(), mimetype='application/json')


# Démarrer l'application Flask
if __name__ == '__main__':
    app.run(debug=True)
