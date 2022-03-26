import time

from typing import Tuple

from bs4 import BeautifulSoup

from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import NoSuchElementException

from frogger.script import Script
from frogger.controller import Controller


class RVCScript(Script):

    _name = "RVC script."
    _description = "Script for parcing rusventure.ru"
    _author = "Frogger Team"

    def __init__(self, controller: Controller):
        self.controller = controller
        self.site_url = "https://www.rusventure.ru"
        self.sleep_time = 5

    def truncate_table(self) -> None:
        """Truncates table for RBScript."""
        connection, cursor = self.controller.create_db_conn_and_cursr()
        cursor.execute("truncate table src_rvc")
        connection.commit()
        cursor.close()
        connection.close()

    def show_all_events(self, driver: WebDriver) -> None:
        """Parses site rusventure.ru with provided driver and returns raw events list."""
        driver.get(f"{self.site_url}/calendar")

        last_height = driver.execute_script("return document.body.scrollHeight;")

        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(self.sleep_time)

            try:
                sumbit_button = driver.find_element_by_id("load-more")
                sumbit_button.click()
            except ElementNotInteractableException:
                print("Buttons isn't interactable.")
            except NoSuchElementException:
                print("Button not found.")

            time.sleep(self.sleep_time)

            new_height = driver.execute_script("return document.body.scrollHeight;")
            if new_height == last_height:
                break
            last_height = new_height

    def get_events(self, driver: WebDriver):
        soup = BeautifulSoup(driver.page_source, "html.parser")
        events = soup.find("article", {"class": "span4 no-padding-left data-href"})
        print(f"EVENTS == {type(events)}")
        return events

    def get_parsed_events(self, driver: WebDriver, events) -> list[Tuple[str, str, str, str]]:
        parsed_events = []

        for event in events:
            soup = BeautifulSoup(str(event), "html.parser")
            url = self.site_url + soup.find("div", {"class": "title"}).findChild("a")["href"]

            driver.get(url)

            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                time.sleep(self.sleep_time)

                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            event_soup = BeautifulSoup(driver.page_source, "html.parser")

            name = event_soup.select("h1", {"class": "color4"})[0].text.strip()

            article = event_soup.find("div", {"class": "span4"}).findChild("article")

            date = article.find("h3", {"class": "margin-bottom"}).get_text()
            date = " ".join(date.split())

            preview = article.find("div", {"class": "title event_preview"})  # .findChild("span")
            site = preview.find("a")['href']

            description = article.find("div", {"class": "margin-bottom-40px"}).get_text()

            event_data = (name, date, site, description)
            parsed_events.append(event_data)

        return parsed_events

    def send_to_database(self, parsed_events: list[Tuple[str, str, str, str]]) -> None:
        """Sends event's information to database."""
        connection, cursor = self.controller.create_db_conn_and_cursr()

        insert_event_command = """
        INSERT INTO src_rvc
        (name, event_date, site, descr)
        VALUES (%s, %s, %s, %s)
        """

        for event in parsed_events:
            cursor.execute(insert_event_command, event)

        cursor.callproc("f_get_rvc")
        connection.commit()

        cursor.close()
        connection.close()

    def run(self) -> None:
        self.truncate_table()
        events = self.show_all_events(self.controller.driver)
        events_parsed = self.get_parsed_events(events)
        self.send_to_database(events_parsed)


def setup(controller: Controller) -> None:
    """Loads Script to controller."""
    controller.add_script(RVCScript(controller))
