import sys
import os

os.chdir(os.path.dirname(sys.argv[0]))

if os.path.isdir(sys.argv[1]):

    dirname = sys.argv[1]
    
    os.system(f'python3 xml_mi_rrc.py {dirname}')
    os.system(f'python3 xml_mi_ml1.py {dirname}')
    os.system(f'python3 xml_mi_nr_ml1.py {dirname}')

else:
    print("what the hell is", sys.argv[1])