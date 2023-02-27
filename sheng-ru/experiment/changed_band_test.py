import os
import time

bands = [3,7,8]

count = 0
experiment_time = 600

os.chdir("/home/wmnlab/ntu-experiments/modem-utilities")

start_time = time.time()


while (time.time() - start_time) < experiment_time:

    choice = bands[int(count%3)]
    
    os.system(f"sudo ./band-setting.sh -i qc01 -l {choice}")

    time.sleep(30)

    choice2 = bands[int((count+1)%3)]
    
    os.system(f"sudo ./band-setting.sh -i qc01 -l {choice}")

    time.sleep(30)

    count+=1