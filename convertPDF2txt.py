import PyPDF2

def extraire_texte_de_pdf(chemin_pdf):
    with open(chemin_pdf, 'rb') as fichier:
        lecteur_pdf = PyPDF2.PdfFileReader(fichier)
        texte = ""
        for page in range(lecteur_pdf.getNumPages()):
            texte += lecteur_pdf.getPage(page).extractText()
        return texte
