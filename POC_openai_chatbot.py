from convertPDF2txt import extraire_texte_de_pdf
import openai
from sentence_transformers import SentenceTransformer, util

# Configuration de la clé API
with open('openaikey.txt', 'r') as file:
    openai.api_key = file.read().strip()

# Charger un modèle pré-entraîné pour faire un pré-recherche
model = SentenceTransformer('all-MiniLM-L6-v2')

def vectoriser_texte(texte):
    return model.encode(texte, convert_to_tensor=True)

def trouver_sections_pertinentes(vecteurs_document, vecteur_question, top_n=10):
    similarites = util.pytorch_cos_sim(vecteur_question, vecteurs_document)
    indices_pertinents = similarites.argsort(descending=True)[:top_n]
    return indices_pertinents

def poser_question_aux_sections(textes_sections, question):
    texte_concatené = " ".join(textes_sections)
    reponse = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"Question: {question}\n\n{texte_concatené}",
        max_tokens=100
    )
    return reponse.choices[0].text.strip()

# Exemple d'utilisation
chemins_documents = []
textes_documents = [extraire_texte_de_pdf(chemin) for chemin in chemins_documents ]
vecteurs_document = [vectoriser_texte(texte) for texte in textes_documents]

texte_question = "Votre question ici."
vecteur_question = vectoriser_texte(texte_question)

indice_section = trouver_sections_pertinentes(vecteurs_document, vecteur_question)
texte_section = textes_documents[indice_section]

reponse = poser_question_aux_sections(texte_section, texte_question)
print(f"Réponse : {reponse}")
