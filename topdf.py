from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph
import re


def convert_discussion_to_tuples(discussion):
    # Trouver tous les indices de début pour 'Question:' et 'Réponse:'
    questions = [(m.start(0), "User") for m in re.finditer("Question: ", discussion)]
    reponses = [(m.start(0), "ChatBot") for m in re.finditer("Réponse: ", discussion)]
    
    # Fusionner et trier les indices
    all_indices = sorted(questions + reponses, key=lambda x: x[0])
    
    # Extraire les segments et créer des tuples
    discussion_tuples = []
    for i in range(len(all_indices)):
        start, role = all_indices[i]
        end = all_indices[i+1][0] if i+1 < len(all_indices) else len(discussion)
        text = discussion[start:end].strip()
        if role == "User":
            text = text[len("Question: "):].strip()
        else:
            text = text[len("Réponse: "):].strip()
        discussion_tuples.append((role, text))

    return discussion_tuples


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
    current_discussion = "Question: Comment ça va?\nTrès bien, et toi?\nRéponse: Bien, merci.\nEt toi?\n"
    tuples_list = convert_discussion_to_tuples(current_discussion)
    output_file = "output.pdf"
    create_pdf(tuples_list, output_file)
    print(f"Le fichier PDF a été créé avec succès: {output_file}")
