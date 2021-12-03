from bs4 import BeautifulSoup

import requests
import urllib3


"""
requests.get не будет возвращать ответ сайта, если у того не будет SSL
Строка ниже отключает такую защиту.
"""
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL = "https://generation-startup.ru"
"""URL-Адрес сайта, который мы будем парсить."""


page = requests.get(f"{URL}/calendar", verify=False)
"""
Результат запроса на сайт.

Имеет тип Response. При выводе будет выводить свой код.

Чтобы достать "начинку" сайта - нужно писать `page.content`.

`verify=False` позволяет нам делать запросы на сайты без SSL.
Это опасно, но у этого сайта истёк сертификат.
"""


soup = BeautifulSoup(page.content, "html.parser")
"""
Готовим из начинки сайта самый настоящий суп.

Это объект класса `BeautifulSoup`, имеющий свои методы для парсинга.
"""


events = soup.find_all("a", {"class": "events-startups__item-wrap"})
"""
Список ивентов, найденных на главной странице сайта.
"""

for event in events:
    event_soup = BeautifulSoup(str(event), "html.parser")
    event_url = URL + event_soup.find("a", href=True)["href"]

    event_page = requests.get(event_url, verify=False)
    event_page_cont = BeautifulSoup(event_page.content, "html.parser")
    event_data = event_page_cont.find_all("div", {"class": "events-detail-info__item"})

    event_name = event_page_cont.select("h1", {"class": "h1 active"})[0].text.strip()

    result = event_name + "\n"

    for data in event_data:
        name = data.find("div", {"class": "events-detail-info__name"}).text.strip()
        desc = data.find("div", {"class": "events-detail-info__desc"}).text.strip().replace("\n", "")  # Костыль
        result += f"{name} => {desc}\n"

    print(result)
