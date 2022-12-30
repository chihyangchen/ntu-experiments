
# Autohr: Chih-Yang Chen

# This script is to filter the information from an USB GPS dongle.

# Raw data informationi as below

#{"class":"TPV","device":"/dev/serial/by-id/usb-Prolific_Technology_Inc._USB-Serial_Controller_BSEIb115818-if00-port0","status":2,"mode":3,"time":"2022-12-30T02:15:55.000Z","leapseconds":18,"ept":0.005,"lat":25.018763400,"lon":121.541787000,"altHAE":54.993,"altMSL":37.934,"alt":37.934,"epx":3.316,"epy":3.502,"epv":11.333,"track":64.0314,"magtrack":261.4915,"magvar":-4.6,"speed":0.044,"climb":-0.046,"epd":82.0129,"eps":0.67,"epc":31.75,"ecefx":-3025301.44,"ecefy":4928770.90,"ecefz":2680981.32,"ecefvx":-0.02,"ecefvy":0.05,"ecefvz":-0.02,"ecefpAcc":14.08,"ecefvAcc":0.67,"velN":-0.001,"velE":-0.010,"velD":0.046,"geoidSep":19.364,"eph":8.355,"sep":90.440}

# Goal is to filter the time information and the lontitude and latitude information.
# Input: file contains the sample raw data
# Output: array with time, lontitude and latitude

import sys, csv
from datetime import datetime,timedelta

showresult = True

def main(file_path):
	print("GPS information filter tool")
	output = []
	output.append(["time","lon","lat"])
	target = ["time","lon","lat"]
	time = lon = lat = "" 
	# read the sample
	with open(file_path) as file:
		for line in file:
			# line by line split
			data_list = line.split(",")
			for i, elem in enumerate(data_list):
			    # filter the "time" information
			    # filter the "lon" inforamtion
			    # filter the "lat" information
				if(target[0] in elem):
					time = data_list[i].split('T')[1][:-2].split('.')[0]
					time =str(datetime.strptime(time,'%H:%M:%S')+timedelta(hours=8)).split(' ')[1]
				elif(target[1] in elem):
					lon = data_list[i].split(':')[1]
				elif(target[2] in elem):
					lat = data_list[i].split(':')[1]
				
				# put them into a single array and append into output
				if (time != "" and lon != "" and lat != ""):	
					filter_data = [time,lon,lat]
					output.append(filter_data)
					time = lon = lat = "" 
	if (showresult):
		print(output)
	# save to CSV or else
	with open(file_path + '.csv', 'w') as file:
		writer = csv.writer(file, delimiter=',')
		writer.writerows(output)

if __name__ == '__main__':
	if (len(sys.argv) > 1):
		main(sys.argv[1])
	else:
		print("nothing to do, please enter the file path")


