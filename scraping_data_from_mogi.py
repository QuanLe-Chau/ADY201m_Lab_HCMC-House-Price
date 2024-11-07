# Import Libraries

from bs4 import BeautifulSoup
import requests
import datetime
from datetime import date, timedelta
import pandas as pd
import re
from pathlib import Path

def formated_date(date_str):
    if date_str == 'Hôm nay': 
        return date.today()
    elif date_str == 'Hôm qua':
        yesterday = date.today() - timedelta(days=1)
        return yesterday
    else:
        return datetime.datetime.strptime(date_str, '%d/%m/%Y').date()

proceed = True
current_page = int(input("""
                         How to use: Check the last row of 'Page' column in the data (.csv) file, 
                         input that number to continue the process (Without scraping pages that have already
                         been scraped. )
                         """))
r = "\d+"

data = []
try:
    while (proceed):
        # URL of the website
        url = "https://mogi.vn/ho-chi-minh/mua-nha"+'?cp='+f'{current_page}'

        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')

        page_index = soup.find('div', class_='property-list-result').span.b.text

        page_index = page_index.split('-')
        first = int(page_index[0].replace(".", ""))
        last = int(page_index[1].replace(".", ""))

        # Stop condition - When to stop scraping
        if (last - first < 0):
            proceed = False
        else:
            prop_list = soup.find('ul', class_='props').find_all('li', recursive=False)
            for prop in prop_list:
                prop_info = {}

                prop_info['Page'] = current_page

                prop_info['Title'] = prop.find('h2', class_='prop-title').text

                prop_date = prop.find('div', class_='prop-created').text
                prop_date = formated_date(prop_date)
                prop_info['Date'] = prop_date

                prop_address = prop.find('div', class_='prop-addr').text
                prop_address = prop_address.split(',')
                prop_info['District'] = prop_address[0]
                prop_info['City'] = prop_address[1]
                
                attribute_ls = prop.find('ul', class_='prop-attr').find_all('li')
                prop_info['Ground_Area'] = re.findall(r, attribute_ls[0].text)[0]
                prop_info['Bedroom'] = int(re.findall(r, attribute_ls[1].text)[0])
                prop_info['Restroom'] = int(re.findall(r, attribute_ls[2].text)[0])

                prop_info['Price'] = prop.find('div', class_='price').string

                data.append(prop_info)
            
        current_page += 1
        print(f'scraping page {current_page}')
except KeyboardInterrupt or AttributeError:
    print(f'Stop scraping data at page {current_page}')

# Load data into Dataframe

df = pd.DataFrame(data)

df.tail()

# Writing DataFrame into .csv file for later usage. 

file_path = "hcmc_house_data.csv"

if Path(file_path).is_file():
    # Append to the existing file without writing the header
    df.to_csv(file_path, mode='a', header=False, index=False)
else:
    # Write a new file with the header
    df.to_csv(file_path, mode='w', header=True, index=False)