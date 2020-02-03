import sys
import csv
import pandas as pd
from tqdm import tqdm

if len(sys.argv) != 3:
	print("Must include two url csvs as input")
	exit()

day1 = sys.argv[1]
day2 = sys.argv[2]
destination = "../rounds/new_urls_3_2-3.csv"
print("Day 1: " + day1)
print("Day 2: " + day2)

df_1 = pd.read_csv(day1)
urls_1 = df_1['URL'].values.flatten()
print(urls_1)

df_2 = pd.read_csv(day2)
result = []
for idx in tqdm(range(df_2.shape[0]), desc="Finding new listings", bar_format="{l_bar}{bar}|   "):
	url = df_2.at[idx, 'URL']
	cbsa = df_2.at[idx, 'CBSA']
	zipcode = df_2.at[idx, 'ZIP']
	downtown = df_2.at[idx, 'downtown']
	if url not in urls_1:
		result.append([cbsa, zipcode, downtown, url])

with open(destination, 'w') as f:
	csv_writer = csv.writer(f, delimiter=',')
	csv_writer.writerow(["CBSA", "ZIP", "downtown", "URL"])
	for url in result:
		csv_writer.writerow(url)

print("Total new URLs: {}".format(len(result)))
print("Results written to " + destination)
