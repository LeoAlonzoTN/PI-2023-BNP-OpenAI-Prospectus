from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph

Chatbotname = 'ChatBot'
username = 'User'

def create_pdf(messages, output_file):
    doc = SimpleDocTemplate(output_file, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Définir le style du paragraphe pour le contenu du message
    message_style = ParagraphStyle(
        "MessageStyle",
        parent=styles["Normal"],
        spaceAfter=10,
    )

    # Liste pour stocker les Paragraphes
    story = []

    for role, content in messages:
        # Ajouter le rôle au document
        role_text = f"<b>{role}:</b>"
        role_paragraph = Paragraph(role_text, styles["Heading3"])
        story.append(role_paragraph)

        # Ajouter le contenu du message avec gestion du débordement
        content_paragraph = Paragraph(content, message_style)
        story.append(content_paragraph)

    # Construire le document PDF
    doc.build(story)

if __name__ == '__main__':
    # Exemple d'utilisation
    messages = [
        (Chatbotname, "Hello, how are you?"),
        (username, "I'm fine, thank you!"),
        (Chatbotname, "What are your plans for the weekend? "), 
        (username, "I'm planning to relax and read a book."),
    ]

    output_file = "output.pdf"
    create_pdf(messages, output_file)
    print(f"Le fichier PDF a été créé avec succès: {output_file}")
