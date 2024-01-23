from flask import Flask, request, jsonify, render_template, make_response, redirect
from main import MainApplication

app = Flask(__name__)
main_app = MainApplication()

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

        file_paths = [f"{name}" for name in file_names]
        file_ids = main_app.file_manager.upload_documents(client, file_paths)
        response = main_app.assistant_manager.ask_question(client, assistant_id, file_ids, text)
        metrics = main_app.get_observers_metrics()

        # Construction de la réponse avec gestion des cookies
        resp = make_response(jsonify({"response": True, "message": response, "metrics": metrics}))
        current_discussion = request.cookies.get('discussion', '')
        new_discussion = current_discussion + f"Question: {text}\nRéponse: {response}\n"
        resp.set_cookie('discussion', new_discussion)
        return resp
    except Exception as e:
        return jsonify({"error": str(e), "response": False}), 500

@app.route('/')
def index():
    discussion = request.cookies.get('discussion', '')
    return render_template('index.html', discussion=discussion)

@app.route('/reset_discussion')
def reset_discussion():
    response = make_response(redirect('/'))
    response.set_cookie('discussion', '', expires=0)
    return response

if __name__ == '__main__':
    app.run(debug=True)
