from app import db, oa
from flask import current_app
import requests
from io import BytesIO
from pprint import pprint
from lxml.etree import iterparse
from collections import OrderedDict
from openaustralia import OpenAustralia
from app.models import Hansard, MajorHeading, MinorHeading, Speech, Paragraph, User, Post

def deleteeverything():
    user = User.query.all()
    post = Post.query.all()
    hansard = Hansard.query.all()
    majorheading = MajorHeading.query.all()
    minorheading = MinorHeading.query.all()
    speech = Speech.query.all()
    paragraph = Paragraph.query.all()
    print("starting delete")
    for u in hansard:
        db.session.delete(u)
    print("delete hansard")
    for u in majorheading:
        db.session.delete(u)
    print("delete majorheading")

    for u in minorheading:
        db.session.delete(u)
    print("delete minorheading")

    for u in speech:
        db.session.delete(u)
    print("delete speech")

    for u in paragraph:
        db.session.delete(u)

    print("delete paragraph")

    for u in post:
        db.session.delete(u)
    print("delete post")
    db.session.commit()
    print("commited")
