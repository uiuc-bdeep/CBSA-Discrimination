import os
import csv
import sys
import pandas as pd
import random
from datetime import date, timedelta, datetime
import pytz

if len(sys.argv) != 2:
    print("Must include round number as input")
    exit()

root = '/home/ubuntu/CBSA-Discrimination/'
cbsa_df = pd.read_csv(root + 'rounds/cbsa_zipcode_counts.csv')
round_num = sys.argv[1]
new_dir = root + 'rounds/round_' + str(round_num)
if not os.path.exists(new_dir):
	os.mkdir(new_dir)
	print("Creating directory " + new_dir)
else:
	print("Directory {} already exists. Double check the round_number".format(new_dir))
	exit()
dest = new_dir + "/round_{}_selected_zips.csv".format(round_num)
print("Writing to " + dest)

sample_size = 4 # Select 4 zipcodes downtown and 4 zipcodes uptown for each CBSA

def seperate_by_cbsa(cbsa_df):
    cbsa_dic = {}
    for i in range(length):
        cbsa = cbsa_df.at[i, "CBSA"]
        zipcode = cbsa_df.at[i, "ZIP"]
        num_listings = cbsa_df.at[i, "num_listings"]
	downtown = cbsa_df.at[i, "downtown"]
        if cbsa in cbsa_dic.keys():
            cbsa_dic[cbsa].append((str(zipcode), int(num_listings), int(downtown)))
        else:
            cbsa_dic[cbsa] = [(str(zipcode), int(num_listings), int(downtown))]
    for key in cbsa_dic.keys():
        random.shuffle(cbsa_dic[key])
    return cbsa_dic

def write_selections_to_dest(selections, dest):
    with open(dest, "w") as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerow(["CBSA", "ZIP", "num_listings", "downtown"])
        count = 0
        for cbsa in selections.keys():
            for p in selections[cbsa][0]:
                writer.writerow([cbsa, p[0], p[1], 0])
                count += 1
	    for p in selections[cbsa][1]:
		writer.writerow([cbsa, p[0], p[1], 1])
		count += 1
    print("Successfully written {} lines to {}".format(count, dest))

def select_zips_from_cbsa(cbsa, zip_counts):
    length = len(zip_counts)
    print("{} contains {} zipcodes".format(cbsa, length))
    selections = {0: [], 1: []}
    too_low = 0
    for zipcode, num_listings, downtown in zip_counts:
        #if len(selections) >= (sample_size * length):
        if len(selections[0]) >= sample_size and len(selections[1]) >= sample_size:
            break
        if num_listings > 30:
	    if downtown == 0 and len(selections[0]) < sample_size:
            	selections[0].append((zipcode, num_listings))
	    elif downtown == 1 and len(selections[1]) < sample_size:
		selections[1].append((zipcode, num_listings))
            print("\tAppended zipcode {} with {} listings".format(zipcode, num_listings))
        else:
            too_low += 1
    num_picked = len(selections[0]) + len(selections[1])
    if num_picked != (2* sample_size):
        print(" ----  ERROR ----- CBSA {} only received {} zipcodes".format(cbsa, num_picked))
    #else:
    #    print("\tSelected {} total listings ({} too low)".format(len(selections), too_low))
    return selections

length = cbsa_df.shape[0]
print("Total number of zipcodes = {}".format(length))
cbsa_dic = seperate_by_cbsa(cbsa_df)
selections = {}
for cbsa in cbsa_dic.keys():
    selections[cbsa] = select_zips_from_cbsa(cbsa, cbsa_dic[cbsa])
write_selections_to_dest(selections, dest)

