import requests
import json

response = requests.get('https://theyvoteforyou.org.au/api/v1/people/10001.json?key=k4Pwf%2BFaW2ygOTWEOCVn')
json_data = json.loads(response.text)
print(json_data['id'])
print(json_data['latest_member']['name'])
