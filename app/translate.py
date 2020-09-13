import json
import requests
from flask import current_app
import os

def translate(lines, language):
    uri = "https://api.cognitive.microsofttranslator.com/translate?api-version=3.0&to=" + language

    headers = {
        'Ocp-Apim-Subscription-Key': os.getenv('MS_TRANSLATOR_KEY'),
        'Content-type': 'application/json'
    }

    input=[]

    for line in lines:
        input.append({ "text": line })

    try:
        response = requests.post(uri, headers=headers, json=input)
        response.raise_for_status() # Raise exception if call failed
        results = response.json()

        translated_lines = []

        for result in results:
            for translated_line in result["translations"]:
                translated_lines.append(translated_line["text"])

        return translated_lines

    except requests.exceptions.HTTPError as e:
        return ["Error calling the Translator Text API: " + e.strerror]

    except Exception as e:
        return ["Error calling the Translator Text API"]
