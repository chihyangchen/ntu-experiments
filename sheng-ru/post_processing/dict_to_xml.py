# Author: Sheng-Ru Zemg
# Change dictionary file to xml format

import sys, os
import datetime
import xml.etree.ElementTree as ET

def dict_to_xml(dictionary, root_name='root'):
    root = ET.Element(root_name)
    for key, value in dictionary.items():
        if isinstance(value, dict):
            child = ET.Element('pair')
            child.set('key', key)
            child.set('type', 'dict')
            dict_element = dict_to_xml(value, root_name='dict')
            child.append(dict_element)

        elif isinstance(value, list):
            child = ET.Element('pair')
            child.set('key', key)
            child.set('type', 'list')
            list_element = ET.Element('list')
            for item in value:
                if isinstance(item, dict):
                    item_element = ET.Element('item')
                    item_element.set('type', 'dict')
                    dict_item_element = dict_to_xml(item, root_name= 'dict')
                    item_element.append(dict_item_element)
                    list_element.append(item_element)
                else:
                    item_element = ET.Element('item')
                    item_element.text = str(item)
                    list_element.append(item_element)
            child.append(list_element)
        else:
            child = ET.Element('pair')
            child.set('key', key)
            child.text = str(value)
        root.append(child)
    return root

def process(fname):
    print(f'processing {fname}. >>>>>>>>>>>>>>>>>>.')
    f = open(fname,'r')
    f_out = open(fname[:fname.find(".txt")]+"_new.txt",'w')
    l = f.readline()
    while l:
        res = eval(l)
        res['timestamp'] = res['timestamp'].strftime("%Y-%m-%d %H:%M:%S.%f")
        root_element = dict_to_xml(res, root_name='dm_log_packet')
        xml_string = ET.tostring(root_element, encoding='unicode')
        f_out.write(xml_string+'\n')
        l = f.readline()
    f_out.close()


if os.path.isdir(sys.argv[1]):

    dirname = sys.argv[1]
    filenames = os.listdir(dirname)
    for fname in filenames:
        
        if (fname[-4:] != '.txt' or not fname.startswith('diag_log_dict')):
            continue
        else:
            
            fname = os.path.join(dirname,fname)
            process(fname)

elif sys.argv[1].startswith('diag_log_dict') and sys.argv[1].endswith('.txt'):

    fname = sys.argv[1]
    process(fname)

else:

    print('Invalid Input!!!')