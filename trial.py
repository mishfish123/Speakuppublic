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
        if major_heading in headings_dict.keys():
            pass
        else:
            headings_dict[major_heading] = OrderedDict()
        print(major_heading)
    elif element.tag == 'minor-heading':
        minor_heading = element.text.strip()
        headings_dict[major_heading][minor_heading] = OrderedDict()
        print(minor_heading)

for major_heading, major_heading_elms in headings_dict.items():
    print("MAJOR HEADING:", major_heading)

    for minor_heading, minor_heading_paragraphs in major_heading_elms.items():
        print("MINOR HEADING:", minor_heading)
