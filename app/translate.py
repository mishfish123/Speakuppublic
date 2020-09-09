import json
import requests
from flask import current_app


# def translate(text, source_language, dest_language):
#     if 'MS_TRANSLATOR_KEY' not in app.config or \
#             not app.config['MS_TRANSLATOR_KEY']:
#         return ('Error: the translation service is not configured.')
#     auth = {'Ocp-Apim-Subscription-Key': app.config['MS_TRANSLATOR_KEY']}
#     r = requests.get('https://api.microsofttranslator.com/v2/Ajax.svc'
#                      '/Translate?text={}&from={}&to={}'.format(
#                          text, source_language, dest_language),
#                      headers=auth)
#     if r.status_code != 200:
#         return ('Error: the translation service failed.')
#     return json.loads(r.content.decode('utf-8-sig'))


def translate(lines, language):
    uri = "https://api.cognitive.microsofttranslator.com/translate?api-version=3.0&to=" + language

    headers = {
        'Ocp-Apim-Subscription-Key': app.config['MS_TRANSLATOR_KEY'],
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
