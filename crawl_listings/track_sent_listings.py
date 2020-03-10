import os
import sys
import os.path
import csv
import datetime
import psutil
import random
import json
import pandas as pd
import numpy as np
from sys import exit
from time import sleep
from re import sub
from fake_useragent import UserAgent
from datetime import datetime
import pytz

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options

from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementNotVisibleException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.common.proxy import Proxy

from extract.extract_data import check_off_market
from util import start_firefox

trulia = "https://www.trulia.com"
geckodriver_path = '/usr/bin/geckodriver'
adblock_path = "/home/ubuntu/CBSA-Discrimination/stores/adblock_plus-3.3.1-an+fx.xpi"
uBlock_path = "/home/ubuntu/CBSA-Discrimination/stores/uBlock0@raymondhill.net.xpi"

if len(sys.argv) != 3:
    print("Include round_number and start point as argument")
    exit()

def update_row(idx, destination, round_num):
    url = rentals["URL"][idx]
    day = int(rentals["Days_crawled"][idx]) + 1
    print("Round {} -- Index {} -- URL: {}".format(round_num, idx, url))
    result = open_page(url)
    if result == 0:
        is_off_market = check_off_market(driver)
        rentals.at[idx, "Day_" + str(day)] = is_off_market
        rentals.at[idx, "Days_crawled"] = day
        rentals.to_csv(destination, index=False)
    finish_listing(driver, round_num, idx)

def open_page(url):
    driver.delete_all_cookies()
    d = {}
    waiting = True
    while(waiting):
        try:
            driver.get(url)
            waiting = False
        except:
            print("Error getting URL. Trying again in 30 seconds...")
            sleep(30)
    print(driver.title)
    sleep(3)
    if "Not Found" in driver.title:
        print ("404 in trulia")
        return 1
    elif "Trulia" in driver.title:
        print ("Successfully loaded URL")
        return 0
    else:
        print ("Being blocked from accessing Trulia. Restarting...")
        driver.quit()
        sleep(random.randint(10,40))
        restart("logfile", round_num, start)

def finish_listing(driver, round_num, idx):
    with open("logfile", "ab") as log:
        filewriter = csv.writer(log, delimiter = ',', quoting = csv.QUOTE_MINIMAL)
        filewriter.writerow([round_num, idx])

    #driver.close()
    driver.switch_to_window(driver.window_handles[0])
    sleep(random.randint(10,40))

def start_driver():
    driver = start_firefox(trulia, geckodriver_path, adblock_path, uBlock_path)
    sleep(5)

    try:
        driver.switch_to_window(driver.window_handles[1])
        driver.close()
        driver.switch_to_window(driver.window_handles[0])
        return driver
    except:
        print ("Switching window failed??")
        driver.quit()
        restart("logfile", round_num, start)

def restart(crawler_log, round_num, start):
    print("argv was",sys.argv)
    print("sys.executable was", sys.executable)
    print("Restarting")

    sleep(5)
    try:
        for proc in psutil.process_iter():
            if "firefox" in proc.name():
                proc.kill()
            if "geckodriver" in proc.name():
                proc.kill()

    except:
        print("Error killing processes. Continuing")
        
    if os.path.isfile(crawler_log) == True:
        with open(crawler_log) as f:
            lines = f.readlines()
    else:
        lines = [str(round_num) + "," + str(start)]
   
    arg = sys.argv
    current = lines[-1].rstrip()
    print(current)

    if os.path.isfile(crawler_log):
        arg[2] = str(int(current.split(',')[1]) + 1)
    else:
        arg[2] = current.split(',')[1]

    print(arg)
    os.execv(sys.executable, ['python'] + arg)


round_num = int(sys.argv[1])
round_max = 7
start = int(sys.argv[2])
for curr_round in range(round_num, round_max + 1): 
    round_dir = "../rounds/round_{}/".format(curr_round)
    rentals_path = round_dir + "round_{}_rentals.csv".format(curr_round)
    rentals = pd.read_csv(rentals_path)
    end = rentals.shape[0]
    tz = pytz.timezone('America/Chicago')
    now = datetime.now(tz)
    print("Starting time = {}".format(now.strftime("%m/%d %H:%M:%S")))
    print("Collecting info from {} to {} for round {}".format(start, end, curr_round))
    driver = start_driver()
    if driver != None:
        print("Driver Successfully Started")
    for i in range(start, end):
        update_row(i, rentals_path, curr_round)
    now = datetime.now(tz)
    print("Finished round {} at {}".format(curr_round, now.strftime("%m/%d %H:%M:%S")))
    start = 0

