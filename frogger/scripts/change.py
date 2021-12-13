import os

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

import mysql.connector

from bs4 import BeautifulSoup
# DATABASE = os.getenv("DATABASE")
# DATABASE_USER = os.getenv("DATABASE_USER")
# DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
# DATABASE_HOST = os.getenv("DATABASE_HOST")

URL = "https://changellenge.com/championships/"

"""
Количество секунд, в течении которых программа будет приостановлена,
чтобы не оказаться заблокированным сайтом
"""
scroll_pause_time = 5


s = Service(GeckoDriverManager().install())
driver = webdriver.Firefox(service=s)

driver.get(URL)

soup = BeautifulSoup(driver.page_source, "html.parser")

events = soup.find_all("div", {"class": "champ-card champ-cards__item"})

# Закрываем веб-браузер, он нам больше не нужен.
driver.close()

# Открываем связь с нашим сервером MySQL
# cnx = mysql.connector.connect(
#     user=DATABASE_USER,
#     password=DATABASE_PASSWORD,
#     host=DATABASE_HOST,
#     database=DATABASE
# )

# cursor = cnx.cursor()
"""
Курсор - это структура, посредством которой мы общаемся с БД. Они принимает от нас запрос с данными,
передает результаты в базу (если это запросы типа INSERT)
или возвращает его результаты нам (если это запросы типа SELECT).
"""

print(events)