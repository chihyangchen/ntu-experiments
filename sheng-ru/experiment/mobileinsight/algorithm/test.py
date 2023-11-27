import os, subprocess

os.chdir("../../../../modem-utilities/") # cd modem-utilities folder to use AT command.


# Use AT command to query modem current serving pci, earfcn
def query_pci_earfcn(dev):

    out = subprocess.check_output(f'./get-pci-freq.sh -i {dev}', shell=True)
    out = out.decode('utf-8')
    out = out.split('\n')
    
    if len(out) == 7: # ENDC Mode
        lte_info = out[2].split(',')
        nr_info = out[3].split(',')
        pci, earfcn, band = lte_info[5], lte_info[6], lte_info[7]
        nr_pci = nr_info[3]
        return (pci, earfcn, band, nr_pci)
    elif len(out) == 5: # LTE Mode
        lte_info = out[1].split(',')
        pci, earfcn, band = lte_info[7], lte_info[8], lte_info[9]
        return (pci, earfcn, band)
    
T = query_pci_earfcn('qc00')
print(T)


# print(len(o.split('\n')))    print(lte_info)