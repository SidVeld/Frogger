import dotenv
import os

from mysql import connector
from mysql.connector.connection import MySQLConnection
from mysql.connector.cursor import MySQLCursor

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

URL = "https://generation-startup.ru/startups/"

dotenv.load_dotenv()

DATABASE = os.getenv("DATABASE")
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_HOST = os.getenv("DATABASE_HOST")

service = Service(GeckoDriverManager().install())

driver = webdriver.Firefox(service=service)
driver.get(URL)
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

soup = BeautifulSoup(driver.page_source, "html.parser")

startups = soup.find_all("div", {"class": "main-accelerators__item-wrap"})

total_startups = len(startups)
valid_startupds = 0
expired_startups = 0
parsed_startups = []

for startup in startups:

    name: str = startup.find("div", {"class": "main-accelerators__name"}).text
    url: str = startup.find("a", {"class": "button"})["href"]

    if url.startswith("/"):
        url = ("https://generation-startup.ru" + url).replace(" ", "%20")

    if "Программа завершена" in startup.text:
        expired_startups += 1
        continue

    parsed_startups.append((name, url))
    valid_startupds += 1

# ? Может быть поменять print на логирование через logging ?
print("\nFinished collecting information about startups.")
print(f"Valid: {valid_startupds}; Expired: {expired_startups}; Total: {total_startups}")
print("Trying to connect to the database.")

try:
    connection: MySQLConnection = connector.connect(
            user=DATABASE_USER,
            password=DATABASE_PASSWORD,
            host=DATABASE_HOST,
            database=DATABASE
    )
except Exception as e:
    print(f"Something goes wrong and we failed to connect to database. \n{e}")
    exit(69)

print("A connection to the database has been established.")

cursor: MySQLCursor = connection.cursor()

command = (
    "INSERT INTO src_gs_startups "
    "(name, site) "
    "VALUES (%s, %s)"
)

print("Uploading information to the database.")

for startup_data in parsed_startups:
    cursor.execute(command, startup_data)

print("The upload is completed. Finishig work.")

connection.commit()
cursor.close()
connection.close()
driver.close()
