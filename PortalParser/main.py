import requests
from bs4 import BeautifulSoup as bs
import lxml
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

url = 'https://portal.irkutskoil.ru/'
target_url = 'https://portal.irkutskoil.ru/personal/?USER_ID='
ID = [23456, 23458]  # ID первого и последнего юзверя (6041 по 25152)
login_route = 'login/'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36',
           'Origin': 'https://portal.irkutskoil.ru', 'Referer': url + login_route}
s = requests.session()
login_payload = {'login': '79526380590', 'pwd': '58r93j'}
login_req = s.post(url + login_route, headers=headers, data=login_payload)
for i in range(ID[0], ID[1]):
    target_req = s.get(target_url + str(i))
    with open("all_users/user=" + str(i) + ".html", "w", encoding='utf-8') as file:
        file.write(target_req.text)


