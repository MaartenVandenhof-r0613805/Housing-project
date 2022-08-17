import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.chrome.service import ChromeService, Service
from webdriver_manager.chrome import ChromeDriverManager

from bs4 import BeautifulSoup
import pandas as pd
import time


class Scraper():
    def __init__(self, urlBase, driverName):
        self.UrlBase = urlBase
        self.DriverName = driverName
    def setUrlBase(self, urlBase):
        self.UrlBase = urlBase
    def setDriverName(self, driverName):
        self.DriverName = driverName
    def setchecker(self, checker):
        self.Checker = checker

    def setDriver(driverName):
        if (driverName=='Chrome'):
            driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
            return driver
        else:
            pass
    def scrapeHeader():
        pass
    def scrapeTable():
        pass

    def getLinks():
        pass
    def checkLink():
        pass
    

class Checker():
    def __init__(self) -> None:
        pass
    def check4Robot(driver):
        pass
    def check4Iterations(driver, firstPageElement):
        pass
    def check4Emptypage(driver, container_root):
        pass

