import os, subprocess

current_script_path = os.path.abspath(__file__)
dir_name = os.path.dirname(current_script_path)
for i in range(4):
    dir_name = os.path.dirname(dir_name)
dir_name = os.path.join(dir_name, 'modem-utilities')
print(dir_name)