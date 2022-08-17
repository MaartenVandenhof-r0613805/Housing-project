import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import pandas as pd
import time



container_root = '//*[@id="wrapper"]/div[3]/div[4]/div[2]/div[2]'
first_element = '//*[@class="property-item_link"]'

address_tag = '//*[@id="main-features"]/div/div[1]/div[1]/h2/span[1]'
table_root = '//*[@id="tab-detail"]/div[2]/div/div[4]/div/div' #'//*[@class="block-list"]'

# The two main functions to use in the UI
# 1 fetchlinks will fetch all links on the main page
#   for a site with given detail using the required river
#   The function returns a list of links
# 2 checkLink will get all values for a give link
#   This is done link per link to allow for progression checks
#   the function returns a pandas dataframe with known column values


def fetchLinks(driver,detail,contracttype):
    driver = setDriver(driver)
    
    URL_base = 'https://www.zimmo.be/nl/'+str(detail)+str(contracttype)

    firstPageElement = None
    links = []
    halt = False
    page = 1
    while(halt==False):
        URL = str(URL_base)+'?pagina='+str(page)+'#gallery'

        try:
            driver.get(URL)
        except:
            print('driver.get error')
        else:
            if(check4robot(driver)):break
            halt, firstPageElement = check4iterations(driver, firstPageElement)
            if(halt):break
            if(check4emptypage(driver, container_root)):break

            root = driver.find_element(By.XPATH, container_root)
            items = root.find_elements(By.CLASS_NAME, 'property-item')
            for item in items:
                link = item.find_element(By.XPATH, 'a[1]').get_attribute('href')
                links.append(link)
            
            page += 1
    
    return links


def checkLink(driver,URL):
    #driver = setDriver(driver)
    halted = False
    firstPageElement = None
    
    try:
        driver.get(URL)
    except:
        print('driver.get error')
    else:
        if(check4robot(driver)):halted=True
        halt, firstPageElement = check4iterations(driver, firstPageElement)
        if(halt):halted = True
        if(check4emptypage(driver, container_root)):halted=True

        variableDict = {
            "site":"Zimmo",
            "itemtype":"?",
            "rent":-1,
            "monthly_fee":-1,
            "postal":-1,
            "city":"?",
            "street":"",
            "house_nr":-1,
            "bus_nr":-1,
            "bathrooms":-1,
            "bedrooms":-1,
            "surface":-1,
            "epc_class":"?",
            "rooms":-1,
            "link":URL
        }
    
        variableDict = scrapeHeader(driver,variableDict)
        variableDict = scrapeTable(driver,variableDict)

        columns = ['site','itemtype','rent','monthly_fee','postalcode','city','street','house_number','bus_number','bathrooms','bedrooms','surface','epc_class','link']
        dataframe = pd.DataFrame(columns=columns)
        data = [variableDict['site'],variableDict['itemtype'],variableDict['rent'],variableDict['monthly_fee'],variableDict['postal'],variableDict['city'],variableDict['street'],variableDict['house_nr'],variableDict['bus_nr'],variableDict['bathrooms'],variableDict['bedrooms'],variableDict['surface'],variableDict['epc_class'],variableDict['link']]
        dataframe.loc[0 if pd.isnull(dataframe.index.max()) else dataframe.index.max() + 1] = data
        
        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_rows', None)
        pd.options.display.max_colwidth

        return dataframe

        







    

def check4robot(driver):
    try:
        currentURL = driver.current_url
        if(currentURL.startswith('https://validate.perfdrive.com/')):
           return True
        else:
            return False
    except:
        print('Robot occured')
        return True

def check4iterations(driver, firstPageElement):
    try:
        root = driver.find_element(By.XPATH, first_element).get_attribute("href")
    except:
        halt = True
        print('Iteration occured')
    else:
        if(firstPageElement==str(root)):
            halt = True
        elif(firstPageElement==None):
            halt = False
            firstPageElement = str(root)
        else:
            halt = False
    return halt, firstPageElement

def check4emptypage(driver, container_root):
    try:
        root = driver.find_element(By.XPATH, container_root)
    except:
        print('EmptyPage occured')
        return True
    else:
        return False


def setDriver(driver):
    path = 'C:\Program Files\SeleniumDrivers'
    path = path+str(driver)+'.exe'
    ser = Service(path)
    op = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=ser, options=op)
    return driver

