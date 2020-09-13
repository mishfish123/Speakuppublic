
from app import db, oa
from app.models import Rep
import pandas


def buildrep():
    df = pandas.read_csv('app/Rep.csv', engine='python')
    for index, row in df.iterrows():
        address = ""
        address += row['Electorate Address Line 1']
        address += ", "
        if type(row['Electorate Address Line 2']) == type("hello"):
            address += row['Electorate Address Line 2']
            address += ", "
        address += row['Electorate Suburb']
        address += ", "
        address += row['Electorate State']
        address += ", "
        address += str(row['Electorate PostCode'])
        postaladdress = ""
        postaladdress += row['Electorate Postal Address']
        postaladdress += ", "
        postaladdress += row['Electorate Postal Suburb']
        postaladdress += ", "
        postaladdress += row['Electorate Postal State']
        postaladdress += ", "
        postaladdress += str(row['Electorate Postal Postcode'])
        rep = Rep(Honorific= row['Honorific'],Salutation=row['Salutation'],\
        PostNomination= row['Post Nominals'],Surname=row['Surname'],\
        Image = row['Image'],FirstName=row['First Name'],\
        PreferredName = row['Preferred Name'],Email=row['Email'],\
        Facebook = row['Facebook'],Twitter=row['Twitter'],\
        Other = row['Other'],Telephone=row['Telephone'],\
        ElectorateAddress  = address, ElectoratePhone =row['Electorate Telephone'],\
        ElectoratePostal = postaladdress, ElectorateSuburb = row['Electorate Suburb'],
        Titles = row['Parliamental and Ministerial Titles'], Postcode = row['Electorate PostCode'])
        db.session.add(rep)
        db.session.commit()






#
# class Representative(db.Model):
#
#     ElectorateAddress = db.Column(db.String(140))
#     ElectoratePhone = db.Column(db.String(140))
#     ElectoratePostal = db.Column(db.String(140))
