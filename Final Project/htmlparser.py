from lxml import html
import requests
from bs4 import BeautifulSoup

"""
Dataset links:
http://econpy.pythonanywhere.com/ex/001.html
http://apps2.polkcountyiowa.gov/inmatesontheweb/
"""
url=input("Enter the URL you wish to scrap:")
#page= requests.get(url)
#tree = html.fromstring(page.content)

#buyers = tree.xpath('//div[@title="buyer-name"]/text()')
#prices = tree.xpath('//span[@class="item-price"]/text()')

#print('Buyers: ',buyers)
#print('Prices: ',prices)




page = requests.get(url)

soup = BeautifulSoup(page.content)

page_links = []

for table_row in soup.select(".inmatesList tr"):
    table_cells = table_row.findAll('td')

    if len(table_cells) > 0:

        relative_link_to_inmate_details = table_cells[0].find('a')['href']
        absolute_link_to_inmate_details = url +relative_link_to_inmate_details
        inmate_links.append(absolute_link_to_inmate_details)
