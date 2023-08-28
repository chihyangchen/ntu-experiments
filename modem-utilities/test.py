import subprocess
import os
import re

# import pathlib
# print(pathlib.Path(__file__).parent.absolute())

dev = 'qc00'
# os.system(f'./get-pci-freq.sh -i {dev}')
out = subprocess.check_output(f'./get-pci-freq.sh -i {dev}', shell=True)
out = out.decode('utf-8')
lte_info = out.split('\n')[2]
nr_info = out.split('\n')[3]

print(lte_info.split(',')[7])
# print(lte_info.split(',')[5], lte_info.split(',')[6])
# print(nr_info.split(',')[3])