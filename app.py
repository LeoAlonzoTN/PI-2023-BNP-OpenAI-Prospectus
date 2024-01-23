from flask import Flask, request, jsonify, render_template
from main import MainApplication

main_app = MainApplication()

app = Flask(__name__)

@app.route('/data', methods=['POST'])
def handle_question():
    main_app.initialize_observers()
    data = request.get_json()
    text = data.get('data')
    file_names = data.get("files")

    if not text or not file_names:
        return jsonify({"error": "Question ou noms de fichiers manquants", "response": False}), 400

    try:
        client = main_app.openai_client.get_client()
        assistant_id = main_app.assistant_manager.load_assistant_id()

        if not assistant_id:
            return jsonify({"error": "Assistant ID introuvable", "response": False}), 500

        # Convertir les noms de fichiers en chemins de fichiers
        file_paths = [f"{name}" for name in file_names]

        # Télécharger les documents et poser la question
        file_ids = main_app.file_manager.upload_documents(client, file_paths)
        response = main_app.assistant_manager.ask_question(client, assistant_id, file_ids, text)
        metrics = main_app.get_observers_metrics()

        return jsonify({"response": True, "message": response, "metrics": metrics})
    except Exception as e:
        return jsonify({"error": str(e), "response": False}), 500

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
