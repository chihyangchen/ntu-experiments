#!/usr/bin/python3

import os
import sys
#import numpy

target_nvme=["Sensor 1","Sensor 2","Sensor 3","Sensor 4"]
target_core=["Core 0","Core 1","Core 2","Core 3"]


l_sensor_nvme_1=[]
l_sensor_nvme_2=[]
l_sensor_nvme_3=[]
l_sensor_nvme_4=[]

l_sensor_core_0=[]
l_sensor_core_1=[]
l_sensor_core_2=[]
l_sensor_core_3=[]

def SAVE_FUNC(my_file,content):
	with open(my_file, 'w') as f:
		for line in content:
			f.write("%s\n" % line)


if __name__ == "__main__":
#	if(len(sys.argv) < 3):
#		print("enter file_in_path file_out_path")
#		sys.exit()
	file_in = sys.argv[1]
	file_out = sys.argv[2]

	with open(file_in) as f:
		lines = f.readlines()
#		print (lines)
	for word in lines:
		word=word.split('"')
#		print(word)
		if (len(word) < 2):
			temp_system=word[0]
			temp_system=temp_system.split(":")
			if (temp_system[0] == target_nvme[0]):
#				print(temp_system)
				temp_system=temp_system[1]
				temp_system=temp_system.split("°C")
				l_sensor_nvme_1.append(temp_system[0][-7:].split("+")[1].split(".")[0])
#				print(l_sensor_nvme_1)
#				print(temp_system[0][-5:])
			elif (temp_system[0] == target_nvme[1]):
				temp_system=temp_system[1]
				temp_system=temp_system.split("°C")
				l_sensor_nvme_2.append(temp_system[0][-7:].split("+")[1].split(".")[0])
#				print(temp_system)
			elif (temp_system[0] == target_nvme[2]):
				temp_system=temp_system[1]
				temp_system=temp_system.split("°C")
				l_sensor_nvme_3.append(temp_system[0][-7:].split("+")[1].split(".")[0])
#				print(temp_system)
			elif (temp_system[0] == target_nvme[3]):
				temp_system=temp_system[1]
				temp_system=temp_system.split("°C")
				l_sensor_nvme_4.append(temp_system[0][-7:].split("+")[1].split(".")[0])
#				print(temp_system)


			elif (temp_system[0] == target_core[0]):
#				print(temp_system)
				temp_system=temp_system[1]
				temp_system=temp_system.split("°C")
				l_sensor_core_0.append(temp_system[0][-7:].split("+")[1].split(".")[0])
							
			elif (temp_system[0] == target_core[1]):
#				print(temp_system)
				temp_system=temp_system[1]
				temp_system=temp_system.split("°C")
				l_sensor_core_1.append(temp_system[0][-7:].split("+")[1].split(".")[0])
			elif (temp_system[0] == target_core[2]):
#				print(temp_system)
				temp_system=temp_system[1]
				temp_system=temp_system.split("°C")
				l_sensor_core_2.append(temp_system[0][-7:].split("+")[1].split(".")[0])
			elif (temp_system[0] == target_core[3]):
#				print(temp_system)
				temp_system=temp_system[1]
				temp_system=temp_system.split("°C")
				l_sensor_core_3.append(temp_system[0][-7:].split("+")[1].split(".")[0])
#				print(l_sensor_core_3)
	SAVE_FUNC(file_out + "monitor_core0_temperature",l_sensor_core_0)
	SAVE_FUNC(file_out + "monitor_core1_temperature",l_sensor_core_1)
	SAVE_FUNC(file_out + "monitor_core2_temperature",l_sensor_core_2)
	SAVE_FUNC(file_out + "monitor_core3_temperature",l_sensor_core_3)
	SAVE_FUNC(file_out + "monitor_nvme_temperature",l_sensor_nvme_1)

