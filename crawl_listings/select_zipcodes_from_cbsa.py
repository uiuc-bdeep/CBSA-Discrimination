import os
import csv
import sys
import pandas as pd
import random
from datetime import date, timedelta, datetime
import pytz

if len(sys.argv) != 2:
    print("Must include destination as input")
    exit()

root = '/home/ubuntu/CBSA-Discrimination/'
cbsa_df = pd.read_csv(root + 'rounds/cbsa_zipcode_counts.csv')
dest = root + 'rounds/' + sys.argv[1]
sample_size = 0.05

def seperate_by_cbsa(cbsa_df):
    cbsa_dic = {}
    for i in range(length):
        cbsa = cbsa_df.at[i, "CBSA"]
        zipcode = cbsa_df.at[i, "ZIP"]
        num_listings = cbsa_df.at[i, "num_listings"]
        if cbsa in cbsa_dic.keys():
            cbsa_dic[cbsa].append((str(zipcode), int(num_listings)))
        else:
            cbsa_dic[cbsa] = [(str(zipcode), int(num_listings))]
    for key in cbsa_dic.keys():
        random.shuffle(cbsa_dic[key])
    return cbsa_dic

def write_selections_to_dest(selections, dest):
    with open(dest, "w") as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerow(["CBSA", "ZIP", "num_listings"])
        count = 0
        for cbsa in selections.keys():
            for p in selections[cbsa]:
                writer.writerow([cbsa, p[0], p[1]])
                count += 1
    print("Successfully written {} lines to {}".format(count, dest))

def select_zips_from_cbsa(cbsa, zip_counts):
    length = len(zip_counts)
    print("{} contains {} zipcodes".format(cbsa, length))
    selections = []
    too_low = 0
    for zipcode, num_listings in zip_counts:
        #if len(selections) >= (sample_size * length):
        if len(selections) > 20:
            break
        if num_listings > 30:
            selections.append((zipcode, num_listings))
            print("\tAppended zipcode {} with {} listings".format(zipcode, num_listings))
        else:
            too_low += 1
    if len(selections) < (sample_size * length):
        print(" ----  ERROR ----- \nOnly selected {} of {} expected listings ({} too low)\n ------------)".format(len(selections), (sample_size * length), too_low))
    else:
        print("\tSelected {} total listings ({} too low)".format(len(selections), too_low))
    return selections

length = cbsa_df.shape[0]
print("Total number of zipcodes = {}".format(length))
cbsa_dic = seperate_by_cbsa(cbsa_df)
selections = {}
for cbsa in cbsa_dic.keys():
    selections[cbsa] = select_zips_from_cbsa(cbsa, cbsa_dic[cbsa])
print(selections)
write_selections_to_dest(selections, dest)

