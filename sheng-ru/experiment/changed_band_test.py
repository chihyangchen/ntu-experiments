import os
import time

bands = ['3:7','7:8','8']

count = 0
experiment_time = 300

os.chdir("/home/wmnlab/ntu-experiments/modem-utilities")

start_time = time.time()


while (time.time() - start_time) < experiment_time:

    choice = bands[int(count%3)]
    
    os.system(f"sudo ./band-setting.sh -i qc00 -l {choice}")

    time.sleep(20)

    count+=1