import time

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver

from bs4 import BeautifulSoup, ResultSet
from bs4.element import Tag

from frogger.controller import Controller
from frogger.script import Script


class ChangeScript(Script):

    _name = "Changellenge.com script"
    _description = "Script for parsing Changellenge.com"
    _author = "Frogger Team"

    def __init__(self, controller: Controller):
        self.controller = controller

    def is_database_working(self) -> bool:
        """Tests connection to database."""
        try:
            connection, cursor = self.controller.create_db_conn_and_cursr()
            cursor.close()
            connection.close()
            return True
        except Exception as excpt:
            print(excpt)
            return False

    def truncate_table(self) -> None:
        """Truncates table in database."""

        connection, cursor = self.controller.create_db_conn_and_cursr()
        cursor.execute("truncate table src_change_event")
        connection.commit()
        cursor.close()
        connection.close()

    def load_all_events(self, driver: WebDriver) -> None:
        """Loads additional events in page for full loading."""

        while True:
            try:
                driver.find_element(By.CLASS_NAME, "new-events__load_more").click()
            except NoSuchElementException:
                break
            time.sleep(5)

    def get_events(self, driver: WebDriver) -> ResultSet[Tag]:
        """Gets events from page."""

        driver.get("https://changellenge.com/event/")
        soup = BeautifulSoup(driver.page_source, "html.parser")

        events = soup.find("ul", {"class": "new-events__tab new-events__tab--active"}) \
            .find_all("div", {"class": "new-events-card__content"})

        return events

    def parse_events(self, events: ResultSet[Tag]) -> list:
        """Parses events."""

        parsed_events = []

        for event in events:
            name = event.find("h4",   {"class": "new-events-card__title"}).get_text()

            link = event.find("a").get("href")
            if link[0:8] != "https://" and link[0:7] != "http://":
                link = "https://changellenge.com" + link

            day = event.find("div", {"class": "new-events-card__data-checkin"}).find("span").get_text()

            month = event.find("div", {"class": "new-events-card__data-checkin"}) \
                .find("div", {"class": "new-events-card__date"}) \
                .find("div", {"class": "new-events-card__date"}) \
                .get_text()

            event_type = event.find("span", {"class": "new-events-card__type"}).get_text()

            parsed_events.append((name, day, link, event_type, month))

        return parsed_events

    def load_to_database(self, events: list) -> None:
        "Loads provided events to database."

        connection, cursor = self.controller.create_db_conn_and_cursr()

        command = """
        INSERT INTO src_change_event
        (name, event_day, site, event_type, event_month)
        VALUES (%s, %s, %s, %s, %s)
        """

        for event in events:
            cursor.execute(command, event)
            connection.commit()

        cursor.callproc("f_get_change_event")
        connection.commit()

        cursor.close()
        connection.close()

    def run(self) -> None:
        """Runs script."""

        if self.is_database_working() is False:
            print("database didn't work. Returning.")
            return

        self.truncate_table()
        events = self.get_events(self.controller.driver)
        parsed_events = self.parse_events(events)

        self.load_to_database(parsed_events)


def setup(controller: Controller) -> None:
    """Loads Script to controller."""
    controller.add_script(ChangeScript(controller))
