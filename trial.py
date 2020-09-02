import requests
from io import BytesIO
from pprint import pprint
from lxml.etree import iterparse
from collections import OrderedDict

url = 'http://data.openaustralia.org.au/scrapedxml/representatives_debates/2020-08-27.xml'
url = url[url.rindex('/')+1:-4]
print(url)
# request = requests.get('http://data.openaustralia.org.au/scrapedxml/representatives_debates/2020-08-27.xml')
#
# fake_file = BytesIO(request.text.encode('utf-8'))
# headings_dict = OrderedDict()
# major_heading = None

# for eventname, element in iterparse(fake_file, events=('end',)):
#
#     if element.tag == 'major-heading':
#         major_heading = element.text.strip()
#         if major_heading in headings_dict.keys():
#             pass
#         else:
#             headings_dict[major_heading] = OrderedDict()
#         print(major_heading)
#     elif element.tag == 'minor-heading':
#         minor_heading = element.text.strip()
#         headings_dict[major_heading][minor_heading] = OrderedDict()
#         print(minor_heading)
#
# for major_heading, major_heading_elms in headings_dict.items():
#     print("MAJOR HEADING:", major_heading)
#
#     for minor_heading, minor_heading_paragraphs in major_heading_elms.items():
#         print("MINOR HEADING:", minor_heading)

import requests
from io import BytesIO
from pprint import pprint
from lxml.etree import iterparse
from collections import OrderedDict
from openaustralia import OpenAustralia
from app.models import Hansard
oa = OpenAustralia("AJT4oRBgm69pAze6h3GGVSMQ")


url = 'http://data.openaustralia.org.au/scrapedxml/representatives_debates/2020-08-27.xml'
request = requests.get(url)
fake_file = BytesIO(request.text.encode('utf-8'))
date = url[url.rindex('/')+1:-4]
hansard = Hansard(date=date)

for eventname, element in iterparse(fake_file, events=('end',)):

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
            elif element.tag == 'minor-heading':
                minor_heading = element.text.strip()
                headings_dict[major_heading][minor_heading] = OrderedDict()
            elif element.tag == 'speech':
                author = element.get("speakername", "unknown")
                author = author.split()
                author = author[0]+" "+author[-1]
                if oa.get_representatives(search = author):
                     author_id = oa.get_representatives(search = author)[0]['person_id']
                else:
                     author_id = None
                id = element.get("id", "unknown")
                root = element
                headings_dict[major_heading][minor_heading][id] = {"author":author,"text": []}
                for child in root:
                    if child.tag == 'p':
                        if child.text is not None:
                            headings_dict[major_heading][minor_heading][id]["text"].append(child.text.replace("\xa0", ""))



for major_heading, major_heading_elms in headings_dict.items():
    print("MAJOR HEADING:", major_heading)

    for minor_heading, minor_heading_paragraphs in major_heading_elms.items():
        print("MINOR HEADING:", minor_heading)
        print(minor_heading_paragraphs)
