from app import db, oa
from flask import current_app
import requests
from io import BytesIO
from pprint import pprint
from lxml.etree import iterparse
from collections import OrderedDict
from openaustralia import OpenAustralia
from app.models import Hansard, MajorHeading, MinorHeading, Speech, Paragraph

def deleteeverything():
    hansard = Hansard.query.all()
    majorheading = MajorHeading.query.all()
    minorheading = MinorHeading.query.all()
    speech = Speech.query.all()
    paragraph = Paragraph.query.all()
    for u in hansard:
        db.session.delete(u)
    for u in majorheading:
        db.session.delete(u)
    for u in minorheading:
        db.session.delete(u)
    for u in speech:
        db.session.delete(u)
    for u in paragraph:
        db.session.delete(u)
    db.session.commit()
