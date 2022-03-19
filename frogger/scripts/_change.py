import os
import time

import dotenv
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

import mysql.connector

from bs4 import BeautifulSoup

dotenv.load_dotenv()

DATABASE          = os.getenv("DATABASE")
DATABASE_USER     = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_HOST     = os.getenv("DATABASE_HOST")

# очистка таблицы-источника перед наполнением
cnx = mysql.connector.connect(
        user    =DATABASE_USER,
        password=DATABASE_PASSWORD,
        host    =DATABASE_HOST,
        database=DATABASE
    )
cursor = cnx.cursor()

cursor.execute("truncate table src_change_event")

cnx.commit()

cursor.close()

cnx.close()


URL = "https://changellenge.com/event/"
# было https://changellenge.com/championships/
"""
Количество секунд, в течении которых программа будет приостановлена,
чтобы не оказаться заблокированным сайтом
"""
scroll_pause_time = 5


s = Service(GeckoDriverManager().install())
driver = webdriver.Firefox(service=s)

driver.get(URL)

while True:
    try:
        driver.find_element(By.CLASS_NAME, "new-events__load-more").click()
    except NoSuchElementException:
        break
    time.sleep(5)


soup = BeautifulSoup(driver.page_source, "html.parser")

events = soup.find("ul", {"class" : "new-events__tab new-events__tab--active"}).find_all("div", {"class": "new-events-card__content"})

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
for event in events:
    event_name = event.find("h4",   {"class": "new-events-card__title"}).get_text()
    event_link = event.find("a").get("href")
    if event_link[0:8] != "https://" and event_link[0:7] != "http://":
        event_link = "https://changellenge.com" + event_link
    event_date_day = event.find("div", {"class": "new-events-card__data-checkin"}).find("span").get_text()
    event_date_month = event.find("div", {"class": "new-events-card__data-checkin"}).find("div", {"class": "new-events-card__date"}).find("div", {"class": "new-events-card__date"}).get_text()
    event_type = event.find("span", {"class": "new-events-card__type"}).get_text()

    # result = f"Название: {event_name}\nСсылка: {event_link}\nДата: {event_date_day}{event_date_month}\nКатегория: {event_type}\n"
    # print(result)

    data_event = (event_name, event_date_day, event_link, event_type, event_date_month)
    # Данные мероприятия

    # Строка с запросом в базу на внесение новых данных.
    add_event = """
                    INSERT INTO src_change_event
                    (name, event_day, site, event_type, event_month)
                    VALUES (%s, %s, %s, %s, %s)
                    """

    # Выполняем запрос
    cursor.execute(add_event, data_event)
    cnx.commit()


# вызов процедуры, заполняющей фактовую таблицу
cursor.callproc('f_get_change_event')

# В конце обязательно коммитим изменения БД.
cnx.commit()

# Удаляем курсор
cursor.close()

# Закрываем связь с БД
cnx.close()
