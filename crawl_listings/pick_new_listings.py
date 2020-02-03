import pandas as pd
import random
import sys
import csv

dest = '../rounds/new_urls_3_analysis.csv'

def get_listings_dic(new_listings_path):
	df = pd.read_csv(new_listings_path)
	dic = {}
	for idx in range(df.shape[0]):
		cbsa = df.at[idx, 'CBSA']
		zipcode = df.at[idx, 'ZIP']
		downtown = int(df.at[idx, 'downtown'])
		url = df.at[idx, 'URL']
		off_market = int(df.at[idx, 'Off_market'])
		try:
			days = int(df.at[idx, 'Days_On_Trulia'])
		except:
			days = -1
		if cbsa not in dic.keys():
			dic[cbsa] = {0: [], 1: []}
		dic[cbsa][downtown].append((zipcode, url, off_market, days))
	return dic

def write_listings_from_cbsa(writer, all_listings, cbsa, downtown):
	try:
		selection = random.sample(all_listings[cbsa][downtown], 3)
	except:
		print("ERROR: {} NOT ENOUGH LISTINGS AT {}".format(cbsa, downtown))
		selection = all_listings[cbsa][downtown]

	for zipcode, url in selection:
		writer.writerow([cbsa, zipcode, downtown, url])
	return len(selection)



if len(sys.argv) != 2:
	print("Must include new_listings file as input")
	exit()

new_listings_path = sys.argv[1]
all_listings = get_listings_dic(new_listings_path)

#num_written = 0
#with open(dest, 'w') as f:
#	writer = csv.writer(f, delimiter=',')
#	writer.writerow(['CBSA', 'ZIP', 'downtown', 'URL'])
#	for cbsa in all_listings.keys():
#		num_written += write_listings_from_cbsa(writer, all_listings, cbsa, 0)
#		num_written += write_listings_from_cbsa(writer, all_listings, cbsa, 1)

with open(dest, 'w') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerow(['CBSA', 'downtown', 'total_count', 'off_market', 'too_long', 'new', 'na'])
        for cbsa in all_listings.keys():
		for downtown in range(0, 2):
			off_market_count = 0
			too_long_count = 0
			na_count = 0
			new_count = 0
                	for zipcode, url, off_market, days in all_listings[cbsa][downtown]:
				if off_market != 0:
					off_market_count += 1
					continue
				if days == -1:
					na_count += 1
					continue
				if days >= 5:
					too_long_count += 1
				else:
					new_count += 1
			writer.writerow([cbsa, downtown, len(all_listings[cbsa][downtown]), off_market_count, too_long_count, new_count, na_count])

					

#print("Successfully written {}/300 listings to {}".format(num_written, dest))
