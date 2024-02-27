# PI-2023-BNP-OpenAI-Prospectus

This project was created by ALONZO Léo, KIEFFER Thomas and TAVERNE Léo for BNP Paribas

## Installation

First, we need to create a pyvenv :
```
cd path/to/project
python3 -m venv myenv
```
Then we activate it via this command :
Windows:
```
.\myenv\Scripts\activate
```
Mac/Unix:
```
source myenv/bin/activate
```

Now we can install the requirement:

```
pip install -r requirements.txt
```

Your environnement is now installed. To launch the application you need to execute the app.py file.

```
python app.py
```

On your web explorer you can go to this address 127.0.0.1:5000 to access the website. You can now go through the openai setup key section.

## OpenAI key

To use the application, it needs an acces to openai services. For that you need to create at the root of the project a file openaikey.txt in which you put the openaikey in the first line of the txt. You can then re-launch the project with python app.py to use it.
