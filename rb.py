# ===============================================================================================================================================================
# Необходимы библиотеки: beautifulsoup4, selenium, time
# Установить: pip install beautifulsoup4 mysql-connector-python webdriver-manager
# ===============================================================================================================================================================

from bs4 import BeautifulSoup
"""
BeautifulSoup4 - это библиотека, значительно облегчающая процесс парсинга HTML и XML файлов.
"""

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
"""
Selenium WebDriver – это программная библиотека для управления браузерами.
"""

import time
"""
Time - модуль для работы со временем в Python.
"""

import mysql.connector
"""
MySQL Connector/Python - это драйвер, который позволяет взаимодействовать с серверами MySQL прямо из кода.
"""


# Переменная, содержащая адрес страницы, которую мы хотим парсить.
URL = "https://rb.ru/chance/"

# Переменная, содержащая количество секунд, на которое мы будем приостанавливать программу, чтобы не быть заблокированными сайтом.
scroll_pause_time = 5

# Объект класса Webdriver для браузера Firefox с импортом движка geckodriver
s = Service(GeckoDriverManager().install())
driver = webdriver.Firefox(service=s)

# Передаем веб-драйверу адрес, чтобы он могу установить соединение.
driver.get(URL)

# Определяем высоту открытой веб-драйвером страницы.
last_height = driver.execute_script("return document.body.scrollHeight")

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
cnx = mysql.connector.connect(user='ufaile8o_parser', password='SO8DQrzSxOr1',
                              host='ufaile8o.beget.tech',
                              database='ufaile8o_parser')
# Курсор - это структура, посредством которой мы общаемся с БД. Они принимает от нас запрос с данными,
# передает результаты в базу (если это запросы типа INSERT) или возвращает его результаты нам (если это запросы типа SELECT).
cursor = cnx.cursor()

for event in events:
    
    event_name = event.find("a", {"class": "chance__card-name-item ng-binding"}).get_text()

    event_link = event.find("a", {"class": "chance__card-name-item ng-binding"}).get('href')

    event_date_day = event.find("div", {"class": "chance__card-date-number ng-binding"}).get_text()

    event_date_month = event.find("div", {"class": "chance__card-date-month ng-binding"}).get_text()

    event_type = event.find("div", {"class": "chance__card-name-categ ng-binding"}).get_text()


    result = f"Название: {event_name}\n\
    ссылка: {event_link}\n\
    Дата: {event_date_day} {event_date_month}\n\
    Категория: {event_type}\n"

    print(result)


    # Кортеж с данными о мероприятии, которые мы только что нашли.
    data_event = (event_name, event_date_day, event_link, event_type, event_date_month)

    # Строка с запросом в базу на внесение новых данных.
    add_event = ("INSERT INTO rb "
               "(name, event_day, site, event_type, event_month) "
               "VALUES (%s, %s, %s, %s, %s)")
    

    # Выполняем запрос 
    cursor.execute(add_event, data_event)

# В конце обязательно коммитим изменения БД.
cnx.commit()
# Удаляем курсор и закрываем связь с БД.
cursor.close()
cnx.close()