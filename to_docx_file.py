from docx import Document

def create_docx(messages, output_file):
    doc = Document()

    for role, content in messages:
        # Ajouter le rôle et le contenu au document
        doc.add_paragraph(f"{role}: {content}", style='BodyText')

    # Enregistrer le fichier DOCX
    doc.save(output_file)

# Exemple d'utilisation
messages = [
    ("Sender", "Hello, how are you?"),
    ("Receiver", "I'm fine, thank you!"),
    ("Sender", "What are your plans for the weekend? " * 10),  # Exemple de contenu long
    ("Receiver", "I'm planning to relax and read a book."),
]
if __name__ == '__main__':
    output_file = "output.docx"
    create_docx(messages, output_file)
    print(f"Le fichier DOCX a été créé avec succès: {output_file}")