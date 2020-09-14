import json
import requests
from flask import current_app
import os

def translate(lines, language):
    """ translates lines of text to a particular language """

    uri = "https://api.cognitive.microsofttranslator.com/translate?api-version=3.0&to=" + language #URI to call to access ms translator service

    headers = {
        'Ocp-Apim-Subscription-Key': os.getenv('MS_TRANSLATOR_KEY'), #the authentication key
        'Content-type': 'application/json'
    }

    input=[]

    for line in lines:
        input.append({ "text": line }) #adds list of lines into a dictionary format within a list

    try:
        response = requests.post(uri, headers=headers, json=input) #send request for translation
        response.raise_for_status() # Raise exception if call failed
        results = response.json()

        translated_lines = []

        for result in results:
            for translated_line in result["translations"]: #add translated lines into a list to be returned to users
                translated_lines.append(translated_line["text"])

        return translated_lines

    except requests.exceptions.HTTPError as e: #exception handling
        return ["Error calling the Translator Text API: " + e.strerror]

    except Exception as e:
        return ["Error calling the Translator Text API"]
