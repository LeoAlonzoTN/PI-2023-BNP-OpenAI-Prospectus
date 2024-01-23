import json
import os
import requests

class FileManager:

    @staticmethod
    def get_uploaded_files():
        try:
            with open('uploaded_files.json', 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    @staticmethod
    def save_uploaded_file(file_name, file_id):
        uploaded_files = FileManager.get_uploaded_files()
        uploaded_files[file_name] = file_id
        with open('uploaded_files.json', 'w') as file:
            json.dump(uploaded_files, file)

    @staticmethod
    def delete_file(file_id):
        api_key = FileManager.read_api_key()
        if api_key:
            url = f"https://api.openai.com/v1/files/{file_id}"
            headers = {
                'Authorization': f'Bearer {api_key}'
            }
            response = requests.delete(url, headers=headers)
            if response.status_code == 200:
                FileManager.remove_file_from_json(file_id)
                return response.json()
            else:
                return {'error': 'Failed to delete file'}
        else:
            return {'error': 'API key not found'}

    @staticmethod
    def read_api_key():
        try:
            with open('openaikey.txt', 'r') as file:
                return file.read().strip()
        except FileNotFoundError:
            return None

    @staticmethod
    def remove_file_from_json(file_id):
        uploaded_files = FileManager.get_uploaded_files()
        for file_name, id in uploaded_files.items():
            if id == file_id:
                del uploaded_files[file_name]
                break
        with open('uploaded_files.json', 'w') as file:
            json.dump(uploaded_files, file)


    def upload_documents(self, client, file_paths):
        file_ids = []
        uploaded_files = FileManager.get_uploaded_files()

        for file_path in file_paths:
            file_name = file_path.split('/')[-1]

            if file_name in uploaded_files:
                file_ids.append(uploaded_files[file_name])  # Utiliser l'ID existant
            else:
                with open(file_path, 'rb') as file:
                    file_object = client.files.create(file=file, purpose="assistants")
                    file_id = file_object.id
                    file_ids.append(file_id)
                    FileManager.save_uploaded_file(file_name, file_id)  # Sauvegarder le nouvel ID

        return file_ids
