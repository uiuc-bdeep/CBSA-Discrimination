import re
import os
import csv 
import sys
import math
import random
import psutil
import pandas as pd 
from time import sleep 
from selenium import webdriver
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
from datetime import date, timedelta, datetime
from util import start_firefox, wait_and_get
import pytz

def restart(crawler_log, start, increment):
	print("argv was",sys.argv)
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

	arg = sys.argv

        if os.path.isfile(crawler_log) == True:
                with open(crawler_log) as f:
                        lines = f.readlines()
		idx = int(lines[-1].rstrip())
		if increment:
			idx += 1
		arg[-1] = str(idx)
                
        print(arg)
        os.execv(sys.executable, ['python'] + arg)

root = '/home/ubuntu/CBSA-Discrimination/'
geckodriver_path = root + 'stores/geckodriver'
adblock_path = root + "stores/adblock_plus-3.3.1-an+fx.xpi"
uBlock_path = root + "stores/uBlock0@raymondhill.net.xpi"

ZIP_URL_PRE = 'https://www.trulia.com/for_rent/'
ZIP_URL_SUF = '_zip/date;d_sort/'#3_beds/2_baths/'
ZIP_URL_PAGE = '_p'

# read in zip code csv file 
if len(sys.argv) != 5: 
	print('-------------------------------------------------')
	print('REQUIRED ARGUMENTS:')
	print('python new_url_crawler.py logfile round day start')
	print('-------------------------------------------------')
	exit()

tz = pytz.timezone('America/Chicago')
logfile = sys.argv[1]
round_num = int(sys.argv[2])
day_num = int(sys.argv[3])
start = int(sys.argv[4])
zip_csv = root + "rounds/round_{}/round_{}_selected_zips.csv".format(round_num, round_num)
dest = root + "rounds/round_{}/round_{}_day_{}.csv".format(round_num, round_num, day_num)

logfile = sys.argv[1]
start = int(sys.argv[2])
zip_start = 0

if os.path.isfile(logfile) == True and start == 0:
	print("Warning - logfile exists but startpoint is 0. Please make sure that this is correct")

df_zip    = pd.read_csv(zip_csv) 
zip_list =  list(df_zip['ZIP'].values.flatten())
cbsa_list = list(df_zip['CBSA'].values.flatten())
downtown_list = list(df_zip['downtown'].values.flatten())

try:
	driver = start_firefox('https://www.trulia.com', geckodriver_path, adblock_path, uBlock_path)
except:
	print("Failed to start driver. Restarting...")
	sleep(random.randint(10,20))
	restart(logfile, start, True)

listings_all = []
with open(dest, "a+") as f:
	writer = csv.writer(f)
        if start == 0:
	        writer.writerow(["CBSA", "ZIP", "downtown", "URL", "page_number"])
	for i in range(start, len(zip_list)):
                zipcode = zip_list[i]
                cbsa = cbsa_list[i]
		downtown = downtown_list[i]
                if int(zipcode) < 10000:
                    zipcode = '0' + str(zipcode)
		zip_url = ZIP_URL_PRE + str(zipcode) + ZIP_URL_SUF 
		counter = zip_start
                print(zip_url)
                try:
                    driver.get(zip_url)
                except:
                    print("Unable to get URL. Most likely Timing Out. Restarting...")
                    driver.quit()
                    sleep(random.randint(10,40))
                    restart(logfile, start, True)
                if "this page" in driver.title.lower():
                    print ("Being blocked from accessing Trulia. Restarting...")
                    driver.quit()
                    sleep(random.randint(60,120))
                    restart(logfile, start, True)
		driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		num_listings = list(set(re.findall(r'\w*[0-9]* rentals? available on Trulia',driver.page_source)))
		#print('Page Number: ' + str(counter))
		num_pages    = 0
		if num_listings:
			num_pages    = math.ceil(float((num_listings[0].split(' ')[0]))/30)

		print('=======================================================================================')
		print('Index ' + str(i) + ' - Scraping ' + str(zipcode) + ' with ' + str(num_pages) + ' pages')
		while counter < num_pages: 
			driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
			listings_on_page = []

			next_cond   = EC.presence_of_element_located((By.CSS_SELECTOR,'#resultsColumn > div > div.resultsColumn > div.backgroundControls > div.backgroundBasic > div.paginationContainer.pls.mtl.ptl.mbm > div:nth-child(1) > a > i'))
			next_handle = wait_and_get(driver, next_cond, 15)

			listings_on_page = list(set(re.findall(r'\w*href="\W[a-z]\W[a-z][a-z][\w|\W]*?"',driver.page_source)))

			listings_on_page = [listing.replace('href="','https://www.trulia.com').replace('"','') for listing in listings_on_page]

			listings_on_page = [page for page in listings_on_page if page not in listings_all]
			listings_all = (listings_all) + listings_on_page
			listings_on_page = [[cbsa, zipcode, downtown, page, counter] for page in listings_on_page]
			writer.writerows(listings_on_page)
			#print(listings_on_page)
			f.flush()
                        if len(listings_on_page) != 0:
                            print('Page {}: Number of listings: {}'.format(counter + 1, len(listings_on_page)))
			    print('\tTotal length of listings: {}'.format(len(listings_all)))
                        else:
                            print("No listings on page {}".format(counter + 1))
			counter += 1
			if counter < num_pages:
				try:
					driver.get(zip_url+str(counter) + '_p')
				except:
					print ("Failed to get URL. Most likely timing out. Restarting at page {}...".format(counter))
                                        driver.quit()
                                        sleep(random.randint(60,120))
                                        restart(logfile, start, False)
				sleep(random.randint(2, 4))
				if "this page" in driver.title.lower():
					print ("Being blocked from accessing Trulia before finishing zipcode. Restarting at page {}...".format(counter))
		                    	driver.quit()
                    			sleep(random.randint(60,120))
                    			restart(logfile, start, False)
		
		zip_start = 0
                with open(logfile, "ab") as log:
                        filewriter = csv.writer(log, delimiter = ',', quoting = csv.QUOTE_MINIMAL)
                        filewriter.writerow([i])


driver.quit()

listings_all = list(set(listings_all))
listings_all  = pd.Series(listings_all)
df_listings   = pd.DataFrame()
df_listings['urls'] = listings_all
print("Number of URLS found: " + str(len(df_listings)))
finished = datetime.now(tz)
print("Time finished = {}".format(finished.strftime("%m/%d %H:%M:%S")))

