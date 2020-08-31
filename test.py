import requests
from io import BytesIO
from pprint import pprint
from lxml.etree import iterparse
from collections import OrderedDict

# Download the data from the XML URL
# (might want to download onto hard drive to stop downloading each time)
request = requests.get('http://data.openaustralia.org.au/scrapedxml/representatives_debates/2020-08-27.xml')

# Convert to a stream object which iterparse can accept
# (as it doesn't like strings)
fake_file = BytesIO(request.text.encode('utf-8'))

# Using an OrderedDict to make sure we can go thru the dict
# in the order we assign them later using major_headings.items()!
headings_dict = OrderedDict()

# Iterate through each tag to allow for processing
major_heading = None

for eventname, element in iterparse(fake_file, events=('end',)):

    if element.tag == 'major-heading':
        major_heading = element.text.strip()
        headings_dict[major_heading] = OrderedDict()
    elif element.tag == 'minor-heading':
        minor_heading = element.text.strip()
        headings_dict[major_heading][minor_heading] = []
    elif element.tag == 'speech':
        author = element.get("speakername", "unknown")
        root = element
        for child in root:
            if child.tag == 'p':
                print(str(author))
                headings_dict[major_heading][minor_heading].append({author:child.text})


print()
print("------")

for major_heading, major_heading_elms in headings_dict.items():
    print("MAJOR HEADING:", major_heading)

    for minor_heading, minor_heading_paragraphs in major_heading_elms.items():
        print()
        print("MINOR HEADING:", minor_heading)
        print('---')
        print(minor_heading_paragraphs)
