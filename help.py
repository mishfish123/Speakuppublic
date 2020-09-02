
from app import app, db
import requests
from io import BytesIO
from pprint import pprint
from lxml.etree import iterparse
from collections import OrderedDict
from openaustralia import OpenAustralia
from app.models import Hansard, MajorHeading, MinorHeading, Speech, Paragraph
oa = OpenAustralia("AJT4oRBgm69pAze6h3GGVSMQ")

#
url = 'http://data.openaustralia.org.au/scrapedxml/representatives_debates/2020-08-27.xml'
request = requests.get(url)
fake_file = BytesIO(request.text.encode('utf-8'))
date = url[url.rindex('/')+1:-4]
hansard = Hansard(date=date)
db.session.add(hansard)
db.session.commit()
majorheadingid = 0
minorheadingid = 0
speechid = 0
paragraphid= 0

for eventname, element in iterparse(fake_file, events=('end',)):
    if element.tag == 'major-heading':
        major_heading = element.text.strip()
        if MajorHeading.query.filter_by(body=major_heading).first():
            majorheading = MajorHeading.query.filter_by(body=major_heading).first()
        else:
            majorheading = MajorHeading(body=major_heading, hansard=hansard, order_id = majorheadingid)
            db.session.add(majorheading)
            db.session.commit()
            majorheadingid +=1
    elif element.tag == 'minor-heading':
        minor_heading = element.text.strip()
        minorheading = MinorHeading(body=minor_heading, majorheading=majorheading, order_id = minorheadingid)
        db.session.add(minorheading)
        db.session.commit()
        minorheadingid +=1
    elif element.tag == 'speech':
        author = element.get("speakername", "unknown")
        author = author.split()
        author = author[0]+" "+author[-1]
        id = element.get("id", "unknown")
        speech = Speech(exact_id=id, author_id=author, minorheading=minorheading, order_id = speechid )
        db.session.add(speech)
        speechid +=1
        root = element
        for child in root:
            if child.tag == 'p':
                if child.text is not None:
                    paragraph = Paragraph(body = child.text.replace("\xa0", ""), speech= speech)
                    db.session.add(paragraph)
                    db.session.commit()

print(hansard.majorheading.all()[0]MajorHeading.query.all()[1].minorheading.all())
# speech = Speech.query.all()
# majorheading = MajorHeading.query.all()
# minorheading = MinorHeading.query.all()
# speech = Speech.query.all()
#
# for u in majorheading:
#     db.session.delete(u)
# for u in minorheading:
#     db.session.delete(u)
# db.session.commit()
