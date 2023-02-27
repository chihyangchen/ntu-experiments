# csv_processing
import sys
import os

dirname = sys.argv[1]

filenames = os.listdir(dirname)
for fname in filenames:
    if (fname[-4:] != '.csv' and 'ci' not in fname) or 'new' in fname:
        continue
    print(fname)
    f = open(os.path.join(sys.argv[1], fname), encoding="utf-8")
    f_out = os.path.join(sys.argv[1], fname[:-4]+'_new.csv')
    f2 = open(f_out, 'w')
    print("csv processing >>>>>")

    f_readlines = f.readlines()
    X = 0
    for l in f_readlines:
        x = len(l.split(','))
        X = x if x > X else X

    difference = X - len(f_readlines[0].split(','))
    f2.write(f_readlines[0][:-1]+',-'*difference+'\n')
    for l in f_readlines[1:]:
        f2.write(l)
    f.close()
    f2.close()