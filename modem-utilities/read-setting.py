#!/usr/bin/python3

import os
import sys
content=["IPv4 address","IPv4 subnet mask","IPv4 gateway address","CID"]

def check_content(input):
    for item in content:
        if(item in input[0]):
            return input[1]



if __name__ == "__main__":
    if(len(sys.argv) < 3):
        print("enter file_in_path file_out_path")
        sys.exit()
    file_in = sys.argv[1]
    file_out = sys.argv[2]

    #with open('/tmp/temp-ip1') as f:
    with open(file_in) as f:
        lines = f.readlines()
    #with open('abc.txt', 'w') as temp_file:
    with open(file_out, 'w') as temp_file:
        for word in lines:
            word=word.split(':')
            output=check_content(word)
            if(output != None):
                if("'" in output):
                    output=output.split("'")[1]
                    temp_file.write(output)
                else:
                    temp_file.write(output[1:])
                #print(output)
    #os.system("cat abc.txt")
