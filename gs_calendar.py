from bs4 import BeautifulSoup
"""
BeautifulSoup4 - это библиотека, значительно облегчающая процесс парсинга HTML и XML файлов.
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
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
import urllib3


"""
requests.get не будет возвращать ответ сайта, если у того не будет SSL
Строка ниже отключает такую защиту.
"""
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL = "https://generation-startup.ru"
"""URL-Адрес сайта, который мы будем парсить."""


scroll_pause_time = 5

# Объект класса Webdriver для браузера Firefox с импортом движка geckodriver
s = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=s)

# Передаем веб-драйверу адрес, чтобы он могу установить соединение.
driver.get(f"{URL}/calendar")

# Определяем высоту открытой веб-драйвером страницы.
last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    # Прокручиваем вниз
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Ждем прогрузки страницы, одновременно избегая блокировки браузером.
    time.sleep(scroll_pause_time)

    submit_button = driver.find_element_by_css_selector('.button-add')
    submit_button.click()

    time.sleep(scroll_pause_time)


    # Вычисляем новую высоту и сравниваем ее с предыдущей.
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# Объект класса BeautifulSoup, который содержит в себе страницу в виде вложенной структуры данных
soup = BeautifulSoup(driver.page_source, "html.parser")


events = soup.find_all("a", {"class": "events-startups__item-wrap"})



print()

"""
Список ивентов, найденных на главной странице сайта.
"""
# driver.close()

for event in events:

    event_soup = BeautifulSoup(str(event), "html.parser")

    event_url = URL + event_soup.find("a", {"class": "events-startups__item-wrap"})["href"]

    driver.get(event_url)

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
    
    event_page_cont = BeautifulSoup(driver.page_source, "html.parser")
    
    # event_data = event_page_cont.find_all("div", {"class": "events-detail-info__item"})

    event_name = event_page_cont.select("h1", {"class": "h1 active"})[0].text.strip()

    event_grid = event_page_cont.find("div", {"class": "events-detail-info__grid"})
    # print(event_grid)
    event_date = event_grid.find("div", {"class": "events-detail-info__item data active"}).findChildren("div")[1].get_text().replace("\n", "").replace("  ", "")
    
    event_place = event_grid.find("div", {"class": "events-detail-info__item local active"}).findChildren("div")[1].get_text().replace("\n", "").replace("  ", "")
    
    event_org = event_grid.find("div", {"class": "events-detail-info__item organizer active"}).findChildren("div")[1].get_text().replace("\n", "").replace("  ", "")


    event_site = event_grid.find("div", {"class": "events-detail-info__item site active"})
    if event_site is not None:
        event_site = event_grid.find("div", {"class": "events-detail-info__item site active"}).find("a")['href']
    else:
        event_site = event_page_cont.find("a", {"class": "button button--max active"})['href']

    event_descr = event_page_cont.find("div", {"class": "events-detail__content active"}).get_text()


    print(event_name)
    print(event_date)
    print(event_place)
    print(event_org)
    print(event_site)
    print(event_descr)

    print()

    # result = event_name + "\n" + event_date

    # for data in event_data:
    #     name = data.find("div", {"class": "events-detail-info__name"}).text.strip()
    #     desc = data.find("div", {"class": "events-detail-info__desc"}).text.strip().replace("\n", "")  # Костыль
    #     result += f"{name} => {desc}\n"

    # print(result)