def scrapeHeader(driver,variableDict):
    address = driver.find_element(By.XPATH, address_tag)
    address = address.get_attribute("innerHTML")
    variableDict["street"],variableDict["postal"],variableDict["city"],variableDict["house_nr"],variableDict["bus_nr"] = standardizeAddress(str(address).split())

    variableDict["itemtype"] = driver.find_element(By.XPATH,'//*[@id="main-features"]/div/div[2]/div[1]/ul/li[3]/span').get_attribute('innerHTML')
    
    return variableDict

def scrapeTable(driver,variableDict):
    sections = driver.find_elements(By.XPATH, table_root+'/*')
    for section in sections:
        #rows = section.find_elements(By.XPATH,'section/div/div[2]/*')
        try:
            rowlist = section.find_element(By.CLASS_NAME,'info-list')
        except:
            break
        else:
            rows = rowlist.find_elements(By.XPATH,'*')
            
            for row in rows:
                try:
                    subject = row.find_element(By.XPATH,'div[1]').get_attribute('innerHTML')
                    value = row.find_element(By.XPATH,'div[2]').get_attribute('innerHTML').replace(" ","").replace("\n","").replace("€","").replace("m²","").replace("kWh/","")
                except:
                    driver.quit()
                    break

                if(subject=="Prijs"):variableDict["rent"]=value
                if(subject=="Maandelijks"):variableDict["monthly_fee"]=value
                if(subject=="Woonopp."):variableDict["surface"]=value
                if(subject=="Aantal badkamers"):variableDict["bathrooms"]=value
                if(subject=="Aantal slaapkamers"):variableDict["bedroom"]=value
                if(subject=="Energieklasse"):variableDict["epc_class"]=EPCvalue2class(value)
                if(subject=="EPC-waarde" and variableDict["epc_class"] == "?" and '<a' not in value):variableDict["epc_class"]=standardizeEPC(value)
                #if(subject==""):variableDict[""]=value
    
    return variableDict

def EPCvalue2class(value):
    EPC = "?"
    if value == '<imgclass="energie-label"src="/public/images/energielabels/epc_e.svg">':EPC = 'E'
    if value == '<imgclass="energie-label"src="/public/images/energielabels/epc_d.svg">':EPC = 'D'
    if value == '<imgclass="energie-label"src="/public/images/energielabels/epc_c.svg">':EPC = 'C'
    if value == '<imgclass="energie-label"src="/public/images/energielabels/epc_b.svg">':EPC = 'B'
    if value == '<imgclass="energie-label"src="/public/images/energielabels/epc_a.svg">':EPC = 'A'
    if value == '<imgclass="energie-label"src="/public/images/energielabels/epc_a+.svg">':EPC = 'A+'
    return EPC
    

def standardizeEPC(epc_value):
    try:
        epc_value = int(epc_value)
    except:
        epc_value = epc_value
    else:
        if(epc_value<=0):epc_class='A+'
        if(epc_value<100 and epc_value>=0):epc_class='A'
        if(epc_value<200 and epc_value>=100):epc_class='B'
        if(epc_value<300 and epc_value>=200):epc_class='C'
        if(epc_value<400 and epc_value>=300):epc_class='D'
        if(epc_value<500 and epc_value>=400):epc_class='E'
        if(epc_value>=500):epc_class='F'
    return epc_value

def standardizeAddress(st):
    if '/' in st: st.remove('/')

    for i in range(len(st)):
        if ',' in st[i]: st[i] = st[i].replace(',','')
        if '.' in st[i]: st[i] = st[i].replace('.','')

    street = '?'
    postal = -1
    city = '?'
    house_nr = -1
    bus_nr = -1

    if(len(st)==3):
        street = st[0]
        postal = int(st[1])
        city = st[2]

    if(len(st)==4):
        street = st[0]
        house_nr = st[1]
        postal = int(st[2])
        city = st[3]

    if(len(st)==5):
        while(True):
            if(st[2][0]=='0'):
                st[2]=st[2][1:]
            else:
                break
        street = st[0]
        house_nr = st[1]
        bus_nr = st[2]#int(st[2])
        postal = int(st[3])
        city = st[4]
    return street,postal,city,house_nr,bus_nr
