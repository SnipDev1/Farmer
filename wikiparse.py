# Step 1: Fetch the Wikipedia page
import json

import requests
from bs4 import BeautifulSoup

url = "https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)"  # Replace with the actual URL
response = requests.get(url)
response.raise_for_status()  # Raise an error if the request failed

# Step 2: Parse the HTML
soup = BeautifulSoup(response.text, 'html.parser')

# Step 3: Find the table with the specific class
table = soup.find('table', class_='wikitable')

if table is None:
    print("Table with the specified class was not found.")
else:
    # Step 4: Extract table data
    rows = table.find_all('tr')
    data = []

    for row in rows:
        cells = row.find_all(['th', 'td'])  # Extract header and data cells
        data.append([cell.get_text(strip=True) for cell in cells])

data = data[3:]
data.reverse()

country_list = []
counter = 0
for i in range(len(data)):
    country_data = data[i][0:2]
    country_data[1] = country_data[1].replace(',', '')

    if country_data[1] == "—":
        continue
    country_data[1] = str(int(country_data[1]) * 10**6)
    country_data.append(str(int(country_data[1])//1000))
    country_data_json = {
        "country_name": country_data[0],
        "cost": country_data[1],
        "earn_per_second": country_data[2],
        "item_id": counter
    }
    country_list.append(country_data_json)
    counter+=1

with open("countries.json", 'w', encoding='utf-8') as file:
    json.dump({"countries": country_list}, file, indent=2, ensure_ascii=False)
