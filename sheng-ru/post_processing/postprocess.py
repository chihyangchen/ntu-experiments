import os
import sys

dirname = sys.argv[1]


for a in sorted(os.listdir(dirname)):
    print(a)
    d0 = os.path.join(dirname, a)
    if a == 'ml_data':
        continue
    for b in sorted(os.listdir(d0)):
        # print(os.path.join(d0, b, 'data'))
        os.system("python3 "  + " xml_mi_rrc.py " + os.path.join(d0, b, 'data'))
        os.system("python3 " + " xml_mi_ml1.py " + os.path.join(d0, b, 'data'))
        os.system("python3 " + " xml_mi_nr_ml1.py " + os.path.join(d0, b, 'data'))
        os.system("python3 " + " csv_processing.py " + os.path.join(d0, b, 'data'))