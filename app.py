from flask import Flask, request, jsonify, render_template, make_response, redirect, send_from_directory,send_file, after_this_request
from main import MainApplication
from metric_management import creditManager
from file_management import FileManager
from to_pdf_file import create_pdf, convert_discussion_to_tuples,convert_tuples_to_discussion
import os
from time import sleep
from to_bnp_file import load_bnp,create_bnp
from to_docx_file import create_docx
from time_observer import TimeObserver

app = Flask(__name__)
main_app = MainApplication()
main_app.add_observer(creditManager())
main_app.add_observer(TimeObserver())

@app.route('/data', methods=['POST'])
def handle_question():
    main_app.initialize_observers()
    data = request.get_json()
    text = data.get('data')
    file_names = request.cookies.get('files').split(';')


    if not text or not file_names:
        return jsonify({"error": "Question ou noms de fichiers manquants", "response": False}), 400


    client = main_app.openai_client.get_client()
    assistant_id = main_app.assistant_manager.load_assistant_id()

    if not assistant_id:
        assistant_id = main_app.assistant_manager.create_assistant(main_app.openai_client.get_client())

    file_paths = [f"{name}" for name in file_names if name != '']
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
    response.set_cookie('files', '', expires=0)
    return response

@app.route('/delete_document', methods=['POST'])
def delete_document():
    print("deleting...")
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
    
    files = request.cookies.get('files', '')
    files = files.replace(document_name,'').replace(';','')
    resp = make_response(jsonify({"message": "Document supprimé avec succès", "response": True}), 200)
    resp.set_cookie('files',files)

    return resp


@app.route('/download_pdf', methods=['POST'])
def download_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "Fichier non fourni", "response": False}), 400

    file = request.files['file']
    document_name = file.filename

    try:
        pdf_path = os.path.join('prospectus', document_name)
        os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

        file.save(pdf_path)

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
    response = send_file(pdf_filename, as_attachment=True,download_name="discussion.pdf")

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
    bnp_filename = "tmp/temp.bnp"
    create_bnp(messages,bnp_filename)

    # Envoi du fichier BNP
    response = send_file(bnp_filename, as_attachment=True,download_name="discussion.bnp")

    # Suppression du fichier après envoi
    @after_this_request
    def remove_file(response):
        try:
            os.remove(bnp_filename)
        except Exception as error:
            app.logger.error("Erreur lors de la suppression du fichier", error)
        return response

    return response

@app.route('/save_docxfile')
def save_docxfile():
    discussion = request.cookies.get('discussion', '')
    messages = convert_discussion_to_tuples(discussion)
    docx_filename = "tmp/temp.docx"
    create_docx(messages,docx_filename)

    # Envoi du fichier BNP
    response = send_file(docx_filename, as_attachment=True,download_name="discussion.docx")

    # Suppression du fichier après envoi
    @after_this_request
    def remove_file(response):
        try:
            os.remove(docx_filename)
        except Exception as error:
            app.logger.error("Erreur lors de la suppression du fichier", error)
        return response

    return response

@app.route('/file_selected',methods=['POST'])
def file_selected():
    data = request.get_json()
    document_name = data.get('document_name')

    files = request.cookies.get('files', '')
    if document_name not in files:
        files = files + ";" + document_name

    resp = make_response(jsonify({"response": True, "message": 'file succesfuly added'}))
    resp.set_cookie('files',files)

    print(files)

    return resp

@app.route('/file_deselected',methods=['POST'])
def file_deselected():
    data = request.get_json()
    document_name = data.get('document_name')

    files = request.cookies.get('files', '')
    files = files.replace(document_name,'').replace(';','')

    resp = make_response(jsonify({"response": True, "message": 'file succesfuly added'}))
    resp.set_cookie('files',files)
    print(files)

    return resp

if __name__ == '__main__':
    app.run(debug=True)
