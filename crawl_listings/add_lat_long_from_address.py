import os
import json
import requests
import logging
import time
import random
import sys
import pandas as pd
from pprint import pprint

base_url = 'https://maps.googleapis.com/maps/api/geocode/json?address='
API_key = "AIzaSyCdBTNsiySS3FJRj3Om1U2Ph9YGdOGba5I"

#if len(sys.argv) != 2:
#	print("Must include rentals file as input")
#	exit()

def request_API(url):
	lat = 0
	lng = 0
	try:
		r = requests.get(url)
		response = json.loads(r.content)
		
		if response['status'] == 'OK':
			result = response['results']
			location = result[0]['geometry']['location']
			lat = location['lat']
			lng = location['lng']
			print(url, lat, lng)
		else:
			print("Request status is not OK: " + response['status'])
	except requests.exceptions.RequestException as e:
		print("ERROR: RequestException: " + str(e))
	
	return lat, lng

def get_coordinates(address, city, state):
	if not pd.isna(address):
		if '#' in str(address):
			address = address[:address.index('#') - 1]
		address = address + ', ' + city + ', ' + state
		address = address.replace(' ', '+')
		url = base_url + address + '&key=' + API_key
		lat, lng = request_API(url)
		return lat, lng
	else:
		return "NA", "NA"

#rentals_path = sys.argv[1]
#rentals = pd.read_csv(rentals_path)
#rentals['Latitude'] = rentals['Latitude'].astype(float)
#rentals['Longitude'] = rentals['Longitude'].astype(float)

#for i in range(rentals.shape[0]):
	#lat, lng = get_coordinates(rentals.at[i, "Address"], rentals.at[i, "City"], rentals.at[i, "State"])
	#print(lat, lng)
	#rentals.at[i, "Latitude"] = lat
	#rentals.at[i, "Longitude"] = lng

#rentals.to_csv(rentals_path, index=False, na_rep='NA')
#print("Finished")
