import dotenv
import mysql.connector
import os
import time
import urllib3

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.firefox import GeckoDriverManager

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL = "https://generation-startup.ru"
"""URL-Адрес сайта, который мы будем парсить."""


SLEEP_TIME = 5

dotenv.load_dotenv()

DATABASE          = os.getenv("DATABASE")
DATABASE_USER     = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_HOST     = os.getenv("DATABASE_HOST")


# Объект класса Webdriver для браузера Firefox с импортом движка geckodriver
s = Service(GeckoDriverManager().install())
driver = webdriver.Firefox(service=s)

# Передаем веб-драйверу адрес, чтобы он мог установить соединение.
driver.get(f"{URL}/calendar")

# Определяем высоту открытой веб-драйвером страницы.
last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    # Прокручиваем вниз
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Ждем прогрузки страницы, одновременно избегая блокировки браузером.
    time.sleep(SLEEP_TIME)


    try:
        submit_button = driver.find_element_by_css_selector('.button-add')
        try:
            submit_button.click()
        except ElementNotInteractableException:
            print("Button not found.")
    except NoSuchElementException:
        print("Button not found.")
    

    time.sleep(SLEEP_TIME)

    # Вычисляем новую высоту и сравниваем ее с предыдущей.
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# Объект класса BeautifulSoup, который содержит в себе страницу в виде вложенной структуры данных
soup = BeautifulSoup(driver.page_source, "html.parser")


events = soup.find_all("a", {"class": "events-startups__item-wrap"})
"Список ивентов, найденных на главной странице сайта."

print()

# driver.close()

for event in events:

    event_soup = BeautifulSoup(str(event), "html.parser")

    event_url = URL + event_soup.find("a", {"class": "events-startups__item-wrap"})["href"]

    driver.get(event_url)

    # Определяем высоту открытой веб-драйвером страницы.
    last_height = driver.execute_script("return document.body.scrollHeight")

    type_error_count = 0

    while True:
        # Прокручиваем вниз
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Ждем прогрузки страницы, одновременно избегая блокировки браузером.
        time.sleep(SLEEP_TIME)

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

    try:
        event_date = event_grid.find("div", {"class": "events-detail-info__item data active"})
        if event_date is not None:
            event_date = event_grid.find("div", {"class": "events-detail-info__item data active"}) \
            .findChildren("div")[1].get_text() \
            .replace("\n", "").replace("  ", "")
    except TypeError:
        print(f"{event_name} предал христа. 108 строка")
        type_error_count += 1

    try:
        event_place = event_grid.find("div", {"class": "events-detail-info__item local active"})
        if event_place is not None:
            event_place = event_grid.find("div", {"class": "events-detail-info__item local active"}) \
            .findChildren("div")[1].get_text() \
            .replace("\n", "").replace("  ", "")
    except TypeError:
        print(f"{event_name} предал христа. 116 строка")
        type_error_count += 1

    try:
        event_org = event_grid.find("div", {"class": "events-detail-info__item organizer active"})
        if event_org is not None:
            event_org = event_grid.find("div", {"class": "events-detail-info__item organizer active"}) \
                .findChildren("div")[1].get_text() \
                .replace("\n", "").replace("  ", "")
    except TypeError:
        print(f"{event_name} предал христа. 124 строка")
        type_error_count += 1

    try:
        event_site = event_grid.find("div", {"class": "events-detail-info__item site active"})
        if event_site is not None:
            event_site = event_grid.find("div", {"class": "events-detail-info__item site active"}).find("a")['href']
        else:
            event_site = event_page_cont.find("a", {"class": "button button--max active"})
            if event_site is not None:
                event_site = event_page_cont.find("a", {"class": "button button--max active"})['href']
    except TypeError:
        print(f"{event_name} предал христа. 133 строка")
        type_error_count += 1


    event_descr = event_page_cont.find("div", {"class": "events-detail__content active"}).get_text()

    cnx = mysql.connector.connect(
        user    =DATABASE_USER,
        password=DATABASE_PASSWORD,
        host    =DATABASE_HOST,
        database=DATABASE
    )

    cursor = cnx.cursor()

    event_descr = " ".join(event_descr.split())

    event_data = (event_name, event_date, event_place, event_site, event_descr)

    add_event_command = """
                        INSERT INTO src_gs_calendar
                        (name, event_date, place, site, descr)
                        VALUES (%s, %s, %s, %s, %s)
                        """

    cursor.execute(add_event_command, event_data)

    cnx.commit()

    cursor.close()

    cnx.close()

    # print(event_name)
    # print(event_date)
    # print(event_place)
    # print(event_org)
    # print(event_site)
    # print(event_descr)

    # print()

print(type_error_count)
driver.close()
