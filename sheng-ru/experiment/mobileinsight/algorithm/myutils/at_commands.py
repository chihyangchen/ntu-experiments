import os, subprocess
import re

class AT_Cmd_Runner():

    def __init__(self):
        current_script_path = os.path.abspath(__file__)
        dir_name = os.path.dirname(current_script_path)
        for _ in range(5):
            dir_name = os.path.dirname(dir_name)
        self.dir_name = os.path.join(dir_name, 'modem-utilities')  
        self.band_setting_sh = os.path.join(self.dir_name, 'band-setting.sh')
        self.get_pci_freq_sh = os.path.join(self.dir_name, 'get-pci-freq.sh')
        
    # Query modem current band setting
    def query_band(self, dev):

        out = subprocess.check_output(f'{self.band_setting_sh} -i {dev}', shell=True)
        out = out.decode('utf-8')
        inds = [m.start() for m in re.finditer("lte_band", out)]
        inds2 = [m.start() for m in re.finditer("\r", out)]
        result = out[inds[1]+len('"lte_band"'):inds2[2]]
        print(f'Current Band Setting of {dev} is {result}')
        
        return result
    
    # Use AT command to query modem current serving pci, earfcn
    def query_pci_earfcn(self, dev):

        out = subprocess.check_output(f'{self.get_pci_freq_sh} -i {dev}', shell=True)
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

    # Change band function
    def change_band(self, dev, band, setting):

        subprocess.Popen([f'{self.band_setting_sh} -i {dev} -l {band}'], shell=True)
        print(f"**********Change {dev} from {setting} to {band}.**********")

        