from time import sleep
from selenium import webdriver
from pyvirtualdisplay import Display
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementNotVisibleException
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import re
import os
import sys
import pandas as pd
import random
from datetime import date, timedelta, datetime
import pytz

ZIP_URL_PRE = 'https://www.trulia.com/for_rent/'
ZIP_URL_SUF = '_zip/'#3_beds/2_baths/'
ZIP_URL_PAGE = '_p'

root = '/home/ubuntu/CBSA-Discrimination/'
cbsa_df = pd.read_csv(root + 'rounds/cbsa_zipcodes_full.csv')
dest = root + 'rounds/cbsa_zipcodes_subset.csv'
sample_size = 0.03

def start_driver():
    print("Starting Driver")
    options = Options()
    options.add_argument("--headless")
    fp = webdriver.FirefoxProfile()
    #fp.set_preference("general.useragent.override", UserAgent().random)
    fp.update_preferences()
    driver = webdriver.Firefox(firefox_profile = fp, firefox_options = options, capabilities = webdriver.DesiredCapabilities.FIREFOX, executable_path = root + 'stores/geckodriver')
    #driver.set_page_load_timeout(30) # set a time out for 30 secons
    driver.maximize_window()
    display  = Display(visible=0, size=(1024, 768)) # start display
    display.start() # start the display
    return driver

def count_zip_listings(driver, zipcode):
    if int(zipcode) < 10000:
        zipcode = '0' + str(zipcode)
    zip_url = ZIP_URL_PRE + str(zipcode) + ZIP_URL_SUF
    driver.get(zip_url)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    if driver.title == 'Access to this page has been denied.':
        try_counter = 0
        print(driver.title)
        while driver.title == 'Access to this page has been denied.':
            sleep(random.randint(20,40))
            driver.get(zip_url)
            if try_counter > 5:
                print("Access failed over 5 times in a row")
                return 0
            try_counter += 1
    num_listings  = list(set(re.findall(r'\w*[0-9]* rentals? available on Trulia',driver.page_source)))
    if num_listings:
        num_listings = int(num_listings[0].split(' ')[0])
    else:
        num_listings = 0
    return num_listings

def seperate_by_cbsa(cbsa_df):
    cbsa_dic = {}
    for i in range(length):
        cbsa = cbsa_df.at[i, "CBSA"]
        zipcode = cbsa_df.at[i, "ZIP"]
        if cbsa in cbsa_dic.keys():
            cbsa_dic[cbsa].append(str(zipcode))
        else:
            cbsa_dic[cbsa] = [zipcode]
    for key in cbsa_dic.keys():
        random.shuffle(cbsa_dic[key])
    return cbsa_dic

def select_zips_from_cbsa(driver, cbsa, zipcode_list):
    length = len(zipcode_list)
    print("{} contains {} zipcodes".format(cbsa, length))
    selections = []
    for zipcode in zipcode_list:
        if len(selections) >= (length * sample_size):
            break
        num_listings = count_zip_listings(driver, zipcode)
        if num_listings > 0:
            selections.append((zipcode, num_listings))
            print("\tZipcode {} has {} listings".format(zipcode, num_listings))
        else:
            print("\tZipcode {} has no listings - not adding to list".format(zipcode))
    print("\tSelected {} total listings".format(len(selections)))
    return selections

#length = cbsa_df.shape[0]
#print("Total number of zipcodes = {}".format(length))
#cbsa_dic = seperate_by_cbsa(cbsa_df)
#driver = start_driver()
#selections = {}
#for cbsa in cbsa_dic.keys():
#    selections[cbsa] = select_zips_from_cbsa(driver, cbsa, cbsa_dic[cbsa])
#print(selections)
#driver.quit()
#display.stop()

