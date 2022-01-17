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

URL = "https://www.rusventure.ru"
"""URL-Адрес сайта, который мы будем парсить."""

SLEEP_TIME = 5

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

cursor.execute("truncate table src_rvc")

cnx.commit()

cursor.close()

cnx.close()

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
        submit_button = driver.find_element_by_id('load-more')
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


events = soup.find_all("article", {"class": "span4 no-padding-left data-href"})
"Список ивентов, найденных на главной странице сайта."

for event in events:

    event_soup = BeautifulSoup(str(event), "html.parser")

    event_url = URL + event_soup.find("div", {"class": "title"}).findChild("a")["href"]
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

    event_name = event_page_cont.select("h1", {"class": "color4"})[0].text.strip()

    event_article = event_page_cont.find("div", {"class": "span4"}).findChild("article")

    event_date = event_article.find("h3", {"class": "margin-bottom"}).get_text()
    event_date = " ".join(event_date.split())


    event_preview = event_article.find("div", {"class": "title event_preview"})#.findChild("span")

    event_site = event_preview.find("a")['href']

    event_descr = event_article.find("div", {"class": "margin-bottom-40px"}).get_text()

    cnx = mysql.connector.connect(
        user    =DATABASE_USER,
        password=DATABASE_PASSWORD,
        host    =DATABASE_HOST,
        database=DATABASE
    )
    cursor = cnx.cursor()

    event_data = (event_name, event_date, event_site, event_descr)

    add_event_command = """
                        INSERT INTO src_rvc
                        (name, event_date, site, descr)
                        VALUES (%s, %s, %s, %s)
                        """

    cursor.execute(add_event_command, event_data)
    cnx.commit()

# вызов процедуры, заполняющей фактовую таблицу
cursor.callproc('f_get_rvc')

cnx.commit()

cursor.close()

cnx.close()

    # print(event_name)
    # print(event_date)
    # print(event_site)
    # print(event_descr)

driver.close()
