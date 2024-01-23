import json

Botname = 'ChatBot'
Username = 'User'

def create_bnp(messages,output_file):
    bnp = {}
    i = 0
    for message in messages:
        bnp[i] = {"role":message[0],
                  "content":message[1]
                  }
        i +=1
    with open(output_file, 'w') as fichier_json:
        json.dump(bnp, fichier_json)

def load_bnp(output_file):
    with open(output_file, 'r') as fichier_json:
        data = json.load(fichier_json)
    messages = []
    for i in data:
        role = data[str(i)]["role"]
        content = data[str(i)]["content"]
        messages.append((role,content))
    return messages


if __name__ == '__main__':
    # Exemple d'utilisation
    messages = [
        (Botname, "Hello, how are you?"),
        (Username, "I'm fine, thank you!"),
        (Botname, "What are your plans for the weekend? "), 
        (Username, "I'm planning to relax and read a book."),
    ]

    output_file = "output.bnp"
    create_bnp(messages, output_file)
    print(f"Le fichier BNP a été créé avec succès: {output_file}")
    print(messages==load_bnp(output_file))
    print(f"Le fichier BNP a été load avec succès: {output_file}")