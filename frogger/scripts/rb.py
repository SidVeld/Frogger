import dotenv
import mysql.connector
import os
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

dotenv.load_dotenv()

DATABASE          = os.getenv("DATABASE")
DATABASE_USER     = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_HOST     = os.getenv("DATABASE_HOST")

URL = "https://rb.ru/chance/"
"Адрес страницы для парсинга"

scroll_pause_time = 5
"""
Количество секунд, в течении которых программа будет приостановлена,
чтобы не оказаться заблокированным сайтом
"""

s = Service(GeckoDriverManager().install())
driver = webdriver.Firefox(service=s)

driver.get(URL)

last_height = driver.execute_script("return document.body.scrollHeight")
"Высота открытой страницы"

while True:
    # Прокручиваем вниз
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Ждем прогрузки страницы, одновременно избегая блокировки браузером.
    time.sleep(scroll_pause_time)

    # Вычисляем новую высоту и сравниваем ее с предыдущей.
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# Объект класса BeautifulSoup, который содержит в себе страницу в виде вложенной структуры данных
soup = BeautifulSoup(driver.page_source, "html.parser")

events = soup.find_all("div", {"class": "chance__card"})


# Закрываем веб-браузер, он нам больше не нужен.
driver.close()

# Открываем связь с нашим сервером MySQL
cnx = mysql.connector.connect(
    user    =DATABASE_USER,
    password=DATABASE_PASSWORD,
    host    =DATABASE_HOST,
    database=DATABASE
)

cursor = cnx.cursor()
"""
Курсор - это структура, посредством которой мы общаемся с БД. Они принимает от нас запрос с данными,
передает результаты в базу (если это запросы типа INSERT)
или возвращает его результаты нам (если это запросы типа SELECT).
"""

for event in events:

    event_name       = event.find("a",   {"class": "chance__card-name-item ng-binding"  }).get_text()

    event_link       = event.find("a",   {"class": "chance__card-name-item ng-binding"  }).get('href')

    event_date_day   = event.find("div", {"class": "chance__card-date-number ng-binding"}).get_text()

    event_date_month = event.find("div", {"class": "chance__card-date-month ng-binding" }).get_text()

    event_type       = event.find("div", {"class": "chance__card-name-categ ng-binding" }).get_text()

    result = f"Название: {event_name}\n\
    ссылка: {event_link}\n\
    Дата: {event_date_day} {event_date_month}\n\
    Категория: {event_type}\n"

    print(result)

    data_event = (event_name, event_date_day, event_link, event_type, event_date_month)
    "Данные мероприятия"

    # Строка с запросом в базу на внесение новых данных.
    add_event = """
                INSERT INTO src_rb
                (name, event_day, site, event_type, event_month)
                VALUES (%s, %s, %s, %s, %s)
                """

    # Выполняем запрос
    cursor.execute(add_event, data_event)

# В конце обязательно коммитим изменения БД.
cnx.commit()

# Удаляем курсор
cursor.close()

# Закрываем связь с БД
cnx.close()
