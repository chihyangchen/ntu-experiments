#!/usr/bin/python3

import os
import sys
import pandas as pd
import numpy
target_module_1='m21'
target_module_2='m22'

target=["time","qfe_wtr_pa0","qfe_wtr_pa1","qfe_wtr_pa2","qfe_wtr_pa3","ipa-usr"] #"mdm-5g-usr"]
target_nvme=["Sensor 1","Sensor 2","Sensor 3","Sensor 4"]
target_core=["Core 0","Core 1","Core 2","Core 3"]
target_sata=["drivetemp","temp1"]

l_qfe_wtr_pa0_1=[]
l_qfe_wtr_pa1_1=[]
l_qfe_wtr_pa2_1=[]
l_qfe_wtr_pa3_1=[]
l_mdm_5g_usr_1=[]


l_qfe_wtr_pa0_2=[]
l_qfe_wtr_pa1_2=[]
l_qfe_wtr_pa2_2=[]
l_qfe_wtr_pa3_2=[]
l_mdm_5g_usr_2=[]

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
module1_en=False
module2_en=False


if __name__ == "__main__":
	file_in = sys.argv[1]
#	file_out = sys.argv[2]

	with open(file_in) as f:
		lines = f.readlines()
#		print (lines)
	for word in lines:
		dev=word.split(',')
		if dev[-1][:-1] == target_module_1:
			module1_en = True
			module2_en = False
		elif dev[-1][:-1] == target_module_2:
			module1_en = False
			module2_en = True 
		word=word.split('"')
#		print(dev)
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
			if module1_en:
				l_qfe_wtr_pa0_1.append(word[3])
			elif module2_en:
				l_qfe_wtr_pa0_2.append(word[3])
		elif (len(word) > 2 and word[1] == target[2]):
			if module1_en:
				l_qfe_wtr_pa1_1.append(word[3])
			elif module2_en:
				l_qfe_wtr_pa1_2.append(word[3])
		elif (len(word) > 2 and word[1] == target[3]):
			if module1_en:
				l_qfe_wtr_pa2_1.append(word[3])
			elif module2_en:
				l_qfe_wtr_pa2_2.append(word[3])
		elif (len(word) > 2 and word[1] == target[4]):
			if module1_en:
				l_qfe_wtr_pa3_1.append(word[3])
			elif module2_en:
				l_qfe_wtr_pa3_2.append(word[3])
		elif (len(word) > 2 and word[1] == target[5]):
			if module1_en:
				l_mdm_5g_usr_1.append(word[3])
			elif module2_en:
				l_mdm_5g_usr_2.append(word[3])
#	print(l_mdm_5g_usr_1)
#	print(l_qfe_wtr_pa0_2)
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

#	m_export.append(l_mdm_5g_usr_1)
#	df = pd.DataFrame(numpy.transpose(m_export))
#	df.to_csv('output.csv', index=False, header=False )

	m_export.append(l_qfe_wtr_pa0_1)
	m_export.append(l_qfe_wtr_pa1_1)
	m_export.append(l_qfe_wtr_pa2_1)
	m_export.append(l_qfe_wtr_pa3_1)
	
	m_export.append(l_mdm_5g_usr_2)
	m_export.append(l_qfe_wtr_pa0_2)
	m_export.append(l_qfe_wtr_pa1_2)
	m_export.append(l_qfe_wtr_pa2_2)
	m_export.append(l_qfe_wtr_pa3_2)
	
	m_export.append(l_sensor_core_0)
	m_export.append(l_sensor_core_1)
	m_export.append(l_sensor_core_2)
	m_export.append(l_sensor_core_3)

	m_export.append(l_sensor_nvme_1)
	m_export.append(l_sensor_nvme_2)
	m_export.append(l_sensor_nvme_3)
	m_export.append(l_sensor_nvme_4)
	
	m_export.append(l_sensor_sata_1)
#	print(m_export)
"""
	print("")
	print(numpy.transpose(m_export))
	df = pd.DataFrame(numpy.transpose(m_export))
	df.to_csv('output.csv', index=False, header=False )
"""
