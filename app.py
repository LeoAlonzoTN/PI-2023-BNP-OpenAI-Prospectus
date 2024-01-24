from flask import Flask, request, jsonify, render_template, make_response, redirect, send_from_directory,send_file, after_this_request
from main import MainApplication
from metric_management import creditManager
from file_management import FileManager
from topdf import create_pdf, convert_discussion_to_tuples,convert_tuples_to_discussion
import os
from time import sleep
import base64
from bnp_file import load_bnp,create_bnp

app = Flask(__name__)
main_app = MainApplication()
main_app.add_observer(creditManager())

@app.route('/data', methods=['POST'])
def handle_question():
    main_app.initialize_observers()
    data = request.get_json()
    text = data.get('data')
    file_names = data.get("files")

    if not text or not file_names:
        return jsonify({"error": "Question ou noms de fichiers manquants", "response": False}), 400


    client = main_app.openai_client.get_client()
    assistant_id = main_app.assistant_manager.load_assistant_id()

    if not assistant_id:
        return jsonify({"error": "Assistant ID introuvable", "response": False}), 500

    file_paths = [f"{name}" for name in file_names]
    file_ids = main_app.file_manager.upload_documents(client, file_paths)
    response,input_token,response_without_annotation = main_app.assistant_manager.ask_question(client, assistant_id, file_ids, text)
    main_app.update_metric(input_token,response_without_annotation)
    metrics = main_app.get_metrics()

    # Construction de la réponse avec gestion des cookies

    resp = make_response(jsonify({"response": True, "message": response}))
    current_discussion = request.cookies.get('discussion', '')
    new_discussion = current_discussion + f"Question: {text}\nRéponse: {response}\n"
    resp.set_cookie('discussion', new_discussion)

    print(metrics)
    
    return resp
    

@app.route('/')
def index():
    discussion = request.cookies.get('discussion', '')
    return render_template('index.html', discussion=discussion)

@app.route('/reset_discussion')
def reset_discussion():
    response = make_response(redirect('/'))
    response.set_cookie('discussion', '', expires=0)
    return response

@app.route('/delete_document', methods=['POST'])
def delete_document():
    data = request.get_json()
    document_name = data.get('document_name')

    if not document_name:
        return jsonify({"error": "Nom du document manquant", "response": False}), 400

    file_id = FileManager.get_uploaded_files().get(document_name)

    if not file_id:
        return jsonify({"error": "ID de fichier introuvable pour le document donné", "response": False}), 404

    delete_response = FileManager.delete_file(file_id)

    if delete_response.get('error'):
        return jsonify({"error": delete_response['error'], "response": False}), 500

    return jsonify({"message": "Document supprimé avec succès", "response": True}), 200


@app.route('/download_pdf', methods=['POST'])
def download_pdf():
    data = request.get_json()
    document_name = data.get('document_name')
    pdf_content = data.get('document_content')

    if not document_name or not pdf_content:
        return jsonify({"error": "Nom du document ou contenu manquant", "response": False}), 400

    try:
        # Décodage du contenu PDF depuis base64
        pdf_data = base64.b64decode(pdf_content)
        pdf_path = os.path.join('prospectus', document_name)
        os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

        with open(pdf_path, 'wb') as pdf_file:
            pdf_file.write(pdf_data)
        
        return jsonify({"message": "PDF téléchargé avec succès", "pdf_path": pdf_path, "response": True})
    except Exception as e:
        return jsonify({"error": str(e), "response": False}), 500


@app.route('/upload_document', methods=['POST'])
def upload_to_openai():
    data = request.get_json()
    pdf_path = data.get('pdf_name')
    pdf_path = ["prospectus/" + pdf_path]

    if not pdf_path:
        return jsonify({"error": "Chemin du fichier PDF manquant", "response": False}), 400

    try:
        client = main_app.openai_client.get_client()
        print(pdf_path)
        file_ids = main_app.file_manager.upload_documents(client, pdf_path)
        return jsonify({"message": "Fichier uploadé vers OpenAI", "file_ids": file_ids, "response": True})
    except Exception as e:
        return jsonify({"error": str(e), "response": False}), 500


@app.route("/uploaded_files")
def uploaded_file():
    return send_from_directory(app.root_path,"uploaded_files.json")

@app.route("/save_pdf")
def save2pdf():
    discussion = request.cookies.get('discussion', '')
    messages = convert_discussion_to_tuples(discussion)
    pdf_filename = "tmp/temp.pdf"
    create_pdf(messages, pdf_filename)

    # Envoi du fichier PDF
    response = send_file(pdf_filename, as_attachment=True)

    # Suppression du fichier après envoi
    @after_this_request
    def remove_file(response):
        try:
            os.remove(pdf_filename)
        except Exception as error:
            app.logger.error("Erreur lors de la suppression du fichier", error)
        return response

    return response

@app.route('/load_bnpfile', methods=['POST'])
def load_bnpfile():
    if 'file' not in request.files:
        return jsonify({"error": "Aucun fichier n'a été téléchargé", "response": False}), 400
    
    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "Aucun fichier sélectionné.", "response": False}), 400
    
    messages = load_bnp(file.stream)

    new_discussion = convert_tuples_to_discussion(messages)

    response = make_response(redirect('/'))
    response.set_cookie('discussion', new_discussion)
    return response

@app.route('/save_bnpfile')
def save_bnpfile():
    discussion = request.cookies.get('discussion', '')
    messages = convert_discussion_to_tuples(discussion)
    bnp_filename = "temp.bnp"
    create_bnp(messages,bnp_filename)

    # Envoi du fichier BNP
    response = send_file(bnp_filename, as_attachment=True,download_name="log.bnp")

    # Suppression du fichier après envoi
    @after_this_request
    def remove_file(response):
        try:
            os.remove(bnp_filename)
        except Exception as error:
            app.logger.error("Erreur lors de la suppression du fichier", error)
        return response

    return response

if __name__ == '__main__':
    app.run(debug=True)
