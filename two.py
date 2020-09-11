from xlsxwriter import Workbook
import requests
from bs4 import BeautifulSoup, NavigableString, Tag


workbook = Workbook('first_file.xlsx')
worksheet = workbook.add_worksheet()

url = "https://www.openaustralia.org.au/senators/"
response = requests.get(url)
data = response.text
soup = BeautifulSoup(data, 'html.parser')
tags = soup.find_all("img", class_=["portrait"])
index = 0
for tag in tags:
    worksheet.write(index,0,tag['src'])
    index+=1
workbook.close()
