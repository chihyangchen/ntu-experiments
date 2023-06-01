# Author: Sheng-Ru Zemg
# Change dictionary file to xml format

import sys, os
import xml.etree.ElementTree as ET

def dict_to_xml(dictionary, root_name='root'):
    root = ET.Element(root_name)
    for key, value in dictionary.items():
        if isinstance(value, dict):
            child = dict_to_xml(value, key)
        else:
            child = ET.Element('pair')
            child.set('key', key)
            child.text = str(value)
        root.append(child)
    return root

dirname = sys.argv[1]

if os.path.isdir(sys.argv[1]):

    dirname = sys.argv[1]
    filenames = os.listdir(dirname)
    for fname in filenames:
        if (fname[-4:] != '.txt' or not fname.startswith('diag_log')):
            continue

elif sys.argv[1].startswith('diag_log') and sys.argv[1].endswith('.txt'):

    pass

else:

    print('Invalid Input!!!')