import importlib
import inspect
import json
import pkgutil

from importlib.machinery import ModuleSpec
from pathlib import Path
from typing import Iterator, Tuple

from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

import mysql.connector
from mysql.connector import MySQLConnection
from mysql.connector.cursor import MySQLCursor

from frogger import scripts
from frogger.script import Script


class Controller:
    """
    Main controller.

    Checks, launches, assists and manage Scripts.
    """

    def __init__(self):
        self._scripts: list[Script] = []

    @property
    def scripts(self):
        """List of loaded to Controller sctipts."""
        return self._scripts

    @property
    def driver(self):
        """Controller's driver."""
        return self._driver

    def create_driver(self) -> None:
        """Creates Firefox driver."""
        service = Service(GeckoDriverManager(log_level=30).install())
        options = FirefoxOptions()
        options.add_argument("--headless")
        self._driver = webdriver.Firefox(service=service, options=options)

    def walk_scripts(self) -> Iterator[str]:
        """
        Walks thought script's folder and returns Iterator with paths.

        If module starts with `_` - we skipping this file.
        """

        def on_error(name: str):
            raise ImportError(name=name)

        def unqualify(name: str) -> str:
            """Return an unqualified name given a qualified module/package `name`."""
            return name.rsplit(".", maxsplit=1)[-1]

        for module in pkgutil.walk_packages(scripts.__path__, f"{scripts.__name__}.", onerror=on_error):
            if unqualify(module.name).startswith("_"):
                continue

            if module.ispkg:
                imported = importlib.import_module(module.name)
                if not inspect.isfunction(getattr(imported, "setup", None)):
                    continue

            yield module.name

    def add_script(self, script: Script) -> None:
        """Adds provided `script` to Contoller."""
        self._scripts.append(script)

    def load_script(self, script_path: str) -> None:
        """
        Loads script by provided `script_path`.

        Path shoul looks like frogger.AAA.BBB.CCC
        """
        spec: ModuleSpec = importlib.util.find_spec(script_path)
        lib = importlib.util.module_from_spec(spec)

        spec.loader.exec_module(lib)

        setup_func = getattr(lib, "setup")
        setup_func(self)

    def load_scripts(self) -> None:
        """Loads all known scripts."""
        scripts = set(self.walk_scripts())
        for script in scripts:
            self.load_script(script)

    @staticmethod
    def create_db_connection() -> MySQLConnection:
        """Creates and returns mysql connection."""
        try:
            file = Path("config/database.json").open("r", encoding="UTF-8")
            config = json.load(file)
            database = config["database"]
            user = config["user"]
            host = config["host"]
            password = config["password"]
            return mysql.connector.connect(user=user, password=password, host=host, database=database)
        except FileNotFoundError:
            print("Missing database config file.")

    @staticmethod
    def create_db_cursor(connection: MySQLConnection) -> MySQLCursor:
        """Creates `MySQLCursor` by provided `MySQLConnection`."""
        return connection.cursor()

    def create_db_conn_and_cursr(self) -> Tuple[MySQLConnection, MySQLCursor]:
        """Creates and returns `MySQLConnection` with `MySQLCursor`."""
        connection = self.create_db_connection()
        cursor = self.create_db_cursor(connection)
        return connection, cursor
