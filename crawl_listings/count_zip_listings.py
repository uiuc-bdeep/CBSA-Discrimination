"""Summary
Input: file containing zipcodes for each cbsa
Output: file containing counts of listings for each zip
"""
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
import re
from re import sub
from fake_useragent import UserAgent

#from pyvirtualdisplay import Display
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

from util import start_firefox, restart

trulia = "https://www.trulia.com"
ZIP_URL_PRE = 'https://www.trulia.com/for_rent/'
ZIP_URL_SUF = '_zip/'#3_beds/2_baths/'
ZIP_URL_PAGE = '_p'

def url_from_zipcode(zipcode):
    if int(zipcode) < 10000:
        zipcode = '0' + str(zipcode)
    url = ZIP_URL_PRE + str(zipcode) + ZIP_URL_SUF
    return url

def main(input_file, dest, start, crawler_log, geckodriver_path, adblock_path, uBlock_path):
	"""Main function to do the crawling
	
	Args:
	    input_file (String): Name of the input file
	    output_file (String): Name of the output file
	    start (int): Starting index of the crawling
	    end (int): Ending index of the crawling
	    crawler_log (String): Name of the log
	    geckodriver_path (String): Path to the geckodriver
	    adblock_path (String): Path to the adblock
	    uBlock_path (String): Path to the uBlock
	"""
	try:
		driver = start_firefox(trulia, geckodriver_path, adblock_path, uBlock_path)
		sleep(5)
		driver.switch_to_window(driver.window_handles[1])
		driver.close()
		driver.switch_to_window(driver.window_handles[0])
	except:
		print ("Not able to start Firefox. Restarting...")
		sleep(5)
		driver.quit()
		restart(crawler_log, start)

	df = pd.read_csv(input_file)
        end = df.shape[0]

        if int(start) == 0:
            with open(dest, "a") as f:
                writer = csv.writer(f)
                writer.writerow(['CBSA', 'ZIP', 'num_listings'])


	#try:
	for i in range(int(start), int(end)):
            zipcode = df.at[i, "ZIP"]
            cbsa = df.at[i, "CBSA"]
	    driver.delete_all_cookies()

	    crawled_trulia = True
            url = url_from_zipcode(zipcode)
            loading = True
            while(loading):
                try:
	            driver.get(url)
                    loading = False
                except:
                    print("Error loading URL. Most likely timing out. Trying again soon...")
                    sleep(random.randint(8, 12))
	    #print(driver.title)
	    sleep(3)
            if "this page" in driver.title.lower():
	    	print ("Being blocked from accessing Trulia. Restarting...")
                driver.quit()
                sleep(random.randint(10,40))
    		restart(crawler_log, start)
            else:
                print("{}: Zipcode {}".format(i, zipcode))
                num_listings  = list(set(re.findall(r'\w*[0-9]* rentals? available on Trulia',driver.page_source)))

            if num_listings:
                num_listings = int(num_listings[0].split(' ')[0])
            else:
                num_listings = 0

            print("\tNumber of listings: " + str(num_listings))
            with open(dest, "a") as f:
                writer = csv.writer(f)
                writer.writerow([cbsa, zipcode, num_listings])

	    with open(crawler_log, "ab") as log:
		filewriter = csv.writer(log, delimiter = ',', quoting = csv.QUOTE_MINIMAL)
		filewriter.writerow([i])
				
	    #driver.close()
	    #driver.switch_to_window(driver.window_handles[0])
            sleep(random.randint(2,5))

	#except:
	#    driver.quit()
	#    restart(crawler_log, start)

	driver.quit()

if __name__ == "__main__":
	import argparse
	import platform
	from argparse import RawTextHelpFormatter

	parser = argparse.ArgumentParser(description = 'Crawl Trulia apartment listings and ejscreen given Trulia URLs or Address (optional)', formatter_class=RawTextHelpFormatter, epilog = "Note that input_file must be a CSV file that contains a column 'URL'. \nIt can also contain (A)ddress or (L)atLon")
	#parser.add_argument("type", help = "Whether the input file contains column (A)ddress or (L)atLon", choices = ["U", "A", "L"], nargs = "+")
	parser.add_argument("input_file", help = "Path of input file")
	parser.add_argument("output_file", help = "Path of output file")
	parser.add_argument("log", help = "Name of the log")
	parser.add_argument("start", help = "Start of Input file", type = int)

	args = parser.parse_args()

        root = '/home/ubuntu/CBSA-Discrimination/'

	geckodriver_path = root + 'stores/geckodriver'
	if not os.path.exists(geckodriver_path):
		sys.exit("geckodriver does not exist at {}\nAborting.".format(geckodriver_path))

	adblock_path = root + "stores/adblock_plus-3.3.1-an+fx.xpi"
	if not os.path.exists(adblock_path):
		sys.exit("adblock_plus does not exist at {}\nAborting.".format(adblock_path))

	uBlock_path = root + "stores/uBlock0@raymondhill.net.xpi"
	if not os.path.exists(uBlock_path):
		sys.exit("uBlock does not exist at {}\nAborting.".format(uBlock_path))

	try:
		main(args.input_file, args.output_file, args.start, args.log, geckodriver_path, adblock_path, uBlock_path)
	except:
		for proc in psutil.process_iter():
			if proc.name() == "firefox" or proc.name() == "geckodriver":
				proc.kill()
		raise
