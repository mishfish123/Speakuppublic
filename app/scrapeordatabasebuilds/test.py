from xlsxwriter import Workbook
import requests
from bs4 import BeautifulSoup, NavigableString, Tag


workbook = Workbook('first_file.xlsx')
worksheet = workbook.add_worksheet()

url = "https://www.aph.gov.au/Senators_and_Members/Parliamentarian_Search_Results?q=&sen=1&par=-1&gen=0&ps=96&st=1"
response = requests.get(url)
data = response.text
soup = BeautifulSoup(data, 'html.parser')
tags = soup.find_all("div", class_=["medium-pull-2"])
index = 0
for tag in tags:
    row = tag.find("h4", class_=["title"])
    worksheet.write(index,0,row.get_text())
    col = tag.find("dl", class_=["text-small"])
    for element in col:
        if isinstance(element, NavigableString):
            continue
        else:
            if element.find_all('a', href=True):
                links = element.find_all('a', href=True)
                index2 = 1
                for tea in links:
                    worksheet.write(index,index2,tea['href'])
                    index2 += 1
    index+=1

workbook.close()
