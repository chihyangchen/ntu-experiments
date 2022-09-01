#!/usr/bin/python3
"""
    Author: Chih-Yang Chen
    Description:
        Get the target RM500Q system dev nodes and save to the target path.
        Need the shell script get-cdc-wdm-num.sh.
    Note:
        Interfaces of RM500Q should be named as quectelX. [X should be 0 to 3]

"""
import os
import argparse
parser = argparse.ArgumentParser(description='Process RM500Q interfaces (cdc-wdmX and ttyUSBX)')
parser.add_argument("-P", "--path", type=str,
                    help=":path to save", default="./")

args = parser.parse_args()

path = args.path
#print(path)

modem_interface = ["wwan0","quectel0","quectel1", "quectel2", "quectel3"]

for i in range(len(modem_interface)):
    os.system("./get-cdc-wdm-num.sh -i "+ modem_interface[i] + " -P " + path)
