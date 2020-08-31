import requests
from io import BytesIO
from pprint import pprint
from lxml.etree import iterparse
from collections import OrderedDict

request = requests.get('http://data.openaustralia.org.au/scrapedxml/representatives_debates/2020-08-27.xml')
fake_file = BytesIO(request.text.encode('utf-8'))
headings_dict = OrderedDict()
major_heading = None

for eventname, element in iterparse(fake_file, events=('end',)):

    if element.tag == 'major-heading':
        major_heading = element.text.strip()
        headings_dict[major_heading] = OrderedDict()
    elif element.tag == 'minor-heading':
        minor_heading = element.text.strip()
        headings_dict[major_heading][minor_heading] = {}
    elif element.tag == 'speech':
        author = element.get("speakername", "unknown")
        id = element.get("id", "unknown")
        root = element
        headings_dict[major_heading][minor_heading] = {"speech_id":id,"author":author,"text": ""}
        for child in root:
            if child.tag == 'p':
                if child.text is not None:
                    headings_dict[major_heading][minor_heading]["text"] = headings_dict[major_heading][minor_heading].get("text") + " " + child.text


    for major_heading, major_heading_elms in headings_dict.items():
        print("MAJOR HEADING:", major_heading)

        for minor_heading, minor_heading_paragraphs in major_heading_elms.items():
            print()
            print("MINOR HEADING:", minor_heading)
            print('---')
            print(minor_heading_paragraphs)
