import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time

# selenium 4
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


container_root = '//*[@id="gatsby-focus-wrapper"]/div/div[2]/div[2]/div[2]'
first_element = '//*[@id="gatsby-focus-wrapper"]/div/div[2]/div[2]/div[2]/div[2]/div[1]/div/a'

address_tag = '//*[@id="gatsby-focus-wrapper"]/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div[last()-1]'
#'//*[@id="gatsby-focus-wrapper"]/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div[4]'
table_root = '//*[@id="gatsby-focus-wrapper"]/div/div[2]/div[6]/div'
# '//*[@id="gatsby-focus-wrapper"]/div/div[2]/div[6]/div'

# The two main functions to use in the UI
# 1 fetchlinks will fetch all links on the main page
#   for a site with given detail using the required river
#   The function returns a list of links
# 2 checkLink will get all values for a give link
#   This is done link per link to allow for progression checks
#   the function returns a pandas dataframe with known column values


def fetchLinks(driver,detail,contracttype):
    driver = setDriver(driver)

    #https://www.century21.be/nl/zoeken?agency=VFqBaHQBXt-nJTnOjKXG&listingType=FOR_RENT&location=3000
    # FOR_RENT  FOR_SALE
    # only postal code
    
    URL_base = 'https://www.century21.be/nl/zoeken?'+'listingType='+str(contracttype)+'&location='+str(detail)#+'&type=APARTMENT'

    firstPageElement = None
    links = []
    halt = False
    page = 1
    while(halt==False):

        driver.implicitly_wait(0.4)
        URL = str(URL_base)+'&page='+str(page)
        
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
            items = root.find_elements(By.XPATH, 'div[2]/*')
            for item in items:
                link = item.find_element(By.CLASS_NAME, 'gatsbyLink').get_attribute('href')
                links.append(link)
            
            page += 1
    
    return links


def checkLink(driver,URL):
    driver.implicitly_wait(0.4)
    
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
        print(root)
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
    #driver = webdriver.Chrome(service=ser, options=op)
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

    return driver

def scrapeHeader(driver,variableDict):
    address_a = driver.find_element(By.XPATH, address_tag+'/p[1]/span')
    address_a = address_a.get_attribute("innerHTML")
    address_b = driver.find_element(By.XPATH, address_tag+'/p[2]/span')
    address_b = address_b.get_attribute("innerHTML")
    address = str(address_a)+' '+str(address_b)
    variableDict["street"],variableDict["postal"],variableDict["city"],variableDict["house_nr"],variableDict["bus_nr"] = standardizeAddress(str(address).split())

    variableDict["itemtype"] = driver.find_element(By.XPATH,'//*[@id="gatsby-focus-wrapper"]/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div[1]/span').get_attribute('innerHTML')

    variableDict["rent"] = driver.find_element(By.XPATH,'//*[@id="gatsby-focus-wrapper"]/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div[last()]/span').get_attribute('innerHTML').replace(' ','').replace('€','').replace('.','')
    return variableDict

def scrapeTable(driver,variableDict):
    sections = driver.find_elements(By.XPATH, table_root+'/*')

    for section in sections:
        innersections = section.find_elements(By.XPATH,'*')
    
        for innersection in innersections:
            rows = innersection.find_elements(By.XPATH,'div[1]/*')
            
            for row in rows[1:]:
                try:
                    subject = row.find_element(By.XPATH,'div[1]/div[1]/span').get_attribute('innerHTML')
                    value = row.find_element(By.XPATH,'div/div[2]/span').get_attribute('innerHTML').replace(" ","").replace("\n","").replace("€","").replace("m²","").replace("kWh/","")
                        
                except:
                    break

                else:
                    if(subject=="Maandelijks"):variableDict["monthly_fee"]=value
                    if(subject=="Bewoonbare oppervlakte"):variableDict["surface"]=value
                    if(subject=="Aantal badkamers"):variableDict["bathrooms"]=value
                    if(subject=="Aantal slaapkamers"):variableDict["bedrooms"]=value
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
    #['Parijsstraat', '38', '3000', 'Leuven,', 'België']
    
    if '/' in st: st.remove('/')
    

    for i in range(len(st)):
        if ',' in st[i]: st[i] = st[i].replace(',','')
        if '.' in st[i]: st[i] = st[i].replace('.','')


    for i in range(len(st)):
        if st[i][0].isdigit():
            st = [' '.join(st[0:i])]+st[i:-1]
            break      
        
    street = '?'
    postal = -1
    city = '?'
    house_nr = -1
    bus_nr = -1

    # ['Herbert Hooverplein', '21', '3000', 'Leuven']
    if(len(st)==3):
        street = st[2]
        postal = int(st[0])
        city = st[1]

    if(len(st)==4):
        street = st[0]
        house_nr = st[1]
        postal = int(st[2])
        city = st[3]

    if(len(st)==5):
        while(st[2][0]=='0'):
            st[2]=st[2][1:]
        street = st[0]
        house_nr = st[1]
        bus_nr = st[2]
        postal = int(st[3])
        city = st[4]
    return street,postal,city,house_nr,bus_nr


links = fetchLinks('\chromedriver','3000','FOR_RENT')
#print(links)


driver = setDriver('\chromedriver')
for link in links:#[0:20]:
    #checkLink('\chromedriver',link)
    print("Check for: ",link)
    print(checkLink(driver,link))
driver.quit()

driver = setDriver('\chromedriver')
checkLink(driver,'https://www.century21.be/nl/pand/te-huur/commercieel-pand/leuven/RV0--38Bd9kxpwemLOsP')
driver.quit()


