#!/usr/bin/python3

import os
import sys
import pandas as pd
import numpy

target=["time","qfe_wtr_pa0","qfe_wtr_pa1","qfe_wtr_pa2","qfe_wtr_pa3"]
target_nvme=["Sensor 1","Sensor 2","Sensor 3","Sensor 4"]
target_core=["Core 0","Core 1","Core 2","Core 3"]
target_sata=["drivetemp","temp1"]

l_qfe_wtr_pa0=[]
l_qfe_wtr_pa1=[]
l_qfe_wtr_pa2=[]
l_qfe_wtr_pa3=[]

l_sensor_nvme_1=[]
l_sensor_nvme_2=[]
l_sensor_nvme_3=[]
l_sensor_nvme_4=[]

l_sensor_core_0=[]
l_sensor_core_1=[]
l_sensor_core_2=[]
l_sensor_core_3=[]

l_sensor_sata_1=[]

m_export=[]

sata_en=False

#def check_content(input):
#	for item in target:
#		if(item in input[0]):
#			return input[1]



if __name__ == "__main__":
#	if(len(sys.argv) < 3):
#		print("enter file_in_path file_out_path")
#		sys.exit()
	file_in = sys.argv[1]
#	file_out = sys.argv[2]

	with open(file_in) as f:
		lines = f.readlines()
#		print (lines)
	for word in lines:
		word=word.split('"')
#		print(word)
		if (len(word) < 2):
			temp_system=word[0]
			tmp_for_sata = temp_system.split("-")
			if tmp_for_sata[0] == target_sata[0]:
				sata_en = True
			temp_system=temp_system.split(":")
			if (temp_system[0] == target_nvme[0]):
#				print(temp_system)
				temp_system=temp_system[1]
				temp_system=temp_system.split("°C")
				l_sensor_nvme_1.append(temp_system[0][-8:].split("+")[1])
#				print(l_sensor_nvme_1)
			elif (temp_system[0] == target_nvme[1]):
				temp_system=temp_system[1]
				temp_system=temp_system.split("°C")
				l_sensor_nvme_2.append(temp_system[0][-8:].split("+")[1])
#				print(temp_system)
			elif (temp_system[0] == target_nvme[2]):
				temp_system=temp_system[1]
				temp_system=temp_system.split("°C")
				l_sensor_nvme_3.append(temp_system[0][-8:].split("+")[1])
#				print(temp_system)
			elif (temp_system[0] == target_nvme[3]):
				temp_system=temp_system[1]
				temp_system=temp_system.split("°C")
				l_sensor_nvme_4.append(temp_system[0][-8:].split("+")[1])
#				print(temp_system)


			elif (temp_system[0] == target_core[0]):
#				print(temp_system)
				temp_system=temp_system[1]
				temp_system=temp_system.split("°C")
				l_sensor_core_0.append(temp_system[0][-8:].split("+")[1])
							
			elif (temp_system[0] == target_core[1]):
#				print(temp_system)
				temp_system=temp_system[1]
				temp_system=temp_system.split("°C")
				l_sensor_core_1.append(temp_system[0][-8:].split("+")[1])
			elif (temp_system[0] == target_core[2]):
#				print(temp_system)
				temp_system=temp_system[1]
				temp_system=temp_system.split("°C")
				l_sensor_core_2.append(temp_system[0][-8:].split("+")[1])
			elif (temp_system[0] == target_core[3]):
#				print(temp_system)
				temp_system=temp_system[1]
				temp_system=temp_system.split("°C")
				l_sensor_core_3.append(temp_system[0][-8:].split("+")[1])
#				print(l_sensor_core_3)
			
			elif (temp_system[0] == target_sata[1]) and sata_en:
				temp_system=temp_system[1]
				temp_system=temp_system.split("°C")
				l_sensor_sata_1.append(temp_system[0][-8:].split("+")[1])
				sata_en = False
		elif (len(word) > 2 and word[1] == target[1]):
#			print(word[3])
			l_qfe_wtr_pa0.append(word[3])
		elif (len(word) > 2 and word[1] == target[2]):
			l_qfe_wtr_pa1.append(word[3])
		elif (len(word) > 2 and word[1] == target[3]):
			l_qfe_wtr_pa2.append(word[3])
		elif (len(word) > 2 and word[1] == target[4]):
			l_qfe_wtr_pa3.append(word[3])
#	print(l_qfe_wtr_pa0)
#	print(l_qfe_wtr_pa1)
#	print(l_qfe_wtr_pa2)
#	print(l_qfe_wtr_pa3)
#	print(l_sensor_core_0)
#	print(l_sensor_core_1)
#	print(l_sensor_core_2)
#	print(l_sensor_core_3)
	
#	print(l_sensor_nvme_1)
#	print(l_sensor_nvme_2)
#	print(l_sensor_nvme_3)
#	print(l_sensor_nvme_4)

	print(l_sensor_sata_1)
	m_export.append(l_qfe_wtr_pa0)
	m_export.append(l_qfe_wtr_pa1)
	m_export.append(l_qfe_wtr_pa2)
	m_export.append(l_qfe_wtr_pa3)
	
	m_export.append(l_sensor_core_0)
	m_export.append(l_sensor_core_1)
	m_export.append(l_sensor_core_2)
	m_export.append(l_sensor_core_3)

	m_export.append(l_sensor_nvme_1)
	m_export.append(l_sensor_nvme_2)
	m_export.append(l_sensor_nvme_3)
	m_export.append(l_sensor_nvme_4)
	
	m_export.append(l_sensor_sata_1)
	print(m_export)

	print("")
	print(numpy.transpose(m_export))
	df = pd.DataFrame(numpy.transpose(m_export))
	df.to_csv('output.csv', index=False, header=False )
