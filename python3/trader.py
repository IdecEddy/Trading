#!bin/python
import requests
import datetime
import time
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv


load_dotenv()
finnhubToken = os.getenv("finnhubToken")
headers = {'X-Finnhub-Token': finnhubToken}
url = 'https://finnhub.io/api/v1/search'
payload = {'q':'amd'}

# r = requests.get(url, params=payload, headers=headers)
# print(r.text)

url = 'https://finnhub.io/api/v1/quote'
payload = {'symbol': 'AMD'}

# r = requests.get(url, params=payload, headers=headers)
# print(r.text)


from_date = time.mktime(datetime.datetime(2022, 10, 7, 12, 0).timetuple())
to_date = time.time() 
url = 'https://finnhub.io/api/v1/stock/candle'
payload = {'symbol': 'WE', 'resolution': 'D', 'from': int(from_date), 'to': int(to_date)}

r = requests.get(url, params=payload, headers=headers)
json = r.json()

print(json)
#print(json['t'])
plt.plot([datetime.datetime.fromtimestamp(timestamp) for timestamp in json['t']], json['c'])
plt.ylabel('price')
plt.show()
